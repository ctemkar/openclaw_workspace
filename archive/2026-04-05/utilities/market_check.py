#!/usr/bin/env python3
"""
Quick market check for BTC and ETH
"""

import requests
import json
from datetime import datetime

def get_crypto_price(symbol):
    """Get current crypto price from CoinGecko"""
    try:
        # Map symbols to CoinGecko IDs
        coin_map = {
            "btcusd": "bitcoin",
            "ethusd": "ethereum"
        }
        
        coin_id = coin_map.get(symbol.lower())
        if not coin_id:
            return None
            
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if coin_id in data:
            return {
                "price": data[coin_id]["usd"],
                "change_24h": data[coin_id]["usd_24h_change"],
                "symbol": symbol.upper()
            }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
    
    return None

def get_gemini_order_book(symbol):
    """Get order book from Gemini"""
    try:
        url = f"https://api.gemini.com/v1/book/{symbol}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Extract top bids and asks
        bids = data.get("bids", [])[:5]
        asks = data.get("asks", [])[:5]
        
        return {
            "bids": bids,
            "asks": asks,
            "bid_price": float(bids[0]["price"]) if bids else 0,
            "ask_price": float(asks[0]["price"]) if asks else 0,
            "bid_size": float(bids[0]["amount"]) if bids else 0,
            "ask_size": float(asks[0]["amount"]) if asks else 0
        }
    except Exception as e:
        print(f"Error fetching Gemini order book for {symbol}: {e}")
        return None

def analyze_market(symbol):
    """Analyze market conditions"""
    print(f"\nAnalyzing {symbol.upper()}...")
    
    # Get price data
    price_data = get_crypto_price(symbol)
    if price_data:
        print(f"  Current Price: ${price_data['price']:,.2f}")
        print(f"  24h Change: {price_data['change_24h']:.2f}%")
    
    # Get order book
    order_book = get_gemini_order_book(symbol)
    if order_book:
        spread = (order_book["ask_price"] - order_book["bid_price"]) / order_book["bid_price"] * 100
        print(f"  Bid: ${order_book['bid_price']:,.2f}")
        print(f"  Ask: ${order_book['ask_price']:,.2f}")
        print(f"  Spread: {spread:.3f}%")
        
        # Calculate support/resistance from order book
        if order_book["bids"] and order_book["asks"]:
            support = sum(float(bid["price"]) for bid in order_book["bids"][:3]) / 3
            resistance = sum(float(ask["price"]) for ask in order_book["asks"][:3]) / 3
            
            print(f"  Support (avg top 3 bids): ${support:,.2f}")
            print(f"  Resistance (avg top 3 asks): ${resistance:,.2f}")
            
            current_price = price_data["price"] if price_data else (order_book["bid_price"] + order_book["ask_price"]) / 2
            
            # Determine sentiment
            if current_price > resistance:
                sentiment = "BULLISH"
                reason = "Price above resistance"
            elif current_price < support:
                sentiment = "BEARISH"
                reason = "Price below support"
            else:
                sentiment = "NEUTRAL"
                reason = "Price between support and resistance"
            
            print(f"  Sentiment: {sentiment} - {reason}")
            
            # Trading recommendation
            if sentiment == "BEARISH" and price_data and price_data["change_24h"] < -2:
                print(f"  ⚠️  CAUTION: Strong downtrend, consider waiting")
            elif sentiment == "BULLISH" and price_data and price_data["change_24h"] > 2:
                print(f"  ⚠️  CAUTION: Strong uptrend, consider waiting")
            else:
                print(f"  ✅ Market conditions suitable for conservative trading")
    
    return price_data, order_book

def main():
    print("=" * 60)
    print("CRYPTO MARKET ANALYSIS")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    symbols = ["btcusd", "ethusd"]
    all_data = {}
    
    for symbol in symbols:
        price_data, order_book = analyze_market(symbol)
        all_data[symbol] = {
            "price": price_data,
            "order_book": order_book
        }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    # Conservative trading recommendations
    print("\nConservative Trading Strategy:")
    print("- Max 2 trades per day")
    print("- 5% stop-loss, 10% take-profit")
    print("- $1,000 capital (20% per trade = $200)")
    
    recommendations = []
    
    for symbol in symbols:
        data = all_data[symbol]
        if data["price"] and data["order_book"]:
            price = data["price"]["price"]
            change = data["price"]["change_24h"]
            
            if abs(change) < 3:  # Avoid volatile markets
                if change > 0:
                    action = "Consider small BUY if price pulls back to support"
                else:
                    action = "Consider small SELL if price rallies to resistance"
                
                recommendations.append(f"{symbol.upper()}: ${price:,.2f} ({change:+.2f}%) - {action}")
    
    if recommendations:
        print("\nPotential Opportunities (conservative):")
        for rec in recommendations:
            print(f"  • {rec}")
    else:
        print("\nNo high-confidence opportunities found for conservative trading.")
        print("Recommendation: Wait for clearer market signals.")
    
    print(f"\nAnalysis completed at: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()