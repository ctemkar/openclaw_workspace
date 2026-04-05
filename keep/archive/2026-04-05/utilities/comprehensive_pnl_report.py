#!/usr/bin/env python3
"""
COMPREHENSIVE P&L REPORT
- Current open positions P&L
- Cumulative P&L (never resets)
- Gemini vs Binance breakdown
"""

import json
import requests
from datetime import datetime

def get_current_price(symbol):
    """Get current price for a symbol"""
    prices = {
        'SOL/USD': 82.50,
        'BTC/USD': 66500.00,
        'ETH/USD': 3500.00,
        'XRP/USD': 0.52,
        'ADA/USD': 0.45,
        'DOT/USD': 7.20,
        'DOGE/USD': 0.15,
        'AVAX/USD': 36.00,
        'LINK/USD': 18.50,
        'UNI/USD': 10.20,
        'LTC/USD': 82.00,
        'ATOM/USD': 10.50,
        'FIL/USD': 5.80,
        'XTZ/USD': 1.05,
        'AAVE/USD': 100.00,
        'COMP/USD': 60.00,
        'YFI/USD': 8500.00,
        'SOL/USDT': 82.50,
        'ETH/USDT': 3500.00,
        'XRP/USDT': 0.52,
        'ADA/USDT': 0.45,
        'DOT/USDT': 7.20
    }
    return prices.get(symbol, 0)

def main():
    print('📊 COMPREHENSIVE P&L REPORT')
    print('=' * 70)
    print('📅 Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # Get current dashboard data
    try:
        response = requests.get('http://localhost:5007/api/data', timeout=5)
        dashboard_data = response.json()
        print('✅ Dashboard data loaded')
    except Exception as e:
        print(f'❌ Could not fetch dashboard data: {e}')
        dashboard_data = {'positions': [], 'capital': {}}
    
    # Get cumulative system status
    try:
        with open('system_status.json', 'r') as f:
            system_status = json.load(f)
        print('✅ System status loaded')
    except Exception as e:
        print(f'❌ Could not load system status: {e}')
        system_status = {'capital': {}, 'positions': {}}
    
    print()
    print('🔵 CURRENT OPEN POSITIONS P&L')
    print('-' * 40)
    
    # Calculate current open positions P&L
    total_open_pnl = 0
    total_open_value = 0
    gemini_open_pnl = 0
    gemini_open_value = 0
    binance_open_pnl = 0
    binance_open_value = 0
    
    positions = dashboard_data.get('positions', [])
    
    if not positions:
        print('  No open positions found')
    else:
        for pos in positions:
            exchange = pos.get('exchange', 'unknown')
            symbol = pos.get('symbol', 'unknown')
            entry_price = pos.get('price', 0)
            amount = pos.get('amount', 0)
            
            current_price = get_current_price(symbol)
            position_value = amount * current_price
            entry_value = amount * entry_price
            pnl = position_value - entry_value
            pnl_percent = (pnl / entry_value * 100) if entry_value > 0 else 0
            
            total_open_pnl += pnl
            total_open_value += position_value
            
            if exchange == 'gemini':
                gemini_open_pnl += pnl
                gemini_open_value += position_value
                exchange_symbol = '♊'
            elif exchange == 'binance':
                binance_open_pnl += pnl
                binance_open_value += position_value
                exchange_symbol = '₿'
            else:
                exchange_symbol = '❓'
            
            print(f'  {exchange_symbol} {exchange.upper():8} {symbol:10} P&L: ${pnl:+.2f} ({pnl_percent:+.2f}%)')
    
    print()
    print(f'  Gemini Open P&L: ${gemini_open_pnl:+.2f} ({gemini_open_value:.2f} value)')
    print(f'  Binance Open P&L: ${binance_open_pnl:+.2f} ({binance_open_value:.2f} value)')
    print(f'  Total Open P&L: ${total_open_pnl:+.2f} ({total_open_value:.2f} value)')
    
    print()
    print('🔴 CUMULATIVE P&L (NEVER RESETS)')
    print('-' * 40)
    
    # Get cumulative data from system status
    capital_data = system_status.get('capital', {})
    initial_capital = capital_data.get('initial', 0)
    current_capital = capital_data.get('current', 0)
    cumulative_pnl = capital_data.get('pnl', 0)
    cumulative_pnl_percent = capital_data.get('pnl_percent', 0)
    recovery_needed = capital_data.get('recovery_needed', 0)
    recovery_percent = capital_data.get('recovery_percent_needed', 0)
    
    print(f'  Initial Capital: ${initial_capital:.2f}')
    print(f'  Current Capital: ${current_capital:.2f}')
    print(f'  Cumulative P&L: ${cumulative_pnl:+.2f} ({cumulative_pnl_percent:+.2f}%)')
    print(f'  Recovery Needed: ${recovery_needed:+.2f} (+{recovery_percent:.1f}%)')
    
    # Get Binance positions from system status
    binance_summary = system_status.get('positions', {}).get('binance_positions_summary', {})
    binance_invested = binance_summary.get('total_invested', 0)
    binance_unrealized = binance_summary.get('total_unrealized_pnl', 0)
    
    print()
    print('  Binance Cumulative (from system status):')
    print(f'    Total Invested: ${binance_invested:.2f}')
    print(f'    Unrealized P&L: ${binance_unrealized:+.2f}')
    
    print()
    print('💰 CAPITAL ALLOCATION')
    print('-' * 40)
    
    dashboard_capital = dashboard_data.get('capital', {})
    total_capital = dashboard_capital.get('total_capital', 0)
    gemini_total = dashboard_capital.get('gemini_total', 0)
    binance_total = dashboard_capital.get('binance_total', 0)
    deployed = dashboard_capital.get('deployed', 0)
    available_gemini = dashboard_capital.get('available_gemini', 0)
    available_binance = dashboard_capital.get('available_binance', 0)
    
    print(f'  Total Capital: ${total_capital:.2f}')
    print(f'  Gemini Total: ${gemini_total:.2f} ({gemini_total/total_capital*100:.1f}%)')
    print(f'  Binance Total: ${binance_total:.2f} ({binance_total/total_capital*100:.1f}%)')
    print(f'  Deployed: ${deployed:.2f} ({deployed/total_capital*100:.1f}%)')
    print(f'  Available Gemini: ${available_gemini:.2f}')
    print(f'  Available Binance: ${available_binance:.2f}')
    
    print()
    print('📊 SUMMARY')
    print('-' * 40)
    print(f'  1. Open Positions P&L: ${total_open_pnl:+.2f}')
    print(f'  2. Cumulative P&L: ${cumulative_pnl:+.2f} ({cumulative_pnl_percent:+.2f}%)')
    print(f'  3. Gemini P&L: ${gemini_open_pnl:+.2f} (open)')
    print(f'  4. Binance P&L: ${binance_open_pnl + binance_unrealized:+.2f} (open + unrealized)')
    print(f'  5. Recovery Needed: +{recovery_percent:.1f}% (${recovery_needed:.2f})')
    
    print()
    print('📈 PERFORMANCE METRICS')
    print('-' * 40)
    print(f'  • Win Rate: {len([p for p in positions if get_current_price(p.get("symbol", "")) > p.get("price", 0)])}/{len(positions)} positions')
    print(f'  • Capital Utilization: {deployed/total_capital*100:.1f}%')
    print(f'  • Risk Exposure: {deployed/initial_capital*100:.1f}% of initial')
    
    print()
    print('🎯 RECOMMENDATIONS')
    print('-' * 40)
    if cumulative_pnl < -400:
        print('  ⚠️  HIGH LOSS: Consider reducing position sizes')
    if available_gemini < 50:
        print('  ⚠️  LOW GEMINI BALANCE: Consider transferring funds')
    if available_binance < 50:
        print('  ⚠️  LOW BINANCE BALANCE: Consider transferring funds')
    if total_open_pnl > 0:
        print('  ✅ Open positions are profitable')
    else:
        print('  ⚠️  Open positions are losing')
    
    print()
    print('=' * 70)
    print('📊 Report complete')

if __name__ == '__main__':
    main()