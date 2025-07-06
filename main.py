from fastapi import FastAPI, Request
import logging
from trade import place_order
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("main")

def format_symbol(symbol: str) -> str:
    """Convert symbol to MEXC Futures format (ETH_USDT)"""
    symbol = symbol.upper().replace("-", "_")
    if not symbol.endswith("_USDT"):
        if "USDT" in symbol:
            symbol = symbol.replace("USDT", "_USDT")
        else:
            symbol = f"{symbol}_USDT"
    # Ensure exactly one underscore
    symbol = symbol.replace("__", "_")
    return symbol

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"📥 Incoming webhook: {data}")

        # Validate required fields
        required = ["action", "symbol", "quantity", "leverage"]
        if not all(field in data for field in required):
            raise ValueError(f"Missing required fields. Need: {required}")

        # Format and validate inputs
        symbol = format_symbol(data["symbol"])
        action = data["action"].lower()
        if action not in ["buy", "sell"]:
            raise ValueError("Action must be 'buy' or 'sell'")

        quantity = float(data["quantity"])
        leverage = int(data["leverage"])

        logger.info(f"⚡ Parsed: {action} {quantity} {symbol} @ {leverage}x")

        # Execute trade
        result = place_order(action, symbol, quantity, leverage)
        
        if result.get("error"):
            logger.error(f"❌ Trade failed: {result['error']}")
            return {"status": "error", "message": result["error"]}
            
        logger.info(f"✅ Trade successful: {result}")
        return {"status": "success", "data": result}

    except ValueError as ve:
        logger.error(f"🔴 Validation error: {str(ve)}")
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"🔴 Unexpected error: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}

@app.get("/test-symbol/{symbol}")
async def test_symbol(symbol: str):
    """Test endpoint for symbol formatting"""
    return {
        "original": symbol,
        "formatted": format_symbol(symbol),
        "valid": format_symbol(symbol).endswith("_USDT")
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
