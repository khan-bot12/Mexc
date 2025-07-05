from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
from mexc_trade import place_order
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

SECRET_TOKEN = os.getenv("SECRET_TOKEN")

class WebhookData(BaseModel):
    action: str
    symbol: str
    quantity: float
    leverage: int
    token: str = None

@app.post("/webhook")
async def webhook(data: WebhookData, request: Request):
    print("📥 Incoming webhook data:", data.dict())

    if SECRET_TOKEN and data.token != SECRET_TOKEN:
        print("❌ Invalid token!")
        return {"error": "Unauthorized"}

    try:
        result = place_order(
            symbol=data.symbol,
            action=data.action,
            quantity=data.quantity,
            leverage=data.leverage
        )
        print("📤 Order result:", result)
        return result
    except Exception as e:
        print("❌ Exception:", e)
        return {"error": str(e)}
