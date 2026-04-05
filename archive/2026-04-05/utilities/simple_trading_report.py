#!/usr/bin/env python3
"""
Conservative Crypto Trading Analysis Report
Real analysis with $1,000 capital strategy
"""

import requests
import json
from datetime import datetime

# Gemini API
GEMINI_BASE = "https://api.gemini.com/v1"

# Trading parameters
CAPITAL = 1000.0
STOP_LOSS = 5.0  # 5%
TAKE_PROFIT = 10.0  # 10%
MAX_DAILY_TRADES = 2

def get_price(symbol):
    """Get current price"""
    try:
        url = f"{GEMINI_BASE}/pubticker/{symbol}"
        response = requests.get(url, timeout=10)
        data = response.json()
        return {
            "bid": float(data.get("bid", 0)),
            "ask": float(data.get("ask", 0)),
            "last": float(data.get("last", 0)),
            "success": True
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_order_book(symbol):
    """Get order book for analysis"""
    try:
        url = f"{GEMINI_BASE}/book/{symbol}"
        response = requests.get(url, timeout=10)
        data = response.json()
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def analyze_order_book(order_book_data):
    """Simple order book analysis"""
    bids = order_book_data.get("bids", [])
    asks = order_book_data.get("asks", [])
    
    # Calculate order book imbalance
    total_bid = 0
    total_ask = 0
    
    for bid in bids[:10]:
        if len(bid) >= 2:
            try:
                total_bid += float(bid[1])
            except:
                pass
    
    for ask in asks[:10]:
        if len(ask) >= 2:
            try:
                total_ask += float(ask[1])
            except:
                pass
    
    if total_bid + total_ask > 0:
        imbalance = ((total_bid - total_ask) / (total_bid + total_ask)) * 100
    else:
        imbalance = 0
    
    # Determine sentiment
    if imbalance > 7:
        sentiment = "STRONGLY BULLISH"
    elif imbalance > 3:
        sentiment = "BULLISH"
    elif imbalance < -7:
        sentiment = "STRONGLY BEARISH"
    elif imbalance < -3:
        sentiment = "BEARISH"
    else:
        sentiment = "NEUTRAL"
    
    return {
        "order_book_imbalance": imbalance,
        "market_sentiment": sentiment,
        "total_bid_volume": total_bid,
        "total_ask_volume": total_ask
    }

def calculate_trade_decision(price_data, analysis, symbol):
    """Calculate if we should trade"""
    last_price = price_data["last"]
    sentiment = analysis["market_sentiment"]
    imbalance = analysis["order_book_imbalance"]
    
    # Conservative strategy: only trade with strong signals
    should_trade = False
    side = None
    
    if "STRONGLY" in sentiment:
        if "BULLISH" in sentiment and imbalance > 7:
            should_trade = True
            side = "BUY"
            entry = price_data["ask"]
        elif "BEARISH" in sentiment and imbalance < -7:
            should_trade = True
            side = "SELL"
            entry = price_data["bid"]
    
    if not should_trade:
        return {
            "should_trade": False,
            "reason": f"Market conditions too neutral. Sentiment: {sentiment}, Imbalance: {imbalance:.2f}%"
        }
    
    # Calculate position (max 30% of capital for conservative approach)
    position_value = min(CAPITAL * 0.3, CAPITAL * 0.5)
    position_size = position_value / entry
    
    # Calculate stop loss and take profit
    if side == "BUY":
        stop_loss = entry * (1 - STOP_LOSS / 100)
        take_profit = entry * (1 + TAKE_PROFIT / 100)
    else:  # SELL
        stop_loss = entry * (1 + STOP_LOSS / 100)
        take_profit = entry * (1 - TAKE_PROFIT / 100)
    
    # Risk/Reward
    risk_amount = abs(entry - stop_loss) * position_size
    reward_amount = abs(take_profit - entry) * position_size
    risk_reward = reward_amount / risk_amount if risk_amount > 0 else 0
    
    return {
        "should_trade": True,
        "side": side,
        "entry_price": entry,
        "position_size": position_size,
        "position_value": position_value,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "risk_amount": risk_amount,
        "reward_amount": reward_amount,
        "risk_reward_ratio": risk_reward,
        "market_sentiment": sentiment
    }

def generate_report():
    """Generate trading analysis report"""
    output = []
    output.append("=" * 60)
    output.append("CONSERVATIVE CRYPTO TRADING ANALYSIS")
    output.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    output.append(f"Capital: ${CAPITAL:,.2f}")
    output.append(f"Risk Parameters: {STOP_LOSS}% Stop-Loss, {TAKE_PROFIT}% Take-Profit")
    output.append(f"Max Trades/Day: {MAX_DAILY_TRADES}")
    output.append("=" * 60)
    
    # Analyze BTC/USD
    output.append("\n📊 BTC/USD ANALYSIS:")
    btc_price = get_price("btcusd")
    
    if not btc_price["success"]:
        output.append("  Error fetching BTC price data")
    else:
        btc_book = get_order_book("btcusd")
        if not btc_book["success"]:
            output.append("  Error fetching BTC order book")
        else:
            btc_analysis = analyze_order_book(btc_book["data"])
            btc_trade = calculate_trade_decision(btc_price, btc_analysis, "BTC")
            
            output.append(f"  Current Price: ${btc_price['last']:,.2f}")
            output.append(f"  Bid/Ask: ${btc_price['bid']:,.2f} / ${btc_price['ask']:,.2f}")
            output.append(f"  Market Sentiment: {btc_analysis['market_sentiment']}")
            output.append(f"  Order Book Imbalance: {btc_analysis['order_book_imbalance']:.2f}%")
            
            output.append("\n  🎯 TRADING DECISION:")
            if btc_trade["should_trade"]:
                output.append(f"    ✅ TRADE SIGNAL: {btc_trade['side']}")
                output.append(f"    Entry: ${btc_trade['entry_price']:,.2f}")
                output.append(f"    Position: {btc_trade['position_size']:.6f} BTC (${btc_trade['position_value']:,.2f})")
                output.append(f"    Stop Loss: ${btc_trade['stop_loss']:,.2f}")
                output.append(f"    Take Profit: ${btc_trade['take_profit']:,.2f}")
                output.append(f"    Risk: ${btc_trade['risk_amount']:,.2f}")
                output.append(f"    Potential Reward: ${btc_trade['reward_amount']:,.2f}")
                output.append(f"    Risk/Reward: 1:{btc_trade['risk_reward_ratio']:.2f}")
            else:
                output.append(f"    ⚠️  NO TRADE: {btc_trade['reason']}")
    
    # Analyze ETH/USD
    output.append("\n📊 ETH/USD ANALYSIS:")
    eth_price = get_price("ethusd")
    
    if not eth_price["success"]:
        output.append("  Error fetching ETH price data")
    else:
        eth_book = get_order_book("ethusd")
        if not eth_book["success"]:
            output.append("  Error fetching ETH order book")
        else:
            eth_analysis = analyze_order_book(eth_book["data"])
            eth_trade = calculate_trade_decision(eth_price, eth_analysis, "ETH")
            
            output.append(f"  Current Price: ${eth_price['last']:,.2f}")
            output.append(f"  Bid/Ask: ${eth_price['bid']:,.2f} / ${eth_price['ask']:,.2f}")
            output.append(f"  Market Sentiment: {eth_analysis['market_sentiment']}")
            output.append(f"  Order Book Imbalance: {eth_analysis['order_book_imbalance']:.2f}%")
            
            output.append("\n  🎯 TRADING DECISION:")
            if eth_trade["should_trade"]:
                output.append(f"    ✅ TRADE SIGNAL: {eth_trade['side']}")
                output.append(f"    Entry: ${eth_trade['entry_price']:,.2f}")
                output.append(f"    Position: {eth_trade['position_size']:.6f} ETH (${eth_trade['position_value']:,.2f})")
                output.append(f"    Stop Loss: ${eth_trade['stop_loss']:,.2f}")
                output.append(f"    Take Profit: ${eth_trade['take_profit']:,.2f}")
                output.append(f"    Risk: ${eth_trade['risk_amount']:,.2f}")
                output.append(f"    Potential Reward: ${eth_trade['reward_amount']:,.2f}")
                output.append(f"    Risk/Reward: 1:{eth_trade['risk_reward_ratio']:.2f}")
            else:
                output.append(f"    ⚠️  NO TRADE: {eth_trade['reason']}")
    
    output.append("\n" + "=" * 60)
    output.append("EXECUTION NOTES:")
    output.append("=" * 60)
    output.append("1. This is a CONSERVATIVE strategy requiring strong market signals")
    output.append("2. Real execution requires Gemini API credentials")
    output.append("3. Set GEMINI_API_KEY and GEMINI_API_SECRET environment variables")
    output.append("4. Maximum 2 trades per day to avoid overtrading")
    output.append("5. Always use stop-loss orders to limit risk")
    output.append("6. Monitor trades and adjust as market conditions change")
    output.append("=" * 60)
    
    return "\n".join(output)

def main():
    """Main function"""
    print("Generating conservative crypto trading analysis...")
    report = generate_report()
    print(report)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trading_report_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write(report)
    
    print(f"\nReport saved to: {filename}")
    
    # Also print to console for cron delivery
    print("\n" + "=" * 60)
    print("REPORT COMPLETE - READY FOR CRON DELIVERY")
    print("=" * 60)

if __name__ == "__main__":
    main()