import time
import hmac
import hashlib
import requests
import os
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trade")

# ENV vars
MEXC_API_KEY = os.getenv("MEXC_API_KEY")
MEXC_API_SECRET = os.getenv("MEXC_API_SECRET")
BASE_URL = "https://api.mexc.com"

def generate_signature(secret_key, req_time, params):
    sorted_params = sorted(params.items())
    query_string = "&".join(f"{key}={value}" for key, value in sorted_params)
    message = f"{req_time}{query_string}"
    signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
    return signature

def get_position(symbol):
    try:
        logger.info("📊 Getting current positions...")

        req_time = str(int(time.time() * 1000))
        params = {
            "api_key": MEXC_API_KEY,
            "req_time": req_time,
            "symbol": symbol.upper(),
        }
        sign = generate_signature(MEXC_API_SECRET, req_time, params)
        params["sign"] = sign

        url = f"{BASE_URL}/api/v1/private/position/list/one"
        response = requests.get(url, params=params)
        data = response.json()
        logger.info(f"📊 Current Position Info: {data}")
        return data

    except Exception as e:
        logger.error(f"❌ Error getting position: {e}")
        return {"error": str(e)}

def place_order(action, symbol, quantity, leverage):
    try:
        logger.info("🟢 Placing new order...")

        req_time = str(int(time.time() * 1000))
        side = "OPEN_LONG" if action.lower() == "buy" else "OPEN_SHORT"

        params = {
            "api_key": MEXC_API_KEY,
            "req_time": req_time,
            "symbol": symbol.upper(),
            "price": "0",  # Market order
            "vol": quantity,
            "leverage": leverage,
            "side": side,
            "open_type": 2,  # Cross margin
            "positionId": 0,
            "orderType": 1  # Market order
        }

        sign = generate_signature(MEXC_API_SECRET, req_time, params)
        params["sign"] = sign

        logger.info(f"🔐 Order Payload: {params}")
        url = f"{BASE_URL}/api/v1/private/order/submit"
        response = requests.post(url, data=params)

        logger.info(f"📩 Raw response text: {response.text}")
        data = response.json()
        logger.info(f"✅ Order Response: {data}")
        return data

    except Exception as e:
        logger.error(f"❌ Exception in place_order: {e}")
        return {"error": str(e)}
