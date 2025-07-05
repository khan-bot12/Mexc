from fastapi import FastAPI, Request
from trade import place_order

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print(f"Incoming webhook data: {data}")

        action = data.get("action")
        symbol = data.get("symbol")
        quantity = float(data.get("quantity"))
        leverage = int(data.get("leverage"))

        print(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        if not all([action, symbol, quantity, leverage]):
            return {"error": "Missing required parameters."}

        result = place_order(
            action=action,
            symbol=symbol,
            quantity=quantity,
            leverage=leverage
        )

        print(f"📤 Result from place_order: {result}")
        return result

    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"error": str(e)}
