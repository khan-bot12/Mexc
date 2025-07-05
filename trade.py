import os
import time
import hmac
import hashlib
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

BASE_URL = "https://contract.mexc.com"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trade")

def generate_signature(secret, params):
    sorted_params = sorted(params.items())
    message = '&'.join(f"{k}={v}" for k, v in sorted_params)
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return signature

def get_position(symbol):
    logger.info("📊 Getting current positions...")
    path = "/api/v1/private/position/list/isolated"  # Still used even with open_type = 2
    url = BASE_URL + path
    req_time = str(int(time.time() * 1000))

    params = {
        "api_key": API_KEY,
        "req_time": req_time
    }

    sign = generate_signature(API_SECRET, params)
    params["sign"] = sign

    try:
        response = requests.get(url, params=params)
        data = response.json()
        logger.info(f"📊 Current Position Info: {data}")
        return data
    except Exception as e:
        logger.error(f"❌ Error fetching position: {e}")
        return {"error": str(e)}

def place_order(symbol, action, quantity, leverage):
    logger.info("🟢 Placing new order...")

    path = "/api/v1/private/order/submit"
    url = BASE_URL + path
    req_time = str(int(time.time() * 1000))

    # Ensure action is string before using .lower()
    side = "OPEN_LONG" if str(action).lower() == "buy" else "OPEN_SHORT"

    payload = {
        "api_key": API_KEY,
        "req_time": req_time,
        "symbol": symbol,
        "price": "0",              # 0 for market order
        "vol": quantity,
        "leverage": leverage,
        "side": side,
        "open_type": 2,            # 2 for cross margin
        "positionId": 0,
        "orderType": 1             # 1 for market order
    }

    sign = generate_signature(API_SECRET, payload)
    payload["sign"] = sign

    logger.info(f"🔐 Order Payload: {payload}")
    try:
        response = requests.post(url, data=payload)
        result = response.json()
        logger.info(f"✅ Order Response: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to parse order response: {e}")
        return {"error": str(e)}
