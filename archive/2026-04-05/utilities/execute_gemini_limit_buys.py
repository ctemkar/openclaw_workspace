#!/usr/bin/env python3
"""
Execute LIMIT buy orders on Gemini
Gemini only supports limit orders
"""

import ccxt
import json
from datetime import datetime

def execute_limit_buys():
    """Execute limit buy orders on Gemini"""
    
    print("🎯 EXECUTING GEMINI LIMIT BUY ORDERS")
    print("=" * 50)
    
    try:
        with open('secure_keys/gemini_keys.json') as f:
            gemini_keys = json.load(f)
        
        gemini = ccxt.gemini({
            'apiKey': gemini_keys['api_key'],
            'secret': gemini_keys['api_secret']
        })
        
        print("✅ Gemini connected")
        
        # Check balance
        balance = gemini.fetch_balance()
        usd_available = balance.get('USD', {}).get('free', 0)
        print(f"💰 Available USD: ${usd_available:.2f}")
        
        if usd_available < 15:
            print(f"⚠️ Low USD balance, using ${min(usd_available, 10):.2f}")
            amount_usd = min(usd_available, 10)
        else:
            amount_usd = 5.00
        
        # Limit buy orders (place slightly below current price)
        limit_buys = [
            {"symbol": "ETH/USD", "amount_usd": amount_usd, "price_offset": -0.001},  # 0.1% below
            {"symbol": "SOL/USD", "amount_usd": amount_usd, "price_offset": -0.001},
        ]
        
        executed_orders = []
        
        for buy in limit_buys:
            symbol = buy["symbol"]
            amount_usd = buy["amount_usd"]
            price_offset = buy["price_offset"]
            
            try:
                # Get current price
                ticker = gemini.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Calculate limit price (slightly below current)
                limit_price = current_price * (1 + price_offset)
                
                # Calculate amount in crypto
                amount = amount_usd / limit_price
                
                print(f"\n🔍 {symbol}:")
                print(f"   Current: ${current_price:.4f}")
                print(f"   Limit price: ${limit_price:.4f} ({price_offset*100:+.2f}%)")
                print(f"   Amount USD: ${amount_usd:.2f}")
                print(f"   Amount crypto: {amount:.6f}")
                
                # Execute LIMIT buy order
                print(f"   📤 Placing LIMIT BUY order at ${limit_price:.4f}...")
                
                try:
                    order = gemini.create_limit_buy_order(symbol, amount, limit_price)
                    
                    print(f"   ✅ LIMIT ORDER PLACED!")
                    print(f"   Order ID: {order.get('id', 'N/A')}")
                    print(f"   Status: {order.get('status', 'unknown')}")
                    print(f"   Price: ${order.get('price', limit_price):.4f}")
                    print(f"   Amount: {order.get('amount', amount):.6f}")
                    
                    executed_orders.append({
                        "symbol": symbol,
                        "order_id": order.get('id'),
                        "amount": amount,
                        "limit_price": limit_price,
                        "current_price": current_price,
                        "amount_usd": amount_usd,
                        "status": order.get('status', 'open'),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    print(f"   ❌ Order failed: {str(e)[:60]}")
                
            except Exception as e:
                print(f"❌ Error with {symbol}: {str(e)[:40]}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 ORDER SUMMARY:")
        print("=" * 50)
        
        if executed_orders:
            print(f"✅ {len(executed_orders)} limit buy orders PLACED")
            
            open_orders = [o for o in executed_orders if o['status'] == 'open']
            if open_orders:
                print(f"📋 {len(open_orders)} orders are OPEN (waiting to fill)")
                for order in open_orders:
                    print(f"  • {order['symbol']}: {order['amount']:.6f} at ${order['limit_price']:.4f}")
                
                print("\n💡 LIMIT ORDERS:")
                print("  • Will execute when price reaches limit price")
                print("  • Check Gemini website/app for order status")
                print("  • Orders may take time to fill")
            else:
                print("  All orders filled immediately!")
            
            # Update trades.json with pending orders
            print("\n📝 Adding pending orders to trades.json...")
            try:
                with open('trading_data/trades.json', 'r') as f:
                    trades = json.load(f)
                
                for order in executed_orders:
                    if order['status'] == 'open':
                        trade = {
                            "exchange": "gemini",
                            "symbol": order['symbol'],
                            "side": "buy",
                            "price": order['limit_price'],
                            "amount": order['amount'],
                            "value": order['amount_usd'],
                            "order_id": f"LIMIT_PENDING_{order['order_id']}",
                            "timestamp": order['timestamp'],
                            "current_price": order['current_price'],
                            "pnl": 0.0,
                            "pnl_percent": 0.0,
                            "current_value": order['amount_usd'],
                            "last_updated": order['timestamp'],
                            "signal": "LIMIT_BUY_PENDING",
                            "confidence": 100.0,
                            "execution_type": "limit_order_pending",
                            "status": "pending"
                        }
                        trades.append(trade)
                
                with open('trading_data/trades.json', 'w') as f:
                    json.dump(trades, f, indent=2)
                
                print(f"✅ Added {len(executed_orders)} pending limit orders to trades.json")
                
            except Exception as e:
                print(f"❌ Error updating trades.json: {e}")
                
        else:
            print("❌ No orders placed")
        
        print("\n🔍 Check Gemini for order status:")
        print("   https://exchange.gemini.com/orders")
        print("\n💡 Next steps:")
        print("   1. Wait for limit orders to fill")
        print("   2. Check balances on Gemini")
        print("   3. Dashboards will update when orders fill")
        
    except Exception as e:
        print(f"❌ Gemini connection error: {e}")

if __name__ == "__main__":
    execute_limit_buys()
