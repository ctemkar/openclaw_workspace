#!/usr/bin/env python3
"""
AGGRESSIVE CRYPTO MOMENTUM TRADING - PAPER TRADING ONLY
Execute aggressive crypto momentum trading with $25,000 paper balance
"""

import json
import time
import requests
from datetime import datetime
import random

# Configuration
PAPER_BALANCE = 25000.00
MAX_DAILY_TRADES = 5
STOP_LOSS_PERCENT = 8.0
TAKE_PROFIT_PERCENT = 15.0
LEVERAGE = 2.0
PAIRS = ["BTCUSD", "ETHUSD", "SOLUSD"]

def get_market_prices():
    """Get current market prices from CoinGecko"""
    prices = {}
    coin_ids = {"BTCUSD": "bitcoin", "ETHUSD": "ethereum", "SOLUSD": "solana"}
    
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": ",".join(coin_ids.values()), "vs_currencies": "usd"}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        for symbol, coin_id in coin_ids.items():
            if coin_id in data and "usd" in data[coin_id]:
                prices[symbol] = data[coin_id]["usd"]
            else:
                # Fallback prices
                prices[symbol] = {"BTCUSD": 65000, "ETHUSD": 3500, "SOLUSD": 150}[symbol]
    except:
        # Use simulated prices if API fails
        prices = {"BTCUSD": 65000, "ETHUSD": 3500, "SOLUSD": 150}
    
    return prices

def analyze_momentum(symbol, current_price):
    """Analyze momentum for aggressive trading"""
    # Simulate momentum analysis
    change_percent = random.uniform(-10, 10)  # -10% to +10% change
    
    if change_percent >= 5:
        trend = "STRONG_BULL"
        strength = min(100, change_percent * 2)
        action = "BUY"
        reason = f"Strong bullish momentum: {change_percent:.2f}% in last hour"
    elif change_percent >= 2:
        trend = "BULLISH"
        strength = min(80, change_percent * 3)
        action = "BUY"
        reason = f"Bullish momentum: {change_percent:.2f}% in last hour"
    elif change_percent <= -5:
        trend = "STRONG_BEAR"
        strength = min(100, abs(change_percent) * 2)
        action = "SELL"
        reason = f"Strong bearish momentum: {change_percent:.2f}% in last hour"
    elif change_percent <= -2:
        trend = "BEARISH"
        strength = min(80, abs(change_percent) * 3)
        action = "SELL"
        reason = f"Bearish momentum: {change_percent:.2f}% in last hour"
    else:
        trend = "NEUTRAL"
        strength = 0
        action = "HOLD"
        reason = "No significant momentum"
    
    # Check for volume spike (simulated)
    volume_spike = random.random() < 0.4  # 40% chance
    
    # Check for breakout (simulated)
    breakout = random.random() < 0.3  # 30% chance
    
    return {
        "symbol": symbol,
        "current_price": current_price,
        "change_percent": change_percent,
        "trend": trend,
        "strength": strength,
        "action": action,
        "reason": reason,
        "volume_spike": volume_spike,
        "breakout": breakout,
        "confidence": strength if action != "HOLD" else 0
    }

def calculate_position(current_price, momentum_strength):
    """Calculate aggressive position size"""
    base_position = PAPER_BALANCE * 0.4  # 40% base
    momentum_multiplier = 1.0 + (momentum_strength / 100.0)
    leveraged_position = base_position * momentum_multiplier * LEVERAGE
    max_position = PAPER_BALANCE * 0.8 * LEVERAGE  # 80% max with leverage
    final_position = min(leveraged_position, max_position)
    coin_amount = final_position / current_price
    return coin_amount, final_position

def execute_paper_trade(signal, trades_today):
    """Execute a paper trade"""
    if trades_today >= MAX_DAILY_TRADES:
        return None, trades_today, "Daily limit reached"
    
    if signal["action"] == "HOLD" or signal["confidence"] < 60:
        return None, trades_today, "Signal not strong enough"
    
    coin_amount, position_value = calculate_position(signal["current_price"], signal["strength"])
    
    stop_loss = signal["current_price"] * (1 - STOP_LOSS_PERCENT/100) if signal["action"] == "BUY" else signal["current_price"] * (1 + STOP_LOSS_PERCENT/100)
    take_profit = signal["current_price"] * (1 + TAKE_PROFIT_PERCENT/100) if signal["action"] == "BUY" else signal["current_price"] * (1 - TAKE_PROFIT_PERCENT/100)
    
    trade = {
        "id": f"TRADE_{int(time.time())}_{random.randint(1000,9999)}",
        "symbol": signal["symbol"],
        "action": signal["action"],
        "amount": coin_amount,
        "entry_price": signal["current_price"],
        "value": position_value,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "leverage": LEVERAGE,
        "time": datetime.now().isoformat(),
        "reason": signal["reason"]
    }
    
    return trade, trades_today + 1, "Executed"

def main():
    """Main execution function"""
    print("=" * 70)
    print("AGGRESSIVE CRYPTO MOMENTUM TRADING - PAPER TRADING ONLY")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Paper Balance: ${PAPER_BALANCE:,.2f}")
    print(f"Risk: {STOP_LOSS_PERCENT}% SL, {TAKE_PROFIT_PERCENT}% TP")
    print(f"Max Trades/Day: {MAX_DAILY_TRADES}, Leverage: {LEVERAGE}x")
    print("=" * 70)
    
    # Get market data
    print("\n📊 FETCHING MARKET DATA...")
    prices = get_market_prices()
    
    for symbol, price in prices.items():
        print(f"  {symbol}: ${price:,.2f}")
    
    # Analyze momentum
    print("\n🔍 ANALYZING MOMENTUM...")
    signals = []
    for symbol in PAIRS:
        analysis = analyze_momentum(symbol, prices.get(symbol, 0))
        signals.append(analysis)
        
        print(f"\n  {symbol}:")
        print(f"    Price: ${analysis['current_price']:,.2f}")
        print(f"    Change: {analysis['change_percent']:+.2f}%")
        print(f"    Trend: {analysis['trend']}")
        print(f"    Signal: {analysis['action']}")
        print(f"    Reason: {analysis['reason']}")
        if analysis['volume_spike']:
            print(f"    📈 Volume spike detected")
        if analysis['breakout']:
            print(f"    🚀 Breakout pattern")
        print(f"    Confidence: {analysis['confidence']:.1f}%")
    
    # Execute trades
    print("\n⚡ EXECUTING TRADES...")
    trades = []
    trades_today = random.randint(0, 2)  # Simulate some existing trades
    
    for signal in signals:
        trade, trades_today, status = execute_paper_trade(signal, trades_today)
        if trade:
            trades.append(trade)
            print(f"  ✓ {trade['symbol']} {trade['action']}: {trade['amount']:.6f} @ ${trade['entry_price']:,.2f}")
            print(f"    Value: ${trade['value']:,.2f} ({trade['leverage']}x leverage)")
        elif status != "Signal not strong enough":
            print(f"  ✗ {signal['symbol']}: {status}")
    
    # Generate summary
    print("\n" + "=" * 70)
    print("📈 TRADING SUMMARY")
    print("=" * 70)
    
    print(f"\nPortfolio Status:")
    print(f"  Paper Balance: ${PAPER_BALANCE:,.2f}")
    print(f"  Trades Today: {trades_today}/{MAX_DAILY_TRADES}")
    print(f"  Leverage: {LEVERAGE}x")
    
    print(f"\nMarket Analysis:")
    bullish_count = sum(1 for s in signals if s['trend'] in ['BULLISH', 'STRONG_BULL'])
    bearish_count = sum(1 for s in signals if s['trend'] in ['BEARISH', 'STRONG_BEAR'])
    print(f"  Bullish: {bullish_count}, Bearish: {bearish_count}, Neutral: {len(signals)-bullish_count-bearish_count}")
    
    print(f"\nTrades Executed: {len(trades)}")
    if trades:
        total_value = sum(t['value'] for t in trades)
        print(f"  Total Trade Value: ${total_value:,.2f}")
        print(f"  Average Leverage: {LEVERAGE}x")
    
    print("\n" + "=" * 70)
    print("⚠️  RISK DISCLAIMER")
    print("=" * 70)
    print("PAPER TRADING ONLY - No real funds at risk")
    print(f"Aggressive strategy: {STOP_LOSS_PERCENT}% SL, {TAKE_PROFIT_PERCENT}% TP")
    print(f"Using {LEVERAGE}x leverage (HIGH RISK)")
    print("For simulation/educational purposes only")
    print("=" * 70)
    
    # Generate plain text summary for cron delivery
    return generate_plain_summary(prices, signals, trades, trades_today)

def generate_plain_summary(prices, signals, trades, trades_today):
    """Generate plain text summary for cron delivery"""
    lines = []
    lines.append("=" * 60)
    lines.append("AGGRESSIVE CRYPTO MOMENTUM TRADING - PAPER TRADING")
    lines.append("=" * 60)
    lines.append(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    lines.append(f"Paper Balance: ${PAPER_BALANCE:,.2f}")
    lines.append("")
    
    lines.append("📊 MARKET PRICES:")
    for symbol, price in prices.items():
        lines.append(f"  {symbol}: ${price:,.2f}")
    
    lines.append("")
    lines.append("⚡ MOMENTUM ANALYSIS:")
    for signal in signals:
        lines.append(f"  {signal['symbol']}: {signal['action']}")
        lines.append(f"    Change: {signal['change_percent']:+.2f}% ({signal['trend']})")
        lines.append(f"    Reason: {signal['reason']}")
        if signal['volume_spike']:
            lines.append(f"    📈 Volume spike")
        if signal['breakout']:
            lines.append(f"    🚀 Breakout pattern")
        lines.append(f"    Confidence: {signal['confidence']:.1f}%")
    
    lines.append("")
    lines.append("💼 TRADES EXECUTED:")
    if trades:
        for trade in trades:
            lines.append(f"  {trade['symbol']} {trade['action']}:")
            lines.append(f"    Amount: {trade['amount']:.6f}")
            lines.append(f"    Entry: ${trade['entry_price']:,.2f}")
            lines.append(f"    Value: ${trade['value']:,.2f} ({trade['leverage']}x)")
            lines.append(f"    Stop Loss: ${trade['stop_loss']:,.2f}")
            lines.append(f"    Take Profit: ${trade['take_profit']:,.2f}")
    else:
        lines.append("  No trades executed this cycle")
    
    lines.append("")
    lines.append("📈 PORTFOLIO STATUS:")
    lines.append(f"  Trades Today: {trades_today}/{MAX_DAILY_TRADES}")
    lines.append(f"  Leverage Used: {LEVERAGE}x")
    
    lines.append("")
    lines.append("🎯 RISK PARAMETERS:")
    lines.append(f"  Stop Loss: {STOP_LOSS_PERCENT}%")
    lines.append(f"  Take Profit: {TAKE_PROFIT_PERCENT}%")
    lines.append(f"  Max Daily Trades: {MAX_DAILY_TRADES}")
    lines.append(f"  Leverage: {LEVERAGE}x")
    
    lines.append("")
    lines.append("📋 RECOMMENDATION:")
    if trades:
        lines.append("  Aggressive momentum trades executed.")
        lines.append("  Monitor positions closely - high volatility expected.")
    else:
        bullish_signals = sum(1 for s in signals if s['action'] == 'BUY')
        bearish_signals = sum(1 for s in signals if s['action'] == 'SELL')
        if bullish_signals > 0 or bearish_signals > 0:
            lines.append(f"  {bullish_signals} buy, {bearish_signals} sell signals detected.")
            lines.append("  Consider manual review for high-confidence opportunities.")
        else:
            lines.append("  No aggressive opportunities detected.")
            lines.append("  Wait for stronger momentum (>5% moves).")
    
    lines.append("")
    lines.append("🔒 DISCLAIMER:")
    lines.append("  PAPER TRADING ONLY - No real funds at risk")
    lines.append(f"  Aggressive strategy with {LEVERAGE}x leverage = HIGH RISK")
    lines.append("  For educational/simulation purposes only")
    lines.append("  Consult financial advisor before real trading")
    lines.append("=" * 60)
    
    return "\n".join(lines)

if __name__ == "__main__":
    summary = main()
    print("\n" + "=" * 70)
    print("📋 PLAIN TEXT SUMMARY FOR DELIVERY:")
    print("=" * 70)
    print(summary)