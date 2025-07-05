from fastapi import FastAPI, Request
import logging
import os
from trade import place_order
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.get("/")
async def root():
    return {"message": "MEXC Auto-Trading Bot is live!"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logging.info(f"Incoming webhook data: {data}")

        action = data.get("action")
        symbol = data.get("symbol")
        quantity = float(data.get("quantity"))
        leverage = int(data.get("leverage"))

        logging.info(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        result = place_order(symbol, quantity, leverage, action)
        logging.info(f"📤 Result from place_order: {result}")

        return {"status": "success", "result": result}
    except Exception as e:
        logging.error(f"❌ Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}
