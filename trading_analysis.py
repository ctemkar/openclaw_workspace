#!/usr/bin/env python3
"""
Conservative Crypto Trading Analysis
Real-time market analysis with $1,000 capital strategy
"""

import requests
import json
from datetime import datetime
import time

# Gemini API endpoints
GEMINI_BASE = "https://api.gemini.com/v1"

# Trading parameters
CAPITAL = 1000.0
STOP_LOSS = 5.0  # 5%
TAKE_PROFIT = 10.0  # 10%
MAX_DAILY_TRADES = 2
MAX_POSITION_SIZE = CAPITAL * 0.5  # 50% of capital per trade

def get_market_data(symbol):
    """Fetch market data from Gemini"""
    try:
        # Get ticker data
        ticker_url = f"{GEMINI_BASE}/pubticker/{symbol}"
        ticker_response = requests.get(ticker_url, timeout=10)
        ticker_data = ticker_response.json()
        
        # Get order book
        book_url = f"{GEMINI_BASE}/book/{symbol}"
        book_response = requests.get(book_url, timeout=10)
        book_data = book_response.json()
        
        return {
            "ticker": ticker_data,
            "order_book": book_data,
            "success": True
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def analyze_market(symbol, market_data):
    """Perform conservative market analysis"""
    ticker = market_data["ticker"]
    order_book = market_data["order_book"]
    
    # Extract prices
    last_price = float(ticker.get("last", 0))
    bid = float(ticker.get("bid", 0))
    ask = float(ticker.get("ask", 0))
    
    # Calculate spread
    spread = ((ask - bid) / bid) * 100 if bid > 0 else 0
    
    # Analyze order book
    bids = order_book.get("bids", [])
    asks = order_book.get("asks", [])
    
    # Calculate order book imbalance
    total_bid_volume = 0
    total_ask_volume = 0
    
    # Gemini order book format: [price, amount, timestamp]
    for bid in bids[:10]:
        if len(bid) >= 2:
            try:
                total_bid_volume += float(bid[1])
            except:
                pass
    
    for ask in asks[:10]:
        if len(ask) >= 2:
            try:
                total_ask_volume += float(ask[1])
            except:
                pass
    
    if total_bid_volume + total_ask_volume > 0:
        order_book_imbalance = ((total_bid_volume - total_ask_volume) / 
                               (total_bid_volume + total_ask_volume)) * 100
    else:
        order_book_imbalance = 0
    
    # Determine market sentiment
    if order_book_imbalance > 7:
        sentiment = "STRONGLY BULLISH"
    elif order_book_imbalance > 3:
        sentiment = "BULLISH"
    elif order_book_imbalance < -7:
        sentiment = "STRONGLY BEARISH"
    elif order_book_imbalance < -3:
        sentiment = "BEARISH"
    else:
        sentiment = "NEUTRAL"
    
    # Calculate support/resistance from order book
    support_levels = []
    resistance_levels = []
    
    for bid in bids[:5]:
        if len(bid) >= 1:
            try:
                support_levels.append(float(bid[0]))
            except:
                pass
    
    for ask in asks[:5]:
        if len(ask) >= 1:
            try:
                resistance_levels.append(float(ask[0]))
            except:
                pass
    
    support_levels = sorted(support_levels, reverse=True)
    resistance_levels = sorted(resistance_levels)
    
    # Volume analysis
    volume_data = ticker.get("volume", {})
    if isinstance(volume_data, dict):
        volume_key = symbol.upper().replace("USD", "")
        volume_24h = float(volume_data.get(volume_key, 0))
    else:
        volume_24h = 0
    
    return {
        "symbol": symbol,
        "last_price": last_price,
        "bid": bid,
        "ask": ask,
        "spread_percent": spread,
        "order_book_imbalance": order_book_imbalance,
        "market_sentiment": sentiment,
        "support_levels": support_levels,
        "resistance_levels": resistance_levels,
        "volume_24h": volume_24h,
        "timestamp": datetime.now().isoformat()
    }

def calculate_trade_parameters(analysis, capital=CAPITAL):
    """Calculate conservative trade parameters"""
    last_price = analysis["last_price"]
    
    # Only trade with strong signals for conservative strategy
    sentiment = analysis["market_sentiment"]
    imbalance = analysis["order_book_imbalance"]
    
    # Determine if we should trade
    should_trade = False
    trade_side = None
    
    if "STRONGLY" in sentiment:
        if "BULLISH" in sentiment and imbalance > 7:
            should_trade = True
            trade_side = "BUY"
        elif "BEARISH" in sentiment and imbalance < -7:
            should_trade = True
            trade_side = "SELL"
    
    if not should_trade:
        return {
            "should_trade": False,
            "reason": f"Market conditions too neutral for conservative trading. Sentiment: {sentiment}, Imbalance: {imbalance:.2f}%"
        }
    
    # Calculate position size (max 50% of capital)
    position_value = min(capital * 0.5, capital * 0.3)  # Conservative: 30% of capital
    position_size = position_value / last_price
    
    # Calculate entry price
    if trade_side == "BUY":
        entry_price = analysis["ask"]  # Buy at ask
    else:
        entry_price = analysis["bid"]  # Sell at bid
    
    # Calculate stop loss and take profit
    if trade_side == "BUY":
        stop_loss = entry_price * (1 - STOP_LOSS / 100)
        take_profit = entry_price * (1 + TAKE_PROFIT / 100)
    else:  # SELL
        stop_loss = entry_price * (1 + STOP_LOSS / 100)
        take_profit = entry_price * (1 - TAKE_PROFIT / 100)
    
    # Risk/Reward ratio
    risk_amount = abs(entry_price - stop_loss) * position_size
    reward_amount = abs(take_profit - entry_price) * position_size
    risk_reward_ratio = reward_amount / risk_amount if risk_amount > 0 else 0
    
    return {
        "should_trade": True,
        "side": trade_side,
        "entry_price": entry_price,
        "position_size": position_size,
        "position_value": position_value,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "risk_percent": STOP_LOSS,
        "reward_percent": TAKE_PROFIT,
        "risk_amount": risk_amount,
        "reward_amount": reward_amount,
        "risk_reward_ratio": risk_reward_ratio,
        "market_sentiment": sentiment,
        "order_book_imbalance": imbalance
    }

def format_output(analysis, trade_params):
    """Format output for plain text delivery"""
    output = []
    output.append("=" * 60)
    output.append("CONSERVATIVE CRYPTO TRADING ANALYSIS")
    output.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    output.append(f"Capital: ${CAPITAL:,.2f}")
    output.append("=" * 60)
    
    output.append(f"\n📊 {analysis['symbol'].upper()} MARKET ANALYSIS:")
    output.append(f"  Current Price: ${analysis['last_price']:,.2f}")
    output.append(f"  Bid/Ask: ${analysis['bid']:,.2f} / ${analysis['ask']:,.2f}")
    output.append(f"  Spread: {analysis['spread_percent']:.4f}%")
    output.append(f"  Market Sentiment: {analysis['market_sentiment']}")
    output.append(f"  Order Book Imbalance: {analysis['order_book_imbalance']:.2f}%")
    output.append(f"  24h Volume: {analysis['volume_24h']:,.2f} {analysis['symbol'].replace('usd', '').upper()}")
    
    if analysis['support_levels']:
        output.append(f"  Key Support Levels: ${', $'.join(f'{x:,.2f}' for x in analysis['support_levels'])}")
    if analysis['resistance_levels']:
        output.append(f"  Key Resistance Levels: ${', $'.join(f'{x:,.2f}' for x in analysis['resistance_levels'])}")
    
    output.append("\n⚖️  TRADING PARAMETERS:")
    output.append(f"  Stop Loss: {STOP_LOSS}%")
    output.append(f"  Take Profit: {TAKE_PROFIT}%")
    output.append(f"  Max Daily Trades: {MAX_DAILY_TRADES}")
    output.append(f"  Max Position Size: ${MAX_POSITION_SIZE:,.2f}")
    
    output.append("\n🎯 TRADING DECISION:")
    if trade_params["should_trade"]:
        output.append(f"  ✅ TRADE SIGNAL: {trade_params['side']}")
        output.append(f"  Entry Price: ${trade_params['entry_price']:,.2f}")
        output.append(f"  Position Size: {trade_params['position_size']:.6f} {analysis['symbol'].replace('usd', '').upper()}")
        output.append(f"  Position Value: ${trade_params['position_value']:,.2f}")
        output.append(f"  Stop Loss: ${trade_params['stop_loss']:,.2f}")
        output.append(f"  Take Profit: ${trade_params['take_profit']:,.2f}")
        output.append(f"  Risk Amount: ${trade_params['risk_amount']:,.2f}")
        output.append(f"  Potential Reward: ${trade_params['reward_amount']:,.2f}")
        output.append(f"  Risk/Reward Ratio: 1:{trade_params['risk_reward_ratio']:.2f}")
        
        output.append("\n⚠️  EXECUTION NOTE:")
        output.append("  To execute this trade with real $1,000 capital:")
        output.append("  1. Set GEMINI_API_KEY and GEMINI_API_SECRET environment variables")
        output.append("  2. Run the trading script with real execution enabled")
        output.append("  3. Monitor trade and adjust stop loss/take profit as needed")
    else:
        output.append(f"  ⚠️  NO TRADE: {trade_params['reason']}")
        output.append("\n  Conservative strategy requires strong market signals.")
        output.append("  Waiting for better risk/reward opportunities.")
    
    output.append("\n" + "=" * 60)
    output.append("END OF ANALYSIS")
    output.append("=" * 60)
    
    return "\n".join(output)

def main():
    """Main analysis function"""
    print("Starting conservative crypto trading analysis...")
    
    # Analyze BTC/USD
    print("\nAnalyzing BTC/USD...")
    btc_data = get_market_data("btcusd")
    
    if not btc_data["success"]:
        print(f"Error fetching BTC data: {btc_data.get('error', 'Unknown error')}")
        return
    
    btc_analysis = analyze_market("btcusd", btc_data)
    btc_trade = calculate_trade_parameters(btc_analysis)
    
    # Analyze ETH/USD
    print("Analyzing ETH/USD...")
    eth_data = get_market_data("ethusd")
    
    if not eth_data["success"]:
        print(f"Error fetching ETH data: {eth_data.get('error', 'Unknown error')}")
        # Continue with BTC analysis only
        eth_analysis = None
        eth_trade = {"should_trade": False, "reason": "Data fetch failed"}
    else:
        eth_analysis = analyze_market("ethusd", eth_data)
        eth_trade = calculate_trade_parameters(eth_analysis)
    
    # Generate output
    output = []
    output.append(format_output(btc_analysis, btc_trade))
    
    if eth_analysis:
        output.append("\n" + "=" * 60)
        output.append("ETH/USD ANALYSIS")
        output.append("=" * 60)
        output.append(format_output(eth_analysis, eth_trade))
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trading_analysis_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write("\n".join(output))
    
    print(f"\nAnalysis saved to: {filename}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"BTC/USD: {btc_analysis['market_sentiment']} - Trade: {'YES' if btc_trade['should_trade'] else 'NO'}")
    if eth_analysis:
        print(f"ETH/USD: {eth_analysis['market_sentiment']} - Trade: {'YES' if eth_trade['should_trade'] else 'NO'}")
    print("=" * 60)

if __name__ == "__main__":
    main()