#!/usr/bin/env python3
"""
CLEAR ALL GEMINI HOLDINGS - Sell everything to USD
"""

import ccxt
import json
from datetime import datetime

print("💰 CLEARING ALL GEMINI HOLDINGS")
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
    
    print("\n📊 CURRENT GEMINI HOLDINGS:")
    holdings = []
    total_value = 0
    
    for currency, amount in balance['total'].items():
        if amount > 0.00000001:  # Ignire tiny amounts
            free = balance['free'].get(currency, 0)
            
            if currency == 'USD':
                print(f"  {currency}: ${amount:.2f} (CASH - KEEP)")
                continue
            
            # Get current price
            try:
                if currency == 'BTC':
                    symbol = 'BTC/USD'
                elif currency == 'ETH':
                    symbol = 'ETH/USD'
                else:
                    symbol = f'{currency}/USD'
                
                ticker = exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                value = amount * current_price
                total_value += value
                
                holdings.append({
                    'currency': currency,
                    'amount': amount,
                    'price': current_price,
                    'value': value,
                    'symbol': symbol
                })
                
                print(f"  {currency}: {amount:.8f} (${value:.2f} @ ${current_price:.2f})")
                
            except Exception as e:
                print(f"  {currency}: {amount:.8f} (Price unavailable)")
    
    print(f"\n💰 TOTAL HOLDINGS VALUE: ${total_value:.2f}")
    
    if not holdings:
        print("\n✅ No holdings to clear (only USD cash)")
        exit(0)
    
    print("\n" + "="*60)
    print("🚀 READY TO SELL ALL HOLDINGS")
    print("="*60)
    
    # Ask for confirmation
    response = input(f"\nSell ALL {len(holdings)} holdings (${total_value:.2f})? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Cancelled")
        exit(0)
    
    print("\n⚡ SELLING HOLDINGS...")
    
    sold_holdings = []
    total_sold = 0
    
    for holding in holdings:
        try:
            currency = holding['currency']
            amount = holding['amount']
            symbol = holding['symbol']
            
            print(f"\n📤 Selling {amount:.8f} {currency}...")
            
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
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Failed to sell {currency}: {e}")
    
    print("\n" + "="*60)
    print("🎯 SALE COMPLETE!")
    print("="*60)
    print(f"\n💰 Total sold: ${total_sold:.2f}")
    print(f"📊 Holdings cleared: {len(sold_holdings)}")
    
    # Save sale record
    sale_record = {
        'timestamp': datetime.now().isoformat(),
        'total_sold': total_sold,
        'holdings': sold_holdings
    }
    
    with open("gemini_clearance_record.json", "w") as f:
        json.dump(sale_record, f, indent=2)
    
    print(f"\n📝 Sale record saved to: gemini_clearance_record.json")
    
    # Check new balance
    print("\n🔄 Checking new balance...")
    new_balance = exchange.fetch_balance()
    new_cash = new_balance['total'].get('USD', 0)
    print(f"💰 New USD cash balance: ${new_cash:.2f}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ Script complete")
print("="*60)