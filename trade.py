import time
import hmac
import hashlib
import requests
import os
import logging

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

BASE_URL = "https://api.mexc.com"
headers = {
    "Content-Type": "application/json"
}

def generate_signature(params: dict) -> str:
    sorted_params = sorted(params.items())
    query_string = "&".join(f"{k}={v}" for k, v in sorted_params)
    return hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def get_positions(symbol: str):
    logging.info("📊 Getting current positions...")
    path = "/api/v1/private/futures/position/open_positions"
    url = BASE_URL + path
    req_time = str(int(time.time() * 1000))

    params = {
        "api_key": API_KEY,
        "req_time": req_time,
        "symbol": symbol
    }
    params["sign"] = generate_signature(params)

    try:
        response = requests.get(url, params=params)
        data = response.json()
        logging.info(f"📊 Current Position Info: {data}")
        return data
    except Exception as e:
        logging.error(f"❌ Failed to get positions: {e}")
        return None

def place_order(action, symbol, quantity, leverage):
    logging.info("🟢 Placing new order...")

    path = "/api/v1/private/futures/order/place"
    url = BASE_URL + path
    req_time = str(int(time.time() * 1000))

    side = "OPEN_LONG" if action == "buy" else "OPEN_SHORT"

    payload = {
        "api_key": API_KEY,
        "req_time": req_time,
        "symbol": symbol,
        "price": "0",  # Market order
        "vol": quantity,
        "leverage": leverage,
        "side": side,
        "open_type": 2,  # 1 = Isolated, 2 = Cross
        "positionId": 0,
        "orderType": 1  # 1 = Market Order
    }

    payload["sign"] = generate_signature(payload)

    logging.info(f"🔐 Order Payload: {payload}")

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        logging.info(f"✅ Order Response: {data}")
        return data
    except Exception as e:
        logging.error(f"❌ Failed to place order: {e}")
        return {"error": str(e)}
