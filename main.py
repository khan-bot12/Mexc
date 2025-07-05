from fastapi import FastAPI, Request
import uvicorn
from trade import place_order

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print(f"Incoming webhook data: {data}")
        
        action = data.get("action")
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        leverage = data.get("leverage")
        
        if not all([action, symbol, quantity, leverage]):
            return {"error": "Missing required parameters."}
        
        result = place_order(action, symbol, quantity, leverage)
        print(f"📤 Result from place_order: {result}")
        return result
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"error": str(e)}

# For local testing (won't run on Render)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
