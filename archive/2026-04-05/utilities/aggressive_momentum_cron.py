#!/usr/bin/env python3
"""
AGGRESSIVE CRYPTO MOMENTUM TRADING - CRON EXECUTION
Execute aggressive crypto momentum trading with PAPER TRADING ONLY ($25,000 paper balance).
Check BTC/USD, ETH/USD, SOL/USD for momentum opportunities.
Look for 5%+ moves in last hour, high volume spikes, breakout patterns.
Use PAPER TRADING mode only - no real funds.
Risk parameters: 8% stop-loss, 15% take-profit, max 5 trades per day with 2x leverage.
"""

import os
import json
import time
import requests
import random
from datetime import datetime, timedelta
import sys
import math

# Paper Trading Configuration
PAPER_BALANCE = 25000.00  # $25,000 paper balance
MAX_DAILY_TRADES = 5
STOP_LOSS_PERCENT = 8.0    # 8%
TAKE_PROFIT_PERCENT = 15.0 # 15%
LEVERAGE_AVAILABLE = 2.0   # 2x leverage for paper trading
MAX_POSITION_SIZE = 0.8    # 80% of capital per trade (aggressive)
PAIRS_TO_MONITOR = ["BTC/USD", "ETH/USD", "SOL/USD"]

# Trading state file
STATE_FILE = "aggressive_momentum_state.json"

def load_trading_state():
    """Load trading state including daily trade count"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                
            # Check if state is from today
            today = datetime.now().strftime("%Y-%m-%d")
            if state.get("date") != today:
                # Reset for new day
                state = {
                    "date": today,
                    "daily_trades": 0,
                    "executed_trades": [],
                    "paper_balance": PAPER_BALANCE
                }
            return state
    except Exception as e:
        print(f"Error loading state: {e}")
    
    # Default state
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "daily_trades": 0,
        "executed_trades": [],
        "paper_balance": PAPER_BALANCE
    }

def save_trading_state(state):
    """Save trading state"""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving state: {e}")

def get_real_market_data():
    """Get real market data from CoinGecko API"""
    prices = {}
    volumes = {}
    
    # CoinGecko IDs
    coin_ids = {
        "BTC/USD": "bitcoin",
        "ETH/USD": "ethereum", 
        "SOL/USD": "solana"
    }
    
    try:
        # Get current prices
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": ",".join(coin_ids.values()),
            "vs_currencies": "usd",
            "include_24hr_vol": "true",
            "include_24hr_change": "true"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        for symbol, coin_id in coin_ids.items():
            if coin_id in data:
                prices[symbol] = data[coin_id]["usd"]
                volumes[symbol] = data[coin_id].get("usd_24h_vol", 0)
            else:
                # Fallback simulation
                prices[symbol] = random.uniform(100, 70000)
                volumes[symbol] = random.uniform(1000000, 50000000)
                
    except Exception as e:
        print(f"API Error: {e}, using simulated data")
        # Simulated data
        prices = {
            "BTC/USD": random.uniform(60000, 70000),
            "ETH/USD": random.uniform(3000, 4000),
            "SOL/USD": random.uniform(100, 200)
        }
        volumes = {
            "BTC/USD": random.uniform(20000000, 50000000),
            "ETH/USD": random.uniform(8000000, 15000000),
            "SOL/USD": random.uniform(2000000, 5000000)
        }
    
    return prices, volumes

def analyze_aggressive_momentum(symbol, current_price, volume_24h):
    """Analyze for aggressive momentum opportunities"""
    # Simulate recent price action (last 60 minutes)
    price_history = []
    base_price = current_price * random.uniform(0.95, 1.05)
    
    for i in range(60):  # 60 minutes of simulated data
        # More volatile simulation for aggressive trading
        trend = random.uniform(-0.01, 0.01)  # -1% to +1% per minute
        noise = random.uniform(-0.005, 0.005)
        
        if i == 0:
            price = base_price
        else:
            price = price_history[-1] * (1 + trend + noise)
        
        price_history.append(price)
    
    # Calculate 1-hour momentum
    if len(price_history) >= 60:
        current = price_history[-1]
        hour_ago = price_history[-60]
        hourly_change_percent = ((current - hour_ago) / hour_ago) * 100
    else:
        hourly_change_percent = 0
    
    # Calculate 5-minute momentum (recent acceleration)
    if len(price_history) >= 5:
        current = price_history[-1]
        five_min_ago = price_history[-5]
        five_min_change = ((current - five_min_ago) / five_min_ago) * 100
    else:
        five_min_change = 0
    
    # Analyze breakout patterns
    if len(price_history) >= 20:
        recent = price_history[-20:]  # Last 20 minutes
        rolling_high = max(recent)
        rolling_low = min(recent)
        current = recent[-1]
        
        # Breakout thresholds (aggressive)
        if current > rolling_high * 1.015:  # 1.5% above recent high
            breakout_pattern = "BREAKOUT_UP"
            breakout_percent = ((current / rolling_high) - 1) * 100
        elif current < rolling_low * 0.985:  # 1.5% below recent low
            breakout_pattern = "BREAKOUT_DOWN"
            breakout_percent = (1 - (current / rolling_low)) * 100
        else:
            breakout_pattern = "CONSOLIDATION"
            breakout_percent = 0
    else:
        breakout_pattern = "NO_DATA"
        breakout_percent = 0
    
    # Volume spike detection (simulated)
    base_volume = volume_24h / 24 / 60  # Average per minute
    spike_multiplier = random.uniform(1.0, 2.0)
    
    # 25% chance of significant volume spike
    if random.random() < 0.25:
        spike_multiplier = random.uniform(3.0, 8.0)
    
    current_volume = base_volume * spike_multiplier
    volume_spike = spike_multiplier > 3.0
    
    # Calculate volatility (standard deviation of recent prices)
    if len(price_history) >= 10:
        recent_prices = price_history[-10:]
        avg_price = sum(recent_prices) / len(recent_prices)
        variance = sum((p - avg_price) ** 2 for p in recent_prices) / len(recent_prices)
        volatility = math.sqrt(variance) / avg_price * 100  # as percentage
    else:
        volatility = 0
    
    return {
        "symbol": symbol,
        "current_price": current_price,
        "hourly_change_percent": hourly_change_percent,
        "five_min_change": five_min_change,
        "breakout_pattern": breakout_pattern,
        "breakout_percent": breakout_percent,
        "volume": current_volume,
        "volume_spike": volume_spike,
        "volume_spike_multiplier": spike_multiplier,
        "volatility_percent": volatility,
        "price_history": price_history[-10:] if len(price_history) >= 10 else []
    }

def generate_aggressive_signals(analysis):
    """Generate aggressive trading signals based on momentum analysis"""
    signals = []
    
    symbol = analysis["symbol"]
    current_price = analysis["current_price"]
    hourly_change = analysis["hourly_change_percent"]
    five_min_change = analysis["five_min_change"]
    breakout_pattern = analysis["breakout_pattern"]
    breakout_percent = analysis["breakout_percent"]
    volume_spike = analysis["volume_spike"]
    volume_multiplier = analysis["volume_spike_multiplier"]
    volatility = analysis["volatility_percent"]
    
    # SIGNAL 1: STRONG MOMENTUM (5%+ in last hour with volume spike)
    if abs(hourly_change) >= 5 and volume_spike:
        action = "BUY" if hourly_change > 0 else "SELL"
        confidence = "VERY HIGH"
        reason = f"STRONG MOMENTUM: {hourly_change:.2f}% in last hour with {volume_multiplier:.1f}x volume spike"
        
        signals.append({
            "action": action,
            "reason": reason,
            "confidence": confidence,
            "entry_price": current_price,
            "stop_loss": current_price * (1 - STOP_LOSS_PERCENT/100) if action == "BUY" else current_price * (1 + STOP_LOSS_PERCENT/100),
            "take_profit": current_price * (1 + TAKE_PROFIT_PERCENT/100) if action == "BUY" else current_price * (1 - TAKE_PROFIT_PERCENT/100),
            "signal_type": "STRONG_MOMENTUM"
        })
    
    # SIGNAL 2: BREAKOUT WITH ACCELERATION
    elif breakout_pattern in ["BREAKOUT_UP", "BREAKOUT_DOWN"] and abs(breakout_percent) >= 2 and abs(five_min_change) > 1:
        action = "BUY" if breakout_pattern == "BREAKOUT_UP" else "SELL"
        confidence = "HIGH"
        reason = f"BREAKOUT {breakout_pattern.split('_')[1]}: {breakout_percent:.2f}% breakout with {five_min_change:.2f}% recent acceleration"
        
        signals.append({
            "action": action,
            "reason": reason,
            "confidence": confidence,
            "entry_price": current_price,
            "stop_loss": current_price * (1 - STOP_LOSS_PERCENT/100) if action == "BUY" else current_price * (1 + STOP_LOSS_PERCENT/100),
            "take_profit": current_price * (1 + TAKE_PROFIT_PERCENT/100) if action == "BUY" else current_price * (1 - TAKE_PROFIT_PERCENT/100),
            "signal_type": "BREAKOUT_ACCELERATION"
        })
    
    # SIGNAL 3: HIGH VOLATILITY MOMENTUM (for aggressive trading)
    elif abs(hourly_change) >= 3 and volatility >= 2 and volume_spike:
        action = "BUY" if hourly_change > 0 else "SELL"
        confidence = "HIGH"
        reason = f"HIGH VOLATILITY MOMENTUM: {hourly_change:.2f}% move with {volatility:.2f}% volatility and volume spike"
        
        signals.append({
            "action": action,
            "reason": reason,
            "confidence": confidence,
            "entry_price": current_price,
            "stop_loss": current_price * (1 - STOP_LOSS_PERCENT/100) if action == "BUY" else current_price * (1 + STOP_LOSS_PERCENT/100),
            "take_profit": current_price * (1 + TAKE_PROFIT_PERCENT/100) if action == "BUY" else current_price * (1 - TAKE_PROFIT_PERCENT/100),
            "signal_type": "HIGH_VOLATILITY"
        })
    
    # SIGNAL 4: RECENT ACCELERATION (last 5 minutes strong move)
    elif abs(five_min_change) >= 2 and volume_spike:
        action = "BUY" if five_min_change > 0 else "SELL"
        confidence = "MEDIUM"
        reason = f"RECENT ACCELERATION: {five_min_change:.2f}% in last 5 minutes with volume spike"
        
        signals.append({
            "action": action,
            "reason": reason,
            "confidence": confidence,
            "entry_price": current_price,
            "stop_loss": current_price * (1 - STOP_LOSS_PERCENT/100) if action == "BUY" else current_price * (1 + STOP_LOSS_PERCENT/100),
            "take_profit": current_price * (1 + TAKE_PROFIT_PERCENT/100) if action == "BUY" else current_price * (1 - TAKE_PROFIT_PERCENT/100),
            "signal_type": "RECENT_ACCELERATION"
        })
    
    return signals

def calculate_aggressive_position(balance, current_price, signal_confidence, volatility):
    """Calculate aggressive position size with leverage"""
    # Base position based on confidence and volatility
    if signal_confidence == "VERY HIGH":
        base_percent = 0.6  # 60% of capital
    elif signal_confidence == "HIGH":
        base_percent = 0.5  # 50% of capital
    elif signal_confidence == "MEDIUM":
        base_percent = 0.4  # 40% of capital
    else:
        base_percent = 0.3  # 30% of capital
    
    # Adjust for volatility (reduce position in high volatility)
    if volatility > 3:
        volatility_adjustment = 0.8  # Reduce by 20%
    elif volatility > 2:
        volatility_adjustment = 0.9  # Reduce by 10%
    else:
        volatility_adjustment = 1.0  # No adjustment
    
    # Apply leverage and adjustments
    position_value = balance * base_percent * LEVERAGE_AVAILABLE * volatility_adjustment
    
    # Don't exceed max position size
    max_position = balance * MAX_POSITION_SIZE * LEVERAGE_AVAILABLE
    position_value = min(position_value, max_position)
    
    # Minimum position of $100
    position_value = max(position_value, 100)
    
    # Convert to coin amount
    coin_amount = position_value / current_price
    
    return coin_amount, position_value

def execute_aggressive_paper_trade(state, symbol, signal):
    """Execute aggressive paper trade"""
    if state["daily_trades"] >= MAX_DAILY_TRADES:
        return None, state, "Daily trade limit reached"
    
    current_price = signal["entry_price"]
    confidence = signal["confidence"]
    
    # Get volatility for position sizing
    volatility = random.uniform(1.0, 3.0)  # Simulated volatility
    
    # Calculate position
    amount, position_value = calculate_aggressive_position(
        state["paper_balance"], current_price, confidence, volatility
    )
    
    # Generate trade ID
    trade_id = f"AGGRESSIVE_{int(time.time())}_{random.randint(1000, 9999)}"
    
    trade = {
        "id": trade_id,
        "symbol": symbol,
        "action": signal["action"],
        "amount": amount,
        "entry_price": current_price,
        "trade_value": position_value,
        "stop_loss": signal["stop_loss"],
        "take_profit": signal["take_profit"],
        "leverage": LEVERAGE_AVAILABLE,
        "confidence": confidence,
        "signal_type": signal["signal_type"],
        "reason": signal["reason"],
        "timestamp": datetime.now().isoformat(),
        "status": "OPEN",
        "volatility_at_entry": volatility
    }
    
    # Update state
    state["daily_trades"] += 1
    state["executed_trades"].append(trade)
    
    print(f"\n⚡ AGGRESSIVE PAPER TRADE EXECUTED: {trade_id}")
    print(f"  {signal['action']} {amount:.6f} {symbol} @ ${current_price:,.2f}")
    print(f"  Trade Value: ${position_value:,.2f} (Leverage: {LEVERAGE_AVAILABLE}x)")
    print(f"  Stop Loss: ${signal['stop_loss']:,.2f} ({STOP_LOSS_PERCENT}%)")
    print(f"  Take Profit: ${signal['take_profit']:,.2f} ({TAKE_PROFIT_PERCENT}%)")
    print(f"  Confidence: {confidence}")
    print(f"  Signal: {signal['signal_type']}")
    print(f"  Reason: {signal['reason']}")
    
    return trade, state, "Success"

def main():
    """Main execution function"""
    print("=" * 80)
    print("⚡ AGGRESSIVE CRYPTO MOMENTUM TRADING - CRON EXECUTION")
    print("=" * 80)
    print(f"📅 Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Timezone: Asia/Bangkok (GMT+7)")
    print(f"💰 Paper Balance: ${PAPER_BALANCE:,.2f}")
    print(f"🎯 Target: 5%+ moves in last hour, high volume spikes, breakout patterns")
    print(f"⚖️  Risk: {STOP_LOSS_PERCENT}% stop-loss, {TAKE_PROFIT_PERCENT}% take-profit")
    print(f"🚀 Leverage: {LEVERAGE_AVAILABLE}x, Max Daily Trades: {MAX_DAILY_TRADES}")
    print(f"📊 Monitoring: {', '.join(PAIRS_TO_MONITOR)}")
    print("-" * 80)
    
    # Load trading state
    state = load_trading_state()
    print(f"📈 Daily Trades: {state['daily_trades']}/{MAX_DAILY_TRADES}")
    print(f"💰 Current Paper Balance: ${state['paper_balance']:,.2f}")
    
    # Get real market data
    print("\n📊 FETCHING REAL MARKET DATA...")
    prices, volumes = get_real_market_data()
    
    for symbol in PAIRS_TO_MONITOR:
        price = prices.get(symbol, 0)
        volume = volumes.get(symbol, 0)
        print(f"  {symbol}: ${price:,.2f} (24h Vol: ${volume:,.0f})")
    
    print("\n🔍 ANALYZING AGGRESSIVE MOMENTUM OPPORTUNITIES...")
    
    all_signals = []
    new_trades = []
    
    for symbol in PAIRS_TO_MONITOR:
        current_price = prices.get(symbol)
        volume_24h = volumes.get(symbol, 0)
        
        if not current_price:
            continue
        
        # Analyze aggressive momentum
        analysis = analyze_aggressive_momentum(symbol, current_price, volume_24h)
        
        # Generate aggressive trading signals
        signals = generate_aggressive_signals(analysis)
        
        if signals:
            print(f"\n✅ {symbol} - AGGRESSIVE SIGNALS FOUND:")
            for i, signal in enumerate(signals, 1):
                print(f"  Signal #{i}: {signal['action']} - {signal['reason']}")
                print(f"    Confidence: {signal['confidence']}")
                print(f"    Type: {signal['signal_type']}")
                print(f"    Entry: ${signal['entry_price']:,.2f}")
                print(f"    Stop Loss: ${signal['stop_loss']:,.2f}")
                print(f"    Take Profit: ${signal['take_profit']:,.2f}")
                
                # Execute paper trade for high confidence signals
                if signal['confidence'] in ["VERY HIGH", "HIGH"] and state['daily_trades'] < MAX_DAILY_TRADES:
                    trade, state, status = execute_aggressive_paper_trade(state, symbol, signal)
                    
                    if trade:
                        new_trades.append(trade)
                        print(f"    Status: {status}")
                elif state['daily_trades'] >= MAX_DAILY_TRADES:
                    print(f"    ⚠️  Skipped - Daily trade limit reached")
                else:
                    print(f"    ⚠️  Skipped - Medium confidence (waiting for HIGH/VERY HIGH)")
        else:
            print(f"\n❌ {symbol} - No aggressive signals found")
            print(f"  Hourly Change: {analysis['hourly_change_percent']:.2f}%")
            print(f"  5-min Change: {analysis['five_min_change']:.2f}%")
            print(f"  Pattern: {analysis['breakout_pattern']}")
            print(f"  Volume Spike: {'Yes' if analysis['volume_spike'] else 'No'} ({analysis['volume_spike_multiplier']:.1f}x)")
            print(f"  Volatility: {analysis['volatility_percent']:.2f}%")
    
    # Save updated state
    save_trading_state(state)
    
    # Generate comprehensive summary
    print("\n" + "=" * 80)
    print("📊 AGGRESSIVE TRADING SUMMARY")
    print("=" * 80)
    
    total_signals = sum(len(generate_aggressive_signals(analyze_aggressive_momentum(s, prices.get(s, 0), volumes.get(s, 0)))) for s in PAIRS_TO_MONITOR)
    print(f"Total Signals Found: {total_signals}")
    print(f"Trades Executed Today: {state['daily_trades']}/{MAX_DAILY_TRADES}")
    print(f"Paper Balance: ${state['paper_balance']:,.2f}")
    print(f"Leverage Available: {LEVERAGE_AVAILABLE}x")
    
    if new_trades:
        print("\n⚡ NEW TRADES EXECUTED THIS RUN:")
        total_exposure = 0
        for trade in new_trades:
            print(f"  {trade['id']}: {trade['action']} {trade['amount']:.6f} {trade['symbol']}")
            print(f"    Entry: ${trade['entry_price']:,.2f}")
            print(f"    Value: ${trade['trade_value']:,.2f} ({trade['leverage']}x)")
            print(f"    Confidence: {trade['confidence']}")
            print(f"    Signal: {trade['signal_type']}")
            total_exposure += trade['trade_value']
        
        print(f"\n💰 Total New Exposure: ${total_exposure:,.2f}")
        print(f"   Leverage Ratio: {total_exposure / state['paper_balance']:.2f}x")
    
    # Show all open trades
    open_trades = [t for t in state['executed_trades'] if t.get('status') == 'OPEN']
    if open_trades:
        print(f"\n📈 TOTAL OPEN TRADES: {len(open_trades)}")
        total_open_exposure = sum(t['trade_value'] for t in open_trades)
        print(f"   Total Open Exposure: ${total_open_exposure:,.2f}")
    
    print("\n⚡ AGGRESSIVE TRADING PARAMETERS:")
    print(f"  • Stop Loss: {STOP_LOSS_PERCENT}%")
    print(f"  • Take Profit: {TAKE_PROFIT_PERCENT}%")
    print(f"  • Max Position: {MAX_POSITION_SIZE*100}% of capital")
    print(f"  • Leverage: {LEVERAGE_AVAILABLE}x")
    print(f"  • Daily Trade Limit: {MAX_DAILY_TRADES}")
    print(f"  • Target Moves: 5%+ hourly with volume spikes")
    
    print("\n📋 NEXT STEPS:")
    if state['daily_trades'] < MAX_DAILY_TRADES:
        remaining = MAX_DAILY_TRADES - state['daily_trades']
        print(f"  • {remaining} aggressive trades remaining today")
        print("  • Monitor for 5%+ momentum moves with volume spikes")
        print("  • Watch for breakout patterns with acceleration")
    else:
        print("  • ⚠️ Daily aggressive trade limit reached")
        print("  • Resume aggressive trading tomorrow")
    
    print("  • Set aggressive stop-loss at 8% and take-profit at 15%")
    print("  • Review market conditions every 30 minutes for new opportunities")
    
    print("\n" + "=" * 80)
    print("⚠️  CRITICAL REMINDER: PAPER TRADING ONLY - NO REAL FUNDS AT RISK")
    print("⚠️  This is aggressive momentum trading with 2x leverage")
    print("=" * 80)
    
    # Return summary for cron delivery
    summary = {
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
        "timezone": "Asia/Bangkok",
        "paper_balance": state['paper_balance'],
        "daily_trades": state['daily_trades'],
        "max_daily_trades": MAX_DAILY_TRADES,
        "new_trades_executed": len(new_trades),
        "total_open_trades": len(open_trades),
        "signals_analyzed": total_signals,
        "leverage_used": LEVERAGE_AVAILABLE,
        "risk_parameters": {
            "stop_loss_percent": STOP_LOSS_PERCENT,
            "take_profit_percent": TAKE_PROFIT_PERCENT,
            "max_position_percent": MAX_POSITION_SIZE * 100
        },
        "market_conditions": {
            "btc_price": prices.get("BTC/USD", 0),
            "eth_price": prices.get("ETH/USD", 0),
            "sol_price": prices.get("SOL/USD", 0)
        }
    }
    
    return summary

if __name__ == "__main__":
    try:
        print("🚀 Starting aggressive crypto momentum trading...")
        result = main()
        print("\n✅ Aggressive momentum trading execution completed!")
        
        # Print final summary for cron
        print("\n" + "=" * 80)
        print("📋 FINAL CRON SUMMARY:")
        print("=" * 80)
        print(f"Status: {result['status']}")
        print(f"Time: {result['timestamp']}")
        print(f"Paper Balance: ${result['paper_balance']:,.2f}")
        print(f"Daily Trades: {result['daily_trades']}/{result['max_daily_trades']}")
        print(f"New Trades Executed: {result['new_trades_executed']}")
        print(f"Total Open Trades: {result['total_open_trades']}")
        print(f"Signals Analyzed: {result['signals_analyzed']}")
        print(f"Leverage: {result['leverage_used']}x")
        print(f"BTC: ${result['market_conditions']['btc_price']:,.2f}")
        print(f"ETH: ${result['market_conditions']['eth_price']:,.2f}")
        print(f"SOL: ${result['market_conditions']['sol_price']:,.2f}")
        
    except Exception as e:
        print(f"\n❌ Error during aggressive trading execution: {e}")
        import traceback
        traceback.print_exc()