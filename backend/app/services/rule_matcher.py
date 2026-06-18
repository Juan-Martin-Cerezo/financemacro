"""
RuleMatcher — deterministic transaction categorisation via keyword matching.

Rules are user-defined: each rule binds a keyword to a category.
When a transaction arrives without a category, RuleMatcher scans
all active rules for that user and assigns the first match.

Matching is case-insensitive substring search against the transaction
description. Rules are ordered by creation (oldest first) so the user
can rely on first-match-wins semantics.
"""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import CategorizationRule, Transaction

logger = logging.getLogger(__name__)


class RuleMatcher:
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id
        self._rules: Optional[list[CategorizationRule]] = None

    async def _load_rules(self) -> list[CategorizationRule]:
        if self._rules is None:
            stmt = (
                select(CategorizationRule)
                .where(CategorizationRule.user_id == self.user_id)
                .options(selectinload(CategorizationRule.category))
                .order_by(CategorizationRule.created_at)
            )
            result = await self.db.execute(stmt)
            self._rules = list(result.scalars().all())
        return self._rules

    def invalidate_cache(self) -> None:
        """Call after a rule is created/updated/deleted."""
        self._rules = None

    async def match(self, tx: Transaction) -> Optional[CategorizationRule]:
        """
        Find the first rule whose keyword appears in the transaction description.
        Returns the matched rule (caller sets tx.category_id from it).
        """
        rules = await self._load_rules()
        desc = (tx.description or "").lower()

        for rule in rules:
            if rule.keyword.lower() in desc:
                logger.debug("Rule %s matched tx %s (keyword='%s')", rule.id, tx.id, rule.keyword)
                return rule

        return None

    async def apply(self, tx: Transaction) -> bool:
        """
        Match and assign category to a transaction in one call.
        Returns True if a rule matched, False otherwise.
        """
        rule = await self.match(tx)
        if rule is not None:
            tx.category_id = rule.category_id
            return True
        return False

    async def apply_batch(self, transactions: list[Transaction]) -> int:
        """
        Apply rules to multiple uncategorised transactions.
        Returns count of transactions categorised.
        """
        count = 0
        for tx in transactions:
            if tx.category_id is None:
                if await self.apply(tx):
                    count += 1
        return count
