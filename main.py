from fastapi import FastAPI, Request
import logging
from trade import place_order, get_positions

app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    logging.info(f"Incoming webhook data: {data}")

    try:
        action = data["action"].lower()
        symbol = data["symbol"].upper()
        quantity = float(data["quantity"])
        leverage = int(data["leverage"])

        logging.info(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")

        # Optional: Close opposite position before opening new one
        position_data = get_positions(symbol)
        if position_data and position_data.get("success") and "data" in position_data:
            for pos in position_data["data"]:
                hold_side = pos.get("holdSide", "").lower()
                if (action == "buy" and hold_side == "short") or (action == "sell" and hold_side == "long"):
                    logging.info(f"⚠️ Existing {hold_side} position needs to be closed first (Not yet implemented).")

        result = place_order(action, symbol, quantity, leverage)
        logging.info(f"📤 Result from place_order: {result}")
        return result

    except Exception as e:
        logging.error(f"❌ Error processing webhook: {e}")
        return {"error": str(e)}
