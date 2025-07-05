import time
import hmac
import hashlib
import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trade")

# Environment variables
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")
BASE_URL = "https://contract.mexc.com"

HEADERS = {"Content-Type": "application/json"}

def sign(params):
    sorted_params = sorted(params.items())
    query_string = '&'.join(f"{k}={v}" for k, v in sorted_params)
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return signature

def get_position(symbol):
    """Get current positions"""
    path = "/api/v1/position/open_positions"
    url = BASE_URL + path
    req_time = str(int(time.time() * 1000))
    params = {
        "api_key": API_KEY,
        "req_time": req_time,
        "symbol": symbol
    }
    params["sign"] = sign(params)

    response = requests.get(url, headers=HEADERS, params=params)
    logger.info(f"📨 Raw Position Response: {response.text}")  # Log full response

    try:
        return response.json()
    except Exception as e:
        logger.error(f"❌ Error parsing position info: {e}")
        return {"error": str(e)}

def place_order(symbol, quantity, leverage, side):
    """Place order based on side (buy/sell)"""
    logger.info("🟢 Placing new order...")

    req_time = str(int(time.time() * 1000))
    order_side = "OPEN_LONG" if side.lower() == "buy" else "OPEN_SHORT"

    payload = {
        "api_key": API_KEY,
        "req_time": req_time,
        "symbol": symbol,
        "price": "0",              # market order
        "vol": quantity,
        "leverage": leverage,
        "side": order_side,
        "open_type": 2,            # 2 = cross margin
        "positionId": 0,
        "orderType": 1             # 1 = market order
    }

    payload["sign"] = sign(payload)
    logger.info(f"🔐 Order Payload: {payload}")

    url = BASE_URL + "/api/v1/order/submit"
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        logger.info(f"✅ Order Response: {response.text}")
        return response.json()
    except Exception as e:
        logger.error(f"❌ Order failed: {e}")
        return {"error": str(e)}
