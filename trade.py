import requests
import time
import hmac
import hashlib
import os

# Load environment variables
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

BASE_URL = "https://contract.mexc.com"

def get_timestamp():
    return int(time.time() * 1000)

def sign_request(params):
    query_string = '&'.join(f"{key}={params[key]}" for key in sorted(params))
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return signature

def get_position(symbol):
    path = "/api/v1/position/open_positions"
    url = BASE_URL + path
    params = {
        "api_key": API_KEY,
        "req_time": get_timestamp(),
        "symbol": symbol,
    }
    params["sign"] = sign_request(params)
    response = requests.get(url, params=params)
    return response.json()

def place_order(action, symbol, quantity, leverage):
    try:
        print("📊 Checking current position...")
        current_position = get_position(symbol)
        print(f"📊 Current Position Info: {current_position}")

        path = "/api/v1/private/order/submit"
        url = BASE_URL + path

        # MEXC side: OPEN_BUY / OPEN_SELL / CLOSE_BUY / CLOSE_SELL
        side_map = {
            "buy": ("CLOSE_SELL", "OPEN_BUY"),
            "sell": ("CLOSE_BUY", "OPEN_SELL")
        }

        close_side, open_side = side_map.get(action.lower(), (None, None))
        if not close_side or not open_side:
            return {"error": "Invalid action provided. Must be 'buy' or 'sell'"}

        # Step 1: Close existing position (if any)
        if current_position["success"] and current_position["data"]:
            for pos in current_position["data"]:
                if pos["symbol"] == symbol and float(pos["position_volume"]) > 0:
                    close_params = {
                        "api_key": API_KEY,
                        "req_time": get_timestamp(),
                        "symbol": symbol,
                        "price": 0,  # Market order
                        "vol": pos["position_volume"],
                        "side": close_side,
                        "open_type": "cross",
                        "position_id": pos["position_id"],
                        "leverage": leverage,
                        "external_oid": str(int(time.time() * 1000))
                    }
                    close_params["sign"] = sign_request(close_params)
                    print("❌ Closing opposite position...")
                    res = requests.post(url, data=close_params)
                    print("🔁 Close Response:", res.json())

        # Step 2: Place new order
        order_params = {
            "api_key": API_KEY,
            "req_time": get_timestamp(),
            "symbol": symbol,
            "price": 0,  # Market order
            "vol": quantity,
            "side": open_side,
            "open_type": "cross",
            "leverage": leverage,
            "external_oid": str(int(time.time() * 1000))
        }
        order_params["sign"] = sign_request(order_params)

        print("🟢 Placing new order...")
        response = requests.post(url, data=order_params)
        print("✅ Order Response:", response.json())
        return response.json()

    except Exception as e:
        print(f"❌ Exception in place_order: {e}")
        return {"error": str(e)}
