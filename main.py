from fastapi import FastAPI, Request
import uvicorn
from trade import place_order

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print(f"Incoming webhook data: {data}")

        action = data.get("action")
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        leverage = data.get("leverage")

        print(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        result = place_order(action, symbol, quantity, leverage)
        print(f"📤 Result from place_order: {result}")
        return {"status": "success", "result": result}

    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
