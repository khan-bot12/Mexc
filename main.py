from fastapi import FastAPI, Request
import logging
from trade import place_order

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"Incoming webhook data: {data}")

        action = data.get("action")
        symbol = data.get("symbol")
        quantity = float(data.get("quantity"))
        leverage = int(data.get("leverage"))

        logger.info(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        result = place_order(action, symbol, quantity, leverage)
        logger.info(f"📤 Result from place_order: {result}")

        return {"status": "ok", "result": result}

    except Exception as e:
        logger.exception("❌ Error processing webhook:")
        return {"status": "error", "message": str(e)}
