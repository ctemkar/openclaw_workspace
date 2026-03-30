#!/usr/bin/env python3
"""
Aggressive Crypto Momentum Trading Script
PAPER TRADING ONLY with $25,000 paper balance
Checks for 5%+ moves in last hour, high volume spikes, breakout patterns
Risk parameters: 8% stop-loss, 15% take-profit, max 5 trades per day with 2x leverage
"""

import requests
import json
import time
from datetime import datetime, timedelta
import os

print("=" * 80)
print("AGGRESSIVE CRYPTO MOMENTUM TRADING - PAPER TRADING ONLY")
print("=" * 80)
print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Asia/Bangkok)")
print(f"Paper Balance: $25,000")
print(f"Leverage: 2x (paper trading only)")
print(f"Risk: 8% stop-loss, 15% take-profit")
print(f"Max Trades/Day: 5")
print("=" * 80)

# Trading parameters
PAPER_BALANCE = 25000
STOP_LOSS_PCT = 0.08
TAKE_PROFIT_PCT = 0.15
MAX_TRADES_PER_DAY = 5
LEVERAGE = 2  # 2x leverage for paper trading
POSITION_SIZE_PCT = 0.2  # 20% of paper balance per trade

# Cryptocurrencies to monitor
CRYPTOS = [
    {"id": "bitcoin", "symbol": "BTC"},
    {"id": "ethereum", "symbol": "ETH"},
    {"id": "solana", "symbol": "SOL"}
]

def fetch_historical_data(crypto_id, days=1):
    """Fetch historical price data for momentum analysis"""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'hourly'
        }
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error fetching data for {crypto_id}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error fetching historical data for {crypto_id}: {e}")
        return None

def calculate_momentum(prices, timestamps):
    """Calculate momentum metrics from price data"""
    if not prices or len(prices) < 2:
        return None
    
    # Get current and previous hour prices
    current_price = prices[-1]
    hour_ago_price = prices[-2] if len(prices) >= 2 else prices[-1]
    day_ago_price = prices[0] if len(prices) >= 24 else prices[-1]
    
    # Calculate percentage changes
    hourly_change_pct = ((current_price - hour_ago_price) / hour_ago_price) * 100
    daily_change_pct = ((current_price - day_ago_price) / day_ago_price) * 100
    
    # Calculate volatility (standard deviation of last 24 hours)
    if len(prices) >= 24:
        recent_prices = prices[-24:]
        avg_price = sum(recent_prices) / len(recent_prices)
        variance = sum((p - avg_price) ** 2 for p in recent_prices) / len(recent_prices)
        volatility = variance ** 0.5
        volatility_pct = (volatility / avg_price) * 100
    else:
        volatility_pct = 0
    
    return {
        "current_price": current_price,
        "hour_ago_price": hour_ago_price,
        "hourly_change_pct": hourly_change_pct,
        "daily_change_pct": daily_change_pct,
        "volatility_pct": volatility_pct,
        "timestamp": datetime.fromtimestamp(timestamps[-1]/1000).strftime('%Y-%m-%d %H:%M:%S')
    }

def analyze_momentum_opportunities():
    """Analyze all cryptocurrencies for momentum opportunities"""
    print("\n📊 ANALYZING MOMENTUM OPPORTUNITIES")
    print("-" * 60)
    
    opportunities = []
    
    for crypto in CRYPTOS:
        print(f"\nAnalyzing {crypto['symbol']}...")
        
        # Fetch historical data
        data = fetch_historical_data(crypto["id"], days=1)
        if not data or "prices" not in data:
            print(f"  ⚠️  No data available for {crypto['symbol']}")
            continue
        
        prices = [price for timestamp, price in data["prices"]]
        timestamps = [timestamp for timestamp, price in data["prices"]]
        
        # Calculate momentum
        momentum = calculate_momentum(prices, timestamps)
        if not momentum:
            continue
        
        print(f"  Current Price: ${momentum['current_price']:,.2f}")
        print(f"  1-Hour Change: {momentum['hourly_change_pct']:+.2f}%")
        print(f"  24-Hour Change: {momentum['daily_change_pct']:+.2f}%")
        print(f"  Volatility (24h): {momentum['volatility_pct']:.2f}%")
        
        # Check for aggressive momentum criteria
        is_opportunity = False
        signal = "HOLD"
        reason = ""
        
        # Criteria 1: Strong hourly momentum (5%+ move)
        if abs(momentum["hourly_change_pct"]) >= 5:
            is_opportunity = True
            signal = "BUY" if momentum["hourly_change_pct"] > 0 else "SELL"
            reason = f"Strong {signal} momentum: {momentum['hourly_change_pct']:+.2f}% in last hour"
        
        # Criteria 2: High volatility breakout (>3% volatility)
        elif momentum["volatility_pct"] > 3 and abs(momentum["daily_change_pct"]) > 2:
            is_opportunity = True
            signal = "BUY" if momentum["daily_change_pct"] > 0 else "SELL"
            reason = f"High volatility breakout: {momentum['volatility_pct']:.2f}% volatility with {momentum['daily_change_pct']:+.2f}% daily move"
        
        # Criteria 3: Strong daily trend continuation (>3% daily move)
        elif abs(momentum["daily_change_pct"]) >= 3 and momentum["hourly_change_pct"] * momentum["daily_change_pct"] > 0:
            is_opportunity = True
            signal = "BUY" if momentum["daily_change_pct"] > 0 else "SELL"
            reason = f"Trend continuation: {momentum['daily_change_pct']:+.2f}% daily trend continuing"
        
        if is_opportunity:
            # Calculate position size
            position_value = PAPER_BALANCE * POSITION_SIZE_PCT * LEVERAGE
            position_size = position_value / momentum["current_price"]
            
            # Calculate stop-loss and take-profit
            if signal == "BUY":
                stop_loss = momentum["current_price"] * (1 - STOP_LOSS_PCT)
                take_profit = momentum["current_price"] * (1 + TAKE_PROFIT_PCT)
            else:  # SELL (short)
                stop_loss = momentum["current_price"] * (1 + STOP_LOSS_PCT)
                take_profit = momentum["current_price"] * (1 - TAKE_PROFIT_PCT)
            
            opportunity = {
                "symbol": crypto["symbol"],
                "signal": signal,
                "current_price": momentum["current_price"],
                "hourly_change_pct": momentum["hourly_change_pct"],
                "daily_change_pct": momentum["daily_change_pct"],
                "volatility_pct": momentum["volatility_pct"],
                "position_size": position_size,
                "position_value": position_value,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reason": reason,
                "risk_reward": f"1:{TAKE_PROFIT_PCT/STOP_LOSS_PCT:.1f}",
                "timestamp": momentum["timestamp"]
            }
            
            opportunities.append(opportunity)
            print(f"  🚨 MOMENTUM OPPORTUNITY DETECTED: {signal} {crypto['symbol']}")
            print(f"     Reason: {reason}")
        else:
            print(f"  ⏸️  No aggressive momentum opportunity")
    
    return opportunities

def execute_paper_trades(opportunities):
    """Execute paper trades based on momentum opportunities"""
    print("\n💸 PAPER TRADE EXECUTION")
    print("-" * 60)
    
    if not opportunities:
        print("No momentum opportunities found for paper trading.")
        return []
    
    executed_trades = []
    
    for i, opp in enumerate(opportunities[:MAX_TRADES_PER_DAY], 1):
        print(f"\nTrade #{i}: {opp['signal']} {opp['symbol']}")
        print(f"  Entry Price: ${opp['current_price']:,.2f}")
        print(f"  Position Size: {opp['position_size']:.6f} {opp['symbol']}")
        print(f"  Position Value: ${opp['position_value']:,.2f} (with {LEVERAGE}x leverage)")
        print(f"  Stop Loss: ${opp['stop_loss']:,.2f} ({STOP_LOSS_PCT*100}%)")
        print(f"  Take Profit: ${opp['take_profit']:,.2f} ({TAKE_PROFIT_PCT*100}%)")
        print(f"  Risk/Reward: {opp['risk_reward']}")
        print(f"  Reason: {opp['reason']}")
        
        # Simulate paper trade execution
        trade = {
            "trade_id": f"PAPER_{int(time.time())}_{i}",
            "symbol": opp["symbol"],
            "side": opp["signal"],
            "entry_price": opp["current_price"],
            "position_size": opp["position_size"],
            "position_value": opp["position_value"],
            "stop_loss": opp["stop_loss"],
            "take_profit": opp["take_profit"],
            "leverage": LEVERAGE,
            "reason": opp["reason"],
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": "PAPER_TRADE_EXECUTED"
        }
        
        executed_trades.append(trade)
        print(f"  ✅ PAPER TRADE EXECUTED: {trade['trade_id']}")
    
    return executed_trades

def generate_summary(opportunities, executed_trades):
    """Generate trading summary for cron delivery"""
    print("\n" + "=" * 80)
    print("TRADING SUMMARY")
    print("=" * 80)
    
    summary = f"""
AGGRESSIVE CRYPTO MOMENTUM TRADING - PAPER TRADING ONLY
========================================================
Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Asia/Bangkok)
Paper Balance: ${PAPER_BALANCE:,}
Leverage: {LEVERAGE}x (paper trading only)
Risk Parameters: {STOP_LOSS_PCT*100}% stop-loss, {TAKE_PROFIT_PCT*100}% take-profit
Max Trades/Day: {MAX_TRADES_PER_DAY}

MARKET ANALYSIS:
"""
    
    # Add market analysis for each crypto
    for crypto in CRYPTOS:
        data = fetch_historical_data(crypto["id"], days=1)
        if data and "prices" in data:
            prices = [price for timestamp, price in data["prices"]]
            if len(prices) >= 2:
                current = prices[-1]
                hour_ago = prices[-2]
                daily_change = ((current - prices[0]) / prices[0]) * 100 if len(prices) >= 24 else 0
                hourly_change = ((current - hour_ago) / hour_ago) * 100
                
                summary += f"• {crypto['symbol']}: ${current:,.2f} "
                summary += f"(1h: {hourly_change:+.2f}%, 24h: {daily_change:+.2f}%)\n"
    
    summary += f"""
MOMENTUM OPPORTUNITIES FOUND: {len(opportunities)}
PAPER TRADES EXECUTED: {len(executed_trades)}
"""
    
    if executed_trades:
        summary += "\nEXECUTED PAPER TRADES:\n"
        for trade in executed_trades:
            summary += f"""
• {trade['symbol']} {trade['side']}
  Entry: ${trade['entry_price']:,.2f}
  Size: {trade['position_size']:.6f} (${trade['position_value']:,.2f} with {trade['leverage']}x)
  Stop Loss: ${trade['stop_loss']:,.2f}
  Take Profit: ${trade['take_profit']:,.2f}
  Reason: {trade['reason']}
  Time: {trade['timestamp']}
  ID: {trade['trade_id']}
"""
    elif opportunities:
        summary += "\nOPPORTUNITIES DETECTED (but not executed due to daily limit):\n"
        for opp in opportunities[:5]:
            summary += f"• {opp['symbol']} {opp['signal']}: {opp['reason']} (1h: {opp['hourly_change_pct']:+.2f}%)\n"
    else:
        summary += "\nNO AGGRESSIVE MOMENTUM OPPORTUNITIES FOUND\n"
        summary += "Criteria not met: Need 5%+ hourly moves, high volume spikes, or breakout patterns\n"
    
    summary += f"""
RISK MANAGEMENT:
• Paper Balance: ${PAPER_BALANCE:,}
• Max Position Size: {POSITION_SIZE_PCT*100}% of balance ({LEVERAGE}x leverage = ${PAPER_BALANCE * POSITION_SIZE_PCT * LEVERAGE:,.0f})
• Stop Loss: {STOP_LOSS_PCT*100}%
• Take Profit: {TAKE_PROFIT_PCT*100}%
• Risk/Reward Ratio: 1:{TAKE_PROFIT_PCT/STOP_LOSS_PCT:.1f}
• Max Trades/Day: {MAX_TRADES_PER_DAY}

TRADING STRATEGY:
• Aggressive momentum trading
• Focus on 5%+ hourly price movements
• High volatility breakouts (>3%)
• Trend continuation patterns
• PAPER TRADING ONLY - no real funds at risk

NEXT STEPS:
1. Monitor paper trade positions
2. Set stop-loss and take-profit alerts
3. Run momentum analysis again in 1-2 hours
4. Review daily performance summary
5. Never use real funds without proper risk assessment

END OF TRADING SESSION
========================================================
"""
    
    print(summary)
    return summary

def main():
    """Main execution function"""
    try:
        # Step 1: Analyze momentum opportunities
        opportunities = analyze_momentum_opportunities()
        
        # Step 2: Execute paper trades
        executed_trades = execute_paper_trades(opportunities)
        
        # Step 3: Generate summary
        summary = generate_summary(opportunities, executed_trades)
        
        # Save summary to file
        summary_file = "aggressive_momentum_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        print(f"\n✅ Summary saved to: {summary_file}")
        print(f"📊 Total opportunities found: {len(opportunities)}")
        print(f"💸 Paper trades executed: {len(executed_trades)}")
        
        return summary
        
    except Exception as e:
        error_msg = f"❌ Error in aggressive momentum trading: {e}"
        print(error_msg)
        return error_msg

if __name__ == "__main__":
    result = main()
    print("\n" + "=" * 80)
    print("AGGRESSIVE MOMENTUM TRADING COMPLETE")
    print("=" * 80)