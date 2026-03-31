#!/usr/bin/env python3
"""
Check REAL positions on Binance vs our records
"""

import ccxt
import json

def load_binance_keys():
    """Load Binance API keys"""
    try:
        with open("secure_keys/.binance_key", "r") as f:
            api_key = f.read().strip()
        with open("secure_keys/.binance_secret", "r") as f:
            api_secret = f.read().strip()
        return api_key, api_secret
    except Exception as e:
        print(f"❌ Failed to load Binance keys: {e}")
        return None, None

def check_real_vs_recorded():
    """Compare real Binance positions with our records"""
    
    print("🔍 CHECKING REAL VS RECORDED POSITIONS")
    print("=" * 60)
    
    # Load API keys
    api_key, api_secret = load_binance_keys()
    if not api_key or not api_secret:
        return
    
    # Initialize Binance Futures
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',
        }
    })
    
    # Get real positions from Binance
    print("\n📊 REAL POSITIONS ON BINANCE:")
    real_positions = exchange.fetch_positions()
    open_real_positions = []
    
    for pos in real_positions:
        contracts = float(pos['contracts'])
        if contracts != 0:
            open_real_positions.append(pos)
            print(f"  {pos['symbol']}: {contracts} contracts | P&L: ${pos['unrealizedPnl']:.2f}")
    
    print(f"\n✅ Real open positions: {len(open_real_positions)}")
    
    # Get our recorded positions
    print("\n📊 OUR RECORDED POSITIONS:")
    try:
        with open('26_crypto_trade_history.json', 'r') as f:
            recorded = json.load(f)
        
        open_recorded = [p for p in recorded if p.get('status') == 'OPEN']
        closed_recorded = [p for p in recorded if p.get('status') == 'CLOSED']
        
        print(f"Open: {len(open_recorded)}")
        for pos in open_recorded:
            print(f"  {pos['symbol']}: {pos.get('pnl_percent', 0):.2f}%")
        
        print(f"\nClosed: {len(closed_recorded)}")
        
    except Exception as e:
        print(f"Error reading recorded positions: {e}")
    
    # Compare
    print("\n🔍 COMPARISON:")
    real_symbols = {p['symbol'] for p in open_real_positions}
    recorded_symbols = {p['symbol'] for p in open_recorded}
    
    print(f"Real but not recorded: {real_symbols - recorded_symbols}")
    print(f"Recorded but not real: {recorded_symbols - real_symbols}")
    
    # Check balance
    print("\n💰 AVAILABLE BALANCE:")
    balance = exchange.fetch_balance()
    print(f"Free USDT: ${balance['USDT']['free']:.2f}")
    print(f"Total USDT: ${balance['USDT']['total']:.2f}")
    
    return open_real_positions, open_recorded

def fix_corrupted_data(real_positions):
    """Fix corrupted position data"""
    print("\n🛠️  FIXING CORRUPTED DATA...")
    
    # Create clean position data
    clean_positions = []
    
    for pos in real_positions:
        contracts = float(pos['contracts'])
        if contracts != 0:
            # This is a REAL open position
            clean_positions.append({
                'exchange': 'binance',
                'symbol': pos['symbol'],
                'side': 'sell' if contracts < 0 else 'buy',
                'type': 'SHORT' if contracts < 0 else 'LONG',
                'entry_price': float(pos['entryPrice']),
                'current_price': float(pos['markPrice']),
                'position_size': abs(contracts * float(pos['entryPrice'])),
                'unrealized_pnl': float(pos['unrealizedPnl']),
                'pnl_percent': (float(pos['unrealizedPnl']) / abs(contracts * float(pos['entryPrice']))) * 100,
                'status': 'OPEN',
                'amount': abs(contracts),
                'leverage': 3,
                'notes': 'REAL POSITION - CORRECTED'
            })
    
    # Also add recently closed positions
    try:
        with open('26_crypto_trade_history.json', 'r') as f:
            old_data = json.load(f)
        
        # Keep only CLOSED positions from old data
        closed_positions = [p for p in old_data if p.get('status') == 'CLOSED']
        
        # Combine
        all_positions = clean_positions + closed_positions
        
        # Save
        with open('26_crypto_trade_history_CORRECTED.json', 'w') as f:
            json.dump(all_positions, f, indent=2)
        
        print(f"✅ Created corrected file with:")
        print(f"   {len(clean_positions)} open positions")
        print(f"   {len(closed_positions)} closed positions")
        
        # Replace old file
        import shutil
        shutil.copy('26_crypto_trade_history_CORRECTED.json', '26_crypto_trade_history.json')
        print("✅ Replaced corrupted file with corrected data")
        
    except Exception as e:
        print(f"❌ Error fixing data: {e}")

if __name__ == "__main__":
    real_positions, recorded_positions = check_real_vs_recorded()
    
    if real_positions:
        fix_corrupted_data(real_positions)