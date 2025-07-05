import time
import hmac
import hashlib
import requests
import logging
import os

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")
BASE_URL = "https://api.mexc.com"

headers = {
    "Content-Type": "application/json",
    "ApiKey": API_KEY
}

def generate_signature(req_time, sign_params):
    sign_str = f"{API_KEY}{req_time}{sign_params}"
    signature = hmac.new(API_SECRET.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature

def place_order(action, symbol, quantity, leverage):
    try:
        side = "OPEN_LONG" if action == "buy" else "OPEN_SHORT"
        position_side = "LONG" if action == "buy" else "SHORT"
        margin_mode = "crossed"  # For cross margin

        # Step 1: Get current positions (optional)
        pos_req_time = str(int(time.time() * 1000))
        pos_params = f"symbol={symbol}&marginMode={margin_mode}"
        pos_sign = generate_signature(pos_req_time, pos_params)
        pos_headers = headers.copy()
        pos_headers.update({
            "Request-Time": pos_req_time,
            "Signature": pos_sign
        })

        pos_url = f"{BASE_URL}/api/v1/private/futures/position/open-position"
        logging.info(f"📊 Getting current positions...")
        pos_response = requests.get(pos_url + "?" + pos_params, headers=pos_headers)
        logging.info(f"📊 Current Position Info: {pos_response.json()}")

        # Step 2: Place order
        order_req_time = str(int(time.time() * 1000))
        order_params = {
            "symbol": symbol,
            "price": "0",  # Market Order
            "vol": quantity,
            "leverage": leverage,
            "side": side,
            "openType": "isolated",  # Use 'isolated' or 'cross' if supported
            "positionId": 0,
            "marginMode": margin_mode,
            "orderType": 1  # 1 = Market Order
        }
        order_body = "&".join([f"{k}={v}" for k, v in order_params.items()])
        order_sign = generate_signature(order_req_time, order_body)

        order_headers = headers.copy()
        order_headers.update({
            "Request-Time": order_req_time,
            "Signature": order_sign
        })

        logging.info("🟢 Placing new order...")
        logging.info(f"🔐 Order Payload: {order_params}")

        order_url = f"{BASE_URL}/api/v1/private/futures/order/place"
        order_response = requests.post(order_url, headers=order_headers, json=order_params)
        logging.info(f"✅ Order Response: {order_response.json()}")
        return order_response.json()

    except Exception as e:
        logging.error(f"❌ Exception in place_order: {e}")
        return {"error": str(e)}
