#!/usr/bin/env python3
"""
Check Binance balance and margin status
"""

import os
import sys
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Read Binance API keys from secure_keys/
try:
    with open('secure_keys/.binance_key', 'r') as f:
        api_key = f.read().strip()
    with open('secure_keys/.binance_secret', 'r') as f:
        api_secret = f.read().strip()
except FileNotFoundError as e:
    print(f"❌ Error reading API keys: {e}")
    sys.exit(1)

print("🔍 Checking Binance Account Status")
print("="*60)

try:
    # Initialize client
    client = Client(api_key, api_secret)
    
    # Get account info
    account = client.futures_account()
    
    print(f"✅ Account connected")
    print(f"   Total margin balance: ${float(account['totalMarginBalance']):.2f}")
    print(f"   Total wallet balance: ${float(account['totalWalletBalance']):.2f}")
    print(f"   Available balance: ${float(account['availableBalance']):.2f}")
    print(f"   Unrealized P&L: ${float(account['totalUnrealizedProfit']):.2f}")
    
    # Check positions
    positions = client.futures_position_information()
    open_positions = [p for p in positions if float(p['positionAmt']) != 0]
    
    print(f"\n📊 Open Positions: {len(open_positions)}")
    for pos in open_positions:
        symbol = pos['symbol']
        amount = float(pos['positionAmt'])
        entry_price = float(pos['entryPrice'])
        mark_price = float(pos['markPrice'])
        pnl = float(pos['unRealizedProfit'])
        leverage = float(pos['leverage'])
        
        print(f"   {symbol}: {amount} contracts")
        print(f"     Entry: ${entry_price:.2f}, Current: ${mark_price:.2f}")
        print(f"     P&L: ${pnl:.2f}, Leverage: {leverage}x")
    
    # Check margin requirements
    print(f"\n💰 Margin Requirements:")
    print(f"   Initial margin: ${float(account['totalInitialMargin']):.2f}")
    print(f"   Maintenance margin: ${float(account['totalMaintMargin']):.2f}")
    print(f"   Margin ratio: {float(account['marginRatio'])*100:.2f}%")
    
    # Check if we can open a $13.43 position
    required_margin = 13.43  # Position size bot is trying
    available = float(account['availableBalance'])
    
    print(f"\n🔍 Can we open a ${required_margin:.2f} position?")
    print(f"   Available balance: ${available:.2f}")
    print(f"   Required: ${required_margin:.2f}")
    
    if available >= required_margin:
        print(f"   ✅ YES - Sufficient margin available")
    else:
        print(f"   ❌ NO - Insufficient margin")
        print(f"   Need ${required_margin - available:.2f} more")
        
    # Check if we need to enable cross margin
    print(f"\n⚙️ Account Mode:")
    print(f"   Position mode: {account['positionMode']}")
    print(f"   Multi-assets mode: {account['multiAssetsMargin']}")
    
except BinanceAPIException as e:
    print(f"❌ Binance API error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)