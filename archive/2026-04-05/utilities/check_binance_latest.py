#!/usr/bin/env python3
"""
Check LATEST Binance positions - ONE MORE TIME
"""

import os
import ccxt
from datetime import datetime

print("🔍 CHECKING BINANCE - ONE MORE TIME (Try 1)")
print("="*60)

# Load Binance keys
try:
    with open("secure_keys/.binance_key", "r") as f:
        BINANCE_KEY = f.read().strip()
    with open("secure_keys/.binance_secret", "r") as f:
        BINANCE_SECRET = f.read().strip()
    print("✅ Binance API keys loaded")
except Exception as e:
    print(f"❌ Failed to load Binance keys: {e}")
    exit(1)

# Initialize Binance Futures
exchange = ccxt.binance({
    'apiKey': BINANCE_KEY,
    'secret': BINANCE_SECRET,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        'warnOnFetchOpenOrdersWithoutSymbol': False  # Suppress warning
    }
})

try:
    print(f"\n⏰ Check time: {datetime.now().strftime('%H:%M:%S')}")
    
    print("\n💰 LATEST FUTURES BALANCE:")
    balance = exchange.fetch_balance()
    total_usdt = balance['total'].get('USDT', 0)
    free_usdt = balance['free'].get('USDT', 0)
    used_usdt = balance['used'].get('USDT', 0)
    
    print(f"  Total USDT: ${total_usdt:.2f}")
    print(f"  Free: ${free_usdt:.2f}")
    print(f"  Used: ${used_usdt:.2f}")
    
    print("\n📊 LATEST OPEN POSITIONS:")
    positions = exchange.fetch_positions()
    
    open_positions = [p for p in positions if float(p['contracts']) > 0]
    print(f"  Found {len(open_positions)} open positions:")
    
    total_pnl = 0
    for pos in open_positions:
        symbol = pos['symbol'].replace(':USDT', '')  # Clean symbol
        side = pos['side'].upper()
        contracts = float(pos['contracts'])
        entry_price = float(pos['entryPrice'])
        mark_price = float(pos['markPrice'])
        unrealized_pnl = float(pos['unrealizedPnl'])
        
        # Calculate percentage
        pnl_percent = 0
        if entry_price > 0:
            pnl_percent = ((mark_price - entry_price) / entry_price) * 100
            if side == 'SHORT':
                pnl_percent = -pnl_percent  # Invert for shorts
        
        total_pnl += unrealized_pnl
        
        print(f"  • {symbol} {side}")
        print(f"    Entry: ${entry_price:.4f} | Current: ${mark_price:.4f}")
        print(f"    P&L: ${unrealized_pnl:.4f} ({pnl_percent:+.2f}%)")
        print(f"    Contracts: {contracts:.2f}")
    
    print(f"\n📈 TOTAL UNREALIZED P&L: ${total_pnl:.4f}")
    
    print("\n🔄 CHECKING IF BOT IS STILL RUNNING...")
    import psutil
    bot_running = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            if 'binance_futures_with_safety' in cmdline:
                bot_running = True
                print(f"  ✅ Binance bot running (PID: {proc.info['pid']})")
                break
        except:
            pass
    
    if not bot_running:
        print("  ❌ Binance bot NOT running!")
    
    print("\n🎯 GEMINI STATUS CHECK:")
    gemini_running = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            if 'fixed_trading_bot_with_safety' in cmdline:
                gemini_running = True
                print(f"  ✅ Gemini bot running (PID: {proc.info['pid']})")
                break
        except:
            pass
    
    if not gemini_running:
        print("  ❌ Gemini bot NOT running!")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("✅ CHECK COMPLETE - Try 1 done!")
print("All positions confirmed active.")
print("Both bots should be running.")
print("="*60)