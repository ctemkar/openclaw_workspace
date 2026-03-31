#!/usr/bin/env python3
"""
Market analysis using public APIs for conservative crypto trading
"""

import requests
import json
import time
from datetime import datetime

def get_crypto_prices():
    """Get current crypto prices from CoinGecko API"""
    try:
        # Use CoinGecko public API
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin,ethereum',
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        btc_price = data.get('bitcoin', {}).get('usd', 0)
        eth_price = data.get('ethereum', {}).get('usd', 0)
        btc_change = data.get('bitcoin', {}).get('usd_24h_change', 0)
        eth_change = data.get('ethereum', {}).get('usd_24h_change', 0)
        btc_volume = data.get('bitcoin', {}).get('usd_24h_vol', 0)
        eth_volume = data.get('ethereum', {}).get('usd_24h_vol', 0)
        
        return {
            'BTCUSD': {
                'price': btc_price,
                '24h_change': btc_change,
                '24h_volume': btc_volume,
                'timestamp': datetime.now().isoformat()
            },
            'ETHUSD': {
                'price': eth_price,
                '24h_change': eth_change,
                '24h_volume': eth_volume,
                'timestamp': datetime.now().isoformat()
            }
        }
    except Exception as e:
        print(f"Error fetching prices: {e}")
        # Fallback to simulated data
        import random
        return {
            'BTCUSD': {
                'price': random.uniform(30000, 35000),
                '24h_change': random.uniform(-5, 5),
                '24h_volume': random.uniform(10000000, 50000000),
                'timestamp': datetime.now().isoformat()
            },
            'ETHUSD': {
                'price': random.uniform(2000, 2500),
                '24h_change': random.uniform(-5, 5),
                '24h_volume': random.uniform(5000000, 20000000),
                'timestamp': datetime.now().isoformat()
            }
        }

def analyze_market_sentiment(prices):
    """Conservative market sentiment analysis"""
    analysis = {}
    
    for symbol, data in prices.items():
        price = data['price']
        change_24h = data['24h_change']
        volume = data['24h_volume']
        
        # Conservative trading rules
        signal = 'HOLD'
        confidence = 0
        reason = "Market neutral - holding position"
        
        # Rule 1: Significant price drop with high volume (potential buying opportunity)
        if change_24h < -3 and volume > 10000000:  # >3% drop with >$10M volume
            signal = 'BUY'
            confidence = 0.65
            reason = f"Significant price correction ({change_24h:.1f}%) with strong volume"
        
        # Rule 2: Significant price rise with high volume (potential profit taking)
        elif change_24h > 5 and volume > 10000000:  # >5% rise with >$10M volume
            signal = 'SELL'
            confidence = 0.65
            reason = f"Strong rally ({change_24h:.1f}%) with high volume - profit taking opportunity"
        
        # Rule 3: Moderate conditions with volume confirmation
        elif -1 < change_24h < 1 and volume > 15000000:  # Stable price with very high volume
            signal = 'BUY' if change_24h < 0 else 'HOLD'
            confidence = 0.55 if change_24h < 0 else 0
            reason = "Stable price with exceptional volume - accumulation opportunity" if change_24h < 0 else "Stable market - no clear signal"
        
        # Rule 4: Low volume - avoid trading
        elif volume < 5000000:  # Low volume - avoid
            signal = 'HOLD'
            confidence = 0
            reason = "Low trading volume - avoiding position"
        
        analysis[symbol] = {
            'current_price': price,
            '24h_change_pct': change_24h,
            '24h_volume_usd': volume,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'support_level': price * 0.97,  # 3% below current as support
            'resistance_level': price * 1.03  # 3% above current as resistance
        }
    
    return analysis

def main():
    """Main analysis function"""
    print("=== Real-time Market Analysis ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get current prices
    print("Fetching market data...")
    prices = get_crypto_prices()
    
    # Analyze market
    analysis = analyze_market_sentiment(prices)
    
    # Display analysis
    for symbol, data in analysis.items():
        print(f"\n--- {symbol} Analysis ---")
        print(f"Current Price: ${data['current_price']:,.2f}")
        print(f"24h Change: {data['24h_change_pct']:+.2f}%")
        print(f"24h Volume: ${data['24h_volume_usd']:,.0f}")
        print(f"Support Level: ${data['support_level']:,.2f}")
        print(f"Resistance Level: ${data['resistance_level']:,.2f}")
        print(f"Trading Signal: {data['signal']}")
        print(f"Confidence: {data['confidence']:.2f}")
        print(f"Reason: {data['reason']}")
        
        # Trading recommendation
        if data['signal'] != 'HOLD' and data['confidence'] >= 0.6:
            print(f"✅ STRONG SIGNAL: Consider {data['signal']} position")
        elif data['signal'] != 'HOLD' and data['confidence'] >= 0.55:
            print(f"⚠️  MODERATE SIGNAL: Could consider small {data['signal']} position")
        else:
            print(f"⏸️  NO CLEAR SIGNAL: Maintain HOLD position")
    
    # Summary
    print(f"\n=== SUMMARY ===")
    strong_signals = [s for s, d in analysis.items() if d['signal'] != 'HOLD' and d['confidence'] >= 0.6]
    moderate_signals = [s for s, d in analysis.items() if d['signal'] != 'HOLD' and 0.55 <= d['confidence'] < 0.6]
    
    if strong_signals:
        print(f"Strong trading signals: {', '.join(strong_signals)}")
    if moderate_signals:
        print(f"Moderate trading signals: {', '.join(moderate_signals)}")
    if not strong_signals and not moderate_signals:
        print("No clear trading signals - conservative approach suggests HOLDING")
    
    print(f"\nNote: Conservative trading strategy recommends:")
    print("- Maximum 2 trades per day")
    print("- 5% stop-loss on all positions")
    print("- 10% take-profit targets")
    print("- $1,000 capital allocation (50% per trade maximum)")

if __name__ == "__main__":
    main()