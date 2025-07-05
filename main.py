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

        action = str(data.get("action", "")).lower()
        symbol = data.get("symbol", "").upper()
        quantity = float(data.get("quantity", 0))
        leverage = int(data.get("leverage", 1))

        logging.info(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        result = place_order(symbol, action, quantity, leverage)
        logging.info(f"📤 Result from place_order: {result}")
        return result

    except Exception as e:
        logging.error(f"❌ Error processing webhook: {e}")
        return {"error": str(e)}
