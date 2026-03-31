#!/usr/bin/env python3
"""
Conservative Crypto Market Analysis
Fetches real market data and provides trading analysis
"""

import requests
import json
from datetime import datetime
import time

def get_gemini_ticker(symbol="btcusd"):
    """Get ticker data from Gemini public API"""
    url = f"https://api.gemini.com/v1/pubticker/{symbol}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {symbol} data: {e}")
        return None

def get_gemini_order_book(symbol="btcusd"):
    """Get order book data from Gemini public API"""
    url = f"https://api.gemini.com/v1/book/{symbol}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {symbol} order book: {e}")
        return None

def analyze_market_sentiment(order_book):
    """Analyze market sentiment from order book"""
    if not order_book:
        return "NEUTRAL"
    
    bids = order_book.get("bids", [])
    asks = order_book.get("asks", [])
    
    # Calculate volume for top 10 bids/asks
    bid_volume = sum(float(bid["amount"]) for bid in bids[:10]) if bids else 0
    ask_volume = sum(float(ask["amount"]) for ask in asks[:10]) if asks else 0
    
    if bid_volume == 0 or ask_volume == 0:
        return "NEUTRAL"
    
    ratio = bid_volume / ask_volume
    
    if ratio > 1.3:
        return "BULLISH"
    elif ratio < 0.7:
        return "BEARISH"
    else:
        return "NEUTRAL"

def calculate_support_resistance(order_book):
    """Calculate support and resistance levels"""
    if not order_book:
        return {"support": [], "resistance": []}
    
    bids = order_book.get("bids", [])
    asks = order_book.get("asks", [])
    
    # Top 3 strongest support levels (highest bid volumes)
    support_levels = []
    for i, bid in enumerate(bids[:5]):
        price = float(bid["price"])
        volume = float(bid["amount"])
        support_levels.append({
            "price": price,
            "volume": volume,
            "strength": volume * (5 - i)  # Weight by position
        })
    
    # Top 3 strongest resistance levels (highest ask volumes)
    resistance_levels = []
    for i, ask in enumerate(asks[:5]):
        price = float(ask["price"])
        volume = float(ask["amount"])
        resistance_levels.append({
            "price": price,
            "volume": volume,
            "strength": volume * (5 - i)  # Weight by position
        })
    
    # Sort by strength
    support_levels.sort(key=lambda x: x["strength"], reverse=True)
    resistance_levels.sort(key=lambda x: x["strength"], reverse=True)
    
    return {
        "support": support_levels[:3],
        "resistance": resistance_levels[:3]
    }

def get_trading_signal(current_price, sentiment, support_levels, resistance_levels):
    """Determine trading signal based on conservative strategy"""
    
    # Find nearest support and resistance
    nearest_support = None
    nearest_resistance = None
    
    if support_levels:
        nearest_support = min(support_levels, 
                            key=lambda x: abs(x["price"] - current_price))
    
    if resistance_levels:
        nearest_resistance = min(resistance_levels, 
                               key=lambda x: abs(x["price"] - current_price))
    
    # Calculate distances as percentages
    support_distance_pct = 0
    resistance_distance_pct = 0
    
    if nearest_support:
        support_distance_pct = ((current_price - nearest_support["price"]) / current_price) * 100
    
    if nearest_resistance:
        resistance_distance_pct = ((nearest_resistance["price"] - current_price) / current_price) * 100
    
    # Conservative trading rules
    signal = "HOLD"
    reason = "No clear trading opportunity"
    
    # Rule 1: Buy near strong support with bullish sentiment
    if support_distance_pct < 1.5 and sentiment == "BULLISH":
        signal = "BUY"
        reason = f"Price near strong support ({support_distance_pct:.2f}% away) with bullish sentiment"
    
    # Rule 2: Sell near strong resistance with bearish sentiment  
    elif resistance_distance_pct < 1.5 and sentiment == "BEARISH":
        signal = "SELL"
        reason = f"Price near strong resistance ({resistance_distance_pct:.2f}% away) with bearish sentiment"
    
    # Rule 3: Very conservative - only trade with strong signals
    elif support_distance_pct < 1.0 and sentiment in ["BULLISH", "NEUTRAL"]:
        signal = "BUY"
        reason = f"Price very close to strong support ({support_distance_pct:.2f}% away)"
    
    elif resistance_distance_pct < 1.0 and sentiment in ["BEARISH", "NEUTRAL"]:
        signal = "SELL"
        reason = f"Price very close to strong resistance ({resistance_distance_pct:.2f}% away)"
    
    return {
        "signal": signal,
        "reason": reason,
        "support_distance_pct": support_distance_pct,
        "resistance_distance_pct": resistance_distance_pct,
        "nearest_support": nearest_support["price"] if nearest_support else None,
        "nearest_resistance": nearest_resistance["price"] if nearest_resistance else None
    }

def analyze_pair(symbol, pair_name):
    """Complete analysis for a trading pair"""
    print(f"\n{'='*50}")
    print(f"ANALYZING {pair_name}")
    print(f"{'='*50}")
    
    # Get market data
    ticker = get_gemini_ticker(symbol)
    if not ticker:
        return None
    
    order_book = get_gemini_order_book(symbol)
    
    current_price = float(ticker["last"])
    change_24h = float(ticker.get("percentChange24h", 0))
    
    # Analyze
    sentiment = analyze_market_sentiment(order_book)
    levels = calculate_support_resistance(order_book)
    signal_data = get_trading_signal(current_price, sentiment, 
                                   levels["support"], levels["resistance"])
    
    # Display results
    print(f"Current Price: ${current_price:,.2f}")
    print(f"24h Change: {change_24h:+.2f}%")
    print(f"Market Sentiment: {sentiment}")
    print(f"Trading Signal: {signal_data['signal']}")
    print(f"Signal Reason: {signal_data['reason']}")
    
    if levels["support"]:
        print(f"\nTop Support Levels:")
        for i, level in enumerate(levels["support"][:3], 1):
            distance_pct = ((current_price - level["price"]) / current_price) * 100
            print(f"  {i}. ${level['price']:,.2f} (Volume: {level['volume']:.4f}, Distance: {distance_pct:.2f}%)")
    
    if levels["resistance"]:
        print(f"\nTop Resistance Levels:")
        for i, level in enumerate(levels["resistance"][:3], 1):
            distance_pct = ((level["price"] - current_price) / current_price) * 100
            print(f"  {i}. ${level['price']:,.2f} (Volume: {level['volume']:.4f}, Distance: {distance_pct:.2f}%)")
    
    # Calculate position size for potential trade
    if signal_data["signal"] in ["BUY", "SELL"]:
        capital = 1000.0
        position_size = (capital * 0.5) / current_price  # 50% of capital
        print(f"\nPotential Trade:")
        print(f"  Action: {signal_data['signal']}")
        print(f"  Position Size: {position_size:.6f} {pair_name.split('/')[0]}")
        print(f"  Position Value: ${position_size * current_price:,.2f}")
        print(f"  Stop Loss: {5}% (${current_price * (0.95 if signal_data['signal'] == 'BUY' else 1.05):,.2f})")
        print(f"  Take Profit: {10}% (${current_price * (1.10 if signal_data['signal'] == 'BUY' else 0.90):,.2f})")
    
    return {
        "pair": pair_name,
        "symbol": symbol,
        "price": current_price,
        "change_24h": change_24h,
        "sentiment": sentiment,
        "signal": signal_data["signal"],
        "reason": signal_data["reason"],
        "support_levels": levels["support"],
        "resistance_levels": levels["resistance"]
    }

def main():
    """Main analysis function"""
    print(f"\n{'='*60}")
    print(f"CONSERVATIVE CRYPTO TRADING ANALYSIS")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    print(f"\nTRADING PARAMETERS:")
    print(f"  Capital: $1,000")
    print(f"  Risk: 5% stop-loss, 10% take-profit")
    print(f"  Daily Limit: 2 trades")
    print(f"  Strategy: Conservative (only clear opportunities)")
    
    # Analyze trading pairs
    pairs = [
        ("btcusd", "BTC/USD"),
        ("ethusd", "ETH/USD")
    ]
    
    results = []
    for symbol, pair_name in pairs:
        result = analyze_pair(symbol, pair_name)
        if result:
            results.append(result)
        time.sleep(1)  # Rate limiting
    
    # Generate summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    trades_recommended = sum(1 for r in results if r["signal"] in ["BUY", "SELL"])
    
    print(f"\nTotal Trading Opportunities: {trades_recommended}/2 (daily limit)")
    
    if trades_recommended > 0:
        print("\nRecommended Trades:")
        for result in results:
            if result["signal"] in ["BUY", "SELL"]:
                print(f"  {result['pair']}: {result['signal']} at ${result['price']:,.2f}")
                print(f"    Reason: {result['reason']}")
    else:
        print("\nNo clear trading opportunities detected.")
        print("Conservative strategy recommends holding positions.")
    
    # Market overview
    print(f"\nMARKET OVERVIEW:")
    for result in results:
        print(f"  {result['pair']}: ${result['price']:,.2f} ({result['change_24h']:+.2f}%), Sentiment: {result['sentiment']}")
    
    # Generate plain text summary for delivery
    plain_summary = f"""
CRYPTO TRADING ANALYSIS REPORT
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TRADING PARAMETERS:
- Capital: $1,000
- Risk Management: 5% stop-loss, 10% take-profit
- Daily Limit: Maximum 2 trades
- Strategy: Conservative (only clear opportunities)

MARKET ANALYSIS:
"""
    
    for result in results:
        plain_summary += f"""
{result['pair']}:
  Current Price: ${result['price']:,.2f}
  24h Change: {result['change_24h']:+.2f}%
  Market Sentiment: {result['sentiment']}
  Trading Signal: {result['signal']}
  Signal Reason: {result['reason']}
"""
    
    plain_summary += f"""
TRADING RECOMMENDATIONS:
Total Opportunities: {trades_recommended}/2 trades recommended

"""
    
    if trades_recommended > 0:
        plain_summary += "Recommended Actions:\n"
        for result in results:
            if result["signal"] in ["BUY", "SELL"]:
                position_size = (1000 * 0.5) / result["price"]
                plain_summary += f"- {result['signal']} {result['pair']} at ${result['price']:,.2f}\n"
                plain_summary += f"  Position: {position_size:.6f} {result['pair'].split('/')[0]} (${position_size * result['price']:,.2f})\n"
                plain_summary += f"  Stop Loss: 5% (${result['price'] * (0.95 if result['signal'] == 'BUY' else 1.05):,.2f})\n"
                plain_summary += f"  Take Profit: 10% (${result['price'] * (1.10 if result['signal'] == 'BUY' else 0.90):,.2f})\n"
    else:
        plain_summary += "No trades recommended at this time.\n"
        plain_summary += "Conservative strategy advises holding positions and waiting for clearer opportunities.\n"
    
    plain_summary += f"""
NEXT ANALYSIS:
Next scheduled analysis will run according to cron schedule.
Current trades used today: 0/2
"""
    
    # Save summary to file
    with open("trading_analysis_summary.txt", "w") as f:
        f.write(plain_summary)
    
    print(f"\n{'='*60}")
    print("Analysis complete. Summary saved to trading_analysis_summary.txt")
    print(f"{'='*60}")
    
    return plain_summary

if __name__ == "__main__":
    summary = main()
    print("\n" + "="*60)
    print("PLAIN TEXT SUMMARY FOR CRON DELIVERY:")
    print("="*60)
    print(summary)