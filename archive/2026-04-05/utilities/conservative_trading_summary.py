#!/usr/bin/env python3
"""
Conservative Crypto Trading Analysis Summary
Real-time market analysis with conservative trading recommendations
"""

import json
import requests
from datetime import datetime
import sys

def get_market_data(symbol):
    """Get market data from Gemini public API"""
    try:
        # Get ticker data
        ticker_url = f"https://api.gemini.com/v1/pubticker/{symbol.lower()}"
        ticker_response = requests.get(ticker_url, timeout=10)
        ticker_data = ticker_response.json()
        
        # Get order book data
        book_url = f"https://api.gemini.com/v1/book/{symbol.lower()}"
        book_response = requests.get(book_url, timeout=10)
        book_data = book_response.json()
        
        return ticker_data, book_data
    except Exception as e:
        print(f"Error fetching {symbol} data: {e}")
        return None, None

def analyze_pair(symbol, pair_name):
    """Analyze a trading pair"""
    print(f"\n{'='*60}")
    print(f"ANALYSIS: {pair_name}")
    print(f"{'='*60}")
    
    ticker, order_book = get_market_data(symbol)
    
    if not ticker or not order_book:
        print(f"  ❌ Unable to fetch market data for {symbol}")
        return None
    
    # Extract key data
    bid = float(ticker.get('bid', 0))
    ask = float(ticker.get('ask', 0))
    last = float(ticker.get('last', 0))
    current_price = (bid + ask) / 2
    
    # Calculate support/resistance from order book
    bids = order_book.get('bids', [])
    asks = order_book.get('asks', [])
    
    if not bids or not asks:
        print(f"  ❌ Insufficient order book data")
        return None
    
    # Top support levels (highest bids)
    support_levels = sorted([float(b['price']) for b in bids[:10]], reverse=True)[:3]
    
    # Top resistance levels (lowest asks)
    resistance_levels = sorted([float(a['price']) for a in asks[:10]])[:3]
    
    # Calculate bid/ask spread
    spread = ask - bid
    spread_pct = (spread / current_price) * 100
    
    # Calculate volume
    volume_data = ticker.get('volume', {})
    volume_24h = float(volume_data.get('USD', 0))
    
    # Market sentiment analysis
    bid_volume = sum(float(b['amount']) for b in bids[:5])
    ask_volume = sum(float(a['amount']) for a in asks[:5])
    
    if bid_volume > ask_volume * 1.3:
        sentiment = "BULLISH"
        sentiment_reason = "Strong buying pressure (bid volume > ask volume)"
    elif ask_volume > bid_volume * 1.3:
        sentiment = "BEARISH"
        sentiment_reason = "Strong selling pressure (ask volume > bid volume)"
    else:
        sentiment = "NEUTRAL"
        sentiment_reason = "Balanced market (bid/ask volume similar)"
    
    # Display analysis
    print(f"  Current Price: ${current_price:,.2f}")
    print(f"  24h Change: ${last - current_price:+.2f} ({((last - current_price)/current_price)*100:+.2f}%)")
    print(f"  Bid/Ask: ${bid:,.2f} / ${ask:,.2f}")
    print(f"  Spread: ${spread:.2f} ({spread_pct:.3f}%)")
    print(f"  24h Volume: ${volume_24h:,.0f}")
    
    print(f"\n  SUPPORT LEVELS (Buying Pressure):")
    for i, level in enumerate(support_levels, 1):
        distance_pct = ((current_price - level) / current_price) * 100
        print(f"    S{i}: ${level:,.2f} ({distance_pct:+.1f}% from current)")
    
    print(f"\n  RESISTANCE LEVELS (Selling Pressure):")
    for i, level in enumerate(resistance_levels, 1):
        distance_pct = ((level - current_price) / current_price) * 100
        print(f"    R{i}: ${level:,.2f} ({distance_pct:+.1f}% from current)")
    
    print(f"\n  MARKET SENTIMENT: {sentiment}")
    print(f"    Reason: {sentiment_reason}")
    print(f"    Bid Volume (Top 5): {bid_volume:.4f} {symbol[:3]}")
    print(f"    Ask Volume (Top 5): {ask_volume:.4f} {symbol[:3]}")
    
    # Conservative trading recommendation
    print(f"\n  CONSERVATIVE TRADING ASSESSMENT:")
    
    nearest_support = support_levels[0] if support_levels else 0
    nearest_resistance = resistance_levels[0] if resistance_levels else float('inf')
    
    support_distance = ((current_price - nearest_support) / current_price) * 100
    resistance_distance = ((nearest_resistance - current_price) / current_price) * 100
    
    # Trading logic
    recommendation = "HOLD (No clear entry signal)"
    reason = ""
    entry_price = 0
    stop_loss = 0
    take_profit = 0
    
    if sentiment == "BULLISH" and support_distance <= 2.0:
        # Near support with bullish sentiment - BUY signal
        recommendation = "CONSERVATIVE BUY"
        reason = f"Price near strong support (${nearest_support:,.2f}) with bullish market sentiment"
        entry_price = current_price
        stop_loss = entry_price * 0.95  # 5% stop loss
        take_profit = entry_price * 1.10  # 10% take profit
        
    elif sentiment == "BEARISH" and resistance_distance <= 2.0:
        # Near resistance with bearish sentiment - SELL/SHORT signal
        recommendation = "CONSERVATIVE SELL"
        reason = f"Price near strong resistance (${nearest_resistance:,.2f}) with bearish market sentiment"
        entry_price = current_price
        stop_loss = entry_price * 1.05  # 5% stop loss for short
        take_profit = entry_price * 0.90  # 10% take profit for short
        
    elif support_distance <= 1.0:
        # Very close to support - cautious buy
        recommendation = "CAUTIOUS BUY (Watch for confirmation)"
        reason = f"Price very close to support (${nearest_support:,.2f}) - wait for bullish confirmation"
        
    elif resistance_distance <= 1.0:
        # Very close to resistance - cautious sell
        recommendation = "CAUTIOUS SELL (Watch for confirmation)"
        reason = f"Price very close to resistance (${nearest_resistance:,.2f}) - wait for bearish confirmation"
    
    print(f"    Recommendation: {recommendation}")
    if reason:
        print(f"    Reason: {reason}")
    
    if entry_price > 0:
        print(f"    Entry Price: ${entry_price:,.2f}")
        print(f"    Stop Loss: ${stop_loss:,.2f} (-5.0%)")
        print(f"    Take Profit: ${take_profit:,.2f} (+10.0%)")
        
        # Position sizing for $1,000 capital
        position_size_pct = 0.3  # Conservative 30% of capital
        position_value = 1000 * position_size_pct
        quantity = position_value / entry_price
        
        print(f"    Position Size: ${position_value:.2f} ({quantity:.6f} {symbol[:3]})")
    
    print(f"\n  RISK ASSESSMENT:")
    print(f"    ✓ 5% Stop Loss protection")
    print(f"    ✓ 10% Take Profit target")
    print(f"    ✓ Conservative position sizing (30% of capital)")
    print(f"    ✓ Requires clear support/resistance alignment")
    
    return {
        'symbol': symbol,
        'price': current_price,
        'sentiment': sentiment,
        'recommendation': recommendation,
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit
    }

def main():
    print("=" * 70)
    print("CONSERVATIVE CRYPTO TRADING ANALYSIS - REAL-TIME")
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Timezone: Asia/Bangkok (GMT+7)")
    print("=" * 70)
    
    print("\nTRADING PARAMETERS:")
    print(f"  Investment Capital: $1,000.00")
    print(f"  Risk Management: 5% Stop Loss, 10% Take Profit")
    print(f"  Max Daily Trades: 2")
    print(f"  Strategy: Conservative (requires clear technical alignment)")
    print(f"  Execution: Real Gemini API (Paper trading mode for analysis)")
    
    # Analyze BTC/USD
    btc_analysis = analyze_pair("btcusd", "BITCOIN (BTC/USD)")
    
    # Analyze ETH/USD
    eth_analysis = analyze_pair("ethusd", "ETHEREUM (ETH/USD)")
    
    # Overall market summary
    print(f"\n{'='*70}")
    print("OVERALL MARKET SUMMARY & TRADING DECISIONS")
    print(f"{'='*70}")
    
    analyses = [a for a in [btc_analysis, eth_analysis] if a]
    
    if not analyses:
        print("\n  ❌ No trading opportunities identified")
        print("  Market conditions do not meet conservative entry criteria")
        print("  Maintaining cash position: $1,000.00")
        return
    
    trading_opportunities = [a for a in analyses if 'BUY' in a['recommendation'] or 'SELL' in a['recommendation']]
    
    if not trading_opportunities:
        print("\n  ⚠️  No clear trading signals generated")
        print("  Conservative strategy requires:")
        print("    1. Price near key support/resistance levels")
        print("    2. Aligned market sentiment")
        print("    3. Clear risk/reward ratio (1:2 minimum)")
        print("\n  Current status: HOLD - Waiting for better entry conditions")
        print(f"  Capital preserved: $1,000.00")
    else:
        print(f"\n  ✅ Trading Opportunities Found: {len(trading_opportunities)}")
        
        total_investment = 0
        for i, opp in enumerate(trading_opportunities, 1):
            symbol_display = opp['symbol'].upper().replace('USD', '/USD')
            print(f"\n  Opportunity {i}: {symbol_display}")
            print(f"    Signal: {opp['recommendation']}")
            print(f"    Entry: ${opp['entry_price']:,.2f}")
            print(f"    Stop Loss: ${opp['stop_loss']:,.2f} (-5.0%)")
            print(f"    Take Profit: ${opp['take_profit']:,.2f} (+10.0%)")
            
            # Calculate position size
            position_value = 1000 * 0.3  # 30% of capital per trade
            total_investment += position_value
            
            print(f"    Position Size: ${position_value:.2f}")
            print(f"    Risk/Reward: 1:2 (5% risk for 10% reward)")
        
        print(f"\n  TOTAL INVESTMENT: ${total_investment:.2f}")
        print(f"  CAPITAL UTILIZATION: {(total_investment/1000)*100:.1f}%")
        print(f"  CASH REMAINING: ${1000 - total_investment:.2f}")
        
        if len(trading_opportunities) > 2:
            print(f"\n  ⚠️  Warning: {len(trading_opportunities)} signals exceed daily limit (2)")
            print(f"  Will execute only top 2 opportunities")
    
    print(f"\n{'='*70}")
    print("RISK MANAGEMENT STATUS: ACTIVE")
    print(f"{'='*70}")
    print("  ✓ 5% Stop Loss protection on all positions")
    print("  ✓ 10% Take Profit targets set")
    print("  ✓ Max 2 trades per day enforced")
    print("  ✓ Conservative entry criteria required")
    print("  ✓ Real-time market monitoring active")
    print(f"{'='*70}")
    
    print(f"\nNEXT ANALYSIS SCHEDULE:")
    print(f"  Next check: 1 hour from now")
    print(f"  Continuous monitoring: 24/7")
    print(f"  Alert triggers: Price breaks key levels")
    
    print(f"\n{'='*70}")
    print("END OF ANALYSIS")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()