#!/usr/bin/env python3
"""
Fetch real market data from public APIs for better analysis
"""

import requests
import json
from datetime import datetime

def get_binance_price(symbol: str) -> dict:
    """Get price data from Binance"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        return {
            'symbol': symbol,
            'price': float(data['lastPrice']),
            'change_24h': float(data['priceChangePercent']),
            'high_24h': float(data['highPrice']),
            'low_24h': float(data['lowPrice']),
            'volume': float(data['volume']),
            'quote_volume': float(data['quoteVolume']),
            'source': 'binance'
        }
    except Exception as e:
        print(f"Error fetching Binance data for {symbol}: {e}")
        return None

def get_coingecko_price(coin_id: str, vs_currency: str = 'usd') -> dict:
    """Get price data from CoinGecko"""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': vs_currency,
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if coin_id in data:
            coin_data = data[coin_id]
            return {
                'symbol': coin_id,
                'price': coin_data.get(vs_currency, 0),
                'change_24h': coin_data.get(f'{vs_currency}_24h_change', 0),
                'volume_24h': coin_data.get(f'{vs_currency}_24h_vol', 0),
                'last_updated': coin_data.get('last_updated_at', 0),
                'source': 'coingecko'
            }
    except Exception as e:
        print(f"Error fetching CoinGecko data for {coin_id}: {e}")
    return None

def get_market_sentiment() -> dict:
    """Get crypto market sentiment indicators"""
    try:
        # Fear & Greed Index (alternative source since original requires API key)
        # Using simplified sentiment based on price movements
        btc_data = get_binance_price('BTCUSDT')
        eth_data = get_binance_price('ETHUSDT')
        
        if btc_data and eth_data:
            avg_change = (btc_data['change_24h'] + eth_data['change_24h']) / 2
            
            # Simple sentiment calculation
            if avg_change > 5:
                sentiment = "Very Bullish"
                score = 80
            elif avg_change > 2:
                sentiment = "Bullish"
                score = 65
            elif avg_change > -2:
                sentiment = "Neutral"
                score = 50
            elif avg_change > -5:
                sentiment = "Bearish"
                score = 35
            else:
                sentiment = "Very Bearish"
                score = 20
            
            return {
                'sentiment': sentiment,
                'score': score,
                'avg_24h_change': avg_change,
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        print(f"Error calculating sentiment: {e}")
    
    return {
        'sentiment': 'Neutral',
        'score': 50,
        'avg_24h_change': 0,
        'timestamp': datetime.now().isoformat()
    }

def calculate_support_resistance(price_data: dict) -> tuple:
    """Calculate simple support and resistance levels"""
    price = price_data['price']
    high = price_data.get('high_24h', price * 1.05)
    low = price_data.get('low_24h', price * 0.95)
    
    # Simple calculation: support at recent low, resistance at recent high
    support = low
    resistance = high
    
    # Add psychological levels (round numbers)
    rounded_support = round(price * 0.95 / 100) * 100
    rounded_resistance = round(price * 1.05 / 100) * 100
    
    return support, resistance, rounded_support, rounded_resistance

def main():
    print("=== Real Market Analysis ===")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 50)
    
    # Get BTC data
    print("\n--- Bitcoin (BTC) ---")
    btc_binance = get_binance_price('BTCUSDT')
    btc_coingecko = get_coingecko_price('bitcoin')
    
    btc_data = btc_binance or btc_coingecko
    if btc_data:
        support, resistance, r_support, r_resistance = calculate_support_resistance(btc_data)
        print(f"Price: ${btc_data['price']:,.2f}")
        print(f"24h Change: {btc_data.get('change_24h', 0):.2f}%")
        print(f"24h High: ${btc_data.get('high_24h', btc_data['price'] * 1.05):,.2f}")
        print(f"24h Low: ${btc_data.get('low_24h', btc_data['price'] * 0.95):,.2f}")
        print(f"Support: ${support:,.2f} (Rounded: ${r_support:,.0f})")
        print(f"Resistance: ${resistance:,.2f} (Rounded: ${r_resistance:,.0f})")
        print(f"24h Volume: ${btc_data.get('quote_volume', btc_data.get('volume_24h', 0)):,.0f}")
        print(f"Source: {btc_data['source']}")
    else:
        print("Could not fetch BTC data")
        btc_data = None
    
    # Get ETH data
    print("\n--- Ethereum (ETH) ---")
    eth_binance = get_binance_price('ETHUSDT')
    eth_coingecko = get_coingecko_price('ethereum')
    
    eth_data = eth_binance or eth_coingecko
    if eth_data:
        support, resistance, r_support, r_resistance = calculate_support_resistance(eth_data)
        print(f"Price: ${eth_data['price']:,.2f}")
        print(f"24h Change: {eth_data.get('change_24h', 0):.2f}%")
        print(f"24h High: ${eth_data.get('high_24h', eth_data['price'] * 1.05):,.2f}")
        print(f"24h Low: ${eth_data.get('low_24h', eth_data['price'] * 0.95):,.2f}")
        print(f"Support: ${support:,.2f} (Rounded: ${r_support:,.0f})")
        print(f"Resistance: ${resistance:,.2f} (Rounded: ${r_resistance:,.0f})")
        print(f"24h Volume: ${eth_data.get('quote_volume', eth_data.get('volume_24h', 0)):,.0f}")
        print(f"Source: {eth_data['source']}")
    else:
        print("Could not fetch ETH data")
        eth_data = None
    
    # Get market sentiment
    print("\n--- Market Sentiment ---")
    sentiment = get_market_sentiment()
    print(f"Sentiment: {sentiment['sentiment']}")
    print(f"Score: {sentiment['score']}/100")
    print(f"Average 24h Change: {sentiment['avg_24h_change']:.2f}%")
    
    # Conservative trading analysis
    print("\n--- Conservative Trading Analysis ---")
    
    trading_decisions = []
    
    if btc_data:
        btc_price = btc_data['price']
        btc_change = btc_data.get('change_24h', 0)
        btc_support = btc_data.get('low_24h', btc_price * 0.95)
        
        # Conservative BTC analysis
        btc_decision = "HOLD"
        btc_reason = "Neutral conditions"
        
        if btc_change < -3 and btc_price <= btc_support * 1.02:
            btc_decision = "BUY"
            btc_reason = "Price near support with recent dip"
        elif btc_change > 3 and btc_price >= btc_data.get('high_24h', btc_price * 1.05) * 0.98:
            btc_decision = "SELL"
            btc_reason = "Price near resistance with recent gain"
        
        print(f"BTC Decision: {btc_decision}")
        print(f"Reason: {btc_reason}")
        trading_decisions.append(('BTC', btc_decision, btc_reason, btc_price))
    
    if eth_data:
        eth_price = eth_data['price']
        eth_change = eth_data.get('change_24h', 0)
        eth_support = eth_data.get('low_24h', eth_price * 0.95)
        
        # Conservative ETH analysis
        eth_decision = "HOLD"
        eth_reason = "Neutral conditions"
        
        if eth_change < -3 and eth_price <= eth_support * 1.02:
            eth_decision = "BUY"
            eth_reason = "Price near support with recent dip"
        elif eth_change > 3 and eth_price >= eth_data.get('high_24h', eth_price * 1.05) * 0.98:
            eth_decision = "SELL"
            eth_reason = "Price near resistance with recent gain"
        
        print(f"ETH Decision: {eth_decision}")
        print(f"Reason: {eth_reason}")
        trading_decisions.append(('ETH', eth_decision, eth_reason, eth_price))
    
    # Save analysis
    analysis_data = {
        'timestamp': datetime.now().isoformat(),
        'btc': btc_data,
        'eth': eth_data,
        'sentiment': sentiment,
        'trading_decisions': trading_decisions
    }
    
    with open('market_analysis.json', 'w') as f:
        json.dump(analysis_data, f, indent=2)
    
    print(f"\nAnalysis saved to market_analysis.json")
    print("=" * 50)
    
    return analysis_data

if __name__ == "__main__":
    main()