#!/usr/bin/env python3
"""
Advanced Crypto Market Analysis
Adds RSI, moving averages, and support/resistance levels
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up/down if down != 0 else 0
    rsi = 100 - 100/(1 + rs)
    
    for i in range(period+1, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0
        else:
            upval = 0
            downval = -delta
        
        up = (up*(period-1) + upval)/period
        down = (down*(period-1) + downval)/period
        rs = up/down if down != 0 else 0
        rsi = np.append(rsi, 100 - 100/(1 + rs))
    
    return rsi

def get_historical_data(symbol, days=30):
    """Get historical price data"""
    try:
        if symbol == 'BTCUSD':
            coin_id = 'bitcoin'
        elif symbol == 'ETHUSD':
            coin_id = 'ethereum'
        else:
            return None
        
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart'
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        prices = [point[1] for point in data['prices']]
        timestamps = [datetime.fromtimestamp(point[0]/1000) for point in data['prices']]
        
        return pd.DataFrame({
            'timestamp': timestamps,
            'price': prices
        })
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None

def analyze_technical_indicators(symbol):
    """Analyze technical indicators for trading decisions"""
    df = get_historical_data(symbol, days=30)
    if df is None or len(df) < 20:
        return None
    
    prices = df['price'].values
    
    # Calculate indicators
    rsi = calculate_rsi(prices)
    current_rsi = rsi[-1] if len(rsi) > 0 else 50
    
    # Moving averages
    ma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else prices[-1]
    ma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else prices[-1]
    
    # Support and resistance levels
    recent_prices = prices[-10:]
    support = np.min(recent_prices)
    resistance = np.max(recent_prices)
    current_price = prices[-1]
    
    # Determine signal based on technicals
    signal = 'hold'
    reasoning = []
    
    # RSI analysis
    if current_rsi < 30:
        reasoning.append("RSI indicates oversold conditions")
        signal = 'buy'
    elif current_rsi > 70:
        reasoning.append("RSI indicates overbought conditions")
        signal = 'sell'
    else:
        reasoning.append("RSI in neutral range")
    
    # Moving average analysis
    if current_price > ma_20 > ma_50:
        reasoning.append("Bullish MA alignment (price > MA20 > MA50)")
        if signal == 'hold':
            signal = 'buy'
    elif current_price < ma_20 < ma_50:
        reasoning.append("Bearish MA alignment (price < MA20 < MA50)")
        if signal == 'hold':
            signal = 'sell'
    
    # Support/resistance analysis
    distance_to_support = abs(current_price - support) / current_price
    distance_to_resistance = abs(current_price - resistance) / current_price
    
    if distance_to_support < 0.02:  # Within 2% of support
        reasoning.append("Near support level, potential bounce")
        signal = 'buy'
    elif distance_to_resistance < 0.02:  # Within 2% of resistance
        reasoning.append("Near resistance level, potential rejection")
        signal = 'sell'
    
    return {
        'symbol': symbol,
        'current_price': current_price,
        'rsi': round(current_rsi, 2),
        'ma_20': round(ma_20, 2),
        'ma_50': round(ma_50, 2),
        'support': round(support, 2),
        'resistance': round(resistance, 2),
        'signal': signal,
        'reasoning': reasoning,
        'timestamp': datetime.now().isoformat()
    }

def main():
    """Run advanced technical analysis"""
    print("\n" + "="*70)
    print("ADVANCED TECHNICAL ANALYSIS")
    print("="*70)
    
    symbols = ['BTCUSD', 'ETHUSD']
    
    for symbol in symbols:
        print(f"\nAnalyzing {symbol}...")
        analysis = analyze_technical_indicators(symbol)
        
        if analysis:
            print(f"  Current Price: ${analysis['current_price']:,.2f}")
            print(f"  RSI (14): {analysis['rsi']}")
            print(f"  MA20: ${analysis['ma_20']:,.2f}")
            print(f"  MA50: ${analysis['ma_50']:,.2f}")
            print(f"  Support: ${analysis['support']:,.2f}")
            print(f"  Resistance: ${analysis['resistance']:,.2f}")
            print(f"  Technical Signal: {analysis['signal'].upper()}")
            
            if analysis['reasoning']:
                print("  Reasoning:")
                for reason in analysis['reasoning']:
                    print(f"    • {reason}")
        
        time.sleep(1)  # Rate limiting

if __name__ == "__main__":
    main()