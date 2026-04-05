#!/usr/bin/env python3
"""
Conservative Crypto Trading Analysis
Real-time analysis with $1,000 capital, 5% stop-loss, 10% take-profit
Maximum 2 trades per day
"""

import requests
import json
import os
from datetime import datetime

# Configuration
CAPITAL = 1000.0  # $1,000 capital
STOP_LOSS_PCT = 0.05  # 5% stop-loss
TAKE_PROFIT_PCT = 0.10  # 10% take-profit
MAX_POSITION_SIZE = 0.5  # 50% of capital per trade
MAX_DAILY_TRADES = 2

GEMINI_API_URL = "https://api.gemini.com"

def fetch_market_data():
    """Fetch current BTC and ETH market data"""
    print("📊 Fetching real-time market data...")
    
    data = {
        "btc": {},
        "eth": {},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC+7"),
        "success": False
    }
    
    try:
        # BTC/USD
        btc_response = requests.get(f"{GEMINI_API_URL}/v1/pubticker/btcusd", timeout=10)
        if btc_response.status_code == 200:
            btc_data = btc_response.json()
            data["btc"] = {
                "price": float(btc_data.get("last", 0)),
                "bid": float(btc_data.get("bid", 0)),
                "ask": float(btc_data.get("ask", 0)),
                "volume": float(btc_data.get("volume", {}).get("USD", 0))
            }
        
        # ETH/USD
        eth_response = requests.get(f"{GEMINI_API_URL}/v1/pubticker/ethusd", timeout=10)
        if eth_response.status_code == 200:
            eth_data = eth_response.json()
            data["eth"] = {
                "price": float(eth_data.get("last", 0)),
                "bid": float(eth_data.get("bid", 0)),
                "ask": float(eth_data.get("ask", 0)),
                "volume": float(eth_data.get("volume", {}).get("USD", 0))
            }
        
        data["success"] = bool(data["btc"] and data["eth"])
        
    except Exception as e:
        print(f"❌ Error fetching market data: {e}")
    
    return data

def calculate_support_resistance(symbol: str) -> Dict:
    """Calculate support and resistance levels from order book"""
    try:
        response = requests.get(f"{GEMINI_API_URL}/v1/book/{symbol}", timeout=10)
        if response.status_code != 200:
            return {"support": 0, "resistance": 0}
        
        order_book = response.json()
        bids = order_book.get("bids", [])
        asks = order_book.get("asks", [])
        
        # Support = average of top 5 bids
        support = 0
        if bids and len(bids) >= 5:
            top_bids = [float(bid["price"]) for bid in bids[:5]]
            support = sum(top_bids) / len(top_bids)
        
        # Resistance = average of top 5 asks
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
        
    except Exception as e:
        print(f"❌ Error calculating S/R for {symbol}: {e}")
        return {"support": 0, "resistance": 0}

def analyze_market_sentiment(market_data):
    """Analyze market sentiment based on price action and volume"""
    btc_price = market_data["btc"].get("price", 0)
    eth_price = market_data["eth"].get("price", 0)
    btc_volume = market_data["btc"].get("volume", 0)
    eth_volume = market_data["eth"].get("volume", 0)
    
    if btc_price == 0 or eth_price == 0:
        return "UNKNOWN", "Insufficient data"
    
    # Volume analysis
    if btc_volume > 20000000 and eth_volume > 10000000:
        volume_signal = "High volume - Strong market interest"
        sentiment_score = 1
    elif btc_volume < 8000000 or eth_volume < 4000000:
        volume_signal = "Low volume - Caution advised"
        sentiment_score = -1
    else:
        volume_signal = "Moderate volume - Normal market conditions"
        sentiment_score = 0
    
    # Price analysis (simplified)
    if btc_price > 65000 and eth_price > 2000:  # Above key levels
        price_signal = "Trading above key psychological levels"
        sentiment_score += 0.5
    else:
        price_signal = "Trading at or below key levels"
        sentiment_score -= 0.5
    
    # Determine overall sentiment
    if sentiment_score >= 1:
        sentiment = "BULLISH"
    elif sentiment_score <= -1:
        sentiment = "BEARISH"
    else:
        sentiment = "NEUTRAL"
    
    reason = f"{volume_signal}. {price_signal}"
    
    return sentiment, reason

def conservative_trading_decision(market_data, btc_sr, eth_sr, sentiment):
    """Make conservative trading decision"""
    
    btc_price = market_data["btc"].get("price", 0)
    eth_price = market_data["eth"].get("price", 0)
    
    # Conservative rules:
    # 1. Only trade in NEUTRAL or BULLISH sentiment
    # 2. Price must be within 1% of support level
    # 3. Maximum 50% position size
    
    if sentiment not in ["NEUTRAL", "BULLISH"]:
        return {
            "signal": "HOLD",
            "symbol": None,
            "reason": f"Market sentiment too cautious: {sentiment}",
            "details": "Conservative strategy avoids trading in bearish conditions"
        }
    
    # Check BTC opportunity
    if btc_price > 0 and btc_sr["support"] > 0:
        distance_pct = abs(btc_price - btc_sr["support"]) / btc_price
        
        if distance_pct <= 0.01:  # Within 1% of support
            position_size = (CAPITAL * MAX_POSITION_SIZE) / btc_price
            stop_loss = btc_price * (1 - STOP_LOSS_PCT)
            take_profit = btc_price * (1 + TAKE_PROFIT_PCT)
            
            return {
                "signal": "BUY",
                "symbol": "BTC/USD",
                "entry_price": round(btc_price, 2),
                "position_size": round(position_size, 6),
                "position_value": round(position_size * btc_price, 2),
                "stop_loss": round(stop_loss, 2),
                "take_profit": round(take_profit, 2),
                "risk_reward": f"1:{TAKE_PROFIT_PCT/STOP_LOSS_PCT:.1f}",
                "reason": f"BTC price within 1% of support (${btc_sr['support']:.2f})",
                "details": f"Conservative buy at support with {STOP_LOSS_PCT*100}% stop-loss"
            }
    
    # Check ETH opportunity
    if eth_price > 0 and eth_sr["support"] > 0:
        distance_pct = abs(eth_price - eth_sr["support"]) / eth_price
        
        if distance_pct <= 0.01:  # Within 1% of support
            position_size = (CAPITAL * MAX_POSITION_SIZE) / eth_price
            stop_loss = eth_price * (1 - STOP_LOSS_PCT)
            take_profit = eth_price * (1 + TAKE_PROFIT_PCT)
            
            return {
                "signal": "BUY",
                "symbol": "ETH/USD",
                "entry_price": round(eth_price, 2),
                "position_size": round(position_size, 6),
                "position_value": round(position_size * eth_price, 2),
                "stop_loss": round(stop_loss, 2),
                "take_profit": round(take_profit, 2),
                "risk_reward": f"1:{TAKE_PROFIT_PCT/STOP_LOSS_PCT:.1f}",
                "reason": f"ETH price within 1% of support (${eth_sr['support']:.2f})",
                "details": f"Conservative buy at support with {STOP_LOSS_PCT*100}% stop-loss"
            }
    
    return {
        "signal": "HOLD",
        "symbol": None,
        "reason": "No conservative trading opportunities found",
        "details": "Prices not near support levels. Waiting for better entry points."
    }

def main():
    print("=" * 70)
    print("CONSERVATIVE CRYPTO TRADING ANALYSIS")
    print("=" * 70)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC+7)")
    print(f"Capital: ${CAPITAL:,.2f}")
    print(f"Risk Management: {STOP_LOSS_PCT*100}% SL, {TAKE_PROFIT_PCT*100}% TP")
    print(f"Position Size: Max {MAX_POSITION_SIZE*100}% of capital")
    print(f"Daily Limit: {MAX_DAILY_TRADES} trades")
    print("=" * 70)
    
    # Step 1: Fetch Market Data
    print("\n1️⃣  MARKET DATA ANALYSIS")
    print("-" * 40)
    
    market_data = fetch_market_data()
    if not market_data["success"]:
        print("❌ Failed to fetch market data. Exiting.")
        return None
    
    btc_price = market_data["btc"]["price"]
    eth_price = market_data["eth"]["price"]
    
    print(f"✅ BTC/USD: ${btc_price:,.2f}")
    print(f"✅ ETH/USD: ${eth_price:,.2f}")
    print(f"✅ BTC 24h Volume: ${market_data['btc']['volume']:,.0f}")
    print(f"✅ ETH 24h Volume: ${market_data['eth']['volume']:,.0f}")
    
    # Step 2: Calculate Support/Resistance
    print("\n2️⃣  SUPPORT/RESISTANCE LEVELS")
    print("-" * 40)
    
    btc_sr = calculate_support_resistance("btcusd")
    eth_sr = calculate_support_resistance("ethusd")
    
    print(f"✅ BTC Support: ${btc_sr['support']:,.2f}")
    print(f"✅ BTC Resistance: ${btc_sr['resistance']:,.2f}")
    print(f"✅ ETH Support: ${eth_sr['support']:,.2f}")
    print(f"✅ ETH Resistance: ${eth_sr['resistance']:,.2f}")
    
    # Step 3: Market Sentiment
    print("\n3️⃣  MARKET SENTIMENT")
    print("-" * 40)
    
    sentiment, sentiment_reason = analyze_market_sentiment(market_data)
    print(f"✅ Market Sentiment: {sentiment}")
    print(f"✅ Reason: {sentiment_reason}")
    
    # Step 4: Trading Analysis
    print("\n4️⃣  TRADING ANALYSIS")
    print("-" * 40)
    
    decision = conservative_trading_decision(market_data, btc_sr, eth_sr, sentiment)
    print(f"✅ Trading Signal: {decision['signal']}")
    print(f"✅ Reason: {decision['reason']}")
    
    # Generate plain text summary
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC+7")
    
    summary = f"""
CONSERVATIVE CRYPTO TRADING ANALYSIS
====================================
Analysis Time: {timestamp}

CAPITAL & RISK PARAMETERS:
• Available Capital: ${CAPITAL:,.2f}
• Max Position Size: {MAX_POSITION_SIZE*100}% (${CAPITAL * MAX_POSITION_SIZE:,.2f})
• Stop Loss: {STOP_LOSS_PCT*100}%
• Take Profit: {TAKE_PROFIT_PCT*100}%
• Max Daily Trades: {MAX_DAILY_TRADES}
• Risk/Reward Ratio: 1:{TAKE_PROFIT_PCT/STOP_LOSS_PCT:.1f}

MARKET DATA:
• BTC/USD: ${btc_price:,.2f}
  Bid: ${market_data['btc']['bid']:,.2f} | Ask: ${market_data['btc']['ask']:,.2f}
  24h Volume: ${market_data['btc']['volume']:,.0f}

• ETH/USD: ${eth_price:,.2f}
  Bid: ${market_data['eth']['bid']:,.2f} | Ask: ${market_data['eth']['ask']:,.2f}
  24h Volume: ${market_data['eth']['volume']:,.0f}

SUPPORT/RESISTANCE LEVELS:
• BTC Support: ${btc_sr['support']:,.2f}
• BTC Resistance: ${btc_sr['resistance']:,.2f}
• ETH Support: ${eth_sr['support']:,.2f}
• ETH Resistance: ${eth_sr['resistance']:,.2f}

MARKET SENTIMENT: {sentiment}
Reason: {sentiment_reason}

TRADING DECISION: {decision['signal']}
Reason: {decision['reason']}
"""
    
    if decision['signal'] == 'BUY':
        summary += f"""
TRADE EXECUTION DETAILS:
• Symbol: {decision['symbol']}
• Action: BUY (Conservative Support-Based)
• Entry Price: ${decision['entry_price']:,.2f}
• Position Size: {decision['position_size']}
• Position Value: ${decision['position_value']:,.2f}
• Stop Loss: ${decision['stop_loss']:,.2f} ({STOP_LOSS_PCT*100}% below entry)
• Take Profit: ${decision['take_profit']:,.2f} ({TAKE_PROFIT_PCT*100}% above entry)
• Risk/Reward Ratio: {decision['risk_reward']}
• Trade Rationale: {decision['details']}

EXECUTION STATUS: ANALYSIS COMPLETE
Note: Manual execution required due to API credential issues

RECOMMENDED ACTION:
1. Verify Gemini API credentials for automated trading
2. Manually execute trade at specified entry price
3. Set stop-loss and take-profit orders immediately
4. Monitor position closely
"""
    else:
        summary += f"""
NO TRADE EXECUTED - CONSERVATIVE STRATEGY:
• Decision: Maintain HOLD position
• Details: {decision['details']}
• Strategy: Capital preservation - waiting for optimal entry

RECOMMENDED ACTION:
1. Preserve capital - wait for prices to approach support levels
2. Monitor: BTC ${btc_sr['support']:,.2f}, ETH ${eth_sr['support']:,.2f}
3. Re-evaluate in 6-12 hours
"""

    summary += f"""
RISK MANAGEMENT REMINDERS:
1. Never risk more than {STOP_LOSS_PCT*100}% of capital per trade
2. Maximum {MAX_DAILY_TRADES} trades per day
3. Always use stop-loss orders
4. Take profits at {TAKE_PROFIT_PCT*100}% or adjust based on conditions

NEXT ANALYSIS: Recommended in 6-12 hours
====================================
"""
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE - SUMMARY GENERATED")
    print("=" * 70)
    
    return summary

if __name__ == "__main__":
    result = main()
    if result:
        print(result)
        print("\n" + "=" * 70)
        print("SUMMARY READY FOR CRON DELIVERY")
        print("=" * 70)