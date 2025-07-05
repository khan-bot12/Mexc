import time
import hmac
import hashlib
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")
BASE_URL = "https://api.mexc.com"

def get_timestamp():
    return str(int(time.time() * 1000))

def sign(params, secret):
    sorted_params = "&".join([f"{key}={params[key]}" for key in sorted(params)])
    return hmac.new(secret.encode(), sorted_params.encode(), hashlib.sha256).hexdigest()

def get_headers(params):
    signature = sign(params, API_SECRET)
    headers = {
        "Content-Type": "application/json",
        "ApiKey": API_KEY,
        "Request-Time": params["timestamp"],
        "Signature": signature
    }
    return headers

def get_position(symbol):
    url = f"{BASE_URL}/api/v1/private/account/position"
    params = {
        "symbol": symbol,
        "timestamp": get_timestamp()
    }
    headers = get_headers(params)
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def close_position(symbol, side):
    opposite = "SELL" if side == "BUY" else "BUY"
    return place_order(opposite.lower(), symbol, 0, 0, close_only=True)

def place_order(action, symbol, quantity, leverage, close_only=False):
    try:
        side = "BUY" if action.lower() == "buy" else "SELL"
        position_data = get_position(symbol)

        print(f"📊 Current Position Info: {position_data}")

        if not close_only:
            # Optional: check and close opposing position before new entry
            for pos in position_data.get("data", []):
                if pos.get("symbol") == symbol:
                    current_side = pos.get("positionSide")
                    if (current_side == "LONG" and side == "SELL") or (current_side == "SHORT" and side == "BUY"):
                        print("❗ Closing opposite position before placing new order")
                        close_position(symbol, side)
                        time.sleep(1)

        print("🟢 Placing new order...")

        url = f"{BASE_URL}/api/v1/private/order/place"

        timestamp = get_timestamp()
        params = {
            "symbol": symbol,
            "price": "0",  # Market order
            "vol": str(quantity),
            "side": side,
            "type": "MARKET",
            "open_type": "CROSS",
            "leverage": str(leverage),
            "timestamp": timestamp
        }

        headers = get_headers(params)
        response = requests.post(url, headers=headers, json=params)
        return response.json()

    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"error": str(e)}
