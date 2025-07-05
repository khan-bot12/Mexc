import time
import hmac
import hashlib
import requests
import logging
import os

# Load credentials from environment
MEXC_API_KEY = os.getenv("MEXC_API_KEY")
MEXC_API_SECRET = os.getenv("MEXC_API_SECRET")

# Set up logger
logger = logging.getLogger("trade")
logging.basicConfig(level=logging.INFO)

BASE_URL = "https://contract.mexc.com"

def generate_signature(api_secret, req_time, params):
    sorted_params = sorted(params.items())
    query_string = "&".join([f"{key}={value}" for key, value in sorted_params])
    to_sign = f"{query_string}&req_time={req_time}"
    return hmac.new(api_secret.encode(), to_sign.encode(), hashlib.sha256).hexdigest()

def get_position(symbol):
    url = f"{BASE_URL}/api/v1/private/position/list"
    req_time = str(int(time.time() * 1000))
    params = {
        "api_key": MEXC_API_KEY,
        "req_time": req_time
    }
    sign = generate_signature(MEXC_API_SECRET, req_time, params)
    params["sign"] = sign

    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        logger.error(f"❌ Error fetching position: {e}")
        return None

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
            "orderType": 1,  # Market order
        }

        sign = generate_signature(MEXC_API_SECRET, req_time, params)
        params["sign"] = sign

        logger.info(f"🔐 Order Payload: {params}")
        url = f"{BASE_URL}/api/v1/private/order/submit"
        response = requests.post(url, data=params)
        logger.info(f"✅ Order Response: {response.json()}")
        return response.json()
    except Exception as e:
        logger.error(f"❌ Exception in place_order: {e}")
        return {"error": str(e)}
