import time
import hashlib
import hmac
import requests
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trade")

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

BASE_URL = "https://contract.mexc.com"

def generate_signature(secret_key, req_time, params):
    sorted_params = sorted(params.items())
    query_string = '&'.join([f"{key}={value}" for key, value in sorted_params])
    message = f"{query_string}&req_time={req_time}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def get_position(symbol):
    url = f"{BASE_URL}/api/v1/private/position/list"
    req_time = str(int(time.time() * 1000))
    params = {
        "api_key": API_KEY,
        "req_time": req_time
    }
    sign = generate_signature(API_SECRET, req_time, params)
    params["sign"] = sign

    try:
        response = requests.get(url, params=params)
        data = response.json()
        logger.info(f"📊 Current Position Info: {data}")
        return data
    except Exception as e:
        logger.error(f"❌ Error fetching position info: {e}")
        return None

def place_order(action, symbol, quantity, leverage):
    logger.info("🟢 Placing new order...")
    url = f"{BASE_URL}/api/v1/private/order/submit"
    req_time = str(int(time.time() * 1000))

    side = 1 if action.lower() == "buy" else 2  # 1=buy/long, 2=sell/short

    payload = {
        "api_key": API_KEY,
        "req_time": req_time,
        "symbol": symbol,
        "price": "0",            # Market order
        "vol": quantity,
        "leverage": leverage,
        "side": side,
        "open_type": 2,          # 2 = cross margin
        "positionId": 0,
        "orderType": 1           # 1 = market order
    }

    payload["sign"] = generate_signature(API_SECRET, req_time, payload)

    logger.info(f"🔐 Order Payload: {payload}")

    try:
        response = requests.post(url, json=payload)
        logger.info(f"📩 Raw response text: {response.text}")
        data = response.json()
        logger.info(f"✅ Order Response: {data}")
        return data
    except Exception as e:
        logger.error(f"❌ Order Placement Failed: {e}")
        return {"error": str(e)}
