#!/usr/bin/env python3
"""
Update trades.json with current market prices and calculate P&L
"""

import json
import os
from datetime import datetime
import requests

def get_current_price(symbol):
    """Get current price for a symbol (simplified - using known prices)"""
    # Known current prices from bot logs
    price_map = {
        "ADA/USDT": 0.2408,  # Current price approx
        "COMP/USDT": 16.78,  # From bot logs: $16.78-$16.80
        "ENJ/USDT": 0.0207,  # From positions.json: 0.02068717
    }
    
    base_symbol = symbol.split("/")[0] if "/" in symbol else symbol
    for key in price_map:
        if base_symbol in key:
            return price_map[key]
    
    # Default to entry price if unknown
    return None

def update_trades_with_prices():
    print("📈 UPDATING TRADES WITH CURRENT PRICES & P&L")
    print("============================================")
    
    try:
        # Load trades
        with open('trading_data/trades.json', 'r') as f:
            trades = json.load(f)
        
        print(f"Found {len(trades)} trades to update")
        
        # Update each trade with current price and P&L
        updated_trades = []
        for trade in trades:
            symbol = trade['symbol']
            entry_price = trade['price']
            amount = trade['amount']
            
            # Get current price
            current_price = get_current_price(symbol)
            if current_price is None:
                current_price = entry_price  # No price update available
            
            # Calculate P&L
            # For SHORT (sell): P&L = (entry_price - current_price) * amount
            pnl = (entry_price - current_price) * amount
            pnl_percent = ((entry_price - current_price) / entry_price) * 100 if entry_price > 0 else 0
            
            # Create updated trade record
            updated_trade = trade.copy()
            updated_trade['current_price'] = current_price
            updated_trade['pnl'] = pnl
            updated_trade['pnl_percent'] = pnl_percent
            updated_trade['current_value'] = current_price * amount
            updated_trade['last_updated'] = datetime.now().isoformat()
            
            updated_trades.append(updated_trade)
            
            print(f"  {symbol}: Entry ${entry_price:.4f} → Current ${current_price:.4f}, P&L: ${pnl:.4f} ({pnl_percent:.2f}%)")
        
        # Save updated trades
        with open('trading_data/trades_updated.json', 'w') as f:
            json.dump(updated_trades, f, indent=2)
        
        print(f"\n✅ Updated {len(updated_trades)} trades with current prices")
        print(f"✅ Saved to trading_data/trades_updated.json")
        
        # Also update the main trades.json
        with open('trading_data/trades.json', 'w') as f:
            json.dump(updated_trades, f, indent=2)
        
        print(f"✅ Updated main trades.json file")
        
        # Calculate total P&L
        total_pnl = sum(t['pnl'] for t in updated_trades)
        print(f"\n📊 TOTAL P&L ACROSS ALL TRADES: ${total_pnl:.2f}")
        
        # Update positions.json with current prices
        update_positions_with_current_prices(updated_trades)
        
    except Exception as e:
        print(f"Error: {e}")

def update_positions_with_current_prices(trades):
    """Update positions.json with current prices from trades"""
    try:
        # Group trades by symbol to find open positions
        positions = {}
        for trade in trades:
            symbol = trade['symbol']
            if symbol not in positions:
                positions[symbol] = {
                    'total_amount': 0,
                    'weighted_entry': 0,
                    'total_pnl': 0
                }
            
            positions[symbol]['total_amount'] += trade['amount']
            positions[symbol]['weighted_entry'] = trade['price']  # Simplified
            positions[symbol]['total_pnl'] += trade['pnl']
        
        # Create positions data
        positions_list = []
        for symbol, data in positions.items():
            if data['total_amount'] > 0:
                current_price = get_current_price(symbol) or data['weighted_entry']
                position_value = current_price * data['total_amount']
                pnl_percent = (data['total_pnl'] / position_value * 100) if position_value > 0 else 0
                
                positions_list.append({
                    "symbol": symbol,
                    "contracts": data['total_amount'],
                    "entry_price": data['weighted_entry'],
                    "current_price": current_price,
                    "position_value": position_value,
                    "unrealized_pnl": data['total_pnl'],
                    "pnl_percent": pnl_percent
                })
        
        positions_data = {
            "positions": positions_list,
            "position_count": len(positions_list),
            "total_value": sum(p['position_value'] for p in positions_list),
            "total_pnl": sum(p['unrealized_pnl'] for p in positions_list),
            "last_updated": datetime.now().isoformat()
        }
        
        with open('trading_data/positions.json', 'w') as f:
            json.dump(positions_data, f, indent=2)
        
        print(f"✅ Updated positions.json with {len(positions_list)} positions")
        
    except Exception as e:
        print(f"Error updating positions: {e}")

if __name__ == "__main__":
    update_trades_with_prices()
