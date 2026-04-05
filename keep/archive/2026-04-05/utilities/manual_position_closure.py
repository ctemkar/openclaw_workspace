#!/usr/bin/env python3
"""
MANUAL POSITION CLOSURE WITH PROPER ORDER TYPES
Uses limit orders for Gemini and handles small positions
"""

import ccxt
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def initialize_exchanges():
    """Initialize exchange connections"""
    exchanges = {}
    
    # Initialize Gemini
    gemini_key = os.getenv('GEMINI_API_KEY')
    gemini_secret = os.getenv('GEMINI_API_SECRET')
    
    if gemini_key and gemini_secret:
        exchanges['gemini'] = ccxt.gemini({
            'apiKey': gemini_key,
            'secret': gemini_secret,
            'enableRateLimit': True,
        })
        print("✅ Gemini exchange initialized")
    else:
        exchanges['gemini'] = None
        print("⚠️ Gemini API keys not found")
    
    # Initialize Binance Futures
    binance_key = os.getenv('BINANCE_API_KEY')
    binance_secret = os.getenv('BINANCE_API_SECRET')
    
    if binance_key and binance_secret:
        exchanges['binance'] = ccxt.binance({
            'apiKey': binance_key,
            'secret': binance_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'},
        })
        print("✅ Binance Futures exchange initialized")
    else:
        exchanges['binance'] = None
        print("⚠️ Binance API keys not found")
    
    return exchanges

def get_current_price(exchange, symbol):
    """Get current market price"""
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        print(f"❌ Error getting price for {symbol}: {e}")
        return None

def close_gemini_position_limit(exchange, asset, total_amount):
    """Close Gemini LONG position using LIMIT order"""
    try:
        symbol = f"{asset}/USD"
        current_price = get_current_price(exchange, symbol)
        
        if not current_price:
            print(f"❌ Cannot get price for {symbol}")
            return None
        
        # Set limit price slightly below current for quick fill
        limit_price = current_price * 0.995  # 0.5% below market
        
        print(f"📊 Closing Gemini {asset} LONG:")
        print(f"  Symbol: {symbol}")
        print(f"  Amount: {total_amount:.6f}")
        print(f"  Current: ${current_price:.2f}")
        print(f"  Limit: ${limit_price:.2f} (0.5% below)")
        
        # Place LIMIT sell order
        order = exchange.create_order(
            symbol=symbol,
            type='limit',
            side='sell',
            amount=total_amount,
            price=limit_price
        )
        
        print(f"✅ Gemini LIMIT SELL order placed: {order['id']}")
        print(f"  Selling {total_amount:.6f} {asset} at ${limit_price:.2f}")
        
        return order
        
    except Exception as e:
        print(f"❌ Error closing Gemini {asset}: {e}")
        return None

def close_binance_position_with_adjustment(exchange, asset, total_amount):
    """Close Binance SHORT position with amount adjustment"""
    try:
        symbol = f"{asset}/USDT"
        
        # Check minimum amount for Binance
        market = exchange.load_markets()
        market_info = market.get(symbol)
        
        if not market_info:
            print(f"❌ Market info not found for {symbol}")
            return None
        
        # Get precision requirements
        amount_precision = market_info['precision']['amount']
        min_amount = market_info['limits']['amount']['min']
        
        print(f"📊 Binance requirements for {symbol}:")
        print(f"  Amount precision: {amount_precision}")
        print(f"  Minimum amount: {min_amount}")
        print(f"  Our amount: {total_amount:.6f}")
        
        # Adjust amount to meet minimum
        if total_amount < min_amount:
            print(f"⚠️  Amount {total_amount:.6f} below minimum {min_amount}")
            print(f"   Need to increase position or use different approach")
            return None
        
        # Round to proper precision
        adjusted_amount = exchange.amount_to_precision(symbol, total_amount)
        
        current_price = get_current_price(exchange, symbol)
        if not current_price:
            return None
        
        # For Binance Futures SHORT, we BUY to close
        # Use market order for Binance (they allow it)
        print(f"🚀 Closing Binance {asset} SHORT:")
        print(f"  Symbol: {symbol}")
        print(f"  Amount: {adjusted_amount} (adjusted)")
        print(f"  Current: ${current_price:.2f}")
        
        order = exchange.create_order(
            symbol=symbol,
            type='market',
            side='buy',  # BUY to close SHORT
            amount=adjusted_amount
        )
        
        print(f"✅ Binance MARKET BUY order placed: {order['id']}")
        print(f"  Buying {adjusted_amount} {asset} to cover SHORT")
        
        return order
        
    except Exception as e:
        print(f"❌ Error closing Binance {asset}: {e}")
        return None

def analyze_positions():
    """Analyze current positions from trades.json"""
    trades_file = os.path.join(BASE_DIR, "trading_data", "trades.json")
    
    with open(trades_file, 'r') as f:
        trades = json.load(f)
    
    positions = {}
    for trade in trades:
        symbol = trade.get('symbol', '')
        if '/' in symbol:
            asset = symbol.split('/')[0]
        elif ':' in symbol:
            asset = symbol.split(':')[0]
        else:
            asset = symbol.replace('USDT', '').replace('USD', '')
        
        exchange = trade.get('exchange', '')
        side = trade.get('side', '')
        amount = trade.get('amount', 0)
        
        if asset not in positions:
            positions[asset] = {'gemini': [], 'binance': []}
        
        if exchange == 'gemini' and side == 'buy':
            positions[asset]['gemini'].append(amount)
        elif exchange == 'binance' and side == 'sell':
            positions[asset]['binance'].append(amount)
    
    # Calculate totals
    result = {}
    for asset, data in positions.items():
        gemini_total = sum(data['gemini'])
        binance_total = sum(data['binance'])
        
        if gemini_total > 0 or binance_total > 0:
            result[asset] = {
                'gemini_total': gemini_total,
                'binance_total': binance_total,
                'gemini_count': len(data['gemini']),
                'binance_count': len(data['binance'])
            }
    
    return result

def main():
    print("="*70)
    print("🛠️  MANUAL POSITION CLOSURE WITH PROPER ORDER TYPES")
    print("="*70)
    
    # Analyze positions
    positions = analyze_positions()
    
    print(f"\n📊 POSITION ANALYSIS:")
    for asset, data in positions.items():
        if data['gemini_total'] > 0 and data['binance_total'] > 0:
            print(f"🚨 {asset}: {data['gemini_total']:.6f} Gemini LONG, {data['binance_total']:.6f} Binance SHORT")
        elif data['gemini_total'] > 0:
            print(f"🔵 {asset}: {data['gemini_total']:.6f} Gemini LONG only")
        elif data['binance_total'] > 0:
            print(f"🟡 {asset}: {data['binance_total']:.6f} Binance SHORT only")
    
    # Initialize exchanges
    exchanges = initialize_exchanges()
    
    if not exchanges['gemini'] or not exchanges['binance']:
        print("❌ Cannot proceed - exchange connections not available")
        return
    
    print("\n" + "="*70)
    print("🔄 ATTEMPTING CLOSURE WITH PROPER ORDER TYPES")
    print("="*70)
    
    results = []
    
    for asset, data in positions.items():
        # Close Gemini LONG if exists
        if data['gemini_total'] > 0:
            print(f"\n📊 Processing Gemini {asset} LONG...")
            order = close_gemini_position_limit(exchanges['gemini'], asset, data['gemini_total'])
            if order:
                results.append({
                    'asset': asset,
                    'exchange': 'gemini',
                    'order_id': order.get('id'),
                    'status': 'SUCCESS'
                })
        
        # Close Binance SHORT if exists
        if data['binance_total'] > 0:
            print(f"\n📊 Processing Binance {asset} SHORT...")
            order = close_binance_position_with_adjustment(exchanges['binance'], asset, data['binance_total'])
            if order:
                results.append({
                    'asset': asset,
                    'exchange': 'binance',
                    'order_id': order.get('id'),
                    'status': 'SUCCESS'
                })
    
    # Save results
    results_file = os.path.join(BASE_DIR, "trading_data", "manual_closure_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*70)
    print("📋 CLOSURE ATTEMPT COMPLETE")
    print("="*70)
    
    successful = [r for r in results if r.get('status') == 'SUCCESS']
    print(f"Successful closures: {len(successful)}")
    print(f"Results saved to: {results_file}")
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. Check if limit orders were filled on Gemini")
    print("2. For Binance margin errors, may need to add more margin")
    print("3. Very small positions may need to be closed manually via UI")
    print("="*70)

if __name__ == "__main__":
    main()