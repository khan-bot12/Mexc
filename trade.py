import time
import hmac
import hashlib
import requests
import os

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")
BASE_URL = "https://contract.mexc.com"

headers = {
    "Content-Type": "application/json",
    "ApiKey": API_KEY
}

def get_signature(params: dict) -> str:
    sorted_params = sorted(params.items())
    query_string = '&'.join(f"{k}={v}" for k, v in sorted_params)
    return hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def get_position(symbol: str):
    path = "/api/v1/position/open_positions"
    timestamp = int(time.time() * 1000)
    params = {
        "api_key": API_KEY,
        "req_time": timestamp,
        "symbol": symbol
    }
    sign = get_signature(params)
    params["sign"] = sign
    response = requests.get(BASE_URL + path, params=params)
    print(f"📊 Current Position Info: {response.json()}")
    return response.json()

def close_position(symbol: str, position_type: str, quantity: float):
    print("🔻 Closing opposite position...")
    path = "/api/v1/private/order/close_position"
    timestamp = int(time.time() * 1000)
    params = {
        "api_key": API_KEY,
        "req_time": timestamp,
        "symbol": symbol,
        "position_type": position_type,  # "LONG" or "SHORT"
        "vol": quantity
    }
    sign = get_signature(params)
    params["sign"] = sign
    response = requests.post(BASE_URL + path, json=params, headers=headers)
    print(f"📴 Close Response: {response.json()}")
    return response.json()

def place_order(action: str, symbol: str, quantity: float, leverage: int = 50):
    try:
        # Close opposite position if needed
        position_data = get_position(symbol)
        if position_data["success"] and position_data["data"]:
            for pos in position_data["data"]:
                side = pos.get("positionType")
                available = float(pos.get("available", 0))
                if available > 0:
                    if action.lower() == "buy" and side == "SHORT":
                        close_position(symbol, "SHORT", available)
                    elif action.lower() == "sell" and side == "LONG":
                        close_position(symbol, "LONG", available)

        print("🟢 Placing new order...")
        side = "OPEN_LONG" if action.lower() == "buy" else "OPEN_SHORT"
        path = "/api/v1/private/order/submit"
        timestamp = int(time.time() * 1000)
        params = {
            "api_key": API_KEY,
            "req_time": timestamp,
            "symbol": symbol,
            "price": 0,  # 0 for market order
            "vol": quantity,
            "leverage": leverage,
            "side": side,
            "open_type": "CROSS",
            "position_id": 0,
            "external_oid": str(timestamp),
            "stop_loss_price": 0,
            "take_profit_price": 0,
            "position_mode": "MERGED_SINGLE"
        }
        sign = get_signature(params)
        params["sign"] = sign

        response = requests.post(BASE_URL + path, json=params, headers=headers)
        print(f"✅ Order Response: {response.json()}")
        return response.json()

    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"error": str(e)}
