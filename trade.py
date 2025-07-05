import time
import hmac
import hashlib
import requests
import logging
import os

# Load API keys from Render environment variables
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

BASE_URL = "https://api.mexc.com"

HEADERS = {
    "Content-Type": "application/json",
    "ApiKey": API_KEY
}

def sign_request(params: dict) -> dict:
    """Generate MEXC signature for request."""
    t = str(int(time.time() * 1000))
    params["timestamp"] = t
    query_string = '&'.join(f"{key}={params[key]}" for key in sorted(params))
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["sign"] = signature
    return params

def get_position(symbol: str):
    """Fetch current position for given symbol."""
    try:
        url = f"{BASE_URL}/api/v1/private/contract/position/list/one"
        params = {
            "symbol": symbol
        }
        signed_params = sign_request(params)
        response = requests.get(url, headers=HEADERS, params=signed_params)
        return response.json()
    except Exception as e:
        logging.error(f"Exception while getting position: {e}")
        return None

def place_order(action, symbol, quantity, leverage):
    try:
        logging.info("📊 Getting current positions...")
        current_pos = get_position(symbol)
        logging.info(f"📊 Current Position Info: {current_pos}")

        # Prepare order
        side = "OPEN_LONG" if action.lower() == "buy" else "OPEN_SHORT"

        payload = {
            "symbol": symbol,
            "price": "0",               # Market order
            "vol": quantity,
            "leverage": leverage,
            "side": side,
            "open_type": 2,            # 2 = cross margin
            "positionId": 0,
            "marginMode": "crossed",
            "orderType": 1             # 1 = market order
        }

        logging.info("🟢 Placing new order...")
        logging.info(f"🔐 Order Payload: {payload}")

        url = f"{BASE_URL}/api/v1/private/contract/order/place"
        signed_payload = sign_request(payload)
        response = requests.post(url, headers=HEADERS, json=signed_payload)
        result = response.json()
        logging.info(f"✅ Order Response: {result}")
        return result

    except Exception as e:
        logging.error(f"❌ Exception: {e}")
        return {"error": str(e)}
