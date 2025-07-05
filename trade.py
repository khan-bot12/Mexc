import time
import hmac
import hashlib
import requests
import os
import logging

# Load API credentials from environment variables
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

# MEXC Futures base URL (cross margin trading)
BASE_URL = "https://contract.mexc.com"

# Logging setup
logger = logging.getLogger("trade")

# === Generate signature ===
def generate_signature(secret_key, params):
    sorted_params = sorted(params.items())
    query_string = "&".join(f"{k}={v}" for k, v in sorted_params)
    return hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()

# === Get position info (optional, basic structure) ===
def get_position(symbol):
    path = "/api/v1/private/position/list/positionHolding"
    url = BASE_URL + path
    req_time = str(int(time.time() * 1000))
    params = {
        "api_key": API_KEY,
        "req_time": req_time,
        "symbol": symbol
    }
    sign = generate_signature(API_SECRET, params)
    params["sign"] = sign
    response = requests.get(url, params=params)
    try:
        return response.json()
    except Exception as e:
        logger.error(f"❌ Error in get_position: {e}")
        return {}

# === Place Order ===
def place_order(action, symbol, quantity, leverage):
    logger.info("🟢 Placing new order...")

    side = "OPEN_LONG" if action.lower() == "buy" else "OPEN_SHORT"
    req_time = str(int(time.time() * 1000))

    payload = {
        "api_key": API_KEY,
        "req_time": req_time,
        "symbol": symbol,
        "price": "0",  # 0 for market order
        "vol": quantity,
        "leverage": leverage,
        "side": side,
        "open_type": 2,  # 1=isolated, 2=crossed
        "positionId": 0,
        "orderType": 1  # 1=market order
    }

    # Sign the payload
    payload["sign"] = generate_signature(API_SECRET, payload)

    logger.info(f"🔐 Order Payload: {payload}")

    try:
        url = BASE_URL + "/api/v1/private/order/submit"
        response = requests.post(url, json=payload)
        result = response.json()
        logger.info(f"✅ Order Response: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ Exception while placing order: {e}")
        return {"error": str(e)}
