from fastapi import FastAPI, Request
import uvicorn
import os
from trade import place_order, get_position

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print("Incoming webhook data:", data)

        action = data.get("action")  # 'buy' or 'sell'
        symbol = data.get("symbol")  # e.g., 'ETHUSDT'
        quantity = data.get("quantity")
        leverage = data.get("leverage")

        if None in (action, symbol, quantity, leverage):
            return {"error": "Missing required parameters"}

        # Check and close opposite position
        position_info = get_position(symbol)
        positions = position_info.get("data", [])

        for pos in positions:
            hold_side = pos.get("holdSide")  # long or short
            if (action == "buy" and hold_side == "short") or (action == "sell" and hold_side == "long"):
                close_action = "buy" if hold_side == "short" else "sell"
                close_qty = float(pos.get("total", 0))
                if close_qty > 0:
                    print(f"🔁 Closing opposite position: {close_action} {close_qty} {symbol}")
                    place_order(symbol, close_qty, leverage, close_action)

        # Place new order
        result = place_order(symbol, quantity, leverage, action)
        print("📤 Result from place_order:", result)
        return {"status": "ok", "result": result}

    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
