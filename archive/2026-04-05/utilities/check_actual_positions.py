#!/usr/bin/env python3
"""
CHECK ACTUAL POSITIONS USING APIS
Fetches real positions from Gemini and Binance and compares with dashboard data
"""

import ccxt
import json
import os
import sys
from datetime import datetime

print("="*70)
print("🔍 CHECKING ACTUAL POSITIONS USING EXCHANGE APIS")
print("="*70)

# Load from .env file directly
def load_env_file():
    """Load environment variables from .env file"""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        return env_vars
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return {}

env_vars = load_env_file()

# Get API keys
gemini_key = env_vars.get('GEMINI_API_KEY')
gemini_secret = env_vars.get('GEMINI_API_SECRET')
binance_key = env_vars.get('BINANCE_API_KEY')
binance_secret = env_vars.get('BINANCE_API_SECRET')

print(f"Found {len(env_vars)} environment variables in .env")

# Initialize exchanges
exchanges = {}

if gemini_key and gemini_secret:
    try:
        exchanges['gemini'] = ccxt.gemini({
            'apiKey': gemini_key,
            'secret': gemini_secret,
            'enableRateLimit': True,
        })
        print("✅ Gemini API connected")
    except Exception as e:
        print(f"❌ Gemini connection failed: {e}")
else:
    print("⚠️ Gemini API keys not found in environment")

if binance_key and binance_secret:
    try:
        exchanges['binance'] = ccxt.binance({
            'apiKey': binance_key,
            'secret': binance_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'},
        })
        print("✅ Binance Futures API connected")
    except Exception as e:
        print(f"❌ Binance connection failed: {e}")
else:
    print("⚠️ Binance API keys not found in environment")

if not exchanges:
    print("\n🚨 CRITICAL: No exchange connections available")
    print("Please check if API keys are set in .env file")
    sys.exit(1)

# Fetch actual positions
print("\n" + "="*70)
print("💰 FETCHING ACTUAL POSITIONS FROM EXCHANGES")
print("="*70)

actual_positions = {'gemini': {}, 'binance': {}}

# Check Gemini (spot)
if 'gemini' in exchanges:
    try:
        print("\n🔍 Checking Gemini (Spot)...")
        
        # Fetch balance
        balance = exchanges['gemini'].fetch_balance()
        print("  Available balances:")
        for currency, amount in balance['free'].items():
            if amount > 0.000001:  # Very small threshold
                print(f"    {currency}: {amount:.6f}")
                actual_positions['gemini'][currency] = {
                    'amount': amount,
                    'type': 'spot'
                }
        
        # Fetch open orders
        open_orders = exchanges['gemini'].fetch_open_orders()
        print(f"  Open orders: {len(open_orders)}")
        for order in open_orders:
            symbol = order['symbol']
            side = order['side']
            amount = order['amount']
            price = order['price']
            print(f"    {symbol}: {side.upper()} {amount:.6f} @ ${price:.2f}")
            
            # Extract asset from symbol
            if '/' in symbol:
                asset = symbol.split('/')[0]
                actual_positions['gemini'][asset] = {
                    'amount': amount,
                    'type': 'open_order',
                    'side': side,
                    'price': price,
                    'order_id': order['id']
                }
        
    except Exception as e:
        print(f"❌ Error fetching Gemini data: {e}")

# Check Binance (futures)
if 'binance' in exchanges:
    try:
        print("\n🔍 Checking Binance (Futures)...")
        
        # Fetch positions
        positions = exchanges['binance'].fetch_positions()
        open_positions = [p for p in positions if abs(p['contracts']) > 0]
        
        print(f"  Open futures positions: {len(open_positions)}")
        for pos in open_positions:
            symbol = pos['symbol']
            side = pos['side']
            contracts = pos['contracts']
            entry_price = pos['entryPrice']
            unrealized_pnl = pos['unrealizedPnl']
            
            # Extract asset from symbol (remove /USDT)
            asset = symbol.replace('/USDT', '').replace(':USDT', '')
            
            print(f"    {symbol}: {side.upper()} {contracts} contracts")
            print(f"      Entry: ${entry_price:.2f}, Unrealized P&L: ${unrealized_pnl:.2f}")
            
            actual_positions['binance'][asset] = {
                'contracts': contracts,
                'side': side,
                'entry_price': entry_price,
                'unrealized_pnl': unrealized_pnl,
                'type': 'futures'
            }
        
        # Fetch balance
        balance = exchanges['binance'].fetch_balance()
        print(f"  Total balance: ${balance['total']['USDT']:.2f} USDT")
        print(f"  Free balance: ${balance['free']['USDT']:.2f} USDT")
        
    except Exception as e:
        print(f"❌ Error fetching Binance data: {e}")

# Load dashboard data
print("\n" + "="*70)
print("📊 LOADING DASHBOARD DATA")
print("="*70)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
trades_file = os.path.join(BASE_DIR, "trading_data", "trades.json")

dashboard_positions = {'gemini': {}, 'binance': {}}

try:
    with open(trades_file, 'r') as f:
        trades = json.load(f)
    
    print(f"Total trades in dashboard: {len(trades)}")
    
    # Process trades
    for trade in trades:
        symbol = trade.get('symbol', '')
        exchange = trade.get('exchange', '')
        side = trade.get('side', '')
        amount = trade.get('amount', 0)
        
        # Extract asset
        if '/' in symbol:
            asset = symbol.split('/')[0]
        elif ':' in symbol:
            asset = symbol.split(':')[0]
        else:
            asset = symbol.replace('USDT', '').replace('USD', '')
        
        if exchange == 'gemini' and side == 'buy':
            if asset not in dashboard_positions['gemini']:
                dashboard_positions['gemini'][asset] = 0
            dashboard_positions['gemini'][asset] += amount
        
        elif exchange == 'binance' and side == 'sell':
            if asset not in dashboard_positions['binance']:
                dashboard_positions['binance'][asset] = 0
            dashboard_positions['binance'][asset] += amount
    
    print("\n🔵 Dashboard Gemini LONG positions:")
    for asset, amount in dashboard_positions['gemini'].items():
        print(f"    {asset}: {amount:.6f}")
    
    print("\n🟡 Dashboard Binance SHORT positions:")
    for asset, amount in dashboard_positions['binance'].items():
        print(f"    {asset}: {amount:.6f}")
        
except Exception as e:
    print(f"❌ Error loading dashboard data: {e}")

# Compare
print("\n" + "="*70)
print("🔍 COMPARISON: ACTUAL VS DASHBOARD")
print("="*70)

print("\n🔵 GEMINI COMPARISON:")
gemini_mismatches = []

for asset in set(list(actual_positions['gemini'].keys()) + list(dashboard_positions['gemini'].keys())):
    actual = actual_positions['gemini'].get(asset)
    dashboard = dashboard_positions['gemini'].get(asset)
    
    actual_amount = actual['amount'] if actual else 0
    dashboard_amount = dashboard if dashboard else 0
    
    if abs(actual_amount - dashboard_amount) > 0.000001:
        gemini_mismatches.append(asset)
        print(f"🚨 {asset}: Actual={actual_amount:.6f}, Dashboard={dashboard_amount:.6f}")
    else:
        print(f"✅ {asset}: Matched ({actual_amount:.6f})")

print("\n🟡 BINANCE COMPARISON:")
binance_mismatches = []

for asset in set(list(actual_positions['binance'].keys()) + list(dashboard_positions['binance'].keys())):
    actual = actual_positions['binance'].get(asset)
    dashboard = dashboard_positions['binance'].get(asset)
    
    actual_amount = abs(actual['contracts']) if actual else 0
    dashboard_amount = dashboard if dashboard else 0
    
    if abs(actual_amount - dashboard_amount) > 0.000001:
        binance_mismatches.append(asset)
        print(f"🚨 {asset}: Actual={actual_amount:.6f}, Dashboard={dashboard_amount:.6f}")
    else:
        print(f"✅ {asset}: Matched ({actual_amount:.6f})")

print("\n" + "="*70)
print("📋 SUMMARY")
print("="*70)

print(f"Gemini mismatches: {len(gemini_mismatches)} assets")
if gemini_mismatches:
    print("  " + ", ".join(gemini_mismatches))

print(f"\nBinance mismatches: {len(binance_mismatches)} assets")
if binance_mismatches:
    print("  " + ", ".join(binance_mismatches))

print("\n💡 INTERPRETATION:")
print("1. Mismatches mean dashboard doesn't match reality")
print("2. Could be due to: positions closed, orders not filled, API errors")
print("3. Check if Gemini has open LIMIT orders (not filled yet)")
print("4. Check if Binance positions were actually closed")

print("\n🚨 RECOMMENDED ACTIONS:")
if gemini_mismatches:
    print("1. Check Gemini open orders - LIMIT SELLs may not be filled")
if binance_mismatches:
    print("2. Verify Binance positions were actually closed")
print("3. Update dashboard to track open/closed status")
print("="*70)

# Save results
results = {
    'timestamp': datetime.now().isoformat(),
    'actual_positions': actual_positions,
    'dashboard_positions': dashboard_positions,
    'mismatches': {
        'gemini': gemini_mismatches,
        'binance': binance_mismatches
    }
}

results_file = os.path.join(BASE_DIR, "trading_data", "position_comparison.json")
with open(results_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n📄 Results saved to: {results_file}")