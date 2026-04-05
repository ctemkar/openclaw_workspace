#!/usr/bin/env python3
"""
Additional market analysis for conservative trading
Checks support/resistance levels and market sentiment
"""

import requests
import json
from datetime import datetime, timedelta

def get_technical_levels(symbol):
    """Get simplified technical levels (simulated for demonstration)"""
    # In production, this would use real technical analysis
    # For now, using simulated levels based on current price
    
    # Get current price
    url = f"https://api.gemini.com/v1/pubticker/{symbol}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            current_price = float(data.get('last', 0))
            
            # Simulated technical levels
            support_1 = current_price * 0.97  # 3% below
            support_2 = current_price * 0.95  # 5% below
            resistance_1 = current_price * 1.03  # 3% above
            resistance_2 = current_price * 1.05  # 5% above
            
            return {
                'current': current_price,
                'support': [support_1, support_2],
                'resistance': [resistance_1, resistance_2],
                'analysis': 'Conservative range based on ±3-5% levels'
            }
    except Exception as e:
        print(f"Error getting technical levels: {e}")
    
    return None

def get_market_sentiment():
    """Get simplified market sentiment (simulated)"""
    # In production, this would analyze news, social media, etc.
    # For now, using a simple simulated sentiment
    
    sentiments = {
        'overall': 'NEUTRAL',
        'btc': 'SLIGHTLY_BULLISH',
        'eth': 'NEUTRAL',
        'fear_greed_index': 45,  # 0-100 scale
        'analysis': 'Market in cautious consolidation phase',
        'recommendation': 'Wait for clearer signals before trading'
    }
    
    return sentiments

def analyze_risk_adjustment():
    """Analyze if risk parameters need adjustment"""
    current_hour = datetime.now().hour
    current_weekday = datetime.now().weekday()
    
    # Conservative adjustments:
    # - Reduce position size during Asian hours (lower liquidity)
    # - Be more cautious on weekends
    
    adjustments = {
        'position_size_multiplier': 1.0,
        'max_trades_today': 2,
        'notes': []
    }
    
    # Time-based adjustments
    if 0 <= current_hour < 8:  # Asian hours
        adjustments['position_size_multiplier'] = 0.7
        adjustments['notes'].append('Reduced position size during Asian hours (lower liquidity)')
    
    # Weekend caution
    if current_weekday >= 5:  # Saturday or Sunday
        adjustments['max_trades_today'] = 1
        adjustments['notes'].append('Weekend trading: Reduced to 1 trade max for caution')
    
    return adjustments

def main():
    """Run additional market analysis"""
    print("\n" + "=" * 60)
    print("DETAILED MARKET ANALYSIS FOR CONSERVATIVE TRADING")
    print("=" * 60)
    
    # Get technical levels
    print("\nTECHNICAL ANALYSIS:")
    symbols = ['btcusd', 'ethusd']
    
    for symbol in symbols:
        levels = get_technical_levels(symbol)
        if levels:
            print(f"\n{symbol.upper()}:")
            print(f"  Current: ${levels['current']:.2f}")
            print(f"  Support Levels: ${levels['support'][0]:.2f}, ${levels['support'][1]:.2f}")
            print(f"  Resistance Levels: ${levels['resistance'][0]:.2f}, ${levels['resistance'][1]:.2f}")
            print(f"  Analysis: {levels['analysis']}")
    
    # Get market sentiment
    print("\nMARKET SENTIMENT:")
    sentiment = get_market_sentiment()
    print(f"  Overall: {sentiment['overall']}")
    print(f"  BTC: {sentiment['btc']}")
    print(f"  ETH: {sentiment['eth']}")
    print(f"  Fear & Greed Index: {sentiment['fear_greed_index']}/100")
    print(f"  Analysis: {sentiment['analysis']}")
    print(f"  Recommendation: {sentiment['recommendation']}")
    
    # Risk adjustments
    print("\nRISK MANAGEMENT ADJUSTMENTS:")
    adjustments = analyze_risk_adjustment()
    print(f"  Position Size Multiplier: {adjustments['position_size_multiplier']:.1f}x")
    print(f"  Max Trades Today: {adjustments['max_trades_today']}")
    if adjustments['notes']:
        print("  Notes:")
        for note in adjustments['notes']:
            print(f"    • {note}")
    
    # Conservative trading rules reminder
    print("\nCONSERVATIVE TRADING RULES:")
    print("  1. Maximum 5% stop-loss on any position")
    print("  2. Minimum 10% take-profit target")
    print("  3. Maximum 2 trades per day (adjusted for weekends)")
    print("  4. Maximum 20% of capital per trade")
    print("  5. Only trade with >50% confidence signals")
    print("  6. Avoid trading during low liquidity periods")
    
    print(f"\nAnalysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("=" * 60)

if __name__ == "__main__":
    main()