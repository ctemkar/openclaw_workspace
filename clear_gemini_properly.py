#!/usr/bin/env python3
"""
CLEAR GEMINI PROPERLY - Sell everything that's sellable
"""

import ccxt
import json
from datetime import datetime

print("💰 CLEARING GEMINI PROPERLY")
print("="*60)

try:
    # Load Gemini keys
    with open("secure_keys/.gemini_key", "r") as f:
        GEMINI_KEY = f.read().strip()
    with open("secure_keys/.gemini_secret", "r") as f:
        GEMINI_SECRET = f.read().strip()
    
    print("✅ Gemini API keys loaded")
    
    # Initialize Gemini
    exchange = ccxt.gemini({
        'apiKey': GEMINI_KEY,
        'secret': GEMINI_SECRET,
        'enableRateLimit': True,
    })
    
    # Get full balance
    balance = exchange.fetch_balance()
    
    print("\n📊 GEMINI HOLDINGS:")
    
    # Known Gemini trading pairs
    gemini_pairs = {
        'BTC': 'BTC/USD',
        'ETH': 'ETH/USD', 
        'SOL': 'SOL/USD',
        'XRP': 'XRP/USD',
        'DOT': 'DOT/USD',
        'DOGE': 'DOGE/USD',
        'AVAX': 'AVAX/USD',
        'LINK': 'LINK/USD',
        'UNI': 'UNI/USD',
        'LTC': 'LTC/USD',
        'ATOM': 'ATOM/USD',
        'FIL': 'FIL/USD',
        'XTZ': 'XTZ/USD',
        'AAVE': 'AAVE/USD',
        'COMP': 'COMP/USD',
        'YFI': 'YFI/USD'
    }
    
    holdings_to_sell = []
    total_value = 0
    
    for currency, amount in balance['total'].items():
        if amount > 0.000001 and currency != 'USD':
            free = balance['free'].get(currency, 0)
            
            if currency in gemini_pairs:
                symbol = gemini_pairs[currency]
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    current_price = ticker['last']
                    value = amount * current_price
                    total_value += value
                    
                    holdings_to_sell.append({
                        'currency': currency,
                        'amount': amount,
                        'price': current_price,
                        'value': value,
                        'symbol': symbol
                    })
                    
                    print(f"  {currency}: {amount:.8f} (${value:.2f} @ ${current_price:.2f}) - WILL SELL")
                    
                except Exception as e:
                    print(f"  {currency}: {amount:.8f} (Cannot get price: {e})")
            else:
                print(f"  {currency}: {amount:.8f} (Not a standard Gemini pair - may need manual sale)")
    
    print(f"\n💰 TOTAL SELLABLE VALUE: ${total_value:.2f}")
    
    if not holdings_to_sell:
        print("\n✅ No standard Gemini holdings to clear")
        print("   (Only USD cash or non-standard tokens)")
        exit(0)
    
    print("\n" + "="*60)
    print("🚀 SELLING GEMINI HOLDINGS")
    print("="*60)
    
    sold_holdings = []
    total_sold = 0
    
    for holding in holdings_to_sell:
        try:
            currency = holding['currency']
            amount = holding['amount']
            symbol = holding['symbol']
            
            print(f"\n📤 Selling {amount:.8f} {currency} ({symbol})...")
            
            # Check minimum order size
            market = exchange.market(symbol)
            min_amount = market['limits']['amount']['min']
            
            if amount < min_amount:
                print(f"   ⚠️  Amount too small (min: {min_amount:.8f}) - skipping")
                continue
            
            # Place market sell order
            order = exchange.create_order(
                symbol=symbol,
                type='market',
                side='sell',
                amount=amount
            )
            
            sold_value = holding['value']
            total_sold += sold_value
            
            print(f"✅ SOLD: {amount:.8f} {currency} for ~${sold_value:.2f}")
            print(f"   Order ID: {order['id']}")
            
            sold_holdings.append({
                'currency': currency,
                'amount': amount,
                'order_id': order['id'],
                'timestamp': datetime.now().isoformat()
            })
            
            # Small delay to avoid rate limits
            import time
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Failed to sell {currency}: {e}")
    
    print("\n" + "="*60)
    print("🎯 GEMINI CLEARANCE COMPLETE")
    print("="*60)
    print(f"\n💰 Total sold: ${total_sold:.2f}")
    print(f"📊 Holdings sold: {len(sold_holdings)}")
    
    # Save sale record
    if sold_holdings:
        sale_record = {
            'timestamp': datetime.now().isoformat(),
            'total_sold': total_sold,
            'holdings': sold_holdings
        }
        
        with open("gemini_proper_clearance.json", "w") as f:
            json.dump(sale_record, f, indent=2)
        
        print(f"\n📝 Sale record saved: gemini_proper_clearance.json")
    
    # Check new balance
    print("\n🔄 Checking new balance...")
    new_balance = exchange.fetch_balance()
    new_cash = new_balance['total'].get('USD', 0)
    
    print(f"💰 New USD cash balance: ${new_cash:.2f}")
    
    # Show what's left
    print("\n📋 REMAINING HOLDINGS (if any):")
    for currency, amount in new_balance['total'].items():
        if amount > 0.000001 and currency != 'USD':
            print(f"  {currency}: {amount:.8f} (may need manual clearance)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ Script complete")
print("="*60)