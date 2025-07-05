from fastapi import FastAPI, Request
import logging
import uvicorn
import json
from trade import place_order, get_positions

app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logging.info(f"Incoming webhook data: {data}")

        # Parse and validate data
        action = data.get("action", "").lower()
        symbol = data.get("symbol", "").upper()
        quantity = float(data.get("quantity", 0))
        leverage = int(data.get("leverage", 1))

        logging.info(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        # Optional: View current positions (for debugging or logic)
        logging.info("📊 Getting current positions...")
        get_positions(symbol)

        # Place order
        result = place_order(action, symbol, quantity, leverage)
        logging.info(f"📤 Result from place_order: {result}")
        return {"status": "ok", "detail": result}

    except Exception as e:
        logging.exception(f"❌ Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

# Optional: If you want to run locally
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
