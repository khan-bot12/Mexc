import time
import hmac
import hashlib
import requests
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trade")

# Load from environment
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")
BASE_URL = "https://api.mexc.com"  # Official MEXC endpoint

def generate_signature(params, secret):
    sorted_params = sorted(params.items())
    query = '&'.join([f"{k}={v}" for k, v in sorted_params])
    return hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()

def place_order(action, symbol, quantity, leverage):
    try:
        logger.info("📊 Getting current positions...")

        # Step 1: Get positions
        timestamp = str(int(time.time() * 1000))
        pos_params = {
            "api_key": API_KEY,
            "req_time": timestamp,
            "symbol": symbol
        }
        pos_params["sign"] = generate_signature(pos_params, API_SECRET)

        pos_resp = requests.get(f"{BASE_URL}/api/v1/private/future/position/open_positions", params=pos_params)
        logger.info(f"📊 Current Position Info: {pos_resp.json()}")

        # Step 2: Determine side
        side = "OPEN_LONG" if action.lower() == "buy" else "OPEN_SHORT"

        # Step 3: Build order payload
        timestamp = str(int(time.time() * 1000))
        payload = {
            "api_key": API_KEY,
            "req_time": timestamp,
            "symbol": symbol,
            "price": "0",  # Market order
            "vol": quantity,
            "leverage": leverage,
            "side": side,
            "open_type": 2,  # Isolated = 1, Cross = 2
            "positionId": 0,
            "orderType": 1,  # Market order
        }
        payload["sign"] = generate_signature(payload, API_SECRET)

        logger.info(f"🟢 Placing new order...")
        logger.info(f"🔐 Order Payload: {payload}")

        order_resp = requests.post(f"{BASE_URL}/api/v1/private/future/order/place", data=payload)
        logger.info(f"✅ Order Response: {order_resp.json()}")

        return order_resp.json()

    except Exception as e:
        logger.exception("❌ Error placing order:")
        return {"error": str(e)}
