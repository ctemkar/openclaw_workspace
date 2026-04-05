#!/usr/bin/env python3
"""
Execute REAL buy orders on Gemini
Small test orders to verify execution
"""

import ccxt
import json
from datetime import datetime

def execute_real_buys():
    """Execute small real buy orders on Gemini"""
    
    print("🎯 EXECUTING REAL GEMINI BUY ORDERS")
    print("=" * 50)
    
    try:
        with open('secure_keys/gemini_keys.json') as f:
            gemini_keys = json.load(f)
        
        gemini = ccxt.gemini({
            'apiKey': gemini_keys['api_key'],
            'secret': gemini_keys['api_secret']
        })
        
        print("✅ Gemini connected")
        
        # Check balance first
        balance = gemini.fetch_balance()
        usd_available = balance.get('USD', {}).get('free', 0)
        print(f"💰 Available USD: ${usd_available:.2f}")
        
        if usd_available < 10:
            print("❌ Insufficient USD for buy orders")
            return
        
        # Small test buys (total ~$15)
        test_buys = [
            {"symbol": "ETH/USD", "amount_usd": 5.00},
            {"symbol": "SOL/USD", "amount_usd": 5.00},
            {"symbol": "LINK/USD", "amount_usd": 5.00}
        ]
        
        executed_orders = []
        
        for buy in test_buys:
            symbol = buy["symbol"]
            amount_usd = buy["amount_usd"]
            
            try:
                # Get current price
                ticker = gemini.fetch_ticker(symbol)
                price = ticker['last']
                
                # Calculate amount in crypto
                amount = amount_usd / price
                
                print(f"\n🔍 {symbol}:")
                print(f"   Price: ${price:.4f}")
                print(f"   Amount USD: ${amount_usd:.2f}")
                print(f"   Amount crypto: {amount:.6f}")
                
                # Execute market buy order
                print(f"   📤 Placing MARKET BUY order...")
                
                try:
                    order = gemini.create_market_buy_order(symbol, amount)
                    
                    print(f"   ✅ ORDER EXECUTED!")
                    print(f"   Order ID: {order.get('id', 'N/A')}")
                    print(f"   Filled: {order.get('filled', 0):.6f}")
                    print(f"   Cost: ${order.get('cost', 0):.2f}")
                    
                    executed_orders.append({
                        "symbol": symbol,
                        "order_id": order.get('id'),
                        "amount": amount,
                        "price": price,
                        "cost": order.get('cost', amount_usd),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    print(f"   ❌ Order failed: {str(e)[:50]}")
                
            except Exception as e:
                print(f"❌ Error with {symbol}: {str(e)[:40]}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 EXECUTION SUMMARY:")
        print("=" * 50)
        
        if executed_orders:
            print(f"✅ {len(executed_orders)} real buy orders executed")
            total_cost = sum(o['cost'] for o in executed_orders)
            print(f"💰 Total cost: ${total_cost:.2f}")
            
            print("\n🔄 Checking updated balance...")
            updated_balance = gemini.fetch_balance()
            
            for order in executed_orders:
                crypto = order['symbol'].split('/')[0]
                holding = updated_balance.get(crypto, {}).get('total', 0)
                print(f"  {crypto}: {holding:.6f}")
            
            # Update trades.json with REAL trades
            print("\n📝 Updating trades.json with real trades...")
            try:
                with open('trading_data/trades.json', 'r') as f:
                    trades = json.load(f)
                
                for order in executed_orders:
                    trade = {
                        "exchange": "gemini",
                        "symbol": order['symbol'],
                        "side": "buy",
                        "price": order['price'],
                        "amount": order['amount'],
                        "value": order['cost'],
                        "order_id": f"REAL_{order['order_id']}",
                        "timestamp": order['timestamp'],
                        "current_price": order['price'],
                        "pnl": 0.0,
                        "pnl_percent": 0.0,
                        "current_value": order['cost'],
                        "last_updated": order['timestamp'],
                        "signal": "REAL_BUY_TEST",
                        "confidence": 100.0,
                        "execution_type": "real_market_order"
                    }
                    trades.append(trade)
                
                with open('trading_data/trades.json', 'w') as f:
                    json.dump(trades, f, indent=2)
                
                print(f"✅ Added {len(executed_orders)} real trades to trades.json")
                
            except Exception as e:
                print(f"❌ Error updating trades.json: {e}")
                
        else:
            print("❌ No orders executed")
        
        print("\n🔗 Dashboards will update with real trades on next refresh")
        
    except Exception as e:
        print(f"❌ Gemini connection error: {e}")

if __name__ == "__main__":
    execute_real_buys()
