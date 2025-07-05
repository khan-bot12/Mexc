import os
import time
import hmac
import hashlib
import json
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trade")

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")
BASE_URL = "https://contract.mexc.com"

HEADERS = {"Content-Type": "application/json"}

def sign(params):
    """Create HMAC SHA256 signature"""
    query_string = "&".join([f"{k}={params[k]}" for k in sorted(params)])
    return hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()

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
    try:
        return response.json()
    except Exception as e:
        logger.error(f"❌ Error parsing position info: {e}")
        return {"error": str(e)}

def place_order(action, symbol, quantity, leverage):
    """Close opposite position and place new order"""
    logger.info("📊 Getting current positions...")
    positions = get_position(symbol)
    logger.info(f"📊 Current Position Info: {positions}")

    side = "OPEN_LONG" if action.lower() == "buy" else "OPEN_SHORT"
    close_side = "CLOSE_SHORT" if action.lower() == "buy" else "CLOSE_LONG"

    if positions.get("success") and positions.get("data"):
        for pos in positions["data"]:
            if pos["positionType"] == 1 and float(pos["availablePosition"]) > 0:
                logger.info("❌ Closing opposite position...")
                close_payload = {
                    "api_key": API_KEY,
                    "req_time": str(int(time.time() * 1000)),
                    "symbol": symbol,
                    "price": "0",  # Market order
                    "vol": float(pos["availablePosition"]),
                    "leverage": leverage,
                    "side": close_side,
                    "open_type": 2,  # 2 = cross
                    "positionId": int(pos["positionId"]),
                    "orderType": 1
                }
                close_payload["sign"] = sign(close_payload)
                close_url = BASE_URL + "/api/v1/order/put_limit"
                close_res = requests.post(close_url, headers=HEADERS, data=json.dumps(close_payload))
                logger.info(f"🔴 Close Order Response: {close_res.text}")

    logger.info("🟢 Placing new order...")
    payload = {
        "api_key": API_KEY,
        "req_time": str(int(time.time() * 1000)),
        "symbol": symbol,
        "price": "0",  # Market order
        "vol": quantity,
        "leverage": leverage,
        "side": side,
        "open_type": 2,  # 2 = cross margin
        "positionId": 0,
        "orderType": 1
    }
    payload["sign"] = sign(payload)

    logger.info(f"🔐 Order Payload: {payload}")
    url = BASE_URL + "/api/v1/order/put_limit"
    response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
    
    try:
        logger.info(f"📤 Full Response Text: {response.text}")
        return response.json()
    except Exception as e:
        logger.error(f"❌ Error decoding JSON: {e}")
        return {"error": str(e)}

