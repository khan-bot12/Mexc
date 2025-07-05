import time
import hmac
import hashlib
import requests
import logging
import os

# Set up logging
logger = logging.getLogger("trade")
logger.setLevel(logging.INFO)

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

BASE_URL = "https://contract.mexc.com"

def sign_request(secret, params):
    sorted_params = sorted(params.items())
    query_string = '&'.join(f"{key}={value}" for key, value in sorted_params)
    signature = hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature

def get_position(symbol):
    """Fetch current position for the symbol."""
    try:
        endpoint = f"{BASE_URL}/api/v1/private/position/list"
        params = {
            "api_key": API_KEY,
            "req_time": str(int(time.time() * 1000))
        }
        params["sign"] = sign_request(API_SECRET, params)
        response = requests.get(endpoint, params=params)
        result = response.json()
        logger.info(f"📊 Current Position Info: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to fetch position: {e}")
        return None

def place_order(action, symbol, quantity, leverage):
    try:
        logger.info("🟢 Placing new order...")

        side = action.lower()
        order_side = 1 if side == "buy" else 2  # 1 = OPEN_LONG, 2 = OPEN_SHORT
        open_type = 2  # 2 = Cross margin

        payload = {
            "api_key": API_KEY,
            "req_time": str(int(time.time() * 1000)),
            "symbol": symbol.upper(),
            "price": "0",  # Market order
            "vol": float(quantity),
            "leverage": int(leverage),
            "side": order_side,
            "open_type": open_type,
            "positionId": 0,
            "orderType": 1  # 1 = Market Order
        }

        # Sign the payload
        payload["sign"] = sign_request(API_SECRET, payload)

        headers = {
            "Content-Type": "application/json"
        }

        endpoint = f"{BASE_URL}/api/v1/private/order/submit"
        response = requests.post(endpoint, headers=headers, json=payload)

        logger.info(f"🔐 Order Payload: {payload}")
        logger.info(f"📩 Raw response text: {response.text}")

        result = response.json()
        logger.info(f"✅ Order Response: {result}")
        return result

    except Exception as e:
        logger.error(f"❌ Exception in place_order: {e}")
        return {"error": str(e)}
