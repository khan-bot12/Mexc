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

        side = 1 if action.lower() == "buy" else 2
        symbol = symbol.replace("USDT", "_USDT")

        params = {
            "api_key": API_KEY,
            "req_time": get_timestamp(),
            "symbol": symbol,
            "price": "0",
            "vol": str(quantity),
            "leverage": str(leverage),
            "side": side,
            "open_type": 2,
            "positionId": 0,
            "orderType": 1,
            "type": 1
        }

        params["sign"] = sign_request(params, API_SECRET)
        logger.info(f"🔐 Order Payload: {params}")

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/private/order/submit",
                json=params,
                headers=headers
            )

            # Console output (Render will show this in logs)
            print(">>> STATUS CODE:", response.status_code)
            print(">>> RESPONSE TEXT:", response.text)

            logger.info(f"📩 Raw response text: {response.text}")
            logger.info(f"📊 Status Code: {response.status_code}")

            result = response.json()
            logger.info(f"✅ Parsed Response: {result}")

            return result

        except Exception as post_error:
            logger.error(f"❌ requests.post failed: {post_error}")
            return {"error": str(post_error)}

    except Exception as e:
        logger.error(f"❌ Error placing order: {e}")
        return {"error": str(e)}
