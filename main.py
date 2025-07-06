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
        # Ensure proper symbol formatting
        if not symbol.endswith("_USDT"):
            symbol = f"{symbol.split('_')[0]}_USDT"
            
        endpoint = f"{BASE_URL}/api/v1/private/position/list"
        params = {
            "api_key": API_KEY,
            "req_time": str(int(time.time() * 1000)),
            "symbol": symbol.upper()
        }
        params["sign"] = sign_request(API_SECRET, params)
        
        headers = {"X-MEXC-APIKEY": API_KEY}
        response = requests.get(endpoint, params=params, headers=headers)
        
        logger.debug(f"🔍 Position Check Request: {response.request.url}")
        logger.debug(f"🔍 Position Check Response: {response.status_code} - {response.text}")
        
        if response.status_code == 404:
            logger.info(f"ℹ️ No existing position for {symbol}, will open new position")
            return 0
            
        response.raise_for_status()
        data = response.json()
        
        if data.get("success", False):
            if data.get("data"):
                return data["data"]["positionId"]
            return 0  # No position exists yet
        raise Exception(f"API Error: {data.get('message', 'Unknown error')}")
            
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"🚨 HTTP Error fetching position: {str(http_err)}")
        return 0
    except Exception as e:
        logger.error(f"🚨 General Error fetching position: {str(e)}")
        return 0

def place_order(action: str, symbol: str, quantity: Union[float, int], leverage: Union[int, float]) -> Dict:
    """Place futures order on MEXC."""
    try:
        # Format symbol correctly
        symbol = symbol.replace("-", "_").replace("USDT", "_USDT")
        position_id = get_position_id(symbol)
        
        # Determine order side (1=Open Long, 2=Open Short, 3=Close Long, 4=Close Short)
        side = 1 if action.lower() == "buy" else 2
        
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
            "type": 1  # 1=open position, 2=close position
        }
        
        payload["sign"] = sign_request(API_SECRET, payload)
        
        headers = {
            "Content-Type": "application/json",
            "X-MEXC-APIKEY": API_KEY
        }
        
        endpoint = f"{BASE_URL}/api/v1/private/order/submit"
        logger.info(f"🚀 Sending order payload: {payload}")
        
        response = requests.post(endpoint, headers=headers, json=payload)
        logger.debug(f"📩 Raw API Response: {response.status_code} - {response.text}")
        
        response.raise_for_status()
        result = response.json()
        
        if not result.get("success", False):
            error_msg = result.get("message", "Unknown error from MEXC")
            raise Exception(f"MEXC API Error: {error_msg}")
            
        return result
        
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP Error: {str(http_err)} - Response: {http_err.response.text}"
        logger.error(f"❌ Order Failed: {error_msg}")
        return {"error": error_msg, "success": False}
    except Exception as e:
        logger.error(f"❌ Order Error: {str(e)}", exc_info=True)
        return {"error": str(e), "success": False}
