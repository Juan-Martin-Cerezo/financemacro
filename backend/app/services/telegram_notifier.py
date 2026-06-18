import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Sends push messages via Telegram bot API.

    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to be set in .env.
    Silent no-op when either is missing.
    """

    BASE = "https://api.telegram.org/bot"

    async def send_message(self, text: str) -> bool:
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            logger.debug("Telegram not configured — skipping message")
            return False

        url = f"{self.BASE}{settings.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": settings.telegram_chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                logger.info("Telegram notification sent: %.80s", text)
                return True
        except Exception as e:
            logger.error("Telegram notification failed: %s", e)
            return False

    async def notify_liquidity_deficit(
        self,
        net_balance: float,
        envelope_targets_total: float,
        user_id: str,
    ) -> bool:
        deficit = envelope_targets_total - net_balance
        text = (
            "🚨 *Liquidity Deficit Alert – FinanceMacro*\n\n"
            f"Net Balance: `${net_balance:.2f}`\n"
            f"Envelope Targets: `${envelope_targets_total:.2f}`\n"
            f"*Deficit: `${deficit:.2f}`*\n\n"
            f"Your envelope commitments exceed available funds. "
            f"Consider allocating more liquidity or reducing targets."
        )
        return await self.send_message(text)
