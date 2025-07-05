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
        quantity = float(data.get("quantity"))
        leverage = int(data.get("leverage"))

        logging.info(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        # Correct argument order
        result = place_order(symbol, quantity, leverage, action)

        logging.info(f"📤 Result from place_order: {result}")
        return {"status": "ok", "result": result}

    except Exception as e:
        logging.error(f"❌ Error processing webhook: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
