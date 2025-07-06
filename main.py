from fastapi import FastAPI, Request
import logging
from trade import place_order
import uvicorn
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"📥 Incoming webhook data: {data}")

        # Validate required fields
        required_fields = ["action", "symbol", "quantity", "leverage"]
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields in webhook payload")

        action = data["action"].lower()
        symbol = data["symbol"].replace("-", "_")  # Format for futures
        quantity = data["quantity"]
        leverage = data["leverage"]

        logger.info(f"📦 Parsed → Action: {action}, Symbol: {symbol}, Quantity: {quantity}, Leverage: {leverage}")

        result = place_order(action, symbol, quantity, leverage)
        logger.info(f"📤 Order Result: {result}")

        if "error" in result:
            return {"status": "error", "message": result["error"]}
        return {"status": "success", "data": result}

    except Exception as e:
        logger.error(f"❌ Webhook Error: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)
