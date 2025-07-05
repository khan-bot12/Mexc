import time
import hmac
import hashlib
import requests
import os

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")
BASE_URL = "https://contract.mexc.com"

HEADERS = {
    "Content-Type": "application/json",
    "ApiKey": API_KEY,
}


def get_timestamp():
    return str(int(time.time() * 1000))


def sign_request(params: dict) -> str:
    query_string = "&".join([f"{key}={params[key]}" for key in sorted(params)])
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return signature


def get_position(symbol):
    url = f"{BASE_URL}/api/v1/private/position/open_positions"
    params = {
        "symbol": symbol,
        "timestamp": get_timestamp()
    }
    signature = sign_request(params)
    params["signature"] = signature

    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()


def place_order(symbol, quantity, leverage, action):
    print(f"📦 Parsed → action: {action}, symbol: {symbol}, quantity: {quantity}, leverage: {leverage}")
    print("📊 Current Position Info:", get_position(symbol))

    url = f"{BASE_URL}/api/v1/private/order/submit"

    data = {
        "symbol": symbol,
        "price": "0",  # Market Order
        "vol": str(quantity),
        "leverage": str(leverage),
        "side": action.upper(),  # BUY or SELL
        "type": 1,               # 1 = Open
        "open_type": "cross",    # Cross Margin
        "position_id": 0,
        "external_oid": str(int(time.time() * 1000)),
        "timestamp": get_timestamp()
    }

    signature = sign_request(data)
    data["signature"] = signature

    print("🟢 Placing new order...")
    response = requests.post(url, headers=HEADERS, json=data)
    print("✅ Order Response:", response.json())
    return response.json()
