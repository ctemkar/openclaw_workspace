#!/usr/bin/env python3
"""Analyze YFI trading losses"""

import ccxt
import os
from datetime import datetime

print("="*70)
print("🚨 YFI TRADING ANALYSIS - LOSING MONEY PATTERN")
print("="*70)

try:
    # Load API keys
    with open('secure_keys/.binance_key', 'r') as f:
        api_key = f.read().strip()
    with open('secure_keys/.binance_secret', 'r') as f:
        api_secret = f.read().strip()
    
    # Initialize Binance
    binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    # Get recent trades
    trades = binance.fetch_my_trades('YFI/USDT', limit=20)
    
    total_profit = 0
    trade_count = 0
    buy_trades = []
    sell_trades = []
    
    print("📊 RECENT YFI TRADES:")
    for trade in trades:
        time_str = datetime.fromtimestamp(trade['timestamp']/1000).strftime('%H:%M:%S')
        side = trade['side']
        amount = trade['amount']
        price = trade['price']
        cost = trade['cost']
        fee = trade['fee']['cost'] if trade['fee'] else 0
        
        if side == 'buy':
            buy_trades.append({'time': time_str, 'price': price, 'amount': amount, 'cost': cost, 'fee': fee})
            print(f'🟢 BUY  {time_str}: {amount:.5f} YFI @ ${price:.2f} = ${cost:.2f} (fee: ${fee:.6f})')
        else:
            sell_trades.append({'time': time_str, 'price': price, 'amount': amount, 'cost': cost, 'fee': fee})
            print(f'🔴 SELL {time_str}: {amount:.5f} YFI @ ${price:.2f} = ${cost:.2f} (fee: ${fee:.6f})')
        
        trade_count += 1
    
    print("\n" + "="*70)
    print("📈 TRADE ANALYSIS:")
    
    # Match buys with sells (FIFO)
    buys = buy_trades.copy()
    sells = sell_trades.copy()
    
    total_pnl = 0
    trade_pairs = []
    
    while buys and sells:
        buy = buys[0]
        sell = sells[0]
        
        # Calculate P&L for this pair
        buy_cost = buy['cost'] + buy['fee']
        sell_revenue = sell['cost'] - sell['fee']
        pnl = sell_revenue - buy_cost
        
        total_pnl += pnl
        
        print(f'\n   {buy["time"]} BUY @${buy["price"]:.2f} → {sell["time"]} SELL @${sell["price"]:.2f}')
        print(f'   Buy: ${buy_cost:.4f}, Sell: ${sell_revenue:.4f}')
        print(f'   P&L: ${pnl:.4f} ({pnl/buy_cost*100:.2f}%)')
        
        trade_pairs.append({
            'buy': buy,
            'sell': sell,
            'pnl': pnl
        })
        
        # Remove matched trades
        buys.pop(0)
        sells.pop(0)
    
    print("\n" + "="*70)
    print(f'💰 TOTAL P&L from {len(trade_pairs)} trade pairs: ${total_pnl:.4f}')
    
    if total_pnl < 0:
        print('🚨 **LOSING MONEY ON YFI TRADES!**')
        print(f'   Total loss: ${abs(total_pnl):.4f}')
    else:
        print('✅ Making profit')
    
    # Check current YFI position
    print("\n" + "="*70)
    print("📊 CURRENT YFI POSITION:")
    
    balance = binance.fetch_balance()
    yfi_balance = balance.get('YFI', {}).get('total', 0)
    usdt_balance = balance.get('USDT', {}).get('free', 0)
    
    print(f'   YFI Balance: {yfi_balance:.6f} YFI')
    print(f'   USDT Balance: ${usdt_balance:.2f}')
    
    if yfi_balance > 0:
        # Get current YFI price
        ticker = binance.fetch_ticker('YFI/USDT')
        current_price = ticker['last']
        yfi_value = yfi_balance * current_price
        
        print(f'   Current YFI Price: ${current_price:.2f}')
        print(f'   YFI Value: ${yfi_value:.2f}')
        
        # Find average buy price
        total_yfi_bought = sum(b['amount'] for b in buy_trades)
        total_cost = sum(b['cost'] + b['fee'] for b in buy_trades)
        
        if total_yfi_bought > 0:
            avg_buy_price = total_cost / total_yfi_bought
            print(f'   Average Buy Price: ${avg_buy_price:.2f}')
            
            # Unrealized P&L
            unrealized_pnl = yfi_value - (yfi_balance * avg_buy_price)
            print(f'   Unrealized P&L: ${unrealized_pnl:.4f}')
    
    print("\n" + "="*70)
    print("🎯 PROBLEM IDENTIFIED:")
    print("   1. Bot is buying YFI at high prices")
    print("   2. Selling at similar or lower prices")
    print("   3. Trading fees eating into profits")
    print("   4. No real arbitrage - just buying/selling same exchange")
    print("\n🔧 SOLUTION NEEDED:")
    print("   1. STOP the current bot immediately")
    print("   2. Implement REAL arbitrage (Binance ↔ Gemini)")
    print("   3. Add spread checking before trades")
    print("   4. Only trade when profitable after fees")
    print("="*70)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()