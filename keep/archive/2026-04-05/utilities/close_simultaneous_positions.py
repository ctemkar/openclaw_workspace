#!/usr/bin/env python3
"""
CLOSE SIMULTANEOUS POSITIONS
Close all simultaneous LONG/SHORT positions to stop hedging losses
"""

import ccxt
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_trades():
    """Load all trades from trades.json"""
    trades_file = os.path.join(BASE_DIR, "trading_data", "trades.json")
    with open(trades_file, 'r') as f:
        return json.load(f)

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

def analyze_simultaneous_positions(trades):
    """Find all simultaneous LONG/SHORT positions"""
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
        
        if asset not in positions:
            positions[asset] = {'gemini': [], 'binance': []}
        
        positions[asset][exchange].append({
            'side': side,
            'symbol': symbol,
            'price': trade.get('price', 0),
            'amount': trade.get('amount', 0),
            'order_id': trade.get('order_id', ''),
            'timestamp': trade.get('timestamp', '')
        })
    
    # Find simultaneous positions
    simultaneous = []
    for asset, data in positions.items():
        gemini_sides = [t['side'] for t in data['gemini']]
        binance_sides = [t['side'] for t in data['binance']]
        
        has_gemini_long = 'buy' in gemini_sides
        has_binance_short = 'sell' in binance_sides
        
        if has_gemini_long and has_binance_short:
            simultaneous.append({
                'asset': asset,
                'gemini_positions': [t for t in data['gemini'] if t['side'] == 'buy'],
                'binance_positions': [t for t in data['binance'] if t['side'] == 'sell']
            })
    
    return simultaneous

def close_gemini_position(exchange, position):
    """Close Gemini LONG position (sell)"""
    try:
        print(f"🚀 Closing Gemini LONG position for {position['asset']}")
        
        # For Gemini, we need to sell to close a LONG position
        symbol = position['gemini_positions'][0]['symbol']  # e.g., "ETH/USD"
        total_amount = sum(p['amount'] for p in position['gemini_positions'])
        
        print(f"  Selling {total_amount:.6f} {position['asset']} on Gemini")
        print(f"  Symbol: {symbol}")
        
        # Place sell order
        order = exchange.create_order(
            symbol=symbol,
            type='market',
            side='sell',
            amount=total_amount
        )
        
        print(f"✅ Gemini position closed: {order['id']}")
        print(f"  Sold {total_amount:.6f} {position['asset']}")
        
        return {
            'asset': position['asset'],
            'exchange': 'gemini',
            'action': 'sell',
            'amount': total_amount,
            'order_id': order['id'],
            'status': 'CLOSED',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error closing Gemini position: {e}")
        return {
            'asset': position['asset'],
            'exchange': 'gemini',
            'status': 'FAILED',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def close_binance_position(exchange, position):
    """Close Binance SHORT position (buy to cover)"""
    try:
        print(f"🚀 Closing Binance SHORT position for {position['asset']}")
        
        # For Binance Futures SHORT, we need to BUY to close
        symbol = position['binance_positions'][0]['symbol']  # e.g., "ETH/USDT"
        total_amount = sum(p['amount'] for p in position['binance_positions'])
        
        print(f"  Buying {total_amount:.6f} {position['asset']} on Binance to cover SHORT")
        print(f"  Symbol: {symbol}")
        
        # Place buy order to cover short
        order = exchange.create_order(
            symbol=symbol,
            type='market',
            side='buy',
            amount=total_amount
        )
        
        print(f"✅ Binance SHORT position closed: {order['id']}")
        print(f"  Bought {total_amount:.6f} {position['asset']} to cover")
        
        return {
            'asset': position['asset'],
            'exchange': 'binance',
            'action': 'buy',
            'amount': total_amount,
            'order_id': order['id'],
            'status': 'CLOSED',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error closing Binance position: {e}")
        return {
            'asset': position['asset'],
            'exchange': 'binance',
            'status': 'FAILED',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def main():
    print("="*70)
    print("🛑 CLOSE SIMULTANEOUS LONG/SHORT POSITIONS")
    print("="*70)
    
    # Load trades
    trades = load_trades()
    print(f"📊 Loaded {len(trades)} trades")
    
    # Find simultaneous positions
    simultaneous = analyze_simultaneous_positions(trades)
    
    if not simultaneous:
        print("✅ No simultaneous positions found. Nothing to close.")
        return
    
    print(f"\n🚨 FOUND {len(simultaneous)} ASSETS WITH SIMULTANEOUS POSITIONS:")
    for pos in simultaneous:
        print(f"  • {pos['asset']}: {len(pos['gemini_positions'])} Gemini LONG, {len(pos['binance_positions'])} Binance SHORT")
    
    print("\n" + "="*70)
    print("⚠️  WARNING: This will close real positions with real money!")
    print("="*70)
    
    # Auto-confirm since user already said "yes"
    print("\n✅ Auto-confirmed: User already provided 'yes' confirmation")
    confirm = 'yes'
    
    # Initialize exchanges
    exchanges = initialize_exchanges()
    
    if not exchanges['gemini'] or not exchanges['binance']:
        print("❌ Cannot proceed - exchange connections not available")
        return
    
    # Close positions
    print("\n" + "="*70)
    print("🔄 CLOSING POSITIONS...")
    print("="*70)
    
    closure_results = []
    
    for position in simultaneous:
        asset = position['asset']
        print(f"\n📊 Processing {asset}...")
        
        # Close Gemini LONG
        if exchanges['gemini']:
            gemini_result = close_gemini_position(exchanges['gemini'], position)
            closure_results.append(gemini_result)
            time.sleep(1)  # Rate limiting
        
        # Close Binance SHORT
        if exchanges['binance']:
            binance_result = close_binance_position(exchanges['binance'], position)
            closure_results.append(binance_result)
            time.sleep(1)  # Rate limiting
    
    # Save closure results
    results_file = os.path.join(BASE_DIR, "trading_data", "position_closures.json")
    with open(results_file, 'w') as f:
        json.dump(closure_results, f, indent=2)
    
    print("\n" + "="*70)
    print("✅ CLOSURE COMPLETE")
    print("="*70)
    
    successful = [r for r in closure_results if r.get('status') == 'CLOSED']
    failed = [r for r in closure_results if r.get('status') == 'FAILED']
    
    print(f"Successful closures: {len(successful)}")
    print(f"Failed closures: {len(failed)}")
    
    if failed:
        print("\n❌ FAILED CLOSURES:")
        for fail in failed:
            print(f"  {fail['asset']} on {fail['exchange']}: {fail.get('error', 'Unknown error')}")
    
    print(f"\n📄 Results saved to: {results_file}")
    print("="*70)

if __name__ == "__main__":
    main()