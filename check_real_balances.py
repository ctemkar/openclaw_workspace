#!/usr/bin/env python3
"""
Check REAL balances on Gemini and Binance
NO HARDCODED VALUES - REAL DATA ONLY
"""

import os
import ccxt
import json
from datetime import datetime

# Load API keys
def load_api_keys():
    """Load Gemini and Binance API keys"""
    keys = {}
    try:
        # Gemini
        with open("secure_keys/.gemini_key", "r") as f:
            keys['gemini_key'] = f.read().strip()
        with open("secure_keys/.gemini_secret", "r") as f:
            keys['gemini_secret'] = f.read().strip()
        print("✅ Gemini API keys loaded")
    except Exception as e:
        print(f"❌ Failed to load Gemini keys: {e}")
        keys['gemini_key'] = None
        keys['gemini_secret'] = None
    
    try:
        # Binance
        with open("secure_keys/.binance_key", "r") as f:
            keys['binance_key'] = f.read().strip()
        with open("secure_keys/.binance_secret", "r") as f:
            keys['binance_secret'] = f.read().strip()
        print("✅ Binance API keys loaded")
    except Exception as e:
        print(f"❌ Failed to load Binance keys: {e}")
        keys['binance_key'] = None
        keys['binance_secret'] = None
    
    return keys

def init_exchanges(keys):
    """Initialize Gemini and Binance exchanges"""
    exchanges = {}
    
    # Initialize Gemini
    if keys['gemini_key'] and keys['gemini_secret']:
        exchanges['gemini'] = ccxt.gemini({
            'apiKey': keys['gemini_key'],
            'secret': keys['gemini_secret'],
            'enableRateLimit': True,
        })
        print("✅ Gemini exchange initialized")
    else:
        exchanges['gemini'] = None
        print("⚠️ Gemini exchange not available")
    
    # Initialize Binance Futures
    if keys['binance_key'] and keys['binance_secret']:
        exchanges['binance'] = ccxt.binance({
            'apiKey': keys['binance_key'],
            'secret': keys['binance_secret'],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
            }
        })
        print("✅ Binance Futures exchange initialized")
    else:
        exchanges['binance'] = None
        print("⚠️ Binance exchange not available")
    
    return exchanges

def check_gemini_balances(exchange):
    """Check REAL Gemini balances"""
    print("\n" + "="*60)
    print("♊ GEMINI REAL BALANCES")
    print("="*60)
    
    try:
        # Fetch balance
        balance = exchange.fetch_balance()
        
        # Get total USD value
        total_usd = balance.get('total', {}).get('USD', 0)
        free_usd = balance.get('free', {}).get('USD', 0)
        used_usd = balance.get('used', {}).get('USD', 0)
        
        print(f"💰 Total USD: ${total_usd:.2f}")
        print(f"💵 Free USD: ${free_usd:.2f}")
        print(f"📊 Used USD: ${used_usd:.2f}")
        
        # Check crypto holdings
        print("\n📈 Crypto Holdings:")
        cryptos = ['BTC', 'ETH', 'SOL', 'XRP', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI', 
                  'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI']
        
        holdings = []
        for crypto in cryptos:
            amount = balance.get('total', {}).get(crypto, 0)
            if amount > 0:
                # Get current price
                try:
                    ticker = exchange.fetch_ticker(f"{crypto}/USD")
                    price = ticker['last']
                    value = amount * price
                    holdings.append({
                        'crypto': crypto,
                        'amount': amount,
                        'price': price,
                        'value': value
                    })
                    print(f"  • {crypto}: {amount:.6f} (${value:.2f})")
                except Exception as e:
                    print(f"  • {crypto}: {amount:.6f} (price unavailable)")
        
        print(f"\n📊 Total crypto holdings: {len(holdings)} positions")
        
        return {
            'total_usd': total_usd,
            'free_usd': free_usd,
            'used_usd': used_usd,
            'holdings': holdings,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error fetching Gemini balance: {e}")
        return None

def check_binance_balances(exchange):
    """Check REAL Binance Futures balances"""
    print("\n" + "="*60)
    print("₿ BINANCE FUTURES REAL BALANCES")
    print("="*60)
    
    try:
        # Fetch balance
        balance = exchange.fetch_balance()
        
        # Get total USD value
        total_usd = balance.get('total', {}).get('USDT', 0)
        free_usd = balance.get('free', {}).get('USDT', 0)
        used_usd = balance.get('used', {}).get('USDT', 0)
        
        print(f"💰 Total USDT: ${total_usd:.2f}")
        print(f"💵 Free USDT: ${free_usd:.2f}")
        print(f"📊 Used USDT: ${used_usd:.2f}")
        
        # Check positions
        print("\n📈 Open Positions:")
        try:
            positions = exchange.fetch_positions()
            open_positions = []
            for pos in positions:
                if float(pos['contracts']) > 0:
                    symbol = pos['symbol']
                    side = pos['side']
                    contracts = float(pos['contracts'])
                    entry_price = float(pos['entryPrice'])
                    mark_price = float(pos['markPrice'])
                    unrealized_pnl = float(pos['unrealizedPnl'])
                    
                    open_positions.append({
                        'symbol': symbol,
                        'side': side,
                        'contracts': contracts,
                        'entry_price': entry_price,
                        'mark_price': mark_price,
                        'unrealized_pnl': unrealized_pnl
                    })
                    
                    pnl_color = "🟢" if unrealized_pnl >= 0 else "🔴"
                    print(f"  • {symbol} {side}: {contracts} contracts")
                    print(f"    Entry: ${entry_price:.2f}, Mark: ${mark_price:.2f}")
                    print(f"    P&L: {pnl_color} ${unrealized_pnl:.2f}")
            
            print(f"\n📊 Total open positions: {len(open_positions)}")
            
            return {
                'total_usdt': total_usd,
                'free_usdt': free_usd,
                'used_usdt': used_usd,
                'open_positions': open_positions,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error fetching positions: {e}")
            return {
                'total_usdt': total_usd,
                'free_usdt': free_usd,
                'used_usdt': used_usd,
                'open_positions': [],
                'timestamp': datetime.now().isoformat()
            }
        
    except Exception as e:
        print(f"❌ Error fetching Binance balance: {e}")
        return None

def main():
    print("🔍 CHECKING REAL BALANCES - NO HARDCODED VALUES")
    print("="*60)
    
    # Load keys
    keys = load_api_keys()
    
    # Initialize exchanges
    exchanges = init_exchanges(keys)
    
    results = {}
    
    # Check Gemini
    if exchanges['gemini']:
        gemini_data = check_gemini_balances(exchanges['gemini'])
        results['gemini'] = gemini_data
    else:
        print("\n⚠️ Skipping Gemini - exchange not available")
    
    # Check Binance
    if exchanges['binance']:
        binance_data = check_binance_balances(exchanges['binance'])
        results['binance'] = binance_data
    else:
        print("\n⚠️ Skipping Binance - exchange not available")
    
    # Save results
    with open('real_balances.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*60)
    print("✅ REAL BALANCE CHECK COMPLETE")
    print("📁 Results saved to real_balances.json")
    print("="*60)

if __name__ == "__main__":
    main()