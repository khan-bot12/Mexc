from fastapi import FastAPI, Request
import logging
from trade import place_order

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"Incoming webhook data: {data}")

        # Extract and validate fields
        action = str(data.get("action")).lower()
        symbol = str(data.get("symbol")).upper()
        quantity = float(data.get("quantity"))
        leverage = int(data.get("leverage"))

        logger.info(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        # Call place_order from trade.py
        result = place_order(action, symbol, quantity, leverage)
        logger.info(f"📤 Result from place_order: {result}")

        return {"status": "success", "details": result}
    
    except Exception as e:
        logger.error(f"❌ Error in webhook handler: {e}")
        return {"status": "error", "message": str(e)}
