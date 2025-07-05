from fastapi import FastAPI, Request
import uvicorn
import logging
from trade import place_order

app = FastAPI()

logging.basicConfig(level=logging.INFO)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    logging.info(f"Incoming webhook data: {data}")

    try:
        action = data.get("action")
        symbol = data.get("symbol")
        quantity = float(data.get("quantity"))
        leverage = int(data.get("leverage"))

        logging.info(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        result = place_order(action, symbol, quantity, leverage)
        logging.info(f"📤 Result from place_order: {result}")
        return {"status": "success", "detail": result}
    except Exception as e:
        logging.error(f"❌ Exception: {e}")
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
