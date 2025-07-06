from fastapi import FastAPI, Request
import logging
from trade import place_order
import uvicorn
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app = FastAPI()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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

        # Format symbol correctly for MEXC Futures
        symbol = data["symbol"].replace("-", "_").replace("USDT", "_USDT")
        action = data["action"].lower()
        quantity = float(data["quantity"])
        leverage = int(data["leverage"])

        logger.info(f"📦 Parsed → Action: {action}, Symbol: {symbol}, "
                   f"Quantity: {quantity}, Leverage: {leverage}")

        # Place order
        result = place_order(action, symbol, quantity, leverage)
        
        if "error" in result:
            logger.error(f"❌ Order Failed: {result['error']}")
            return {
                "status": "error",
                "message": result["error"],
                "symbol": symbol,
                "action": action
            }
            
        logger.info(f"✅ Order Successful: {result}")
        return {
            "status": "success",
            "data": result,
            "symbol": symbol,
            "action": action
        }

    except ValueError as ve:
        logger.error(f"❌ Validation Error: {str(ve)}")
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"❌ Unexpected Error: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)
