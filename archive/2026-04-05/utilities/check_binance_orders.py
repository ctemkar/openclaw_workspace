#!/usr/bin/env python3
"""
Check ACTUAL Binance orders and positions
"""

import os
import ccxt
import json
from datetime import datetime

print("🔍 CHECKING BINANCE ORDERS & POSITIONS")
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
        'defaultType': 'future',  # Futures trading
    }
})

try:
    print("\n💰 CHECKING FUTURES BALANCE...")
    balance = exchange.fetch_balance()
    
    print("Futures Account Balance:")
    for currency, amount in balance['total'].items():
        if amount > 0:
            free = balance['free'].get(currency, 0)
            used = balance['used'].get(currency, 0)
            print(f"  {currency}: {amount:.8f} (Free: {free:.8f}, Used: {used:.8f})")
    
    total_usdt = balance['total'].get('USDT', 0)
    print(f"\n📊 Total USDT in Futures: ${total_usdt:.2f}")
    
    print("\n📋 CHECKING OPEN ORDERS...")
    # Check specific symbols we tried to trade
    symbols_to_check = ['DOGE/USDT', 'ADA/USDT', 'DOT/USDT', 'COMP/USDT', 'SNX/USDT']
    
    all_orders = []
    for symbol in symbols_to_check:
        try:
            orders = exchange.fetch_open_orders(symbol=symbol)
            all_orders.extend(orders)
        except:
            pass
    
    print(f"Found {len(all_orders)} open orders:")
    
    for order in all_orders[:10]:  # Show first 10
        symbol = order['symbol']
        side = order['side'].upper()
        order_type = order['type']
        price = order['price']
        amount = order['amount']
        remaining = order['remaining']
        status = order['status']
        
        print(f"  {symbol} {side} {order_type}")
        print(f"    Amount: {remaining:.6f}/{amount:.6f} @ ${price:.4f}")
        print(f"    Status: {status}")
        print(f"    ID: {order['id']}")
    
    print("\n📊 CHECKING OPEN POSITIONS...")
    positions = exchange.fetch_positions()
    
    open_positions = [p for p in positions if float(p['contracts']) > 0]
    print(f"Found {len(open_positions)} open positions:")
    
    for pos in open_positions:
        symbol = pos['symbol']
        side = pos['side'].upper()
        contracts = float(pos['contracts'])
        entry_price = float(pos['entryPrice'])
        mark_price = float(pos['markPrice'])
        unrealized_pnl = float(pos['unrealizedPnl'])
        leverage = pos.get('leverage', 'N/A')
        
        print(f"  {symbol} {side}")
        print(f"    Contracts: {contracts:.6f}")
        print(f"    Entry: ${entry_price:.4f}")
        print(f"    Current: ${mark_price:.4f}")
        print(f"    P&L: ${unrealized_pnl:.4f}")
        print(f"    Leverage: {leverage}x")
        
        # Calculate percentage change
        if entry_price > 0:
            pnl_percent = ((mark_price - entry_price) / entry_price) * 100
            if side == 'SHORT':
                pnl_percent = -pnl_percent  # Invert for shorts
            print(f"    P&L %: {pnl_percent:.2f}%")
    
    print("\n📜 CHECKING RECENT TRADES...")
    # Check recent trades for today
    trades = exchange.fetch_my_trades(symbol='DOGE/USDT', limit=10)
    if trades:
        print(f"Recent DOGE/USDT trades ({len(trades)}):")
        for trade in trades:
            time_str = exchange.iso8601(trade['timestamp'])
            side = trade['side'].upper()
            price = trade['price']
            amount = trade['amount']
            cost = trade['cost']
            print(f"  {time_str[11:19]} - {side} {amount:.2f} @ ${price:.4f} (${cost:.2f})")
    
    # Also check ADA
    trades_ada = exchange.fetch_my_trades(symbol='ADA/USDT', limit=5)
    if trades_ada:
        print(f"\nRecent ADA/USDT trades ({len(trades_ada)}):")
        for trade in trades_ada:
            time_str = exchange.iso8601(trade['timestamp'])
            side = trade['side'].upper()
            price = trade['price']
            amount = trade['amount']
            cost = trade['cost']
            print(f"  {time_str[11:19]} - {side} {amount:.2f} @ ${price:.4f} (${cost:.2f})")
    
except Exception as e:
    print(f"❌ Error checking Binance: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("🎯 To see in Binance app:")
print("1. Open Binance app")
print("2. Go to Futures trading")
print("3. Check 'Positions' tab")
print("4. Check 'Order History' tab")
print("="*60)