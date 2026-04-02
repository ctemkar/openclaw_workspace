#!/usr/bin/env python3
"""
RESTORE INVESTMENT TRACKING
Show TOTAL investment amount and REAL cumulative P&L
"""

import json
import os
from datetime import datetime

print("="*70)
print("💰 RESTORING INVESTMENT TRACKING - TOTAL MONEY INVESTED")
print("="*70)

def calculate_total_investment():
    """Calculate total money invested from all historical trades"""
    backup_file = 'trading_data/trades_backup.json'
    
    if not os.path.exists(backup_file):
        print("❌ No backup trades found")
        return 0, 0, 0
    
    with open(backup_file, 'r') as f:
        trades = json.load(f)
    
    total_investment = 0
    total_withdrawn = 0
    gemini_investment = 0
    binance_investment = 0
    
    for trade in trades:
        exchange = trade.get('exchange', '')
        side = trade.get('side', '')
        price = trade.get('price', 0)
        amount = trade.get('amount', 0)
        
        trade_value = price * amount
        
        if side == 'buy':
            total_investment += trade_value
            if exchange == 'gemini':
                gemini_investment += trade_value
            elif exchange == 'binance':
                binance_investment += trade_value
        elif side == 'sell':
            total_withdrawn += trade_value
    
    net_investment = total_investment - total_withdrawn
    
    return total_investment, total_withdrawn, net_investment, gemini_investment, binance_investment

def get_current_portfolio_value():
    """Get current portfolio value from updated trades.json"""
    with open('trading_data/trades.json', 'r') as f:
        trades = json.load(f)
    
    current_value = 0
    cash_value = 0
    position_value = 0
    
    for trade in trades:
        value = trade.get('value', 0)
        symbol = trade.get('symbol', '')
        
        if 'USD/CASH' in symbol or 'CASH' in symbol:
            cash_value += value
        else:
            position_value += value
        
        current_value += value
    
    return current_value, cash_value, position_value

def main():
    # Calculate total investment
    total_invested, total_withdrawn, net_invested, gemini_invested, binance_invested = calculate_total_investment()
    
    # Get current value
    current_value, cash_value, position_value = get_current_portfolio_value()
    
    # Calculate REAL cumulative P&L (never resets!)
    cumulative_pnl = current_value - net_invested
    cumulative_pnl_percent = (current_value / net_invested - 1) * 100 if net_invested > 0 else 0
    
    print(f"\n📊 TOTAL INVESTMENT HISTORY:")
    print(f"  Total invested: ${total_invested:.2f}")
    print(f"  Total withdrawn: ${total_withdrawn:.2f}")
    print(f"  Net investment: ${net_invested:.2f}")
    print(f"    • Gemini: ${gemini_invested:.2f}")
    print(f"    • Binance: ${binance_invested:.2f}")
    
    print(f"\n💰 CURRENT PORTFOLIO:")
    print(f"  Total value: ${current_value:.2f}")
    print(f"    • Cash: ${cash_value:.2f}")
    print(f"    • Positions: ${position_value:.2f}")
    
    print(f"\n📈 REAL CUMULATIVE P&L (NEVER RESETS):")
    print(f"  Amount: ${cumulative_pnl:.2f}")
    print(f"  Percentage: {cumulative_pnl_percent:+.2f}%")
    
    if cumulative_pnl < 0:
        print(f"  🚨 LOSS: ${abs(cumulative_pnl):.2f} ({abs(cumulative_pnl_percent):.2f}%)")
    
    print(f"\n🎯 RECOVERY NEEDED:")
    if cumulative_pnl < 0:
        recovery_amount = abs(cumulative_pnl)
        recovery_percent = (recovery_amount / current_value * 100) if current_value > 0 else 0
        print(f"  Need to gain: ${recovery_amount:.2f}")
        print(f"  That's: {recovery_percent:.1f}% from current portfolio")
    
    # Update trades.json to include investment tracking
    print("\n🔄 UPDATING TRADES.JSON WITH INVESTMENT TRACKING...")
    
    with open('trading_data/trades.json', 'r') as f:
        current_trades = json.load(f)
    
    # Add investment summary as a special trade
    investment_trade = {
        'exchange': 'system',
        'symbol': 'INVESTMENT/SUMMARY',
        'side': 'info',
        'price': 0,
        'amount': 0,
        'current_price': 0,
        'pnl': cumulative_pnl,
        'pnl_percent': cumulative_pnl_percent,
        'value': net_invested,
        'timestamp': datetime.now().isoformat(),
        'type': 'summary',
        'note': f'TOTAL INVESTMENT: ${net_invested:.2f} | CURRENT: ${current_value:.2f} | CUMULATIVE P&L: ${cumulative_pnl:.2f} ({cumulative_pnl_percent:+.2f}%)'
    }
    
    # Insert at beginning
    current_trades.insert(0, investment_trade)
    
    # Save updated trades
    with open('trading_data/trades.json', 'w') as f:
        json.dump(current_trades, f, indent=2)
    
    print(f"✅ Added investment tracking to trades.json")
    
    # Create investment tracking file
    investment_data = {
        'timestamp': datetime.now().isoformat(),
        'total_invested': total_invested,
        'total_withdrawn': total_withdrawn,
        'net_investment': net_invested,
        'breakdown': {
            'gemini': gemini_invested,
            'binance': binance_invested
        },
        'current_portfolio': {
            'total_value': current_value,
            'cash': cash_value,
            'positions': position_value
        },
        'cumulative_pnl': {
            'amount': cumulative_pnl,
            'percent': cumulative_pnl_percent
        },
        'recovery_needed': abs(cumulative_pnl) if cumulative_pnl < 0 else 0
    }
    
    investment_file = 'trading_data/investment_tracking.json'
    with open(investment_file, 'w') as f:
        json.dump(investment_data, f, indent=2)
    
    print(f"📄 Investment tracking saved to: {investment_file}")
    
    print("\n" + "="*70)
    print("🎯 INVESTMENT TRACKING RESTORED!")
    print("="*70)
    print(f"TOTAL MONEY INVESTED: ${net_invested:.2f}")
    print(f"CURRENT PORTFOLIO: ${current_value:.2f}")
    print(f"REAL CUMULATIVE P&L: ${cumulative_pnl:.2f} ({cumulative_pnl_percent:+.2f}%)")
    print("="*70)
    
    print("\n💡 CRITICAL METRICS NOW TRACKED:")
    print("1. Total money invested (never forgets!)")
    print("2. Real cumulative P&L (never resets!)")
    print("3. Recovery amount needed")
    print("4. Portfolio allocation (cash vs positions)")
    print("="*70)

if __name__ == "__main__":
    main()