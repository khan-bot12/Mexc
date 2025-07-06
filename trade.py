import time
import hmac
import hashlib
import requests
import logging
import os
from typing import Dict, Union

# Configure logging
logger = logging.getLogger("trade")
logger.setLevel(logging.INFO)

# API Config
BASE_URL = "https://contract.mexc.com"
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

# MEXC Error Codes
ERROR_CODES = {
    10001: "Invalid symbol",
    10002: "Invalid order type",
    10003: "Invalid price",
    10004: "Invalid quantity",
    10005: "Trading restricted",
    10006: "Insufficient balance"
}

def sign_request(secret: str, params: Dict) -> str:
    """Generate HMAC SHA256 signature"""
    sorted_params = sorted(params.items())
    query_string = '&'.join(f"{k}={v}" for k,v in sorted_params)
    return hmac.new(
        secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def verify_symbol(symbol: str) -> str:
    """Ensure proper symbol formatting"""
    symbol = symbol.upper().replace("__", "_")
    if not symbol.endswith("_USDT"):
        raise ValueError(f"Invalid symbol {symbol}. Must end with _USDT")
    return symbol

def handle_api_error(response) -> str:
    """Parse MEXC API errors"""
    try:
        error_data = response.json()
        code = error_data.get("code")
        if code in ERROR_CODES:
            return f"{ERROR_CODES[code]} (Code {code})"
        return error_data.get("message", f"Unknown error (Status {response.status_code})")
    except:
        return f"HTTP {response.status_code}: {response.text}"

def get_position_id(symbol: str) -> int:
    """Get position ID for symbol (0 if new position)"""
    try:
        symbol = verify_symbol(symbol)
        endpoint = f"{BASE_URL}/api/v1/private/position/list"
        params = {
            "api_key": API_KEY,
            "req_time": str(int(time.time() * 1000)),
            "symbol": symbol
        }
        params["sign"] = sign_request(API_SECRET, params)
        
        headers = {"X-MEXC-APIKEY": API_KEY}
        response = requests.get(endpoint, params=params, headers=headers)
        
        logger.debug(f"🔍 Position check: {response.status_code} {response.text}")
        
        if response.status_code == 404:
            return 0  # New position
            
        response.raise_for_status()
        data = response.json()
        
        if data.get("success") and data.get("data"):
            return data["data"]["positionId"]
        return 0
        
    except Exception as e:
        logger.error(f"⚠️ Position check failed: {str(e)}")
        return 0

def place_order(
    action: str, 
    symbol: str, 
    quantity: Union[float, int], 
    leverage: Union[int, float]
) -> Dict:
    """Execute futures trade on MEXC"""
    try:
        symbol = verify_symbol(symbol)
        position_id = get_position_id(symbol)
        
        # 1=Open Long, 2=Open Short
        side = 1 if action.lower() == "buy" else 2
        
        payload = {
            "api_key": API_KEY,
            "req_time": str(int(time.time() * 1000)),
            "symbol": symbol,
            "price": "0",  # Market order
            "vol": str(quantity),
            "leverage": str(leverage),
            "side": side,
            "open_type": 2,  # Cross margin
            "positionId": position_id,
            "orderType": 1,  # Market
            "type": 1  # Open position
        }
        payload["sign"] = sign_request(API_SECRET, payload)
        
        headers = {
            "Content-Type": "application/json",
            "X-MEXC-APIKEY": API_KEY
        }
        
        endpoint = f"{BASE_URL}/api/v1/private/order/submit"
        logger.info(f"🚀 Order payload: {payload}")
        
        response = requests.post(endpoint, headers=headers, json=payload)
        logger.debug(f"📩 Response: {response.status_code} {response.text}")
        
        if response.status_code != 200:
            error_msg = handle_api_error(response)
            raise Exception(f"MEXC API Error: {error_msg}")
            
        result = response.json()
        
        if not result.get("success"):
            error_msg = result.get("message", "Unknown API error")
            if "code" in result:
                error_msg = f"Code {result['code']}: {error_msg}"
            raise Exception(error_msg)
            
        return {
            "success": True,
            "order_id": result.get("data", {}).get("orderId"),
            "symbol": symbol,
            "quantity": quantity,
            "leverage": leverage,
            "side": "long" if side == 1 else "short"
        }
        
    except requests.exceptions.RequestException as re:
        error_msg = f"Network error: {str(re)}"
        logger.error(f"❌ Order failed: {error_msg}")
        return {"error": error_msg, "success": False}
    except Exception as e:
        logger.error(f"❌ Order error: {str(e)}")
        return {"error": str(e), "success": False}
