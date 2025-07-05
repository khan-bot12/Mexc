from fastapi import FastAPI, Request
from pydantic import BaseModel
from mexc_trade import place_order

app = FastAPI()

class WebhookData(BaseModel):
    action: str
    symbol: str
    quantity: float
    leverage: int

@app.post("/webhook")
async def webhook_endpoint(data: WebhookData, request: Request):
    print(f"Incoming webhook data: {data.dict()}")

    try:
        result = place_order(
            action=data.action.lower(),
            symbol=data.symbol,
            quantity=data.quantity,
            leverage=data.leverage
        )
        print(f"📤 Result from place_order: {result}")
        return {"status": "ok", "result": result}

    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"status": "error", "error": str(e)}
from fastapi import FastAPI, Request
from pydantic import BaseModel
from mexc_trade import place_order

app = FastAPI()

class WebhookData(BaseModel):
    action: str
    symbol: str
    quantity: float
    leverage: int

@app.post("/webhook")
async def webhook_endpoint(data: WebhookData, request: Request):
    print(f"Incoming webhook data: {data.dict()}")

    try:
        result = place_order(
            action=data.action.lower(),
            symbol=data.symbol,
            quantity=data.quantity,
            leverage=data.leverage
        )
        print(f"📤 Result from place_order: {result}")
        return {"status": "ok", "result": result}

    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"status": "error", "error": str(e)}
