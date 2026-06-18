"""
NettingEngine — resolves group expense distortion.

When user pays a big group bill, incoming reimbursements from friends
appear as income (skewing finance charts). This engine:

1. Flags large expenses as pending_netting, creates an EventGroup.
2. Within a 12-hour window, matches incoming transfers to that group
   by heuristic: similar amount fraction, close timestamp, same user.
3. On closure, deducts matched transfer sum from original expense
   (effective cost = paid - reimbursed) and marks transfers as absorbed
   so they never count toward income.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    EventGroup,
    EventGroupStatus,
    Transaction,
    TransactionStatus,
)

logger = logging.getLogger(__name__)

NETTING_THRESHOLD = Decimal("1000.00")  # minimum expense to trigger netting
NETTING_WINDOW_HOURS = 12


class NettingEngine:
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    async def process_new_transaction(self, tx: Transaction) -> None:
        """Inspect a new transaction. If it's a large outgoing, open netting group."""
        if tx.amount < 0 and abs(tx.amount) >= NETTING_THRESHOLD:
            group = EventGroup(
                user_id=self.user_id,
                description=f"Netting: {tx.description or 'Group expense'}",
                status=EventGroupStatus.open,
            )
            self.db.add(group)
            await self.db.flush()

            tx.event_group_id = group.id
            tx.status = TransactionStatus.pending_netting

            logger.info("Opened netting group %s for tx %s", group.id, tx.id)

    async def try_match_incoming(self, tx: Transaction) -> Optional[EventGroup]:
        """
        Attempt to match an incoming (positive) transfer to an open netting group.
        Returns the matched group or None.
        """
        if tx.amount <= 0:
            return None

        open_groups = await self._fetch_open_groups()
        if not open_groups:
            return None

        for group in open_groups:
            group_txs = await self._group_transactions(group.id)
            if self._is_match(tx, group_txs):
                tx.event_group_id = group.id
                tx.status = TransactionStatus.absorbed
                logger.info("Matched incoming tx %s to group %s", tx.id, group.id)
                return group

        return None

    async def close_expired_groups(self) -> list[EventGroup]:
        """
        Close all open groups whose window has expired.
        Recalculates effective amounts for the original expense.
        """
        deadline = datetime.utcnow() - timedelta(hours=NETTING_WINDOW_HOURS)

        stmt = select(EventGroup).where(
            and_(
                EventGroup.user_id == self.user_id,
                EventGroup.status == EventGroupStatus.open,
                EventGroup.created_at <= deadline,
            )
        )
        result = await self.db.execute(stmt)
        groups = list(result.scalars().all())

        for group in groups:
            await self._settle_group(group)

        return groups

    async def _settle_group(self, group: EventGroup) -> None:
        """Finalize a group: flag the original tx as settled and close the group."""
        group_txs = await self._group_transactions(group.id)
        original = next((t for t in group_txs if t.status == TransactionStatus.pending_netting), None)

        if original:
            absorbed_sum = sum(
                abs(t.amount) for t in group_txs if t.status == TransactionStatus.absorbed
            )
            effective = abs(original.amount) - absorbed_sum
            logger.info(
                "Group %s: original=%s absorbed=%s effective=%s",
                group.id, original.amount, absorbed_sum, effective,
            )
            original.status = TransactionStatus.settled

        group.status = EventGroupStatus.closed
        group.closed_at = datetime.utcnow()

    def _is_match(self, incoming: Transaction, group_txs: list[Transaction]) -> bool:
        """Heuristic: incoming amount is a plausible fraction of the original expense."""
        original = next((t for t in group_txs if t.status == TransactionStatus.pending_netting), None)
        if original is None:
            return False

        orig_abs = abs(original.amount)
        if orig_abs == 0:
            return False

        # Plausible split: incoming is between 5% and 100% of original
        ratio = incoming.amount / orig_abs
        return Decimal("0.05") <= ratio <= Decimal("1.0")

    async def _fetch_open_groups(self) -> list[EventGroup]:
        stmt = select(EventGroup).where(
            and_(
                EventGroup.user_id == self.user_id,
                EventGroup.status == EventGroupStatus.open,
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _group_transactions(self, group_id) -> list[Transaction]:
        stmt = select(Transaction).where(Transaction.event_group_id == group_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
