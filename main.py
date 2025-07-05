from fastapi import FastAPI, Request
import logging
import os
from trade import place_order

# Initialize app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional token protection (uncomment if using)
SECRET_TOKEN = os.getenv("WEBHOOK_TOKEN")

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"Incoming webhook data: {data}")

        # Optional token check (uncomment if using token in alerts)
        # if SECRET_TOKEN and data.get("token") != SECRET_TOKEN:
        #     return {"error": "Unauthorized"}

        # Parse and normalize
        action = str(data.get("action")).lower()
        symbol = str(data.get("symbol")).upper()
        quantity = float(data.get("quantity"))
        leverage = int(data.get("leverage"))

        logger.info(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        # Place the order
        result = place_order(action, symbol, quantity, leverage)

        logger.info(f"📤 Result from place_order: {result}")
        return result

    except Exception as e:
        logger.exception(f"❌ Error processing webhook: {e}")
        return {"error": str(e)}
