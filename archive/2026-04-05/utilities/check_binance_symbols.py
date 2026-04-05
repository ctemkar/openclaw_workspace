#!/usr/bin/env python3
"""
Check which symbols are available on Binance Futures
"""

import ccxt
import os

print("🔍 CHECKING BINANCE FUTURES SYMBOLS")
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

try:
    # Fetch all markets
    markets = exchange.load_markets()
    
    # Our target cryptos
    target_cryptos = [
        'BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
        'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI', 'SNX', 'MKR', 'BAT',
        'ZRX', 'OMG', 'ENJ', 'MATIC', 'SUSHI', 'CRV'
    ]
    
    print(f"\n📊 CHECKING {len(target_cryptos)} CRYPTOS:")
    print("-" * 40)
    
    available = []
    not_available = []
    
    for crypto in target_cryptos:
        symbol = f"{crypto}/USDT:USDT"
        if symbol in markets:
            market = markets[symbol]
            available.append({
                'crypto': crypto,
                'symbol': symbol,
                'active': market.get('active', False),
                'type': market.get('type', 'unknown')
            })
        else:
            # Try alternative symbol format
            symbol2 = f"{crypto}USDT"
            if symbol2 in markets:
                market = markets[symbol2]
                available.append({
                    'crypto': crypto,
                    'symbol': symbol2,
                    'active': market.get('active', False),
                    'type': market.get('type', 'unknown')
                })
            else:
                not_available.append(crypto)
    
    print(f"✅ AVAILABLE ({len(available)}):")
    for item in available:
        status = "🟢" if item['active'] else "🟡"
        print(f"   {status} {item['crypto']}: {item['symbol']} ({item['type']})")
    
    print(f"\n❌ NOT AVAILABLE ({len(not_available)}):")
    for crypto in not_available:
        print(f"   🔴 {crypto}")
    
    # Check specific problematic ones
    print(f"\n🔍 SPECIFIC CHECKS:")
    for crypto in ['MATIC', 'MKR']:
        symbol = f"{crypto}/USDT:USDT"
        if symbol in markets:
            market = markets[symbol]
            print(f"   {crypto}: {symbol} - Active: {market.get('active', 'N/A')}")
            
            # Check if trading is restricted
            info = market.get('info', {})
            if 'status' in info:
                print(f"     Status: {info['status']}")
            if 'permissions' in info:
                print(f"     Permissions: {info['permissions']}")
        else:
            print(f"   {crypto}: Symbol not found")
    
    # Update bot configuration
    print(f"\n🔄 UPDATING BOT CONFIGURATION...")
    
    # Read current bot config
    with open('real_26_crypto_trader.py', 'r') as f:
        content = f.read()
    
    # Create new list of available cryptos
    available_cryptos = [item['crypto'] for item in available if item['active']]
    
    print(f"   Available for trading: {len(available_cryptos)} cryptos")
    print(f"   List: {', '.join(available_cryptos)}")
    
    # Update the ALL_CRYPTOS list in the bot
    old_list = "ALL_CRYPTOS = [\n    'BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',\n    'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI', 'SNX', 'MKR', 'BAT',\n    'ZRX', 'OMG', 'ENJ', 'MATIC', 'SUSHI', 'CRV'\n]"
    
    new_list = "ALL_CRYPTOS = [\n    "
    new_list += "', '".join(available_cryptos)
    new_list += "\n]"
    
    if old_list in content:
        content = content.replace(old_list, new_list)
        
        with open('real_26_crypto_trader.py', 'w') as f:
            f.write(content)
        
        print(f"✅ Updated bot configuration")
        print(f"   Now trading {len(available_cryptos)} available cryptos")
    else:
        print(f"⚠️ Could not find ALL_CRYPTOS list to update")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)