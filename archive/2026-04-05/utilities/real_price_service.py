#!/usr/bin/env python3
"""
REAL PRICE SERVICE - No hardcoded values, real data only
Fetches prices from multiple sources, shows errors if APIs fail
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, Optional, Tuple

class RealPriceService:
    """Service to get real prices from exchanges - NO HARDCODED VALUES"""
    
    @staticmethod
    def get_sol_price() -> Tuple[Optional[float], str]:
        """Get SOL price from multiple sources, return (price, source) or (None, error)"""
        sources = [
            ("Kraken", "https://api.kraken.com/0/public/Ticker?pair=SOLUSD"),
            ("KuCoin", "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=SOL-USDT"),
            ("Gate.io", "https://api.gateio.ws/api/v4/spot/tickers?currency_pair=SOL_USDT"),
        ]
        
        for source_name, url in sources:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    if source_name == "Kraken":
                        if "result" in data and "SOLUSD" in data["result"]:
                            price = float(data["result"]["SOLUSD"]["c"][0])
                            return price, f"Kraken ({datetime.now().strftime('%H:%M:%S')})"
                    
                    elif source_name == "KuCoin":
                        if "data" in data and "price" in data["data"]:
                            price = float(data["data"]["price"])
                            return price, f"KuCoin ({datetime.now().strftime('%H:%M:%S')})"
                    
                    elif source_name == "Gate.io":
                        if data and len(data) > 0 and "last" in data[0]:
                            price = float(data[0]["last"])
                            return price, f"Gate.io ({datetime.now().strftime('%H:%M:%S')})"
                            
            except Exception as e:
                print(f"[{source_name}] Error: {e}")
                continue
        
        return None, "ALL_PRICE_APIS_FAILED"
    
    @staticmethod
    def get_btc_price() -> Tuple[Optional[float], str]:
        """Get BTC price"""
        try:
            # Try Gemini public API
            response = requests.get("https://api.gemini.com/v1/pubticker/btcusd", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return float(data["last"]), f"Gemini ({datetime.now().strftime('%H:%M:%S')})"
        except:
            pass
        
        return None, "BTC_PRICE_UNAVAILABLE"
    
    @staticmethod
    def get_price(symbol: str) -> Tuple[Optional[float], str]:
        """Get price for any symbol"""
        symbol_map = {
            "SOL/USD": RealPriceService.get_sol_price,
            "BTC/USD": RealPriceService.get_btc_price,
            "ETH/USD": lambda: RealPriceService._get_eth_price(),
            # Add more symbols as needed
        }
        
        if symbol in symbol_map:
            return symbol_map[symbol]()
        else:
            return None, f"UNSUPPORTED_SYMBOL: {symbol}"
    
    @staticmethod
    def _get_eth_price() -> Tuple[Optional[float], str]:
        """Get ETH price"""
        try:
            # Try CoinGecko for ETH
            response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "ethereum" in data and "usd" in data["ethereum"]:
                    return data["ethereum"]["usd"], f"CoinGecko ({datetime.now().strftime('%H:%M:%S')})"
        except:
            pass
        
        return None, "ETH_PRICE_UNAVAILABLE"

def test_price_service():
    """Test the price service"""
    print("🧪 TESTING REAL PRICE SERVICE (NO HARDCODED VALUES)")
    print("=" * 60)
    
    # Test SOL price
    sol_price, sol_source = RealPriceService.get_sol_price()
    if sol_price:
        print(f"✅ SOL/USD: ${sol_price:.3f} (Source: {sol_source})")
    else:
        print(f"❌ SOL/USD: PRICE UNAVAILABLE (Error: {sol_source})")
    
    # Test BTC price
    btc_price, btc_source = RealPriceService.get_btc_price()
    if btc_price:
        print(f"✅ BTC/USD: ${btc_price:.2f} (Source: {btc_source})")
    else:
        print(f"❌ BTC/USD: PRICE UNAVAILABLE (Error: {btc_source})")
    
    print("\n⚠️  IMPORTANT: If prices show as unavailable,")
    print("   check internet connection and API availability.")
    print("   NEVER hardcode values as fallback!")

if __name__ == "__main__":
    test_price_service()