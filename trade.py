import time
import hashlib
import hmac
import requests
import logging
import os

# ENV values
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")
BASE_URL = "https://api.mexc.com"

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trade")

# Sign function
def generate_signature(secret, params: dict) -> str:
    sorted_params = sorted(params.items())
    query_string = '&'.join([f"{key}={value}" for key, value in sorted_params])
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

# Place order
def place_order(action, symbol, quantity, leverage):
    logger.info("📊 Getting current positions...")

    # Optional: Get positions logic can go here if needed

    logger.info("🟢 Placing new order...")

    side = "OPEN_LONG" if action.lower() == "buy" else "OPEN_SHORT"

    path = "/api/v1/private/futures/v1/order/place"
    url = BASE_URL + path

    req_time = str(int(time.time() * 1000))
    body = {
        "api_key": API_KEY,
        "req_time": req_time,
        "symbol": symbol.upper(),
        "price": "0",  # market order
        "vol": quantity,
        "leverage": leverage,
        "side": side,
        "open_type": 2,            # 2 = cross margin
        "positionId": 0,
        "orderType": 1             # 1 = market order
    }

    body["sign"] = generate_signature(API_SECRET, body)

    logger.info(f"🔐 Order Payload: {body}")
    response = requests.post(url, json=body)
    result = response.json()
    logger.info(f"✅ Order Response: {result}")
    return result
