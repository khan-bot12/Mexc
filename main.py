# ===== main.py =====
from fastapi import FastAPI, Request
from trade import place_order
import os
import json

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print("Incoming webhook data:", data)

        action = data.get("action")
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        leverage = data.get("leverage")

        print(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        result = place_order(symbol, quantity, leverage, action)
        print("\U0001F4E4 Result from place_order:", result)

        return {"status": "success", "data": result}
    except Exception as e:
        print("\u274C Exception:", str(e))
        return {"status": "error", "message": str(e)}
