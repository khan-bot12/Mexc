from fastapi import FastAPI, Request
import uvicorn
import logging
from trade import place_order

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"Incoming webhook data: {data}")

        # Extract data from webhook
        action = data.get("action")
        symbol = data.get("symbol")
        quantity = float(data.get("quantity"))
        leverage = int(data.get("leverage"))

        logger.info(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        # Place the order
        result = place_order(action, symbol, quantity, leverage)
        logger.info(f"📤 Result from place_order: {result}")
        return {"status": "ok", "result": result}

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

# Optional: Run this if using `python main.py` locally
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
