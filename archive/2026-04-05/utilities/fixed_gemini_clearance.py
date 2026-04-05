#!/usr/bin/env python3
"""
FIXED Gemini Clearance Script
Properly sells all Gemini holdings
"""

import ccxt
import json
import time
from datetime import datetime

print("💰 FIXED GEMINI CLEARANCE")
print("="*60)

def safe_sell(exchange, symbol, amount, currency):
    """Safely sell cryptocurrency with proper error handling"""
    try:
        print(f"  Selling {amount:.8f} {currency} ({symbol})...")
        
        # Get market info
        market = exchange.market(symbol)
        min_amount = market['limits']['amount']['min']
        
        # Check minimum
        if amount < min_amount:
            print(f"    ⚠️  Amount too small (min: {min_amount:.8f})")
            return None, f"Amount below minimum {min_amount:.8f}"
        
        # Get current price for logging
        ticker = exchange.fetch_ticker(symbol)
        price = ticker['last']
        value = amount * price
        
        print(f"    Price: ${price:.2f}, Value: ${value:.2f}")
        
        # Place market sell order
        order = exchange.create_order(
            symbol=symbol,
            type='market',
            side='sell',
            amount=amount
        )
        
        print(f"    ✅ SOLD! Order ID: {order['id']}")
        return order, None
        
    except Exception as e:
        error_msg = str(e)
        print(f"    ❌ Failed: {error_msg[:100]}")
        return None, error_msg

def main():
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
        
        # Load markets (CRITICAL FIX!)
        print("📊 Loading Gemini markets...")
        exchange.load_markets()
        print(f"✅ Loaded {len(exchange.markets)} markets")
        
        # Get full balance
        balance = exchange.fetch_balance()
        
        print("\n📊 GEMINI HOLDINGS:")
        
        # Map cryptocurrencies to their Gemini symbols
        # Gemini uses CRYPTO/USD format
        crypto_to_symbol = {
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
            'YFI': 'YFI/USD',
            'FET': 'FET/USD',  # Added based on your holdings
            'PEPE': 'PEPE/USD',  # May not exist
            'BONK': 'BONK/USD',  # May not exist
        }
        
        holdings = []
        total_estimated_value = 0
        
        for currency, amount in balance['total'].items():
            if amount > 0.00000001 and currency != 'USD':
                free = balance['free'].get(currency, 0)
                
                if currency in crypto_to_symbol:
                    symbol = crypto_to_symbol[currency]
                    
                    # Check if symbol exists
                    if symbol in exchange.markets:
                        try:
                            ticker = exchange.fetch_ticker(symbol)
                            price = ticker['last']
                            value = amount * price
                            total_estimated_value += value
                            
                            holdings.append({
                                'currency': currency,
                                'amount': amount,
                                'free': free,
                                'symbol': symbol,
                                'price': price,
                                'value': value
                            })
                            
                            print(f"  {currency}: {amount:.8f} (${value:.2f} @ ${price:.2f})")
                            
                        except Exception as e:
                            print(f"  {currency}: {amount:.8f} (Price error: {str(e)[:50]})")
                    else:
                        print(f"  {currency}: {amount:.8f} (No {symbol} market)")
                else:
                    print(f"  {currency}: {amount:.8f} (Unknown symbol mapping)")
        
        print(f"\n💰 TOTAL ESTIMATED VALUE: ${total_estimated_value:.2f}")
        
        if not holdings:
            print("\n✅ No standard Gemini holdings to clear")
            return
        
        print("\n" + "="*60)
        print("🚀 READY TO SELL")
        print("="*60)
        
        # Ask for confirmation
        response = input(f"\nSell {len(holdings)} holdings (${total_estimated_value:.2f})? (yes/no): ")
        
        if response.lower() != 'yes':
            print("❌ Cancelled")
            return
        
        print("\n⚡ SELLING HOLDINGS...")
        
        sold_holdings = []
        failed_holdings = []
        total_sold_value = 0
        
        for holding in holdings:
            currency = holding['currency']
            amount = holding['amount']
            symbol = holding['symbol']
            
            order, error = safe_sell(exchange, symbol, amount, currency)
            
            if order:
                sold_holdings.append({
                    'currency': currency,
                    'amount': amount,
                    'symbol': symbol,
                    'order_id': order['id'],
                    'timestamp': datetime.now().isoformat()
                })
                total_sold_value += holding['value']
            else:
                failed_holdings.append({
                    'currency': currency,
                    'amount': amount,
                    'symbol': symbol,
                    'error': error
                })
            
            # Rate limiting
            time.sleep(2)
        
        print("\n" + "="*60)
        print("🎯 CLEARANCE COMPLETE")
        print("="*60)
        
        print(f"\n✅ Successfully sold: {len(sold_holdings)} holdings")
        print(f"❌ Failed to sell: {len(failed_holdings)} holdings")
        print(f"💰 Estimated total sold: ${total_sold_value:.2f}")
        
        if sold_holdings:
            # Save success record
            success_record = {
                'timestamp': datetime.now().isoformat(),
                'total_sold_value': total_sold_value,
                'holdings': sold_holdings
            }
            
            with open("gemini_successful_clearance.json", "w") as f:
                json.dump(success_record, f, indent=2)
            
            print(f"\n📝 Success record saved: gemini_successful_clearance.json")
        
        if failed_holdings:
            # Save failure record
            failure_record = {
                'timestamp': datetime.now().isoformat(),
                'failed_holdings': failed_holdings
            }
            
            with open("gemini_failed_clearance.json", "w") as f:
                json.dump(failure_record, f, indent=2)
            
            print(f"📝 Failure record saved: gemini_failed_clearance.json")
        
        # Check new balance
        print("\n🔄 Checking new balance...")
        new_balance = exchange.fetch_balance()
        new_cash = new_balance['total'].get('USD', 0)
        
        print(f"💰 New USD cash balance: ${new_cash:.2f}")
        
        # Show remaining holdings
        print("\n📋 REMAINING HOLDINGS:")
        remaining = False
        for currency, amount in new_balance['total'].items():
            if amount > 0.00000001 and currency != 'USD':
                print(f"  {currency}: {amount:.8f}")
                remaining = True
        
        if not remaining:
            print("  None (all cleared!)")
        
        print("\n" + "="*60)
        print("✅ FIXED CLEARANCE COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()