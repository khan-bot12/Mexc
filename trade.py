import time
import hmac
import hashlib
import requests
import os
import logging

# Load your MEXC API keys from Render environment variables
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

BASE_URL = "https://contract.mexc.com"

HEADERS = {
    "Content-Type": "application/json",
    "ApiKey": API_KEY
}

# Helper function to create MEXC request signature
def generate_signature(params):
    sorted_params = sorted(params.items())
    query_string = "&".join([f"{key}={value}" for key, value in sorted_params])
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return signature

# Fetch current position to handle one-trade-at-a-time logic
def get_position(symbol):
    endpoint = "/api/v1/position/list/history-position"
    url = BASE_URL + endpoint
    params = {
        "symbol": symbol
    }
    params["apiKey"] = API_KEY
    params["reqTime"] = int(time.time() * 1000)
    params["sign"] = generate_signature(params)

    response = requests.get(url, headers=HEADERS, params=params)
    try:
        return response.json()
    except Exception as e:
        logging.error(f"❌ Error in get_position: {e}")
        return {"code": 500, "msg": str(e)}

# Cancel opposite trade (if long is active and short comes in, or vice versa)
def cancel_opposite(symbol, side):
    position_info = get_position(symbol)
    # Simplified: you can implement logic here to cancel opposite positions if needed.
    logging.info(f"📊 Current Position Info: {position_info}")
    return position_info

# Main function to place buy/sell orders
def place_order(action, symbol, quantity, leverage):
    try:
        cancel_opposite(symbol, action)

        endpoint = "/api/v1/order/submit"
        url = BASE_URL + endpoint
        order_type = 1  # market order
        open_type = 1   # cross margin

        side = 1 if action.lower() == "buy" else 2

        params = {
            "symbol": symbol,
            "price": 0,  # market order
            "vol": quantity,
            "leverage": leverage,
            "side": side,
            "type": order_type,
            "openType": open_type,
            "positionId": 0,
            "externalOid": str(int(time.time() * 1000)),
            "apiKey": API_KEY,
            "reqTime": int(time.time() * 1000)
        }

        params["sign"] = generate_signature(params)

        logging.info("🟢 Placing new order...")
        response = requests.post(url, headers=HEADERS, json=params)
        return response.json()

    except Exception as e:
        logging.error(f"❌ Exception in place_order: {e}")
        return {"error": str(e)}
