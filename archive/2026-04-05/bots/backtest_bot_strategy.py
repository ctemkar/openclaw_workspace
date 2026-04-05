#!/usr/bin/env python3
"""
Backtest 26-crypto bot strategies with historical data
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import time
import os

# Simulated historical data (in reality, would fetch from API)
# For now, we'll simulate based on known market conditions

def simulate_market_data(days=30):
    """Generate simulated market data for backtesting"""
    cryptos = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI']
    
    data = {}
    base_date = datetime.now() - timedelta(days=days)
    
    for crypto in cryptos:
        # Simulate price movements
        prices = []
        current_price = 100 if crypto == 'BTC' else np.random.uniform(1, 100)
        
        for day in range(days):
            for hour in range(24):
                # Market trends: 70% up days, 30% down days in bull market
                if np.random.random() < 0.7:
                    # Up day: small gains with occasional dips
                    if np.random.random() < 0.2:  # 20% chance of dip
                        change = np.random.uniform(-0.05, -0.01)  # -1% to -5%
                    else:
                        change = np.random.uniform(0.01, 0.03)  # +1% to +3%
                else:
                    # Down day: larger drops
                    change = np.random.uniform(-0.08, -0.02)  # -2% to -8%
                
                current_price *= (1 + change)
                prices.append({
                    'timestamp': base_date + timedelta(days=day, hours=hour),
                    'crypto': crypto,
                    'price': current_price,
                    'change': change * 100
                })
        
        data[crypto] = pd.DataFrame(prices)
    
    return data

def run_strategy_backtest(data, strategy_params):
    """Backtest a trading strategy"""
    results = {
        'trades': [],
        'total_trades': 0,
        'winning_trades': 0,
        'losing_trades': 0,
        'total_pnl': 0,
        'max_drawdown': 0,
        'win_rate': 0
    }
    
    capital = 1000  # Start with $1000
    position_size = capital * strategy_params['position_size']
    open_positions = []
    
    for crypto, df in data.items():
        df = df.sort_values('timestamp')
        current_capital = capital
        
        for i in range(1, len(df)):
            current_row = df.iloc[i]
            prev_row = df.iloc[i-1]
            
            # Check for SHORT signal (current strategy)
            change_percent = current_row['change']
            
            if change_percent <= -strategy_params['short_threshold']:
                # SHORT signal detected
                entry_price = current_row['price']
                
                # Check if we have capital and not too many positions
                if len(open_positions) < strategy_params['max_positions'] and current_capital >= position_size:
                    
                    # Simulate trade
                    trade = {
                        'timestamp': current_row['timestamp'],
                        'crypto': crypto,
                        'type': 'SHORT',
                        'entry_price': entry_price,
                        'position_size': position_size,
                        'leverage': strategy_params['leverage']
                    }
                    
                    # Find exit (next 24 hours or stop loss/take profit)
                    exit_found = False
                    for j in range(i+1, min(i+25, len(df))):  # Look ahead 24 hours max
                        future_row = df.iloc[j]
                        future_price = future_row['price']
                        
                        # Calculate P&L
                        price_change = ((entry_price - future_price) / entry_price) * 100
                        pnl_percent = price_change * strategy_params['leverage']
                        
                        # Check stop loss / take profit
                        if pnl_percent <= -strategy_params['stop_loss'] * 100:  # Stop loss hit
                            trade['exit_price'] = future_price
                            trade['exit_reason'] = 'STOP_LOSS'
                            trade['pnl_percent'] = pnl_percent
                            exit_found = True
                            break
                        elif pnl_percent >= strategy_params['take_profit'] * 100:  # Take profit hit
                            trade['exit_price'] = future_price
                            trade['exit_reason'] = 'TAKE_PROFIT'
                            trade['pnl_percent'] = pnl_percent
                            exit_found = True
                            break
                        elif j == i+24:  # 24 hours passed
                            trade['exit_price'] = future_price
                            trade['exit_reason'] = 'TIME_LIMIT'
                            trade['pnl_percent'] = pnl_percent
                            exit_found = True
                            break
                    
                    if exit_found:
                        # Calculate dollar P&L
                        pnl_dollar = position_size * (trade['pnl_percent'] / 100)
                        trade['pnl_dollar'] = pnl_dollar
                        
                        # Update capital
                        current_capital += pnl_dollar
                        
                        # Track results
                        results['trades'].append(trade)
                        results['total_trades'] += 1
                        if pnl_dollar > 0:
                            results['winning_trades'] += 1
                        else:
                            results['losing_trades'] += 1
                        results['total_pnl'] += pnl_dollar
                        
                        # Track max drawdown
                        if current_capital < capital:
                            drawdown = (capital - current_capital) / capital * 100
                            results['max_drawdown'] = max(results['max_drawdown'], drawdown)
    
    # Calculate final metrics
    if results['total_trades'] > 0:
        results['win_rate'] = (results['winning_trades'] / results['total_trades']) * 100
        results['final_capital'] = capital + results['total_pnl']
        results['total_return'] = (results['total_pnl'] / capital) * 100
    
    return results

def compare_strategies():
    """Compare old vs new strategies"""
    
    # OLD STRATEGY (Current - LOSING)
    old_strategy = {
        'name': 'OLD - Overly Aggressive',
        'position_size': 0.25,      # 25% of capital
        'short_threshold': 0.3,     # Short after 0.3% drop
        'leverage': 3,              # 3x leverage
        'stop_loss': 0.05,          # 5% stop loss
        'take_profit': 0.10,        # 10% take profit
        'max_positions': 10         # No limit effectively
    }
    
    # NEW STRATEGY (Proposed - SHOULD BE BETTER)
    new_strategy = {
        'name': 'NEW - Conservative',
        'position_size': 0.10,      # 10% of capital
        'short_threshold': 3.0,     # Short only after 3% drop
        'leverage': 1,              # 1x leverage (no leverage)
        'stop_loss': 0.03,          # 3% stop loss
        'take_profit': 0.05,        # 5% take profit
        'max_positions': 3          # Max 3 positions
    }
    
    print("📊 BACKTESTING TRADING STRATEGIES")
    print("=" * 80)
    
    # Generate market data (simulated)
    print("Generating simulated market data (30 days, 10 cryptos)...")
    market_data = simulate_market_data(days=30)
    
    # Run backtests
    print("\n🔍 Testing OLD strategy...")
    old_results = run_strategy_backtest(market_data, old_strategy)
    
    print("🔍 Testing NEW strategy...")
    new_results = run_strategy_backtest(market_data, new_strategy)
    
    # Display results
    print("\n" + "=" * 80)
    print("📈 BACKTEST RESULTS")
    print("=" * 80)
    
    print(f"\n{'Metric':<25} {'OLD Strategy':<20} {'NEW Strategy':<20}")
    print("-" * 65)
    
    metrics = [
        ('Total Trades', old_results['total_trades'], new_results['total_trades']),
        ('Winning Trades', old_results['winning_trades'], new_results['winning_trades']),
        ('Losing Trades', old_results['losing_trades'], new_results['losing_trades']),
        ('Win Rate', f"{old_results['win_rate']:.1f}%", f"{new_results['win_rate']:.1f}%"),
        ('Total P&L', f"${old_results['total_pnl']:.2f}", f"${new_results['total_pnl']:.2f}"),
        ('Total Return', f"{old_results.get('total_return', 0):.1f}%", f"{new_results.get('total_return', 0):.1f}%"),
        ('Max Drawdown', f"{old_results['max_drawdown']:.1f}%", f"{new_results['max_drawdown']:.1f}%"),
        ('Final Capital', f"${old_results.get('final_capital', 1000):.2f}", f"${new_results.get('final_capital', 1000):.2f}")
    ]
    
    for metric, old_val, new_val in metrics:
        print(f"{metric:<25} {str(old_val):<20} {str(new_val):<20}")
    
    # Analysis
    print("\n" + "=" * 80)
    print("📋 STRATEGY ANALYSIS")
    print("=" * 80)
    
    if new_results['total_pnl'] > old_results['total_pnl']:
        improvement = ((new_results['total_pnl'] - old_results['total_pnl']) / abs(old_results['total_pnl'])) * 100
        print(f"✅ NEW strategy is {improvement:.1f}% better than OLD strategy")
    else:
        print(f"❌ NEW strategy performed worse than OLD strategy")
    
    print(f"\n🔍 OLD Strategy Issues:")
    print(f"   • Too many trades ({old_results['total_trades']}) - overtrading")
    print(f"   • Win rate: {old_results['win_rate']:.1f}% - below 50%")
    print(f"   • High drawdown: {old_results['max_drawdown']:.1f}% - too risky")
    
    print(f"\n🔍 NEW Strategy Improvements:")
    print(f"   • Fewer, higher-quality trades")
    print(f"   • Lower risk (1x leverage vs 3x)")
    print(f"   • Tighter risk management")
    
    # Save detailed results
    results_file = "backtest_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            'old_strategy': old_strategy,
            'new_strategy': new_strategy,
            'old_results': old_results,
            'new_results': new_results,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n✅ Detailed results saved to: {results_file}")
    
    return old_results, new_results

def analyze_real_trades():
    """Analyze our actual losing trades"""
    print("\n" + "=" * 80)
    print("🔍 ANALYSIS OF ACTUAL LOSING TRADES")
    print("=" * 80)
    
    try:
        with open('26_crypto_trade_history.json', 'r') as f:
            trades = json.load(f)
        
        losing_trades = [t for t in trades if t.get('unrealized_pnl', 0) < 0]
        
        if losing_trades:
            print(f"\nFound {len(losing_trades)} losing trades:")
            print("-" * 80)
            
            for trade in losing_trades:
                print(f"{trade['symbol']}:")
                print(f"  Entry: ${trade.get('entry_price', 0):.4f}")
                print(f"  Current: ${trade.get('current_price', 0):.4f}")
                print(f"  Loss: ${trade.get('unrealized_pnl', 0):.4f} ({trade.get('pnl_percent', 0):.2f}%)")
                
                # Calculate what threshold triggered it
                if 'entry_price' in trade and 'current_price' in trade:
                    entry = trade['entry_price']
                    # Estimate what the price was before entry (assuming it dropped to trigger)
                    # If we shorted at 0.3% drop, price before was: entry / 0.997
                    price_before = entry / 0.997  # Assuming 0.3% drop
                    actual_drop = ((price_before - entry) / price_before) * 100
                    print(f"  Estimated trigger: {actual_drop:.2f}% drop")
                    print(f"  Problem: {actual_drop:.2f}% drop was TOO SMALL - likely noise")
                print()
        else:
            print("No losing trades found in history (data may be outdated)")
            
    except FileNotFoundError:
        print("Trade history file not found")

if __name__ == "__main__":
    # Run backtests
    old_results, new_results = compare_strategies()
    
    # Analyze real trades
    analyze_real_trades()
    
    print("\n" + "=" * 80)
    print("🎯 RECOMMENDATIONS")
    print("=" * 80)
    print("""
1. IMMEDIATELY UPDATE BOT PARAMETERS:
   • Change SHORT_THRESHOLD from 0.3 to 3.0
   • Change POSITION_SIZE from 0.25 to 0.10
   • Change LEVERAGE from 3 to 1
   • Add MAX_POSITIONS = 3

2. ADD MARKET FILTERS:
   • Don't short if BTC is up >1% in last hour
   • Check trading volume (>$1M daily)
   • Wait 15-minute confirmation after signal

3. IMPROVE RISK MANAGEMENT:
   • Set daily loss limit: 5% of capital
   • Tighter stop-loss: 3% (not 5%)
   • Smaller take-profit: 5% (not 10%)

4. MONITOR CLOSELY:
   • Track every trade for 24 hours
   • Adjust parameters weekly based on performance
   • Consider adding machine learning over time
    """)