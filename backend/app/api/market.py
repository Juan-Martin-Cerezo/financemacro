import asyncio
import json
import logging
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()

MOCK_TICKERS = {
    "USD_MEP": {"price": 1210.50, "change": 0.15},
    "CEDEAR_GGAL": {"price": 8500.25, "change": -0.42},
    "CEDEAR_MELI": {"price": 6200.00, "change": 1.10},
    "SP500": {"price": 5500.80, "change": 0.33},
}


async def mock_price_generator():
    """Yields randomised tick data each cycle, simulating live WebSocket ticks."""
    import random
    while True:
        for symbol, base in MOCK_TICKERS.items():
            drift = base["price"] * random.uniform(-0.005, 0.005)
            yield {
                "symbol": symbol,
                "price": round(base["price"] + drift, 2),
                "change": round(base["change"] + random.uniform(-0.1, 0.1), 2),
                "timestamp": datetime.utcnow().isoformat(),
            }
        await asyncio.sleep(2)


@router.websocket("/api/v1/market/ws")
async def market_websocket(ws: WebSocket):
    """Live market quotes via WebSocket. Sends mock tick data every 2s."""
    await ws.accept()
    logger.info("Market WS connected")
    gen = mock_price_generator()
    try:
        async for tick in gen:
            await ws.send_text(json.dumps(tick))
    except WebSocketDisconnect:
        logger.info("Market WS disconnected")
