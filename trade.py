import time
import hmac
import hashlib
import requests
import os
from dotenv import load_dotenv
import logging

# Load API keys from .env
load_dotenv()
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

# Setup logging
logger = logging.getLogger("trade")

logger.info(f"🔍 API KEY from .env: {API_KEY}")
logger.info(f"🔍 API SECRET loaded: {'Yes' if API_SECRET else 'No'}")

# MEXC API URL
BASE_URL = "https://contract.mexc.com"

def get_timestamp():
    return str(int(time.time() * 1000))

def sign_request(params: dict, secret: str) -> str:
    query_string = "&".join([f"{key}={params[key]}" for key in sorted(params)])
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def place_order(action: str, symbol: str, quantity: float, leverage: int):
    try:
        logger.info("🟢 Placing new order...")

        # Convert action to side (1 = buy, 2 = sell)
        side = 1 if action.lower() == "buy" else 2

        # Convert symbol to MEXC format
        symbol = symbol.replace("USDT", "_USDT")

        # Prepare request parameters
        params = {
            "api_key": API_KEY,
            "req_time": get_timestamp(),
            "symbol": symbol,
            "price": "0",            # Market order
            "vol": str(quantity),
            "leverage": str(leverage),
            "side": side,
            "open_type": 2,          # Isolated margin
            "positionId": 0,         # Auto-detect
            "orderType": 1,          # Open
            "type": 1                # Market order
        }

        # Sign the request
        params["sign"] = sign_request(params, API_SECRET)
        logger.info(f"🔐 Order Payload: {params}")

        # Set headers for JSON request
        headers = {
            "Content-Type": "application/json"
        }

        # Send order to MEXC
        response = requests.post(
            f"{BASE_URL}/api/v1/private/order/submit",
            json=params,
            headers=headers
        )

        # Log raw response
        logger.info(f"📩 Raw response text: {response.text}")
        logger.info(f"📊 Status Code: {response.status_code}")

        # Log parsed response
        result = response.json()
        logger.info(f"✅ Parsed Response: {result}")

        return result

    except Exception as e:
        logger.error(f"❌ Error placing order: {e}")
        return {"error": str(e)}
