import time
import hmac
import hashlib
import requests
import os

MEXC_API_KEY = os.getenv("MEXC_API_KEY")
MEXC_SECRET_KEY = os.getenv("MEXC_SECRET_KEY")

BASE_URL = "https://contract.mexc.com"

def get_timestamp():
    return str(int(time.time() * 1000))

def generate_signature(params):
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return hmac.new(MEXC_SECRET_KEY.encode(), sorted_params.encode(), hashlib.sha256).hexdigest()

def place_order(symbol, action, quantity, leverage):
    endpoint = "/api/v1/private/order/submit"
    url = BASE_URL + endpoint

    side = 1 if action == "buy" else 2  # 1=Open Long, 2=Open Short
    params = {
        "api_key": MEXC_API_KEY,
        "req_time": get_timestamp(),
        "symbol": symbol,
        "price": 0,  # 0 for market order
        "vol": quantity,
        "leverage": leverage,
        "side": side,
        "open_type": 1,  # Isolated
        "position_id": 0,
        "external_oid": str(int(time.time() * 100000)),
        "order_type": 1,  # Market
    }
    params["sign"] = generate_signature(params)

    try:
        res = requests.post(url, data=params)
        return res.json()
    except Exception as e:
        return {"error": str(e)}
