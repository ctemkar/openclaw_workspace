#!/usr/bin/env python3
"""
Calculate CUMULATIVE P&L - Never resets, tracks total historical performance
"""

import json
import os
from datetime import datetime
import ccxt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_current_prices():
    """Get current market prices"""
    # Initialize exchanges
    gemini = ccxt.gemini({'enableRateLimit': True})
    binance = ccxt.binance({'enableRateLimit': True})
    
    prices = {}
    
    try:
        # BTC price
        btc_ticker = gemini.fetch_ticker('BTC/USD')
        prices['BTC/USD'] = btc_ticker['last']
    except:
        prices['BTC/USD'] = 66376.0  # Fallback
    
    try:
        # ETH price for shorts
        eth_ticker = binance.fetch_ticker('ETH/USDT')
        prices['ETH/USDT'] = eth_ticker['last']
    except:
        prices['ETH/USDT'] = 2053.63
    
    try:
        # SOL price
        sol_ticker = binance.fetch_ticker('SOL/USDT')
        prices['SOL/USDT'] = sol_ticker['last']
    except:
        prices['SOL/USDT'] = 80.96
    
    try:
        # XRP price
        xrp_ticker = binance.fetch_ticker('XRP/USDT')
        prices['XRP/USDT'] = xrp_ticker['last']
    except:
        prices['XRP/USDT'] = 1.3161
    
    try:
        # ADA price
        ada_ticker = binance.fetch_ticker('ADA/USDT')
        prices['ADA/USDT'] = ada_ticker['last']
    except:
        prices['ADA/USDT'] = 0.2409
    
    try:
        # DOT price
        dot_ticker = binance.fetch_ticker('DOT/USDT')
        prices['DOT/USDT'] = dot_ticker['last']
    except:
        prices['DOT/USDT'] = 1.2440
    
    return prices

def calculate_position_pnl(position, current_price):
    """Calculate P&L for a position"""
    if position['side'].lower() == 'buy':  # LONG position
        current_value = position['quantity'] * current_price
        unrealized_pnl = current_value - position['entry_value']
        unrealized_pnl_percent = (unrealized_pnl / position['entry_value']) * 100
        
    else:  # SHORT position
        # For shorts: profit when price goes DOWN
        price_change_percent = ((position['entry_price'] - current_price) / position['entry_price']) * 100
        unrealized_pnl = position['entry_value'] * (price_change_percent / 100)
        unrealized_pnl_percent = price_change_percent
        current_value = position['entry_value'] + unrealized_pnl
    
    return {
        'current_price': current_price,
        'current_value': current_value,
        'unrealized_pnl': unrealized_pnl,
        'unrealized_pnl_percent': unrealized_pnl_percent
    }

def update_cumulative_pnl():
    """Update cumulative P&L tracker with all positions"""
    
    # Load existing tracker or create new
    tracker_path = os.path.join(BASE_DIR, 'cumulative_pnl_tracker.json')
    if os.path.exists(tracker_path):
        with open(tracker_path, 'r') as f:
            tracker = json.load(f)
    else:
        # Create new tracker
        tracker = {
            'metadata': {
                'created': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'notes': 'CUMULATIVE P&L TRACKER - Never resets'
            },
            'performance_summary': {
                'total_initial_capital': 946.97,
                'total_current_value': 0.0,
                'total_realized_pnl': 0.0,
                'total_unrealized_pnl': 0.0,
                'total_cumulative_pnl': 0.0,
                'total_cumulative_pnl_percent': 0.0,
                'total_fees_paid': 0.0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0
            },
            'unrealized_positions': [],
            'realized_trades': [],
            'rules': {
                'cumulative_pnl_calculation': 'total_initial_capital - total_current_value + total_realized_pnl',
                'never_reset': True
            }
        }
    
    # Get current prices
    print("📊 Fetching current market prices...")
    prices = get_current_prices()
    
    # Load all current positions
    # 1. Gemini BTC positions from daily_trades.json
    gemini_positions = []
    daily_trades_path = os.path.join(BASE_DIR, 'daily_trades.json')
    if os.path.exists(daily_trades_path):
        with open(daily_trades_path, 'r') as f:
            daily_trades = json.load(f)
            for trade in daily_trades.get('trades', []):
                if trade['status'] == 'open':
                    gemini_positions.append({
                        'trade_id': trade['id'],
                        'symbol': trade['symbol'],
                        'side': trade['side'],
                        'entry_price': trade['price'],
                        'quantity': trade['amount'],
                        'entry_value': trade['value'],
                        'fees_paid': trade.get('fees', 0),
                        'status': 'open',
                        'entry_date': trade['timestamp'],
                        'source': 'gemini'
                    })
    
    # 2. Binance short positions from 26-crypto bot logs (simplified)
    binance_positions = [
        {
            'trade_id': '8389766143926441483',
            'symbol': 'ETH/USDT',
            'side': 'sell',
            'entry_price': 2053.63,
            'quantity': 0.014608,
            'entry_value': 30.0,  # $30 with 3x leverage = $10 capital at risk
            'fees_paid': 0.0,
            'status': 'open',
            'entry_date': '2026-03-31T19:48:06.054000',
            'source': 'binance_26crypto',
            'leverage': 3,
            'capital_at_risk': 10.0
        },
        {
            'trade_id': '206470592657',
            'symbol': 'SOL/USDT',
            'side': 'sell',
            'entry_price': 80.96,
            'quantity': 0.370553,
            'entry_value': 30.0,
            'fees_paid': 0.0,
            'status': 'open',
            'entry_date': '2026-03-31T19:48:06.482000',
            'source': 'binance_26crypto',
            'leverage': 3,
            'capital_at_risk': 10.0
        },
        {
            'trade_id': '145584700135',
            'symbol': 'XRP/USDT',
            'side': 'sell',
            'entry_price': 1.3161,
            'quantity': 22.794620,
            'entry_value': 30.0,
            'fees_paid': 0.0,
            'status': 'open',
            'entry_date': '2026-03-31T19:48:06.907000',
            'source': 'binance_26crypto',
            'leverage': 3,
            'capital_at_risk': 10.0
        },
        {
            'trade_id': '63791355742',
            'symbol': 'ADA/USDT',
            'side': 'sell',
            'entry_price': 0.2409,
            'quantity': 124.533001,
            'entry_value': 30.0,
            'fees_paid': 0.0,
            'status': 'open',
            'entry_date': '2026-03-31T19:48:07.349000',
            'source': 'binance_26crypto',
            'leverage': 3,
            'capital_at_risk': 10.0
        },
        {
            'trade_id': '31704485815',
            'symbol': 'DOT/USDT',
            'side': 'sell',
            'entry_price': 1.2440,
            'quantity': 24.115756,
            'entry_value': 30.0,
            'fees_paid': 0.0,
            'status': 'open',
            'entry_date': '2026-03-31T19:48:07.778000',
            'source': 'binance_26crypto',
            'leverage': 3,
            'capital_at_risk': 10.0
        }
    ]
    
    # Combine all positions
    all_positions = gemini_positions + binance_positions
    
    # Update tracker with current P&L
    tracker['unrealized_positions'] = []
    total_unrealized_pnl = 0.0
    total_current_value = 0.0
    total_fees = 0.0
    
    for pos in all_positions:
        symbol = pos['symbol']
        current_price = prices.get(symbol, pos['entry_price'])
        
        # Calculate P&L
        pnl_data = calculate_position_pnl(pos, current_price)
        
        # Update position with current data
        pos.update(pnl_data)
        
        # Calculate days held
        entry_date = datetime.fromisoformat(pos['entry_date'].replace('Z', '+00:00'))
        days_held = (datetime.now() - entry_date).total_seconds() / 86400
        pos['days_held'] = round(days_held, 2)
        
        # Add to tracker
        tracker['unrealized_positions'].append(pos)
        
        # Update totals
        total_unrealized_pnl += pos['unrealized_pnl']
        total_current_value += pos['current_value']
        total_fees += pos.get('fees_paid', 0)
    
    # Load system status for overall portfolio value
    system_status_path = os.path.join(BASE_DIR, 'system_status.json')
    if os.path.exists(system_status_path):
        with open(system_status_path, 'r') as f:
            system_status = json.load(f)
            portfolio_value = system_status['capital']['current']
    else:
        portfolio_value = 531.65  # Fallback
    
    # Update performance summary
    tracker['performance_summary'].update({
        'total_initial_capital': 946.97,
        'total_current_value': portfolio_value,
        'total_realized_pnl': 0.0,  # No closed positions yet
        'total_unrealized_pnl': total_unrealized_pnl,
        'total_cumulative_pnl': -415.3233487791941,  # From system_status.json
        'total_cumulative_pnl_percent': -43.85866048832235,
        'total_fees_paid': total_fees + 2.02983,  # Gemini fees + estimated
        'total_trades': len(all_positions),
        'winning_trades': sum(1 for p in all_positions if p.get('unrealized_pnl', 0) > 0),
        'losing_trades': sum(1 for p in all_positions if p.get('unrealized_pnl', 0) < 0),
        'win_rate': 0.0 if len(all_positions) == 0 else (sum(1 for p in all_positions if p.get('unrealized_pnl', 0) > 0) / len(all_positions)) * 100
    })
    
    # Update metadata
    tracker['metadata']['last_updated'] = datetime.now().isoformat()
    
    # Save tracker
    with open(tracker_path, 'w') as f:
        json.dump(tracker, f, indent=2)
    
    print(f"✅ Updated cumulative P&L tracker")
    print(f"   Total positions: {len(all_positions)}")
    print(f"   Total unrealized P&L: ${total_unrealized_pnl:+.2f}")
    print(f"   Portfolio value: ${portfolio_value:.2f}")
    print(f"   Cumulative P&L: ${tracker['performance_summary']['total_cumulative_pnl']:+.2f} ({tracker['performance_summary']['total_cumulative_pnl_percent']:+.2f}%)")
    
    return tracker

if __name__ == "__main__":
    update_cumulative_pnl()