import os
import time
import hmac
import hashlib
import requests
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trade")

# Get MEXC API credentials from environment variables
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

BASE_URL = "https://contract.mexc.com"

def generate_signature(api_secret, params):
    sorted_params = sorted(params.items())
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    return hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def get_position(symbol):
    """Fetch current positions for the given symbol."""
    endpoint = "/api/v1/private/position/list/positions"
    url = BASE_URL + endpoint
    timestamp = str(int(time.time() * 1000))

    payload = {
        "api_key": API_KEY,
        "req_time": timestamp,
    }
    payload["sign"] = generate_signature(API_SECRET, payload)

    try:
        response = requests.get(url, params=payload)
        logger.info(f"📊 Current Position Info: {response.json()}")
        return response.json()
    except Exception as e:
        logger.error(f"❌ Error fetching position: {e}")
        return None

def place_order(action, symbol, quantity, leverage):
    """Place a long or short order based on action ('buy' or 'sell')."""
    logger.info("🟢 Placing new order...")

    side = 1 if str(action).lower() == "buy" else 2  # 1 = OPEN_LONG, 2 = OPEN_SHORT

    timestamp = str(int(time.time() * 1000))

    payload = {
        "api_key": API_KEY,
        "req_time": timestamp,
        "symbol": symbol.upper(),
        "price": "0",  # Market order
        "vol": quantity,
        "leverage": leverage,
        "side": side,
        "open_type": 2,  # 2 = Cross margin
        "positionId": 0,
        "orderType": 1  # 1 = Market order
    }

    payload["sign"] = generate_signature(API_SECRET, payload)

    headers = {"Content-Type": "application/json"}
    endpoint = f"{BASE_URL}/api/v1/private/order/submit"

    try:
        logger.info(f"🔐 Order Payload: {payload}")
        response = requests.post(endpoint, headers=headers, json=payload)
        logger.info(f"📩 Raw response text: {response.text}")  # Log full response
        result = response.json()
        logger.info(f"✅ Order Response: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ Error placing order: {e}")
        return {"error": str(e)}
