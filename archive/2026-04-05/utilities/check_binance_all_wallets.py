#!/usr/bin/env python3
"""
Check Binance ALL wallet types for USDT balance
"""

import ccxt
import os
import json
from datetime import datetime

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

def check_all_binance_balances():
    """Check all Binance account types"""
    print("=" * 70)
    print("CHECKING BINANCE ALL WALLET TYPES")
    print("=" * 70)
    
    try:
        # Read keys
        with open(os.path.join(BASE_DIR, '.binance_key'), 'r') as f:
            api_key = f.read().strip()
        with open(os.path.join(BASE_DIR, '.binance_secret'), 'r') as f:
            api_secret = f.read().strip()
        
        print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
        print(f"Secret: {'*' * len(api_secret)}")
        
        # Try different account types
        account_types = ['spot', 'margin', 'future', 'delivery']
        
        total_usdt = 0
        
        for acc_type in account_types:
            print(f"\n🔍 Checking {acc_type.upper()} account...")
            
            try:
                if acc_type == 'spot':
                    exchange = ccxt.binance({
                        'apiKey': api_key,
                        'secret': api_secret,
                        'options': {'defaultType': 'spot'},
                        'enableRateLimit': True
                    })
                elif acc_type == 'margin':
                    exchange = ccxt.binance({
                        'apiKey': api_key,
                        'secret': api_secret,
                        'options': {'defaultType': 'margin'},
                        'enableRateLimit': True
                    })
                elif acc_type == 'future':
                    exchange = ccxt.binance({
                        'apiKey': api_key,
                        'secret': api_secret,
                        'options': {'defaultType': 'future'},
                        'enableRateLimit': True
                    })
                elif acc_type == 'delivery':
                    exchange = ccxt.binance({
                        'apiKey': api_key,
                        'secret': api_secret,
                        'options': {'defaultType': 'delivery'},
                        'enableRateLimit': True
                    })
                
                # Fetch balance
                balance = exchange.fetch_balance()
                
                # Check for USDT
                if 'USDT' in balance:
                    usdt_free = balance['USDT'].get('free', 0)
                    usdt_used = balance['USDT'].get('used', 0)
                    usdt_total = balance['USDT'].get('total', 0)
                    
                    if usdt_total > 0:
                        print(f"  ✅ USDT found in {acc_type}:")
                        print(f"     Free:  ${usdt_free:.2f}")
                        print(f"     Used:  ${usdt_used:.2f}")
                        print(f"     Total: ${usdt_total:.2f}")
                        total_usdt += usdt_total
                    else:
                        print(f"  ⚠️  No USDT in {acc_type}")
                else:
                    print(f"  ⚠️  USDT not found in {acc_type} balance response")
                    
            except Exception as e:
                print(f"  ❌ Error checking {acc_type}: {e}")
        
        print(f"\n" + "=" * 70)
        print("💰 TOTAL USDT ACROSS ALL ACCOUNTS:")
        print(f"   ${total_usdt:.2f}")
        
        if total_usdt >= 50:
            print(f"✅ SUFFICIENT FUNDS: ${total_usdt:.2f} available")
            print(f"💡 Transfer at least $50 to SPOT wallet for trading")
        elif total_usdt > 0:
            print(f"⚠️  LOW BALANCE: ${total_usdt:.2f} total (need $50+)")
        else:
            print(f"❌ NO USDT FOUND in any account")
            print(f"💡 Check if funds are in a different currency")
        
        # Also check other stablecoins
        print(f"\n🔍 Checking other stablecoins...")
        try:
            exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'options': {'defaultType': 'spot'},
                'enableRateLimit': True
            })
            
            balance = exchange.fetch_balance()
            
            stablecoins = ['USDC', 'BUSD', 'TUSD', 'DAI', 'PAX']
            for coin in stablecoins:
                if coin in balance:
                    amount = balance[coin].get('total', 0)
                    if amount > 0:
                        print(f"  ✅ {coin}: ${amount:.2f}")
        
        except Exception as e:
            print(f"  Error checking stablecoins: {e}")
        
        print(f"\n" + "=" * 70)
        print("🎯 RECOMMENDED ACTION:")
        print("1. Go to Binance → Wallet → Overview")
        print("2. Find your $77.68 USDT")
        print("3. Click 'Transfer'")
        print("4. Move $50+ to SPOT wallet")
        print("5. The trading bot will detect it immediately")
        
        return total_usdt
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

def main():
    """Main function"""
    print("FIND YOUR BINANCE USDT BALANCE")
    print("=" * 70)
    print("You have $77.68 USDT but API shows $0.00")
    print("This means funds are NOT in SPOT wallet")
    print("=" * 70)
    
    total = check_all_binance_balances()
    
    print(f"\n⏰ Checked at: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()