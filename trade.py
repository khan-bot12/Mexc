import time
import hashlib
import hmac
import requests
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trade")

# Load API keys from environment variables
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

# Base URL for MEXC Futures
BASE_URL = "https://contract.mexc.com/api/v1/private/order/submit"  # Correct for MEXC futures

def sign_params(params, secret_key):
    sorted_params = sorted(params.items())
    query_string = "&".join([f"{key}={value}" for key, value in sorted_params])
    signature = hmac.new(
        secret_key.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return signature

def place_order(action, symbol, quantity, leverage):
    try:
        # Convert to MEXC symbol format (e.g., ETH_USDT)
        if "_" not in symbol:
            symbol = symbol.upper().replace("USDT", "_USDT")

        side = 1 if action.lower() == "buy" else 2  # 1: OPEN_LONG, 2: OPEN_SHORT

        req_time = str(int(time.time() * 1000))
        params = {
            "api_key": API_KEY,
            "req_time": req_time,
            "symbol": symbol,
            "price": "0",
            "vol": str(quantity),
            "leverage": str(leverage),
            "side": side,
            "open_type": 2,             # Cross margin
            "positionId": 0,
            "orderType": 1,             # Market order
            "type": 1                   # 1 = open
        }

        # Sign the request
        sign = sign_params(params, API_SECRET)
        params["sign"] = sign

        logger.info("🟢 Placing new order...")
        logger.info(f"🔐 Order Payload: {params}")

        response = requests.post(BASE_URL, json=params, headers={"Content-Type": "application/json"})
        logger.info(f"✅ Order Response: {response.status_code} | {response.text}")
        return response.json()

    except Exception as e:
        logger.error(f"❌ Error placing order: {e}")
        return {"error": str(e)}
