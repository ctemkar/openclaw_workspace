#!/usr/bin/env python3
"""
Final Conservative Crypto Trading Analysis
Provides comprehensive analysis with conservative recommendations
"""

import requests
import json
import os
from datetime import datetime
import time

# Configuration
CAPITAL = 1000.0  # $1,000 capital as requested
STOP_LOSS_PCT = 0.05  # 5% stop-loss
TAKE_PROFIT_PCT = 0.10  # 10% take-profit
MAX_POSITION_SIZE = 0.5  # 50% of capital per trade
MAX_DAILY_TRADES = 2

GEMINI_API_URL = "https://api.gemini.com"

def fetch_market_data():
    """Fetch comprehensive market data"""
    print("📊 Fetching comprehensive market data...")
    
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
                "volume": float(btc_data.get("volume", {}).get("USD", 0)),
                "high": float(btc_data.get("high", 0)),
                "low": float(btc_data.get("low", 0))
            }
        
        # ETH/USD
        eth_response = requests.get(f"{GEMINI_API_URL}/v1/pubticker/ethusd", timeout=10)
        if eth_response.status_code == 200:
            eth_data = eth_response.json()
            data["eth"] = {
                "price": float(eth_data.get("last", 0)),
                "bid": float(eth_data.get("bid", 0)),
                "ask": float(eth_data.get("ask", 0)),
                "volume": float(eth_data.get("volume", {}).get("USD", 0)),
                "high": float(eth_data.get("high", 0)),
                "low": float(eth_data.get("low", 0))
            }
        
        data["success"] = bool(data["btc"] and data["eth"])
        
    except Exception as e:
        print(f"❌ Error fetching market data: {e}")
    
    return data

def calculate_technical_levels(symbol, market_data):
    """Calculate technical analysis levels"""
    try:
        # Get order book for support/resistance
        response = requests.get(f"{GEMINI_API_URL}/v1/book/{symbol}", timeout=10)
        if response.status_code != 200:
            return {"support": 0, "resistance": 0, "rsi": 50, "trend": "neutral"}
        
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
        
        # Simple RSI calculation based on daily high/low
        current_price = market_data["price"]
        daily_high = market_data["high"]
        daily_low = market_data["low"]
        
        if daily_high > daily_low:
            rsi_position = (current_price - daily_low) / (daily_high - daily_low) * 100
        else:
            rsi_position = 50
        
        # Determine trend
        if rsi_position > 70:
            trend = "overbought"
        elif rsi_position < 30:
            trend = "oversold"
        else:
            trend = "neutral"
        
        return {
            "support": round(support, 2),
            "resistance": round(resistance, 2),
            "rsi": round(rsi_position, 1),
            "trend": trend,
            "bid_depth": len(bids),
            "ask_depth": len(asks)
        }
        
    except Exception as e:
        print(f"❌ Error calculating technical levels for {symbol}: {e}")
        return {"support": 0, "resistance": 0, "rsi": 50, "trend": "neutral"}

def analyze_market_sentiment(market_data):
    """Comprehensive market sentiment analysis"""
    btc_price = market_data["btc"].get("price", 0)
    eth_price = market_data["eth"].get("price", 0)
    btc_volume = market_data["btc"].get("volume", 0)
    eth_volume = market_data["eth"].get("volume", 0)
    btc_high = market_data["btc"].get("high", 0)
    btc_low = market_data["btc"].get("low", 0)
    
    if btc_price == 0 or eth_price == 0:
        return "UNKNOWN", "Insufficient data"
    
    # Volume analysis
    volume_signal = ""
    if btc_volume > 20000000 and eth_volume > 10000000:
        volume_signal = "High volume - Strong interest"
        volume_score = 1
    elif btc_volume < 8000000 or eth_volume < 4000000:
        volume_signal = "Low volume - Caution advised"
        volume_score = -1
    else:
        volume_signal = "Moderate volume - Normal market"
        volume_score = 0
    
    # Price position analysis
    if btc_high > btc_low:
        btc_position = (btc_price - btc_low) / (btc_high - btc_low) * 100
        if btc_position > 80:
            price_signal = "Trading near daily highs"
            price_score = -1  # Conservative: avoid buying at highs
        elif btc_position < 20:
            price_signal = "Trading near daily lows"
            price_score = 1  # Conservative: consider buying at lows
        else:
            price_signal = "Trading in middle range"
            price_score = 0
    else:
        price_signal = "Insufficient price range data"
        price_score = 0
    
    # Overall sentiment
    total_score = volume_score + price_score
    
    if total_score >= 1:
        sentiment = "BULLISH"
        reason = f"{volume_signal}, {price_signal}"
    elif total_score <= -1:
        sentiment = "BEARISH"
        reason = f"{volume_signal}, {price_signal}"
    else:
        sentiment = "NEUTRAL"
        reason = f"{volume_signal}, {price_signal}"
    
    return sentiment, reason

def conservative_trading_decision(market_data, btc_tech, eth_tech, sentiment):
    """Make conservative trading decision"""
    
    btc_price = market_data["btc"].get("price", 0)
    eth_price = market_data["eth"].get("price", 0)
    
    # Conservative rules:
    # 1. Only trade in NEUTRAL or BULLISH sentiment
    # 2. Price must be near support (within 2%)
    # 3. RSI should not be overbought (< 60)
    # 4. Maximum 50% position size
    
    if sentiment not in ["NEUTRAL", "BULLISH"]:
        return {
            "signal": "HOLD",
            "symbol": None,
            "reason": f"Market sentiment too cautious: {sentiment}",
            "details": "Conservative strategy avoids trading in bearish conditions"
        }
    
    # Check BTC opportunity
    btc_opportunity = False
    btc_reason = ""
    
    if btc_price > 0 and btc_tech["support"] > 0:
        distance_pct = abs(btc_price - btc_tech["support"]) / btc_price
        
        if distance_pct <= 0.02:  # Within 2% of support
            if btc_tech["rsi"] < 60:  # Not overbought
                btc_opportunity = True
                btc_reason = f"BTC near support (${btc_tech['support']:.2f}), RSI {btc_tech['rsi']} (not overbought)"
            else:
                btc_reason = f"BTC near support but RSI {btc_tech['rsi']} indicates overbought conditions"
        else:
            btc_reason = f"BTC not near support (${btc_tech['support']:.2f}, {distance_pct*100:.1f}% away)"
    
    # Check ETH opportunity
    eth_opportunity = False
    eth_reason = ""
    
    if eth_price > 0 and eth_tech["support"] > 0:
        distance_pct = abs(eth_price - eth_tech["support"]) / eth_price
        
        if distance_pct <= 0.02:  # Within 2% of support
            if eth_tech["rsi"] < 60:  # Not overbought
                eth_opportunity = True
                eth_reason = f"ETH near support (${eth_tech['support']:.2f}), RSI {eth_tech['rsi']} (not overbought)"
            else:
                eth_reason = f"ETH near support but RSI {eth_tech['rsi']} indicates overbought conditions"
        else:
            eth_reason = f"ETH not near support (${eth_tech['support']:.2f}, {distance_pct*100:.1f}% away)"
    
    # Make decision
    if btc_opportunity:
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
            "reason": btc_reason,
            "details": f"Conservative buy at support with {STOP_LOSS_PCT*100}% stop-loss"
        }
    
    elif eth_opportunity:
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
            "reason": eth_reason,
            "details": f"Conservative buy at support with {STOP_LOSS_PCT*100}% stop-loss"
        }
    
    else:
        return {
            "signal": "HOLD",
            "symbol": None,
            "reason": "No conservative trading opportunities found",
            "details": f"BTC: {btc_reason}\nETH: {eth_reason}"
        }

def generate_plain_text_summary(market_data, btc_tech, eth_tech, sentiment, sentiment_reason, decision):
    """Generate plain text summary for cron delivery"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC+7")
    
    summary = f"""
CONSERVATIVE CRYPTO TRADING ANALYSIS - REAL TIME
================================================
Analysis Time: {timestamp}

CAPITAL & RISK PARAMETERS:
• Available Capital: ${CAPITAL:,.2f}
• Max Position Size: {MAX_POSITION_SIZE*100}% (${CAPITAL * MAX_POSITION_SIZE:,.2f})
• Stop Loss: {STOP_LOSS_PCT*100}%
• Take Profit: {TAKE_PROFIT_PCT*100}%
• Max Daily Trades: {MAX_DAILY_TRADES}
• Risk/Reward Ratio: 1:{TAKE_PROFIT_PCT/STOP_LOSS_PCT:.1f}

MARKET DATA:
• BTC/USD: ${market_data['btc']['price']:,.2f}
  Bid: ${market_data['btc']['bid']:,.2f} | Ask: ${market_data['btc']['ask']:,.2f}
  24h High: ${market_data['btc']['high']:,.2f} | Low: ${market_data['btc']['low']:,.2f}
  24h Volume: ${market_data['btc']['volume']:,.0f}

• ETH/USD: ${market_data['eth']['price']:,.2f}
  Bid: ${market_data['eth']['bid']:,.2f} | Ask: ${market_data['eth']['ask']:,.2f}
  24h High: ${market_data['eth']['high']:,.2f} | Low: ${market_data['eth']['low']:,.2f}
  24h Volume: ${market_data['eth']['volume']:,.0f}

TECHNICAL ANALYSIS:
• BTC Support: ${btc_tech['support']:,.2f}
• BTC Resistance: ${btc_tech['resistance']:,.2f}
• BTC RSI: {btc_tech['rsi']} ({btc_tech['trend']})
• BTC Order Book: {btc_tech['bid_depth']} bids, {btc_tech['ask_depth']} asks

• ETH Support: ${eth_tech['support']:,.2f}
• ETH Resistance: ${eth_tech['resistance']:,.2f}
• ETH RSI: {eth_tech['rsi']} ({eth_tech['trend']})
• ETH Order Book: {eth_tech['bid_depth']} bids, {eth_tech['ask_depth']} asks

MARKET SENTIMENT: {sentiment}
Reason: {sentiment_reason}

TRADING DECISION: {decision['signal']}
{decision['reason']}

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

EXECUTION STATUS: ANALYSIS COMPLETE - MANUAL EXECUTION REQUIRED
Note: Gemini API credentials need verification for automated trading

RECOMMENDED ACTION:
1. Verify Gemini API credentials are valid
2. Manually execute trade at specified entry price
3. Set stop-loss and take-profit orders immediately
4. Monitor position and adjust if market conditions change
"""
    else:
        summary += f"""
NO TRADE EXECUTED - CONSERVATIVE STRATEGY:
• Decision: Maintain HOLD position
• Details: {decision['details']}
• Strategy: Capital preservation during uncertain conditions

RECOMMENDED ACTION:
1. Preserve capital - wait for better entry points
2. Monitor support levels: BTC ${btc_tech['support']:,.2f}, ETH ${eth_tech['support']:,.2f}
3. Re-evaluate in 6-12 hours or if prices approach support levels
4. Consider dollar-cost averaging if long-term bullish
"""

    summary += f"""
RISK MANAGEMENT REMINDERS:
1. Never risk more than {STOP_LOSS_PCT*100}% of capital per trade
2. Maximum {MAX_DAILY_TRADES} trades per day to avoid overtrading
3. Always use stop-loss orders to protect capital
4. Take profits at {TAKE_PROFIT_PCT*100}% or adjust based on market conditions
5. If trade moves against you by {STOP_LOSS_PCT*100}%, exit immediately

NEXT ANALYSIS SCHEDULE:
• Recommended next analysis: 6-12 hours
• Key levels to watch: BTC ${btc_tech['support']:,.2f} support, ETH ${eth_tech['support']:,.2f} support
• Market conditions requiring review
"""

    return summary