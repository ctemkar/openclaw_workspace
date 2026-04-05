#!/usr/bin/env python3
"""
Real market data check using public APIs
"""

import requests
import json
from datetime import datetime

def get_crypto_prices():
    """Get real crypto prices from public API"""
    try:
        # Using CoinGecko public API
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin,ethereum',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        btc_price = data.get('bitcoin', {}).get('usd', 0)
        eth_price = data.get('ethereum', {}).get('usd', 0)
        btc_change = data.get('bitcoin', {}).get('usd_24h_change', 0)
        eth_change = data.get('ethereum', {}).get('usd_24h_change', 0)
        
        return {
            'BTC/USD': {
                'price': btc_price,
                '24h_change': btc_change,
                'timestamp': datetime.now().isoformat()
            },
            'ETH/USD': {
                'price': eth_price,
                '24h_change': eth_change,
                'timestamp': datetime.now().isoformat()
            }
        }
    except Exception as e:
        print(f"Error fetching real prices: {e}")
        return None

def generate_real_analysis():
    """Generate analysis based on real market data"""
    print("🔍 FETCHING REAL MARKET DATA")
    print("=" * 50)
    
    prices = get_crypto_prices()
    
    if not prices:
        print("⚠ Could not fetch real market data")
        print("Using conservative HOLD recommendation for safety")
        return "CONSERVATIVE CRYPTO TRADING ANALYSIS\n" + \
               "=" * 50 + "\n" + \
               "Time: " + datetime.now().isoformat() + "\n" + \
               "Status: REAL MARKET DATA UNAVAILABLE\n" + \
               "Recommendation: HOLD (Conservative - Data Unavailable)\n" + \
               "Action: No trades executed - Safety First\n" + \
               "Note: Check API connectivity for real-time data\n" + \
               "=" * 50
    
    print("✓ Real market data fetched successfully")
    print()
    
    analysis = []
    analysis.append("CONSERVATIVE CRYPTO TRADING ANALYSIS")
    analysis.append("=" * 50)
    analysis.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    analysis.append(f"Data Source: CoinGecko Public API")
    analysis.append("")
    
    for pair, data in prices.items():
        price = data['price']
        change = data['24h_change']
        
        analysis.append(f"{pair}:")
        analysis.append(f"  Current Price: ${price:,.2f}")
        analysis.append(f"  24h Change: {change:+.2f}%")
        
        # Conservative analysis based on price movement
        if change < -5:
            analysis.append(f"  Signal: OVERSOLD (24h drop >5%)")
            analysis.append(f"  Recommendation: BUY (Low Confidence)")
            analysis.append(f"  Risk: High volatility - wait for stabilization")
        elif change > 5:
            analysis.append(f"  Signal: OVERBOUGHT (24h gain >5%)")
            analysis.append(f"  Recommendation: SELL (Low Confidence)")
            analysis.append(f"  Risk: Potential pullback - consider partial profit")
        else:
            analysis.append(f"  Signal: NEUTRAL (Normal volatility)")
            analysis.append(f"  Recommendation: HOLD (Conservative)")
            analysis.append(f"  Action: Monitor for better entry")
        
        analysis.append("")
    
    # Overall conservative recommendation
    analysis.append("OVERALL STRATEGY:")
    analysis.append("  • Capital: $1,000")
    analysis.append("  • Max Trades/Day: 2")
    analysis.append("  • Stop Loss: 5%")
    analysis.append("  • Take Profit: 10%")
    analysis.append("")
    analysis.append("CURRENT MARKET ASSESSMENT:")
    
    btc_change = prices['BTC/USD']['24h_change']
    eth_change = prices['ETH/USD']['24h_change']
    
    if abs(btc_change) < 3 and abs(eth_change) < 3:
        analysis.append("  ✓ Low volatility environment")
        analysis.append("  ✓ Suitable for conservative trading")
        analysis.append("  ⚠ Wait for clearer signals")
    else:
        analysis.append("  ⚠ Elevated volatility detected")
        analysis.append("  ⚠ Conservative approach: HOLD")
        analysis.append("  ✓ Preserving capital during uncertainty")
    
    analysis.append("")
    analysis.append("TRADES EXECUTED TODAY: 0/2")
    analysis.append("REASON: Conservative HOLD - Waiting for optimal conditions")
    analysis.append("")
    analysis.append("NEXT STEPS:")
    analysis.append("  1. Monitor for RSI <30 (oversold) or >70 (overbought)")
    analysis.append("  2. Look for clear support/resistance breaks")
    analysis.append("  3. Consider small position if confidence increases")
    analysis.append("")
    analysis.append("⚠ SAFETY NOTE:")
    analysis.append("  Real trading requires:")
    analysis.append("  • Gemini API credentials")
    analysis.append("  • Proper risk management")
    analysis.append("  • Live market data feed")
    analysis.append("=" * 50)
    
    return "\n".join(analysis)

if __name__ == "__main__":
    summary = generate_real_analysis()
    print(summary)
    
    # Save to file
    with open('real_market_analysis.txt', 'w') as f:
        f.write(summary)