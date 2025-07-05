import time
import hmac
import hashlib
import requests
import logging
import os

# Load API credentials from environment variables (set in Render)
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

# MEXC Futures base URL (Contract trading)
BASE_URL = "https://api.mexc.com"
ORDER_ENDPOINT = "/api/v1/private/order/submit"
POSITION_ENDPOINT = "/api/v1/private/position/list"

logger = logging.getLogger("trade")

def get_timestamp():
    return str(int(time.time() * 1000))

def generate_signature(params: dict, secret: str) -> str:
    sorted_params = sorted(params.items())
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def get_positions(symbol: str):
    url = f"{BASE_URL}{POSITION_ENDPOINT}"
    timestamp = get_timestamp()

    params = {
        "api_key": API_KEY,
        "req_time": timestamp,
        "symbol": symbol.upper(),
    }

    sign = generate_signature(params, API_SECRET)
    params["sign"] = sign

    try:
        response = requests.post(url, data=params, timeout=10)
        result = response.json()
        logger.info(f"📊 Current Position Info: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ Error fetching positions: {e}")
        return None

def place_order(action, symbol, quantity, leverage):
    logger.info("🟢 Placing new order...")

    side = "OPEN_LONG" if action.lower() == "buy" else "OPEN_SHORT"
    timestamp = get_timestamp()

    payload = {
        "api_key": API_KEY,
        "req_time": timestamp,
        "symbol": symbol.upper(),
        "price": "0",                  # Market order
        "vol": quantity,
        "leverage": leverage,
        "side": side,
        "open_type": 2,               # 2 = Cross margin
        "positionId": 0,
        "orderType": 1                # 1 = Market
    }

    sign = generate_signature(payload, API_SECRET)
    payload["sign"] = sign

    headers = {"Content-Type": "application/json"}
    logger.info(f"🔐 Order Payload: {payload}")

    try:
        url = f"{BASE_URL}{ORDER_ENDPOINT}"
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()
        logger.info(f"✅ Order Response: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ Order failed: {e}")
        return {"error": str(e)}
