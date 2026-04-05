#!/usr/bin/env python3
"""
GEMINI MICROSECOND NONCE FIX
- Uses microseconds (time.time() * 1000000) instead of milliseconds
- Prevents nonce collisions in high-frequency trading
- Your solution is CORRECT!
"""

import time
import json
import base64
import hmac
import hashlib
import requests
import os

class GeminiMicrosecondFix:
    def __init__(self):
        # Load Gemini API keys from secure_keys directory
        self.gemini_api_key = self.load_key('gemini_key')
        self.gemini_api_secret = self.load_key('gemini_secret').encode()
        
        print(f"🔧 Gemini API Key loaded: {self.gemini_api_key[:10]}...")
        print(f"🔧 Gemini Secret loaded: {len(self.gemini_api_secret)} bytes")
        
    def load_key(self, key_name):
        """Load API key from secure_keys directory"""
        key_file = f"secure_keys/.{key_name}"
        if os.path.exists(key_file):
            with open(key_file, 'r') as f:
                return f.read().strip()
        return ""
    
    def gemini_request(self, endpoint, parameters=None):
        """Make Gemini API request with MICROSECOND nonce"""
        url = "https://api.gemini.com/v1" + endpoint
        
        # ✅ YOUR SOLUTION: Use MICROSECONDS for the nonce
        nonce = int(time.time() * 1000000)  # 1,000,000 values per second
        
        payload_json = {
            "request": "/v1" + endpoint,
            "nonce": nonce
        }
        
        if parameters:
            payload_json.update(parameters)
        
        payload = base64.b64encode(json.dumps(payload_json).encode())
        signature = hmac.new(self.gemini_api_secret, payload, hashlib.sha384).hexdigest()
        
        headers = {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": self.gemini_api_key,
            "X-GEMINI-PAYLOAD": payload.decode(),
            "X-GEMINI-SIGNATURE": signature,
            "Cache-Control": "no-cache"
        }
        
        print(f"🔧 Request: {endpoint}")
        print(f"🔧 Nonce: {nonce} (microseconds)")
        print(f"🔧 Headers: X-GEMINI-APIKEY: {self.gemini_api_key[:10]}...")
        
        try:
            response = requests.post(url, headers=headers, timeout=10)
            result = response.json()
            print(f"✅ Response: {result}")
            return result
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"error": str(e)}
    
    def test_connection(self):
        """Test Gemini connection"""
        print("\n" + "="*60)
        print("🧪 TESTING GEMINI CONNECTION WITH MICROSECOND NONCE")
        print("="*60)
        
        # Test 1: Get symbols
        print("\n📊 Test 1: Get available symbols")
        symbols = self.gemini_request("/symbols")
        
        # Test 2: Get ticker for MANA
        print("\n📊 Test 2: Get MANA ticker")
        ticker = self.gemini_request("/pubticker/manausd")
        
        # Test 3: Get account balance (if permissions allow)
        print("\n📊 Test 3: Get account balances")
        balances = self.gemini_request("/balances")
        
        return {
            "symbols": symbols,
            "mana_ticker": ticker,
            "balances": balances
        }
    
    def place_test_order(self):
        """Place a test order (small amount)"""
        print("\n" + "="*60)
        print("🧪 PLACING TEST ORDER WITH MICROSECOND NONCE")
        print("="*60)
        
        order_params = {
            "symbol": "manausd",
            "amount": "1",  # 1 MANA
            "price": "0.10",  # Low price (won't execute)
            "side": "buy",
            "type": "exchange limit",
            "options": ["maker-or-cancel"]  # Won't execute if not at limit
        }
        
        print(f"🔧 Order params: {order_params}")
        response = self.gemini_request("/order/new", order_params)
        
        if "order_id" in response:
            print(f"✅ Test order placed! Order ID: {response['order_id']}")
            
            # Cancel the test order
            print("\n📊 Cancelling test order...")
            cancel_params = {"order_id": response['order_id']}
            cancel_response = self.gemini_request("/order/cancel", cancel_params)
            print(f"✅ Cancel response: {cancel_response}")
        else:
            print(f"❌ Order failed: {response}")
        
        return response

def main():
    """Main function"""
    print("🚀 GEMINI MICROSECOND NONCE FIX")
    print("="*60)
    print("Problem: Standard Unix timestamps (seconds) are too slow")
    print("Solution: Use MICROSECONDS (time.time() * 1000000)")
    print("="*60)
    
    fix = GeminiMicrosecondFix()
    
    # Test connection
    results = fix.test_connection()
    
    # Check if API is working
    if "error" not in results.get("symbols", {}):
        print("\n" + "="*60)
        print("✅ GEMINI API IS WORKING WITH MICROSECOND NONCE!")
        print("="*60)
        
        # Try placing a test order
        fix.place_test_order()
    else:
        print("\n" + "="*60)
        print("❌ GEMINI API ERROR - Check credentials")
        print("="*60)
        print(f"Error: {results.get('symbols', {}).get('error', 'Unknown')}")

if __name__ == "__main__":
    main()