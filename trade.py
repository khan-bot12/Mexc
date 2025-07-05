import time
import uuid
import hmac
import hashlib
import requests
import os
import logging

from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")
BASE_URL = "https://contract.mexc.com"

logger = logging.getLogger(__name__)

def get_signature(params, secret_key):
    query_string = urlencode(params)
    return hmac.new(
        secret_key.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def get_position(symbol):
    """Get the current positions for a symbol."""
    endpoint = "/api/v1/private/position/list/pos"
    url = BASE_URL + endpoint

    timestamp = str(int(time.time() * 1000))
    params = {
        "api_key": API_KEY,
        "req_time": timestamp
    }

    signature = get_signature(params, API_SECRET)
    params["sign"] = signature

    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data
    except Exception as e:
        logger.error(f"❌ Exception getting position: {e}")
        return None

def place_order(symbol, quantity, leverage, action):
    logger.info("📊 Getting current positions...")

    position_info = get_position(symbol)
    logger.info(f"📊 Current Position Info: {position_info}")

    # Determine the side
    if action == "buy":
        side = "OPEN_LONG"
        close_side = "CLOSE_SHORT"
    elif action == "sell":
        side = "OPEN_SHORT"
        close_side = "CLOSE_LONG"
    else:
        return {"error": "Invalid action"}

    # If an opposite position exists, close it first
    if position_info and position_info.get("success"):
        for pos in position_info.get("data", []):
            if pos["symbol"] == symbol and pos["positionSide"] in ["SHORT", "LONG"]:
                if (action == "buy" and pos["positionSide"] == "SHORT") or \
                   (action == "sell" and pos["positionSide"] == "LONG"):
                    logger.info("🔁 Closing opposite position...")
                    close_payload = {
                        "api_key": API_KEY,
                        "req_time": str(int(time.time() * 1000)),
                        "symbol": symbol,
                        "price": "0",  # Market
                        "vol": float(pos["availableVol"]),
                        "leverage": leverage,
                        "side": close_side,
                        "open_type": 2,
                        "positionId": pos["positionId"],
                        "orderType": 1
                    }
                    close_payload["sign"] = get_signature(close_payload, API_SECRET)
                    close_url = BASE_URL + "/api/v1/private/order/submit"
                    try:
                        close_resp = requests.post(close_url, json=close_payload)
                        logger.info(f"🔒 Close Order Response: {close_resp.json()}")
                    except Exception as e:
                        logger.error(f"❌ Exception closing order: {e}")

    logger.info("🟢 Placing new order...")

    payload = {
        "api_key": API_KEY,
        "req_time": str(int(time.time() * 1000)),
        "symbol": symbol,
        "price": "0",  # Market price
        "vol": quantity,
        "leverage": leverage,
        "side": side,
        "open_type": 2,  # 2 = Cross Margin
        "positionId": 0,
        "orderType": 1  # 1 = Market
    }

    payload["sign"] = get_signature(payload, API_SECRET)

    url = BASE_URL + "/api/v1/private/order/submit"
    logger.info(f"🔐 Order Payload: {payload}")

    try:
        response = requests.post(url, json=payload)
        logger.info(f"✅ Order Response: {response.json()}")
        return response.json()
    except Exception as e:
        logger.error(f"❌ Exception placing order: {e}")
        return {"error": str(e)}
