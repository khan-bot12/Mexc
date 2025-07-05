# main.py

from fastapi import FastAPI, Request
import logging
from trade import place_order

app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logging.info(f"Incoming webhook data: {data}")

        action = data.get("action")
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        leverage = data.get("leverage")

        logging.info(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        result = place_order(action, symbol, quantity, leverage)
        logging.info(f"📤 Result from place_order: {result}")

        return {"status": "success", "result": result}

    except Exception as e:
        logging.error(f"❌ Exception: {e}")
        return {"status": "error", "message": str(e)}
