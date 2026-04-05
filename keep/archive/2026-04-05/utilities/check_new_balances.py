#!/usr/bin/env python3
"""
Check NEW balances after moving to primary portfolio
"""

import ccxt
import os
import json
from datetime import datetime

print("💰 CHECKING NEW PRIMARY PORTFOLIO BALANCES")
print("="*60)

# Read API keys from secure_keys/ (should be valid for primary portfolio)
try:
    with open('secure_keys/.gemini_key', 'r') as f:
        gemini_key = f.read().strip()
    with open('secure_keys/.gemini_secret', 'r') as f:
        gemini_secret = f.read().strip()
    with open('secure_keys/.binance_key', 'r') as f:
        binance_key = f.read().strip()
    with open('secure_keys/.binance_secret', 'r') as f:
        binance_secret = f.read().strip()
except FileNotFoundError as e:
    print(f"❌ Error reading API keys: {e}")
    exit(1)

# Initialize exchanges
gemini = ccxt.gemini({
    'apiKey': gemini_key,
    'secret': gemini_secret,
    'enableRateLimit': True,
})

binance = ccxt.binance({
    'apiKey': binance_key,
    'secret': binance_secret,
    'options': {
        'defaultType': 'future',
    },
    'enableRateLimit': True,
})

print("✅ Connected to exchanges")

try:
    print(f"\n1️⃣ NEW GEMINI BALANCE (Primary Portfolio):")
    print("-" * 40)
    
    gemini_balance = gemini.fetch_balance()
    gemini_total_usd = float(gemini_balance['total'].get('USD', 0))
    gemini_free_usd = float(gemini_balance['free'].get('USD', 0))
    
    print(f"   Total USD: ${gemini_total_usd:.2f}")
    print(f"   Free USD: ${gemini_free_usd:.2f}")
    
    # Check crypto holdings
    print(f"\n   Crypto Holdings:")
    crypto_value = 0
    for currency, amount in gemini_balance['total'].items():
        if currency != 'USD' and float(amount) > 0.001:  # More than dust
            try:
                symbol = f"{currency}/USD"
                ticker = gemini.fetch_ticker(symbol)
                price = float(ticker['last'])
                value = float(amount) * price
                crypto_value += value
                
                print(f"     {currency}: {float(amount):.6f} coins")
                print(f"       Price: ${price:.2f}, Value: ${value:.2f}")
            except:
                print(f"     {currency}: {float(amount):.6f} coins (price unavailable)")
    
    print(f"\n   Summary:")
    print(f"     Total Value: ${gemini_total_usd:.2f}")
    print(f"     Crypto Value: ${crypto_value:.2f}")
    print(f"     Cash Value: ${gemini_total_usd - crypto_value:.2f}")
    
    print(f"\n2️⃣ NEW BINANCE BALANCE (Primary Portfolio):")
    print("-" * 40)
    
    binance_balance = binance.fetch_balance()
    binance_total_usdt = float(binance_balance['total'].get('USDT', 0))
    binance_free_usdt = float(binance_balance['free'].get('USDT', 0))
    
    print(f"   Total USDT: ${binance_total_usdt:.2f}")
    print(f"   Free USDT: ${binance_free_usdt:.2f}")
    
    # Check positions
    binance_positions = binance.fetch_positions()
    open_positions = []
    total_position_value = 0
    total_unrealized_pnl = 0
    
    for pos in binance_positions:
        contracts = float(pos['contracts'])
        if abs(contracts) > 0:
            entry_price = float(pos['entryPrice'])
            mark_price = float(pos['markPrice'])
            unrealized_pnl = float(pos['unrealizedPnl'])
            position_value = abs(contracts) * mark_price
            
            position_data = {
                'symbol': pos['symbol'],
                'contracts': contracts,
                'entry_price': entry_price,
                'current_price': mark_price,
                'position_value': position_value,
                'unrealized_pnl': unrealized_pnl,
                'pnl_percent': (unrealized_pnl / (position_value - unrealized_pnl)) * 100 if (position_value - unrealized_pnl) > 0 else 0
            }
            open_positions.append(position_data)
            
            total_position_value += position_value
            total_unrealized_pnl += unrealized_pnl
    
    print(f"\n   Open Positions: {len(open_positions)}")
    for pos in open_positions:
        side = "LONG" if pos['contracts'] > 0 else "SHORT"
        print(f"     {pos['symbol']} {side}:")
        print(f"       Contracts: {abs(pos['contracts']):.4f}")
        print(f"       Entry: ${pos['entry_price']:.4f}, Current: ${pos['current_price']:.4f}")
        print(f"       P&L: ${pos['unrealized_pnl']:.4f} ({pos['pnl_percent']:.2f}%)")
    
    print(f"\n   Summary:")
    print(f"     Total Balance: ${binance_total_usdt:.2f}")
    print(f"     Free Balance: ${binance_free_usdt:.2f}")
    print(f"     Position Value: ${total_position_value:.2f}")
    print(f"     Unrealized P&L: ${total_unrealized_pnl:.2f}")
    
    # Update trading bot configuration
    print(f"\n3️⃣ UPDATING TRADING BOT CONFIGURATION:")
    print("-" * 40)
    
    # Read current bot config
    with open('real_26_crypto_trader.py', 'r') as f:
        content = f.read()
    
    # Update Gemini capital (use 80% of total for safety)
    new_gemini_capital = gemini_total_usd * 0.8  # Use 80% for trading
    old_gemini_line = "GEMINI_CAPITAL = 134.27  # Gemini cash balance"
    new_gemini_line = f"GEMINI_CAPITAL = {new_gemini_capital:.2f}  # Gemini cash balance (80% of ${gemini_total_usd:.2f})"
    
    # Update Binance capital (use free balance + some of deployed)
    new_binance_capital = binance_free_usdt + (total_position_value * 0.5)  # 50% of current positions
    old_binance_line = "BINANCE_CAPITAL = 134.27 # Binance Futures capital"
    new_binance_line = f"BINANCE_CAPITAL = {new_binance_capital:.2f} # Binance Futures capital"
    
    if old_gemini_line in content and old_binance_line in content:
        content = content.replace(old_gemini_line, new_gemini_line)
        content = content.replace(old_binance_line, new_binance_line)
        
        with open('real_26_crypto_trader.py', 'w') as f:
            f.write(content)
        
        print(f"✅ Updated trading bot capital:")
        print(f"   Gemini: ${new_gemini_capital:.2f} (80% of ${gemini_total_usd:.2f})")
        print(f"   Binance: ${new_binance_capital:.2f}")
    else:
        print(f"⚠️ Could not find capital lines to update")
    
    # Update dashboard data
    print(f"\n4️⃣ UPDATING DASHBOARD DATA:")
    print("-" * 40)
    
    capital_data = {
        "gemini_total": gemini_total_usd,
        "binance_total": binance_total_usdt,
        "total_capital": gemini_total_usd + binance_total_usdt,
        "deployed": total_position_value,
        "available_gemini": gemini_free_usd,
        "available_binance": binance_free_usdt,
        "position_count": len(open_positions),
        "avg_position_value": total_position_value / max(len(open_positions), 1),
        "total_pnl": total_unrealized_pnl,
        "pnl_percent": (total_unrealized_pnl / (gemini_total_usd + binance_total_usdt - total_unrealized_pnl)) * 100 if (gemini_total_usd + binance_total_usdt - total_unrealized_pnl) > 0 else 0,
        "last_updated": datetime.now().isoformat()
    }
    
    # Create trading_data directory if it doesn't exist
    os.makedirs('trading_data', exist_ok=True)
    
    # Write capital.json
    with open('trading_data/capital.json', 'w') as f:
        json.dump(capital_data, f, indent=2)
    
    print(f"✅ Updated dashboard data")
    print(f"   Total Capital: ${capital_data['total_capital']:.2f}")
    print(f"   Gemini: ${capital_data['gemini_total']:.2f}")
    print(f"   Binance: ${capital_data['binance_total']:.2f}")
    
    print(f"\n" + "="*60)
    print("✅ PRIMARY PORTFOLIO READY FOR TRADING!")
    print("="*60)
    print(f"\n📊 NEW FUNDING:")
    print(f"   Gemini: ${gemini_total_usd:.2f} total (${new_gemini_capital:.2f} for trading)")
    print(f"   Binance: ${binance_total_usdt:.2f} total (${new_binance_capital:.2f} for trading)")
    print(f"   Total: ${gemini_total_usd + binance_total_usdt:.2f}")
    
    if binance_free_usdt < 20:
        print(f"\n⚠️ WARNING: Low free margin on Binance (${binance_free_usdt:.2f})")
        print(f"   Consider closing some positions or adding funds")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()