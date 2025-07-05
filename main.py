from fastapi import FastAPI, Request
from trade import place_order
import os

app = FastAPI()

# Optional: Secret token for extra webhook protection
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print(f"Incoming webhook data: {data}")

        # Optional secret token check
        if SECRET_TOKEN:
            if "token" not in data or data["token"] != SECRET_TOKEN:
                return {"error": "Invalid or missing token"}

        # Extract required fields
        action = data.get("action")
        symbol = data.get("symbol")
        quantity = float(data.get("quantity"))
        leverage = int(data.get("leverage"))

        print(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        result = place_order(action, symbol, quantity, leverage)
        print(f"📤 Result from place_order: {result}")
        return result

    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"error": str(e)}
