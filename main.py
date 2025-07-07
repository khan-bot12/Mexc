import logging
from fastapi import FastAPI, Request
from trade import place_order
import uvicorn

app = FastAPI()

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("main")

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"📥 Incoming webhook: {data}")

        action = data.get("action")
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        leverage = data.get("leverage")

        logger.info(f"⚡ Parsed: {action} {quantity} {symbol} @ {leverage}x")

        result = place_order(
            action=action,
            symbol=symbol,
            quantity=quantity,
            leverage=leverage
        )

        logger.info(f"📤 Result from place_order: {result}")
        return result

    except Exception as e:
        logger.error(f"❌ Error handling webhook: {e}")
        return {"error": str(e)}

# To run locally with: uvicorn main:app --host 0.0.0.0 --port 10000 --reload
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)
