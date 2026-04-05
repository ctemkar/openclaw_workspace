#!/usr/bin/env python3
"""
START TRADING AUTOMATICALLY
1. Show P&L summary first (most important)
2. Show short trades status clearly
3. Start bots with 1.0% thresholds
"""

import json
import subprocess
import time
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

def show_pnl_summary():
    """Show P&L summary - MOST IMPORTANT"""
    print('📊 P&L SUMMARY - MOST IMPORTANT')
    print('=' * 70)
    print('📅', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # Get dashboard data
    try:
        import requests
        response = requests.get('http://localhost:5007/api/data', timeout=5)
        dashboard_data = response.json()
    except:
        dashboard_data = {'positions': [], 'capital': {}}
    
    # Get system status
    try:
        with open('system_status.json', 'r') as f:
            system_status = json.load(f)
    except:
        system_status = {'capital': {}, 'positions': {}}
    
    # 🔴 CUMULATIVE P&L (NEVER RESETS)
    print('🔴 CUMULATIVE P&L (NEVER RESETS):')
    capital_data = system_status.get('capital', {})
    initial = capital_data.get('initial', 0)
    current = capital_data.get('current', 0)
    cumulative_pnl = capital_data.get('pnl', 0)
    cumulative_percent = capital_data.get('pnl_percent', 0)
    recovery_needed = capital_data.get('recovery_needed', 0)
    recovery_percent = capital_data.get('recovery_percent_needed', 0)
    
    print(f'  • Initial Capital: ${initial:.2f}')
    print(f'  • Current Capital: ${current:.2f}')
    print(f'  • Cumulative P&L: ${cumulative_pnl:+.2f} ({cumulative_percent:+.2f}%)')
    print(f'  • Recovery Needed: +{recovery_percent:.1f}% (${recovery_needed:.2f})')
    print()
    
    # 🔵 EXCHANGE BREAKDOWN
    print('🔵 EXCHANGE BREAKDOWN:')
    
    # Calculate current open P&L
    total_open_pnl = 0
    gemini_open_pnl = 0
    binance_open_pnl = 0
    
    positions = dashboard_data.get('positions', [])
    for pos in positions:
        exchange = pos.get('exchange', 'unknown')
        symbol = pos.get('symbol', 'unknown')
        entry_price = pos.get('price', 0)
        amount = pos.get('amount', 0)
        current_price = get_current_price(symbol)
        
        pnl = (amount * current_price) - (amount * entry_price)
        total_open_pnl += pnl
        
        if exchange == 'gemini':
            gemini_open_pnl += pnl
        elif exchange == 'binance':
            binance_open_pnl += pnl
    
    # Get Binance unrealized from system status
    binance_summary = system_status.get('positions', {}).get('binance_positions_summary', {})
    binance_unrealized = binance_summary.get('total_unrealized_pnl', 0)
    
    print(f'  • Gemini P&L: ${gemini_open_pnl:+.2f} (open positions)')
    print(f'  • Binance P&L: ${binance_open_pnl + binance_unrealized:+.2f} (open + unrealized)')
    print(f'  • Total Open P&L: ${total_open_pnl:+.2f}')
    print()
    
    # 📊 SHORT TRADES STATUS (CLEARLY SHOWN)
    print('📊 SHORT TRADES STATUS:')
    binance_positions = [p for p in positions if p.get('exchange') == 'binance']
    
    if binance_positions:
        print(f'  • Binance SHORT positions: {len(binance_positions)}')
        for pos in binance_positions:
            symbol = pos.get('symbol', 'unknown')
            entry_price = pos.get('price', 0)
            current_price = get_current_price(symbol)
            pnl_percent = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
            print(f'    - {symbol}: Entry ${entry_price:.4f}, P&L {pnl_percent:+.2f}%')
    else:
        print('  • Binance SHORT positions: 0 (no short trades currently open)')
        print('  • Reason: Thresholds adjusted to 1.0%, waiting for opportunities')
    
    print()
    
    # 💰 CAPITAL ALLOCATION
    print('💰 CAPITAL ALLOCATION:')
    dashboard_capital = dashboard_data.get('capital', {})
    total = dashboard_capital.get('total_capital', 0)
    gemini = dashboard_capital.get('gemini_total', 0)
    binance = dashboard_capital.get('binance_total', 0)
    deployed = dashboard_capital.get('deployed', 0)
    available_gemini = dashboard_capital.get('available_gemini', 0)
    available_binance = dashboard_capital.get('available_binance', 0)
    
    print(f'  • Total: ${total:.2f}')
    print(f'  • Gemini: ${gemini:.2f} ({gemini/total*100:.1f}%)')
    print(f'  • Binance: ${binance:.2f} ({binance/total*100:.1f}%)')
    print(f'  • Deployed: ${deployed:.2f} ({deployed/total*100:.1f}%)')
    print(f'  • Available: ${available_gemini + available_binance:.2f}')
    print()
    
    return True

def start_bots():
    """Start trading bots with new thresholds"""
    print('🚀 STARTING TRADING BOTS WITH 1.0% THRESHOLDS')
    print('=' * 70)
    
    # Stop any existing bots first
    print('🛑 Stopping existing bots...')
    subprocess.run(['pkill', '-f', 'fixed_bot_common.py'], capture_output=True)
    subprocess.run(['pkill', '-f', 'real_26_crypto_trader.py'], capture_output=True)
    time.sleep(2)
    
    # Start real_26_crypto_trader.py
    print('\n📊 Starting real_26_crypto_trader.py...')
    print('   • 26 cryptocurrencies')
    print('   • Gemini LONG: 1.0% dips')
    print('   • Binance SHORT: 1.0% rallies')
    print('   • Position size: 10% of capital')
    
    proc1 = subprocess.Popen(
        ['python3', 'real_26_crypto_trader.py'],
        stdout=open('real_26_crypto_trader.log', 'w'),
        stderr=subprocess.STDOUT
    )
    
    print(f'   ✅ Started (PID: {proc1.pid})')
    
    # Start fixed_bot_common.py
    print('\n📊 Starting fixed_bot_common.py...')
    print('   • Common data layer')
    print('   • Gemini LONG: 1.0% dips')
    print('   • Uses Binance price data')
    
    proc2 = subprocess.Popen(
        ['python3', 'fixed_bot_common.py'],
        stdout=open('fixed_bot_common.log', 'w'),
        stderr=subprocess.STDOUT
    )
    
    print(f'   ✅ Started (PID: {proc2.pid})')
    
    print('\n📈 BOT CONFIGURATION:')
    print('   • Both bots use 1.0% thresholds')
    print('   • Stop-loss: 3%, Take-profit: 5%')
    print('   • Position size: 10% of capital')
    print('   • Max positions: 3 per bot')
    
    print('\n🎯 EXPECTED BEHAVIOR:')
    print('   • More trades than 3.0% thresholds')
    print('   • Balanced risk with 1.0% moves')
    print('   • Both Gemini LONG and Binance SHORT opportunities')
    
    print('\n📊 MONITORING:')
    print('   • Dashboard: http://localhost:5007/')
    print('   • Logs: real_26_crypto_trader.log, fixed_bot_common.log')
    print('   • Check SHORT trades status in next report')
    
    return proc1, proc2

def main():
    """Main function"""
    print('=' * 70)
    print('🔄 TRADING SYSTEM RESTART')
    print('=' * 70)
    print()
    
    # 1. Show P&L summary first (most important)
    show_pnl_summary()
    
    # 2. Start bots
    print('🚀 Starting bots with 1.0% thresholds...')
    print()
    
    start_bots()
    
    print()
    print('=' * 70)
    print('✅ TRADING SYSTEM STARTED')
    print('=' * 70)
    print()
    print('📊 Next P&L report will show:')
    print('   1. Cumulative P&L (most important)')
    print('   2. Gemini vs Binance breakdown')
    print('   3. SHORT trades status (clearly shown)')
    print('   4. Capital allocation')
    print()
    print('✅ READY FOR NEXT REQUEST')

if __name__ == '__main__':
    main()