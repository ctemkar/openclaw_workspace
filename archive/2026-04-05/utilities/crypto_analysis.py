#!/usr/bin/env python3
"""
Conservative Crypto Trading Analysis
Real-time market analysis with simulated trading decisions
"""

import requests
import json
from datetime import datetime, timedelta
import time

GEMINI_API_URL = "https://api.gemini.com"

# Trading parameters
CAPITAL = 1000.0  # $1,000
STOP_LOSS_PCT = 0.05  # 5%
TAKE_PROFIT_PCT = 0.10  # 10%
MAX_POSITION_SIZE = 0.5  # 50% of capital per trade
MAX_DAILY_TRADES = 2

def get_ticker(symbol: str):
    """Get ticker data from Gemini"""
    try:
        response = requests.get(f"{GEMINI_API_URL}/v1/pubticker/{symbol}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def get_order_book(symbol: str):
    """Get order book data"""
    try:
        response = requests.get(f"{GEMINI_API_URL}/v1/book/{symbol}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching order book for {symbol}: {e}")
        return None

def calculate_support_resistance(order_book):
    """Calculate support and resistance levels from order book"""
    if not order_book:
        return {"support": 0, "resistance": 0}
    
    bids = order_book.get("bids", [])
    asks = order_book.get("asks", [])
    
    # Calculate support as average of top 5 bids
    support = 0
    if bids and len(bids) >= 5:
        top_bids = [float(bid["price"]) for bid in bids[:5]]
        support = sum(top_bids) / len(top_bids)
    
    # Calculate resistance as average of top 5 asks
    resistance = 0
    if asks and len(asks) >= 5:
        top_asks = [float(ask["price"]) for ask in asks[:5]]
        resistance = sum(top_asks) / len(top_asks)
    
    return {
        "support": round(support, 2),
        "resistance": round(resistance, 2),
        "bid_depth": len(bids),
        "ask_depth": len(asks)
    }

def analyze_market_sentiment():
    """Analyze overall market sentiment"""
    btc_ticker = get_ticker("btcusd")
    eth_ticker = get_ticker("ethusd")
    
    if not btc_ticker or not eth_ticker:
        return {"sentiment": "UNKNOWN", "btc_price": 0, "eth_price": 0}
    
    btc_price = float(btc_ticker.get("last", 0))
    eth_price = float(eth_ticker.get("last", 0))
    
    # Get 24h volume for sentiment analysis
    btc_volume = float(btc_ticker.get("volume", {}).get("USD", 0))
    eth_volume = float(eth_ticker.get("volume", {}).get("USD", 0))
    
    # Simple sentiment based on price levels and volume
    sentiment = "NEUTRAL"
    
    # Check if prices are at reasonable levels (not extreme)
    if btc_price > 50000 and btc_price < 80000:
        if btc_volume > 10000000:  # High volume
            sentiment = "BULLISH"
    elif btc_price < 50000:
        sentiment = "CAUTIOUS"
    
    return {
        "sentiment": sentiment,
        "btc_price": btc_price,
        "eth_price": eth_price,
        "btc_volume": btc_volume,
        "eth_volume": eth_volume,
        "timestamp": datetime.utcnow().isoformat()
    }

def conservative_trading_decision(market_data, btc_sr, eth_sr):
    """Make conservative trading decision"""
    btc_price = market_data["btc_price"]
    eth_price = market_data["eth_price"]
    sentiment = market_data["sentiment"]
    
    # Conservative rules:
    # 1. Only trade in NEUTRAL or BULLISH sentiment
    # 2. Only buy near support levels
    # 3. Maximum 50% position size
    
    trade_signal = "HOLD"
    trade_details = {}
    
    if sentiment in ["NEUTRAL", "BULLISH"]:
        # Check BTC
        if btc_price > 0 and btc_sr["support"] > 0:
            distance_to_support = abs(btc_price - btc_sr["support"]) / btc_price
            
            if distance_to_support < 0.015:  # Within 1.5% of support
                trade_signal = "BUY_BTC"
                position_size = (CAPITAL * MAX_POSITION_SIZE) / btc_price
                stop_loss = btc_price * (1 - STOP_LOSS_PCT)
                take_profit = btc_price * (1 + TAKE_PROFIT_PCT)
                
                trade_details = {
                    "symbol": "BTC/USD",
                    "action": "BUY",
                    "entry_price": round(btc_price, 2),
                    "position_size": round(position_size, 6),
                    "position_value": round(position_size * btc_price, 2),
                    "stop_loss": round(stop_loss, 2),
                    "take_profit": round(take_profit, 2),
                    "reason": f"Price within 1.5% of support (${btc_sr['support']})",
                    "risk_reward": f"1:{TAKE_PROFIT_PCT/STOP_LOSS_PCT:.1f}"
                }
        
        # Check ETH if no BTC signal
        elif eth_price > 0 and eth_sr["support"] > 0:
            distance_to_support = abs(eth_price - eth_sr["support"]) / eth_price
            
            if distance_to_support < 0.015:  # Within 1.5% of support
                trade_signal = "BUY_ETH"
                position_size = (CAPITAL * MAX_POSITION_SIZE) / eth_price
                stop_loss = eth_price * (1 - STOP_LOSS_PCT)
                take_profit = eth_price * (1 + TAKE_PROFIT_PCT)
                
                trade_details = {
                    "symbol": "ETH/USD",
                    "action": "BUY",
                    "entry_price": round(eth_price, 2),
                    "position_size": round(position_size, 6),
                    "position_value": round(position_size * eth_price, 2),
                    "stop_loss": round(stop_loss, 2),
                    "take_profit": round(take_profit, 2),
                    "reason": f"Price within 1.5% of support (${eth_sr['support']})",
                    "risk_reward": f"1:{TAKE_PROFIT_PCT/STOP_LOSS_PCT:.1f}"
                }
    
    return trade_signal, trade_details

def main():
    print("=" * 60)
    print("CONSERVATIVE CRYPTO TRADING ANALYSIS")
    print("=" * 60)
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC+7)")
    print(f"Capital: ${CAPITAL:,.2f}")
    print(f"Risk Parameters: {STOP_LOSS_PCT*100}% SL, {TAKE_PROFIT_PCT*100}% TP")
    print(f"Max Position: {MAX_POSITION_SIZE*100}% of capital")
    print(f"Max Daily Trades: {MAX_DAILY_TRADES}")
    print("=" * 60)
    
    # Fetch market data
    print("\n📊 FETCHING MARKET DATA...")
    
    btc_ticker = get_ticker("btcusd")
    eth_ticker = get_ticker("ethusd")
    
    if not btc_ticker or not eth_ticker:
        print("❌ Failed to fetch market data")
        return
    
    btc_price = float(btc_ticker.get("last", 0))
    eth_price = float(eth_ticker.get("last", 0))
    
    print(f"✅ BTC/USD: ${btc_price:,.2f}")
    print(f"✅ ETH/USD: ${eth_price:,.2f}")
    
    # Get order books for support/resistance
    print("\n📈 ANALYZING SUPPORT/RESISTANCE...")
    
    btc_order_book = get_order_book("btcusd")
    eth_order_book = get_order_book("ethusd")
    
    btc_sr = calculate_support_resistance(btc_order_book)
    eth_sr = calculate_support_resistance(eth_order_book)
    
    print(f"✅ BTC Support: ${btc_sr['support']:,.2f}")
    print(f"✅ BTC Resistance: ${btc_sr['resistance']:,.2f}")
    print(f"✅ ETH Support: ${eth_sr['support']:,.2f}")
    print(f"✅ ETH Resistance: ${eth_sr['resistance']:,.2f}")
    
    # Analyze market sentiment
    print("\n🎯 ANALYZING MARKET SENTIMENT...")
    market_data = analyze_market_sentiment()
    print(f"✅ Market Sentiment: {market_data['sentiment']}")
    
    # Make trading decision
    print("\n🤖 MAKING TRADING DECISION...")
    trade_signal, trade_details = conservative_trading_decision(market_data, btc_sr, eth_sr)
    
    print(f"✅ Trading Decision: {trade_signal}")
    
    if trade_signal != "HOLD":
        print("\n💡 TRADE RECOMMENDATION:")
        print(f"   Symbol: {trade_details['symbol']}")
        print(f"   Action: {trade_details['action']}")
        print(f"   Entry Price: ${trade_details['entry_price']:,.2f}")
        print(f"   Position Size: {trade_details['position_size']}")
        print(f"   Position Value: ${trade_details['position_value']:,.2f}")
        print(f"   Stop Loss: ${trade_details['stop_loss']:,.2f}")
        print(f"   Take Profit: ${trade_details['take_profit']:,.2f}")
        print(f"   Reason: {trade_details['reason']}")
        print(f"   Risk/Reward: {trade_details['risk_reward']}")
    else:
        print("\n💡 No trade recommended at this time")
        print("   Reason: Market conditions don't meet conservative criteria")
    
    # Generate summary for cron delivery
    print("\n" + "=" * 60)
    print("SUMMARY FOR CRON DELIVERY")
    print("=" * 60)
    
    summary = f"""
CONSERVATIVE CRYPTO TRADING ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC+7)

MARKET DATA:
• BTC/USD: ${btc_price:,.2f}
• ETH/USD: ${eth_price:,.2f}
• Market Sentiment: {market_data['sentiment']}

SUPPORT/RESISTANCE LEVELS:
• BTC Support: ${btc_sr['support']:,.2f}
• BTC Resistance: ${btc_sr['resistance']:,.2f}
• ETH Support: ${eth_sr['support']:,.2f}
• ETH Resistance: ${eth_sr['resistance']:,.2f}

TRADING DECISION: {trade_signal}
"""

    if trade_signal != "HOLD":
        summary += f"""
TRADE RECOMMENDATION:
• Symbol: {trade_details['symbol']}
• Action: {trade_details['action']}
• Entry: ${trade_details['entry_price']:,.2f}
• Position Size: {trade_details['position_size']}
• Position Value: ${trade_details['position_value']:,.2f}
• Stop Loss: ${trade_details['stop_loss']:,.2f} ({STOP_LOSS_PCT*100}%)
• Take Profit: ${trade_details['take_profit']:,.2f} ({TAKE_PROFIT_PCT*100}%)
• Reason: {trade_details['reason']}
• Risk/Reward Ratio: {trade_details['risk_reward']}
"""
    else:
        summary += """
NO TRADE RECOMMENDED:
• Market conditions don't meet conservative trading criteria
• Waiting for better risk/reward opportunities
"""

    summary += f"""
RISK MANAGEMENT:
• Capital: ${CAPITAL:,.2f}
• Max Position Size: {MAX_POSITION_SIZE*100}% of capital
• Stop Loss: {STOP_LOSS_PCT*100}%
• Take Profit: {TAKE_PROFIT_PCT*100}%
• Max Daily Trades: {MAX_DAILY_TRADES}

STATUS: Analysis complete. Real trade execution requires Gemini API credentials.
"""

    print(summary)
    
    # Return plain text for cron
    return summary

if __name__ == "__main__":
    result = main()
    if result:
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE - Ready for cron delivery")
        print("=" * 60)