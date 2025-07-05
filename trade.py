import time
import hashlib
import hmac
import requests
import os
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trade")

# MEXC API credentials from Render environment
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

# Base API URL
BASE_URL = "https://contract.mexc.com"

# Helper function: Sign payload using HMAC SHA256
def generate_signature(secret, params):
    query = "&".join([f"{k}={params[k]}" for k in sorted(params)])
    return hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()

# 🟡 Get current positions for the symbol
def get_position(symbol):
    logger.info("📊 Getting current positions...")

    path = "/api/v1/private/position/list/one"
    url = BASE_URL + path
    req_time = str(int(time.time() * 1000))

    params = {
        "api_key": API_KEY,
        "req_time": req_time,
        "symbol": symbol
    }
    sign = generate_signature(API_SECRET, params)
    params["sign"] = sign

    response = requests.get(url, params=params)
    try:
        return response.json()
    except Exception as e:
        logger.error(f"❌ Error in get_position: {e}")
        return {}

# 🟢 Place order (closes opposite position and opens new one)
def place_order(action, symbol, quantity, leverage):
    try:
        side = action.lower()
        logger.info("🟢 Placing new order...")

        # Close opposite position first
        position_info = get_position(symbol)
        logger.info(f"📊 Current Position Info: {position_info}")

        if position_info.get("success", False):
            positions = position_info.get("data", [])
            if positions:
                for pos in positions:
                    hold_side = pos.get("holdSide")
                    if (side == "buy" and hold_side == "short") or (side == "sell" and hold_side == "long"):
                        logger.info("🛑 Closing opposite position before opening new one")
                        close_side = "CLOSE_SHORT" if side == "buy" else "CLOSE_LONG"
                        close_payload = {
                            "api_key": API_KEY,
                            "req_time": str(int(time.time() * 1000)),
                            "symbol": symbol,
                            "price": "0",
                            "vol": quantity,
                            "leverage": leverage,
                            "side": close_side,
                            "open_type": 2,
                            "positionId": 0,
                            "orderType": 1
                        }
                        close_payload["sign"] = generate_signature(API_SECRET, close_payload)
                        close_response = requests.post(BASE_URL + "/api/v1/private/order/submit", json=close_payload)
                        logger.info(f"❌ Close Order Response: {close_response.json()}")
                        time.sleep(0.5)  # small delay to ensure closure

        # Open new position
        order_side = "OPEN_LONG" if side == "buy" else "OPEN_SHORT"
        payload = {
            "api_key": API_KEY,
            "req_time": str(int(time.time() * 1000)),
            "symbol": symbol,
            "price": "0",
            "vol": quantity,
            "leverage": leverage,
            "side": order_side,
            "open_type": 2,  # 1 for isolated, 2 for cross
            "positionId": 0,
            "orderType": 1
        }
        payload["sign"] = generate_signature(API_SECRET, payload)

        logger.info(f"🔐 Order Payload: {payload}")
        response = requests.post(BASE_URL + "/api/v1/private/order/submit", json=payload)
        logger.info(f"📩 Raw response text: {response.text}")

        result = response.json()
        logger.info(f"✅ Order Response: {result}")
        return result

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        return {"error": str(e)}
