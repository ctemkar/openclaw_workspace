#!/usr/bin/env python3
"""
Detailed balance check for Binance and Gemini
"""

import ccxt
import os
import json
from datetime import datetime

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

def check_binance_detailed():
    """Check Binance balance in detail"""
    print("\n" + "="*60)
    print("DETAILED BINANCE BALANCE CHECK")
    print("="*60)
    
    try:
        with open(os.path.join(BASE_DIR, '.binance_key'), 'r') as f:
            api_key = f.read().strip()
        with open(os.path.join(BASE_DIR, '.binance_secret'), 'r') as f:
            api_secret = f.read().strip()
        
        # Initialize Binance with different options
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True
            },
            'enableRateLimit': True
        })
        
        # Test connection first
        print("Testing Binance connection...")
        markets = exchange.load_markets()
        print(f"✅ Connected to Binance. Loaded {len(markets)} markets")
        
        # Fetch balance
        print("\nFetching balance...")
        balance = exchange.fetch_balance()
        
        print("\n📊 BINANCE BALANCE DETAILS:")
        print("-" * 40)
        
        # Check total, used, free for all currencies
        total_balance = 0
        for currency, info in balance.items():
            if isinstance(info, dict) and 'total' in info:
                total = info.get('total', 0)
                free = info.get('free', 0)
                used = info.get('used', 0)
                
                if total > 0 or free > 0 or used > 0:
                    print(f"{currency}:")
                    print(f"  Total: {total:.8f}")
                    print(f"  Free:  {free:.8f}")
                    print(f"  Used:  {used:.8f}")
                    
                    # Try to get USD value for crypto
                    if currency != 'USDT' and currency != 'USD':
                        try:
                            symbol = f"{currency}/USDT"
                            if symbol in markets:
                                ticker = exchange.fetch_ticker(symbol)
                                usd_value = total * ticker['last']
                                print(f"  ≈ ${usd_value:.2f} USD")
                                total_balance += usd_value
                        except:
                            pass
        
        # Check USDT specifically
        if 'USDT' in balance:
            usdt_info = balance['USDT']
            usdt_total = usdt_info.get('total', 0)
            usdt_free = usdt_info.get('free', 0)
            print(f"\n💵 USDT Balance:")
            print(f"  Total: {usdt_total:.2f}")
            print(f"  Free:  {usdt_free:.2f}")
            total_balance += usdt_total
        
        print(f"\n💰 ESTIMATED TOTAL PORTFOLIO VALUE: ${total_balance:.2f}")
        
        return balance
        
    except Exception as e:
        print(f"❌ Error checking Binance: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_gemini_detailed():
    """Check Gemini balance in detail"""
    print("\n" + "="*60)
    print("DETAILED GEMINI BALANCE CHECK")
    print("="*60)
    
    try:
        with open(os.path.join(BASE_DIR, '.gemini_key'), 'r') as f:
            api_key = f.read().strip()
        with open(os.path.join(BASE_DIR, '.gemini_secret'), 'r') as f:
            api_secret = f.read().strip()
        
        # Initialize Gemini
        exchange = ccxt.gemini({
            'apiKey': api_key,
            'secret': api_secret
        })
        
        # Test connection
        print("Testing Gemini connection...")
        markets = exchange.load_markets()
        print(f"✅ Connected to Gemini. Loaded {len(markets)} markets")
        
        # Fetch balance
        print("\nFetching balance...")
        balance = exchange.fetch_balance()
        
        print("\n📊 GEMINI BALANCE DETAILS:")
        print("-" * 40)
        
        # Check total, used, free for all currencies
        total_balance = 0
        for currency, info in balance.items():
            if isinstance(info, dict) and 'total' in info:
                total = info.get('total', 0)
                free = info.get('free', 0)
                used = info.get('used', 0)
                
                if total > 0 or free > 0 or used > 0:
                    print(f"{currency}:")
                    print(f"  Total: {total:.8f}")
                    print(f"  Free:  {free:.8f}")
                    print(f"  Used:  {used:.8f}")
                    
                    # Try to get USD value for crypto
                    if currency != 'USD':
                        try:
                            symbol = f"{currency}/USD"
                            if symbol in markets:
                                ticker = exchange.fetch_ticker(symbol)
                                usd_value = total * ticker['last']
                                print(f"  ≈ ${usd_value:.2f} USD")
                                total_balance += usd_value
                        except:
                            pass
        
        # Check USD specifically
        if 'USD' in balance:
            usd_info = balance['USD']
            usd_total = usd_info.get('total', 0)
            usd_free = usd_info.get('free', 0)
            print(f"\n💵 USD Balance:")
            print(f"  Total: {usd_total:.2f}")
            print(f"  Free:  {usd_free:.2f}")
            total_balance += usd_total
        
        print(f"\n💰 ESTIMATED TOTAL PORTFOLIO VALUE: ${total_balance:.2f}")
        
        return balance
        
    except Exception as e:
        print(f"❌ Error checking Gemini: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("DETAILED EXCHANGE BALANCE CHECK")
    print("="*60)
    
    # Check Binance
    binance_balance = check_binance_detailed()
    
    # Check Gemini
    gemini_balance = check_gemini_detailed()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    print("\n💡 If balances show $0.00, possible reasons:")
    print("1. API keys may have insufficient permissions")
    print("2. Funds might be in a different account type (futures, margin)")
    print("3. API keys could be read-only or disabled")
    print("4. Exchange may require IP whitelisting")
    print("\n✅ Next steps:")
    print("1. Verify API keys have 'trade' permission")
    print("2. Check if funds are in spot wallet")
    print("3. Test API keys with a simple trade or balance query")
    print("4. Consider creating new API keys with proper permissions")

if __name__ == "__main__":
    main()