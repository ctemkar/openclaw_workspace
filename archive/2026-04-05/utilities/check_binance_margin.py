#!/usr/bin/env python3
"""
Check Binance margin situation
"""

import ccxt

print("💰 BINANCE MARGIN ANALYSIS")
print("="*60)

try:
    with open("secure_keys/.binance_key", "r") as f:
        BINANCE_KEY = f.read().strip()
    with open("secure_keys/.binance_secret", "r") as f:
        BINANCE_SECRET = f.read().strip()
    
    exchange = ccxt.binance({
        'apiKey': BINANCE_KEY,
        'secret': BINANCE_SECRET,
        'enableRateLimit': True,
        'options': {'defaultType': 'future'}
    })
    
    # Get balance
    balance = exchange.fetch_balance()
    total_usdt = balance['total'].get('USDT', 0)
    free_usdt = balance['free'].get('USDT', 0)
    used_usdt = balance['used'].get('USDT', 0)
    
    print(f"💰 Futures Balance:")
    print(f"  Total USDT: ${total_usdt:.2f}")
    print(f"  Free: ${free_usdt:.2f}")
    print(f"  Used: ${used_usdt:.2f}")
    
    # Get positions
    positions = exchange.fetch_positions()
    open_positions = [p for p in positions if float(p['contracts']) > 0]
    
    print(f"\n📊 Open Positions: {len(open_positions)}")
    
    total_margin_required = 0
    for pos in open_positions:
        symbol = pos['symbol']
        side = pos['side']
        contracts = float(pos['contracts'])
        entry = float(pos['entryPrice'])
        current = float(pos['markPrice'])
        pnl = float(pos['unrealizedPnl'])
        
        # Estimate margin required to close (approx 1% of position value)
        position_value = contracts * current
        margin_needed = position_value * 0.01  # Rough estimate
        
        total_margin_required += margin_needed
        
        print(f"\n  {symbol} {side}")
        print(f"    Contracts: {contracts:.2f}")
        print(f"    Position value: ${position_value:.2f}")
        print(f"    P&L: ${pnl:.4f}")
        print(f"    Est. margin to close: ${margin_needed:.2f}")
    
    print(f"\n📈 MARGIN ANALYSIS:")
    print(f"  Free margin available: ${free_usdt:.2f}")
    print(f"  Estimated margin needed to close all: ${total_margin_required:.2f}")
    print(f"  Shortfall: ${total_margin_required - free_usdt:.2f}")
    
    if free_usdt < total_margin_required:
        print(f"\n❌ INSUFFICIENT MARGIN!")
        print(f"   Need ${total_margin_required - free_usdt:.2f} more USDT")
        print(f"\n🎯 SOLUTIONS:")
        print(f"   1. Transfer more USDT to Futures wallet")
        print(f"   2. Wait for prices to improve (positions are in loss)")
        print(f"   3. Close positions one by one as margin frees up")
    
    # Check if we can transfer from Spot
    spot_balance = exchange.fetch_balance({'type': 'spot'})
    spot_usdt = spot_balance['total'].get('USDT', 0)
    spot_free = spot_balance['free'].get('USDT', 0)
    
    print(f"\n💵 SPOT WALLET (for transfer):")
    print(f"  Total USDT: ${spot_usdt:.2f}")
    print(f"  Free: ${spot_free:.2f}")
    
    if spot_free > 10:
        print(f"\n✅ You can transfer ${spot_free:.2f} from Spot to Futures!")
        print(f"   This should be enough to close positions.")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("🎯 Quick fix: Transfer $10+ from Spot to Futures wallet")
print("="*60)