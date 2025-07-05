import time
import hmac
import hashlib
import requests
import json
import os

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")
BASE_URL = "https://contract.mexc.com"

HEADERS = {
    "Content-Type": "application/json"
}

def get_timestamp():
    return str(int(time.time() * 1000))

def sign(payload, secret):
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

def get_position(symbol):
    timestamp = get_timestamp()
    req_path = f"/api/v1/private/position/open_positions"
    query = f"api_key={API_KEY}&req_time={timestamp}&symbol={symbol}"
    signature = sign(query, API_SECRET)
    url = f"{BASE_URL}{req_path}?{query}&sign={signature}"

    try:
        response = requests.get(url, headers=HEADERS)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def place_order(action, symbol, quantity, leverage):
    timestamp = get_timestamp()

    # Check current position
    pos_info = get_position(symbol)
    print("\U0001F4CA Current Position Info:", pos_info)

    try:
        # Check if we need to close opposite side
        open_side = None
        if pos_info.get("code") == 200 and pos_info.get("data"):
            for pos in pos_info["data"]:
                if pos["positionAmt"] != "0":
                    open_side = pos["positionSide"]

        side = "open_long" if action == "buy" else "open_short"

        endpoint = "/api/v1/private/order/submit"
        url = BASE_URL + endpoint

        payload = {
            "api_key": API_KEY,
            "req_time": timestamp,
            "symbol": symbol,
            "price": 0,  # Market order
            "vol": quantity,
            "leverage": leverage,
            "side": side,
            "open_type": "cross",
            "position_id": 0,
            "external_oid": str(int(time.time() * 1000))
        }

        sorted_query = "&".join([f"{key}={payload[key]}" for key in sorted(payload)])
        payload["sign"] = sign(sorted_query, API_SECRET)

        print("\U0001F7E2 Placing new order...")
        response = requests.post(url, headers=HEADERS, json=payload)
        print("\u2705 Order Response:", response.json())
        return response.json()

    except Exception as e:
        print("❌ Exception:", e)
        return {"error": str(e)}
