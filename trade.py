import time
import hmac
import hashlib
import requests
import logging
import os

# Setup logging
logger = logging.getLogger("trade")
logger.setLevel(logging.INFO)

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

# Base URL for MEXC Futures
BASE_URL = "https://contract.mexc.com"

def get_server_timestamp():
    return str(int(time.time() * 1000))

def sign_request(params, secret):
    sorted_params = sorted(params.items())
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    signature = hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return signature

def place_order(action, symbol, quantity, leverage):
    try:
        logger.info("📊 Getting current positions...")

        # Step 1: Get current position (optional for now)
        # You may want to close existing position logic here

        # Step 2: Place new order
        logger.info("🟢 Placing new order...")

        # Define side
        side = "OPEN_LONG" if action.lower() == "buy" else "OPEN_SHORT"

        # Build request params
        req_time = get_server_timestamp()
        params = {
            "api_key": API_KEY,
            "req_time": req_time,
            "symbol": symbol,
            "price": "0",  # market order
            "vol": quantity,
            "leverage": leverage,
            "side": side,
            "open_type": 2,  # 1 = isolated, 2 = cross
            "positionId": 0,
            "orderType": 1,  # 1 = market
        }

        # Sign the payload
        params["sign"] = sign_request(params, API_SECRET)
        logger.info(f"🔐 Order Payload: {params}")

        # Send the order
        response = requests.post(f"{BASE_URL}/api/v1/private/order/submit", data=params)
        result = response.json()
        logger.info(f"✅ Order Response: {result}")
        return result

    except Exception as e:
        logger.exception(f"❌ Exception while placing order: {e}")
        return {"error": str(e)}
