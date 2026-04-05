#!/usr/bin/env python3
"""
FINAL Gemini Clearance - Uses LIMIT orders (Gemini doesn't allow market orders)
"""

import ccxt
import json
import time
from datetime import datetime

print("💰 FINAL GEMINI CLEARANCE (LIMIT ORDERS)")
print("="*60)

def sell_with_limit(exchange, symbol, amount, currency):
    """Sell using limit order at current price"""
    try:
        print(f"  Selling {amount:.8f} {currency} ({symbol})...")
        
        # Get market info
        market = exchange.market(symbol)
        min_amount = market['limits']['amount']['min']
        
        # Check minimum
        if amount < min_amount:
            print(f"    ⚠️  Amount too small (min: {min_amount:.8f})")
            return None, f"Amount below minimum {min_amount:.8f}"
        
        # Get current price
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Use a limit order slightly below current price to ensure execution
        limit_price = current_price * 0.995  # 0.5% below current for quick fill
        value = amount * current_price
        
        print(f"    Current: ${current_price:.2f}, Limit: ${limit_price:.2f}")
        print(f"    Value: ${value:.2f}")
        
        # Place LIMIT sell order (Gemini only allows limit orders)
        order = exchange.create_order(
            symbol=symbol,
            type='limit',
            side='sell',
            amount=amount,
            price=limit_price
        )
        
        print(f"    ✅ LIMIT ORDER PLACED! Order ID: {order['id']}")
        print(f"    Selling {amount:.8f} @ ${limit_price:.2f}")
        
        # Wait and check if order filled
        print(f"    ⏳ Waiting for order execution...")
        time.sleep(5)
        
        # Check order status
        order_info = exchange.fetch_order(order['id'], symbol)
        print(f"    Status: {order_info['status']}")
        print(f"    Filled: {order_info['filled']:.8f}")
        
        return order_info, None
        
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
        
        # Load markets
        exchange.load_markets()
        
        # Get balance
        balance = exchange.fetch_balance()
        
        print("\n📊 GEMINI HOLDINGS:")
        
        # Focus on BTC first (main holding)
        btc_amount = balance['total'].get('BTC', 0)
        usd_cash = balance['total'].get('USD', 0)
        
        if btc_amount > 0:
            print(f"  BTC: {btc_amount:.8f}")
            print(f"  USD Cash: ${usd_cash:.2f}")
            
            # Check BTC minimum
            market = exchange.market('BTC/USD')
            min_btc = market['limits']['amount']['min']
            
            if btc_amount >= min_btc:
                ticker = exchange.fetch_ticker('BTC/USD')
                btc_price = ticker['last']
                btc_value = btc_amount * btc_price
                
                print(f"\n💰 BTC VALUE: ${btc_value:.2f} @ ${btc_price:.2f}")
                print(f"📏 Minimum trade: {min_btc:.8f} BTC")
                
                print("\n" + "="*60)
                print("🚀 SELLING BTC WITH LIMIT ORDER")
                print("="*60)
                
                # Auto-confirm for BTC (main holding)
                print(f"\n⚡ Selling {btc_amount:.8f} BTC (${btc_value:.2f})...")
                
                order, error = sell_with_limit(exchange, 'BTC/USD', btc_amount, 'BTC')
                
                if order:
                    # Save record
                    record = {
                        'timestamp': datetime.now().isoformat(),
                        'action': 'BTC sale',
                        'amount': btc_amount,
                        'order_id': order['id'],
                        'status': order['status'],
                        'filled': float(order['filled']),
                        'symbol': 'BTC/USD'
                    }
                    
                    with open("gemini_btc_limit_sale.json", "w") as f:
                        json.dump(record, f, indent=2)
                    
                    print(f"\n📝 Sale record saved")
                else:
                    print(f"\n❌ BTC sale failed: {error}")
            else:
                print(f"\n❌ BTC amount too small (min: {min_btc:.8f})")
        else:
            print("  No BTC holdings")
        
        # Check other cryptos
        print("\n🔍 OTHER HOLDINGS (small amounts):")
        other_cryptos = []
        for currency, amount in balance['total'].items():
            if amount > 0.00000001 and currency not in ['USD', 'BTC']:
                other_cryptos.append((currency, amount))
                print(f"  {currency}: {amount:.8f}")
        
        if other_cryptos:
            print(f"\n⚠️  {len(other_cryptos)} small holdings may need manual clearance")
            print("   (Amounts may be below Gemini minimums)")
        
        # Check final balance
        print("\n🔄 Checking final balance...")
        final_balance = exchange.fetch_balance()
        final_cash = final_balance['total'].get('USD', 0)
        final_btc = final_balance['total'].get('BTC', 0)
        
        print(f"💰 Final USD cash: ${final_cash:.2f}")
        print(f"💰 Final BTC: {final_btc:.8f}")
        
        if final_btc < btc_amount:
            print(f"✅ BTC reduced by {btc_amount - final_btc:.8f}")
        
        print("\n" + "="*60)
        print("🎯 RECOMMENDATIONS:")
        print("="*60)
        print("\n1. Check Gemini app for order status")
        print("2. Small holdings may need manual sale")
        print("3. Limit orders may take time to fill")
        print("4. Cancel/replace if price moves significantly")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()