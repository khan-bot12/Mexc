import time
import hmac
import hashlib
import requests
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trade")

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

BASE_URL = "https://contract.mexc.com"

def generate_signature(api_secret, params):
    sorted_params = sorted(params.items())
    query_string = '&'.join(f"{key}={value}" for key, value in sorted_params)
    return hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def get_position(symbol):
    logger.info("📊 Getting current positions...")

    path = "/api/v1/private/position/open_positions"
    url = BASE_URL + path
    req_time = str(int(time.time() * 1000))
    params = {
        "api_key": API_KEY,
        "req_time": req_time,
    }

    sign = generate_signature(API_SECRET, params)
    params["sign"] = sign

    response = requests.get(url, params=params)
    try:
        data = response.json()
        logger.info(f"📊 Current Position Info: {data}")
        return data
    except Exception as e:
        logger.error(f"❌ Failed to parse position response: {e}")
        return {}

def place_order(symbol, action, quantity, leverage):
    logger.info("🟢 Placing new order...")

    path = "/api/v1/private/order/submit"
    url = BASE_URL + path
    req_time = str(int(time.time() * 1000))

    # Map action to side
    side = "OPEN_LONG" if action.lower() == "buy" else "OPEN_SHORT"

    payload = {
        "api_key": API_KEY,
        "req_time": req_time,
        "symbol": symbol,
        "price": "0",  # Market order
        "vol": quantity,
        "leverage": leverage,
        "side": side,
        "open_type": 2,             # cross margin
        "positionId": 0,
        "orderType": 1              # market
    }

    sign = generate_signature(API_SECRET, payload)
    payload["sign"] = sign

    logger.info(f"🔐 Order Payload: {payload}")
    response = requests.post(url, data=payload)

    try:
        result = response.json()
        logger.info(f"✅ Order Response: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to parse order response: {e}")
        return {"error": str(e)}
