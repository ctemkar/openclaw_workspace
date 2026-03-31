#!/usr/bin/env python3
"""Check real market data from public APIs"""

import requests
import json
import datetime

def get_crypto_prices():
    """Get real crypto prices from CoinGecko API"""
    try:
        # CoinGecko free API
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin,ethereum',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                'BTC': {
                    'price': data['bitcoin']['usd'],
                    'change': data['bitcoin']['usd_24h_change']
                },
                'ETH': {
                    'price': data['ethereum']['usd'],
                    'change': data['ethereum']['usd_24h_change']
                }
            }
    except Exception as e:
        print(f"Error fetching from CoinGecko: {e}")
    
    return None

def get_binance_data():
    """Get data from Binance public API"""
    try:
        symbols = ['BTCUSDT', 'ETHUSDT']
        results = {}
        
        for symbol in symbols:
            url = f"https://api.binance.com/api/v3/ticker/24hr"
            params = {'symbol': symbol}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results[symbol.replace('USDT', 'USD')] = {
                    'price': float(data['lastPrice']),
                    'change': float(data['priceChangePercent']),
                    'high': float(data['highPrice']),
                    'low': float(data['lowPrice']),
                    'volume': float(data['volume'])
                }
        
        return results
    except Exception as e:
        print(f"Error fetching from Binance: {e}")
    
    return None

def main():
    print("Fetching real market data...")
    print("=" * 50)
    
    # Try CoinGecko first
    print("\n1. CoinGecko API:")
    cg_data = get_crypto_prices()
    if cg_data:
        for coin, data in cg_data.items():
            print(f"{coin}: ${data['price']:,.2f} ({data['change']:+.2f}%)")
    else:
        print("Failed to fetch from CoinGecko")
    
    # Try Binance
    print("\n2. Binance API:")
    binance_data = get_binance_data()
    if binance_data:
        for symbol, data in binance_data.items():
            print(f"{symbol}: ${data['price']:,.2f} ({data['change']:+.2f}%)")
            print(f"  24h Range: ${data['low']:,.2f} - ${data['high']:,.2f}")
            print(f"  Volume: {data['volume']:,.2f}")
    else:
        print("Failed to fetch from Binance")
    
    # Calculate support/resistance levels
    print("\n3. Support/Resistance Analysis:")
    if binance_data:
        for symbol, data in binance_data.items():
            current = data['price']
            # Simple support/resistance based on 24h range
            support = data['low'] * 0.99  # 1% below low
            resistance = data['high'] * 1.01  # 1% above high
            
            print(f"\n{symbol}:")
            print(f"  Current: ${current:,.2f}")
            print(f"  24h Low: ${data['low']:,.2f}")
            print(f"  24h High: ${data['high']:,.2f}")
            print(f"  Calculated Support: ${support:,.2f}")
            print(f"  Calculated Resistance: ${resistance:,.2f}")
            
            # Check if current price is near support/resistance
            if current < data['low'] * 1.02:  # Within 2% of low
                print(f"  → Price near 24h low - potential BUY zone")
            elif current > data['high'] * 0.98:  # Within 2% of high
                print(f"  → Price near 24h high - potential SELL zone")
            else:
                print(f"  → Price in middle range - wait for clearer signal")

if __name__ == "__main__":
    main()