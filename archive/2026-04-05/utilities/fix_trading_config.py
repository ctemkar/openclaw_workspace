#!/usr/bin/env python3
"""
Fix trading configuration:
1. Reduce position size from 10% to 5%
2. Close ENJ position on Binance
"""

import ccxt
import os
import time

print("🔧 FIXING TRADING CONFIGURATION")
print("="*60)

# Read Binance API keys
try:
    with open('secure_keys/.binance_key', 'r') as f:
        api_key = f.read().strip()
    with open('secure_keys/.binance_secret', 'r') as f:
        api_secret = f.read().strip()
except FileNotFoundError as e:
    print(f"❌ Error reading API keys: {e}")
    exit(1)

# Initialize Binance Futures
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'options': {
        'defaultType': 'future',
    },
    'enableRateLimit': True,
})

print("✅ Connected to Binance Futures")

# Step 1: Close ENJ position
print("\n1️⃣ CLOSING ENJ POSITION")
print("-" * 40)

try:
    # Fetch current positions
    positions = exchange.fetch_positions()
    enj_position = None
    
    for pos in positions:
        if pos['symbol'] == 'ENJ/USDT:USDT' and float(pos['contracts']) > 0:
            enj_position = pos
            break
    
    if enj_position:
        contracts = float(enj_position['contracts'])
        entry_price = float(enj_position['entryPrice'])
        mark_price = float(enj_position['markPrice'])
        pnl = float(enj_position['unrealizedPnl'])
        
        print(f"   Found ENJ position: {contracts} contracts")
        print(f"   Entry: ${entry_price:.6f}, Current: ${mark_price:.6f}")
        print(f"   P&L: ${pnl:.4f}")
        
        # Close position (opposite side)
        if contracts > 0:  # Long position
            print(f"   Closing LONG position with SELL order")
            order = exchange.create_market_sell_order('ENJ/USDT:USDT', abs(contracts))
        else:  # Short position
            print(f"   Closing SHORT position with BUY order")
            order = exchange.create_market_buy_order('ENJ/USDT:USDT', abs(contracts))
        
        print(f"   ✅ Order executed: {order['id']}")
        time.sleep(1)  # Wait for order to fill
        
        # Verify position is closed
        positions = exchange.fetch_positions()
        enj_after = [p for p in positions if p['symbol'] == 'ENJ/USDT:USDT' and float(p['contracts']) != 0]
        
        if not enj_after:
            print(f"   ✅ ENJ position successfully closed")
        else:
            print(f"   ⚠️ ENJ position still open: {enj_after[0]['contracts']} contracts")
            
    else:
        print(f"   ℹ️ No ENJ position found")
        
except Exception as e:
    print(f"   ❌ Error closing ENJ: {e}")

# Step 2: Check new balance
print("\n2️⃣ CHECKING UPDATED BALANCE")
print("-" * 40)

try:
    balance = exchange.fetch_balance()
    free_usdt = float(balance['free']['USDT'])
    total_usdt = float(balance['total']['USDT'])
    
    print(f"   Total Balance: ${total_usdt:.2f}")
    print(f"   Free Balance: ${free_usdt:.2f}")
    
    # Check remaining positions
    positions = exchange.fetch_positions()
    open_positions = [p for p in positions if float(p['contracts']) > 0]
    
    print(f"   Open Positions: {len(open_positions)}")
    for pos in open_positions:
        print(f"     {pos['symbol']}: {pos['contracts']} contracts")
        
except Exception as e:
    print(f"   ❌ Error checking balance: {e}")

# Step 3: Update trading bot configuration
print("\n3️⃣ UPDATING TRADING BOT CONFIG")
print("-" * 40)

try:
    # Read current bot configuration
    with open('real_26_crypto_trader.py', 'r') as f:
        content = f.read()
    
    # Update position size from 10% to 5%
    old_line = "    position_size = 0.10  # 10% of capital (MORE AGGRESSIVE!)"
    new_line = "    position_size = 0.05  # 5% of capital (REDUCED FOR MARGIN)"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print(f"   ✅ Updated position size: 10% → 5%")
    else:
        # Try alternative line
        old_line2 = "    position_size = 0.10  # 10% of capital"
        if old_line2 in content:
            content = content.replace(old_line2, new_line)
            print(f"   ✅ Updated position size: 10% → 5%")
        else:
            print(f"   ⚠️ Could not find position size line to update")
    
    # Update position size calculation
    old_calc = "position_value = capital * position_size"
    new_calc = "position_value = capital * position_size  # 5% of capital"
    
    if old_calc in content:
        content = content.replace(old_calc, new_calc)
        print(f"   ✅ Updated position calculation comment")
    
    # Write updated configuration
    with open('real_26_crypto_trader.py', 'w') as f:
        f.write(content)
        
    print(f"   ✅ Trading bot configuration updated")
    
except Exception as e:
    print(f"   ❌ Error updating bot config: {e}")

print("\n" + "="*60)
print("✅ TRADING CONFIGURATION FIXED!")
print("="*60)
print("\nNext steps:")
print("1. Restart the trading bot to apply new 5% position size")
print("2. Bot should now have sufficient margin for trades")
print("3. Monitor for successful trade executions")