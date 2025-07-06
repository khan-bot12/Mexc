from fastapi import FastAPI, Request
import uvicorn
import logging
import os
from trade import place_order

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("main")

# FastAPI app
app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"📥 Incoming webhook: {data}")

        # Extract and validate fields
        action = data.get("action")
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        leverage = data.get("leverage")

        if not all([action, symbol, quantity, leverage]):
            logger.error("❌ Missing required fields in webhook payload.")
            return {"error": "Missing required fields"}

        logger.info(f"⚡ Parsed: {action} {quantity} {symbol} @ {leverage}x")

        result = place_order(action, symbol, quantity, leverage)
        logger.info(f"📤 Result from place_order: {result}")
        return result

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        return {"error": str(e)}

# For local testing (if needed)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
