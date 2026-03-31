#!/usr/bin/env python3
"""
CLEAR ALL BINANCE FUTURES POSITIONS - Close all shorts
"""

import ccxt
import json
from datetime import datetime

print("💰 CLOSING ALL BINANCE FUTURES POSITIONS")
print("="*60)

try:
    # Load Binance keys
    with open("secure_keys/.binance_key", "r") as f:
        BINANCE_KEY = f.read().strip()
    with open("secure_keys/.binance_secret", "r") as f:
        BINANCE_SECRET = f.read().strip()
    
    print("✅ Binance API keys loaded")
    
    # Initialize Binance Futures
    exchange = ccxt.binance({
        'apiKey': BINANCE_KEY,
        'secret': BINANCE_SECRET,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',
        }
    })
    
    # Get open positions
    positions = exchange.fetch_positions()
    open_positions = [p for p in positions if float(p['contracts']) > 0]
    
    print(f"\n📊 CURRENT BINANCE FUTURES POSITIONS: {len(open_positions)}")
    
    if not open_positions:
        print("✅ No open positions to close")
        exit(0)
    
    total_pnl = 0
    total_contracts = 0
    
    for pos in open_positions:
        symbol = pos['symbol']
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
                pnl_percent = -pnl_percent
        
        total_pnl += unrealized_pnl
        total_contracts += contracts
        
        print(f"\n  {symbol} {side}")
        print(f"    Contracts: {contracts:.6f}")
        print(f"    Entry: ${entry_price:.4f}")
        print(f"    Current: ${mark_price:.4f}")
        print(f"    P&L: ${unrealized_pnl:.4f} ({pnl_percent:+.2f}%)")
    
    print(f"\n📈 TOTAL UNREALIZED P&L: ${total_pnl:.4f}")
    print(f"📊 TOTAL CONTRACTS: {total_contracts:.6f}")
    
    print("\n" + "="*60)
    print("🚀 READY TO CLOSE ALL POSITIONS")
    print("="*60)
    
    # Ask for confirmation
    response = input(f"\nClose ALL {len(open_positions)} positions (P&L: ${total_pnl:.4f})? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Cancelled")
        exit(0)
    
    print("\n⚡ CLOSING POSITIONS...")
    
    closed_positions = []
    
    for pos in open_positions:
        try:
            symbol = pos['symbol']
            side = pos['side']
            contracts = float(pos['contracts'])
            
            print(f"\n📤 Closing {symbol} {side}...")
            print(f"   Contracts: {contracts:.6f}")
            
            # For SHORT positions, we need to BUY to close
            # For LONG positions, we need to SELL to close
            close_side = 'buy' if side.lower() == 'sell' else 'sell'
            
            # Place market order to close position
            order = exchange.create_order(
                symbol=symbol,
                type='market',
                side=close_side,
                amount=contracts
            )
            
            print(f"✅ CLOSED: {symbol} {side}")
            print(f"   Order ID: {order['id']}")
            print(f"   Closed {contracts:.6f} contracts")
            
            closed_positions.append({
                'symbol': symbol,
                'side': side,
                'contracts': contracts,
                'order_id': order['id'],
                'timestamp': datetime.now().isoformat()
            })
            
            # Small delay to avoid rate limits
            import time
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Failed to close {symbol}: {e}")
    
    print("\n" + "="*60)
    print("🎯 POSITIONS CLOSED!")
    print("="*60)
    print(f"\n📊 Positions closed: {len(closed_positions)}")
    print(f"📈 Final P&L: ${total_pnl:.4f}")
    
    # Save closure record
    closure_record = {
        'timestamp': datetime.now().isoformat(),
        'total_pnl': total_pnl,
        'positions_closed': len(closed_positions),
        'details': closed_positions
    }
    
    with open("binance_closure_record.json", "w") as f:
        json.dump(closure_record, f, indent=2)
    
    print(f"\n📝 Closure record saved to: binance_closure_record.json")
    
    # Check new positions
    print("\n🔄 Checking for remaining positions...")
    new_positions = exchange.fetch_positions()
    remaining = [p for p in new_positions if float(p['contracts']) > 0]
    
    if remaining:
        print(f"⚠️  {len(remaining)} positions still open!")
        for pos in remaining:
            print(f"  {pos['symbol']}: {pos['contracts']} contracts")
    else:
        print("✅ All positions successfully closed!")
    
    # Check balance
    print("\n💰 Checking futures balance...")
    balance = exchange.fetch_balance()
    total_usdt = balance['total'].get('USDT', 0)
    free_usdt = balance['free'].get('USDT', 0)
    used_usdt = balance['used'].get('USDT', 0)
    
    print(f"  Total USDT: ${total_usdt:.2f}")
    print(f"  Free: ${free_usdt:.2f}")
    print(f"  Used: ${used_usdt:.2f}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ Script complete")
print("="*60)