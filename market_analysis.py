#!/usr/bin/env python3
"""
Real-time market analysis for conservative crypto trading
Fetches actual market data from public APIs
"""

import requests
import json
from datetime import datetime
import time

def get_crypto_price(symbol):
    """Get current crypto price from CoinGecko"""
    try:
        # Map symbols to CoinGecko IDs
        symbol_map = {
            "BTCUSD": "bitcoin",
            "ETHUSD": "ethereum"
        }
        
        coin_id = symbol_map.get(symbol)
        if not coin_id:
            return None
        
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if coin_id in data:
            return {
                "price": data[coin_id]["usd"],
                "change_24h": data[coin_id]["usd_24h_change"],
                "volume_24h": data[coin_id].get("usd_24h_vol", 0)
            }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
    
    return None

def get_binance_order_book(symbol):
    """Get order book from Binance for market depth analysis"""
    try:
        # Convert symbol format
        symbol_map = {
            "BTCUSD": "BTCUSDT",
            "ETHUSD": "ETHUSDT"
        }
        
        binance_symbol = symbol_map.get(symbol)
        if not binance_symbol:
            return None
        
        url = f"https://api.binance.com/api/v3/depth"
        params = {"symbol": binance_symbol, "limit": 10}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Calculate bid-ask spread
        if data.get("bids") and data.get("asks"):
            best_bid = float(data["bids"][0][0])
            best_ask = float(data["asks"][0][0])
            spread_pct = ((best_ask - best_bid) / best_bid) * 100
            
            return {
                "best_bid": best_bid,
                "best_ask": best_ask,
                "spread_pct": spread_pct,
                "bid_depth": sum(float(bid[1]) for bid in data["bids"][:5]),
                "ask_depth": sum(float(ask[1]) for ask in data["asks"][:5])
            }
    except Exception as e:
        print(f"Error fetching order book for {symbol}: {e}")
    
    return None

def analyze_market_sentiment(price_data, order_book):
    """Analyze market sentiment based on price action and order book"""
    if not price_data or not order_book:
        return "NEUTRAL"
    
    price_change = price_data["change_24h"]
    spread_pct = order_book["spread_pct"]
    bid_ask_ratio = order_book["bid_depth"] / order_book["ask_depth"] if order_book["ask_depth"] > 0 else 1
    
    # Sentiment analysis
    if price_change > 3 and spread_pct < 0.1 and bid_ask_ratio > 1.2:
        return "STRONGLY_BULLISH"
    elif price_change > 1.5 and spread_pct < 0.15:
        return "BULLISH"
    elif price_change < -3 and spread_pct < 0.1 and bid_ask_ratio < 0.8:
        return "STRONGLY_BEARISH"
    elif price_change < -1.5 and spread_pct < 0.15:
        return "BEARISH"
    elif abs(price_change) < 1 and spread_pct < 0.05:
        return "CONSOLIDATING"
    else:
        return "NEUTRAL"

def calculate_support_resistance(price, change_24h):
    """Calculate approximate support and resistance levels"""
    # Simple calculation based on 24h change
    if change_24h > 0:
        # In uptrend
        support = price * (1 - abs(change_24h) / 100 * 0.5)
        resistance = price * (1 + abs(change_24h) / 100 * 1.5)
    else:
        # In downtrend
        support = price * (1 - abs(change_24h) / 100 * 1.5)
        resistance = price * (1 + abs(change_24h) / 100 * 0.5)
    
    return support, resistance

def conservative_trading_decision(symbol, price_data, order_book, sentiment):
    """Make conservative trading decision"""
    if not price_data:
        return {"action": "HOLD", "reason": "No price data"}
    
    price = price_data["price"]
    change_24h = price_data["change_24h"]
    support, resistance = calculate_support_resistance(price, change_24h)
    
    # Calculate distance from support/resistance
    dist_to_support = ((price - support) / support) * 100 if support > 0 else 100
    dist_to_resistance = ((resistance - price) / resistance) * 100 if resistance > 0 else 100
    
    # Conservative trading logic
    if sentiment in ["BULLISH", "STRONGLY_BULLISH"] and dist_to_support < 3:
        # Near support in bullish market
        buy_price = price * 0.995  # 0.5% below current
        stop_loss = buy_price * 0.95  # 5% stop-loss
        take_profit = buy_price * 1.10  # 10% take-profit
        
        return {
            "action": "BUY",
            "price": buy_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "sentiment": sentiment,
            "support": support,
            "resistance": resistance,
            "reason": f"Bullish sentiment ({sentiment}), near support ({dist_to_support:.1f}% above)"
        }
    
    elif sentiment in ["BEARISH", "STRONGLY_BEARISH"] and dist_to_resistance < 3:
        # Near resistance in bearish market
        sell_price = price * 1.005  # 0.5% above current
        
        return {
            "action": "SELL",
            "price": sell_price,
            "sentiment": sentiment,
            "support": support,
            "resistance": resistance,
            "reason": f"Bearish sentiment ({sentiment}), near resistance ({dist_to_resistance:.1f}% below)"
        }
    
    else:
        # Hold - conditions not favorable
        return {
            "action": "HOLD",
            "price": price,
            "sentiment": sentiment,
            "support": support,
            "resistance": resistance,
            "reason": f"Market {sentiment.lower().replace('_', ' ')}, not at key levels"
        }

def main():
    """Main analysis function"""
    print("=" * 70)
    print("REAL-TIME CRYPTO MARKET ANALYSIS")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC+7)")
    print("=" * 70)
    
    symbols = ["BTCUSD", "ETHUSD"]
    
    print("\n📊 MARKET DATA")
    print("-" * 70)
    
    market_data = {}
    for symbol in symbols:
        print(f"\n{symbol}:")
        
        # Get price data
        price_data = get_crypto_price(symbol)
        if price_data:
            print(f"  Current Price: ${price_data['price']:,.2f}")
            print(f"  24h Change: {price_data['change_24h']:+.2f}%")
            print(f"  24h Volume: ${price_data['volume_24h']:,.0f}")
            
            # Get order book
            order_book = get_binance_order_book(symbol)
            if order_book:
                print(f"  Best Bid: ${order_book['best_bid']:,.2f}")
                print(f"  Best Ask: ${order_book['best_ask']:,.2f}")
                print(f"  Spread: {order_book['spread_pct']:.3f}%")
                print(f"  Bid Depth: {order_book['bid_depth']:.4f}")
                print(f"  Ask Depth: {order_book['ask_depth']:.4f}")
                
                # Analyze sentiment
                sentiment = analyze_market_sentiment(price_data, order_book)
                print(f"  Sentiment: {sentiment}")
                
                # Calculate support/resistance
                support, resistance = calculate_support_resistance(
                    price_data["price"], price_data["change_24h"]
                )
                print(f"  Support: ${support:,.2f}")
                print(f"  Resistance: ${resistance:,.2f}")
                
                market_data[symbol] = {
                    "price_data": price_data,
                    "order_book": order_book,
                    "sentiment": sentiment,
                    "support": support,
                    "resistance": resistance
                }
            else:
                print("  ❌ Failed to fetch order book")
        else:
            print("  ❌ Failed to fetch price data")
    
    # Trading Analysis
    print("\n🎯 CONSERVATIVE TRADING ANALYSIS")
    print("-" * 70)
    print("Parameters: $1,000 capital, 5% stop-loss, 10% take-profit, max 2 trades/day")
    print("-" * 70)
    
    trading_decisions = {}
    for symbol in symbols:
        if symbol in market_data:
            data = market_data[symbol]
            decision = conservative_trading_decision(
                symbol,
                data["price_data"],
                data["order_book"],
                data["sentiment"]
            )
            
            trading_decisions[symbol] = decision
            
            print(f"\n{symbol} TRADING DECISION:")
            print(f"  Action: {decision['action']}")
            print(f"  Current Price: ${decision['price']:,.2f}")
            print(f"  Market Sentiment: {decision['sentiment']}")
            print(f"  Support: ${decision['support']:,.2f}")
            print(f"  Resistance: ${decision['resistance']:,.2f}")
            print(f"  Reason: {decision['reason']}")
            
            if decision['action'] == 'BUY':
                print(f"  Target Buy Price: ${decision.get('price', 0):,.2f}")
                print(f"  Stop-Loss: ${decision.get('stop_loss', 0):,.2f} (5.0%)")
                print(f"  Take-Profit: ${decision.get('take_profit', 0):,.2f} (10.0%)")
                print(f"  Suggested Position: $250 (25% of $1,000 capital)")
    
    # Summary
    print("\n" + "=" * 70)
    print("TRADING SUMMARY")
    print("=" * 70)
    
    buy_opportunities = [s for s, d in trading_decisions.items() if d['action'] == 'BUY']
    
    if buy_opportunities:
        print(f"\n✅ BUY OPPORTUNITIES FOUND: {len(buy_opportunities)}")
        for symbol in buy_opportunities:
            decision = trading_decisions[symbol]
            print(f"\n  {symbol}:")
            print(f"    Buy at: ${decision.get('price', 0):,.2f}")
            print(f"    Stop: ${decision.get('stop_loss', 0):,.2f}")
            print(f"    Target: ${decision.get('take_profit', 0):,.2f}")
            print(f"    Risk/Reward: 1:2 (5% risk, 10% reward)")
    else:
        print("\n⚠️ NO BUY OPPORTUNITIES")
        print("  Market conditions not favorable for conservative buying")
        print("  Recommended action: HOLD and monitor")
    
    print("\n" + "=" * 70)
    print("DISCLAIMER: This is analysis only. Real trading requires:")
    print("1. Gemini API credentials (GEMINI_API_KEY, GEMINI_API_SECRET)")
    print("2. Actual funded account")
    print("3. Proper risk management")
    print("=" * 70)

if __name__ == "__main__":
    main()