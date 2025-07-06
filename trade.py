import time
import hmac
import hashlib
import requests
import logging
import os
from typing import Dict, Union

# Set up logging
logger = logging.getLogger("trade")
logger.setLevel(logging.INFO)

# API Configuration
BASE_URL = "https://contract.mexc.com"
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

def sign_request(secret: str, params: Dict) -> str:
    """Generate HMAC SHA256 signature for MEXC Futures API."""
    sorted_params = sorted(params.items())
    query_string = '&'.join(f"{key}={value}" for key, value in sorted_params)
    return hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def get_position_id(symbol: str) -> int:
    """Get current position ID for the symbol."""
    try:
        endpoint = f"{BASE_URL}/api/v1/private/position/list"
        params = {
            "api_key": API_KEY,
            "req_time": str(int(time.time() * 1000)),
            "symbol": symbol.upper()
        }
        params["sign"] = sign_request(API_SECRET, params)
        
        headers = {"X-MEXC-APIKEY": API_KEY}
        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get("success", False) and data.get("data"):
            return data["data"]["positionId"]
        return 0
    except Exception as e:
        logger.error(f"❌ Position ID Error: {str(e)}")
        return 0

def place_order(action: str, symbol: str, quantity: Union[str, float], leverage: Union[str, int]) -> Dict:
    """Place futures order on MEXC."""
    try:
        position_id = get_position_id(symbol)
        side = 1 if action.lower() == "buy" else 2  # 1=Open Long, 2=Open Short
        
        payload = {
            "api_key": API_KEY,
            "req_time": str(int(time.time() * 1000)),
            "symbol": symbol.upper(),
            "price": "0",  # Market order
            "vol": str(quantity),
            "leverage": str(leverage),
            "side": side,
            "open_type": 2,  # Cross margin
            "positionId": position_id,
            "orderType": 1,  # Market order
            "type": 1  # 1=open position
        }
        
        payload["sign"] = sign_request(API_SECRET, payload)
        
        headers = {
            "Content-Type": "application/json",
            "X-MEXC-APIKEY": API_KEY
        }
        
        endpoint = f"{BASE_URL}/api/v1/private/order/submit"
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        if not result.get("success", False):
            error_msg = result.get("message", "Unknown error from MEXC")
            raise Exception(f"MEXC API Error: {error_msg}")
            
        return result
        
    except Exception as e:
        logger.error(f"❌ Order Error: {str(e)}", exc_info=True)
        return {"error": str(e), "success": False}
