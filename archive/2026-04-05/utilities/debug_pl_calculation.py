#!/usr/bin/env python3
"""
Debug why P&L is stuck at $0.45
"""

import requests
import json
from datetime import datetime

print('🔍 DEBUGGING P&L CALCULATION')
print('=' * 60)

# Get current data
try:
    response = requests.get('http://localhost:5001/api/data', timeout=5)
    data = response.json()
    
    print('📊 CURRENT DATA:')
    print(f'• Total capital: ${data.get("capital_allocation", {}).get("total_capital", 0):.2f}')
    print(f'• Gemini total: ${data.get("capital_allocation", {}).get("gemini_total", 0):.2f}')
    print(f'• Binance total: ${data.get("capital_allocation", {}).get("binance_total", 0):.2f}')
    print(f'• Deployed: ${data.get("capital_allocation", {}).get("deployed", 0):.2f}')
    print(f'• Available Gemini: ${data.get("capital_allocation", {}).get("available_gemini", 0):.2f}')
    print()
    
    # Check cumulative P&L
    cumulative = data.get('cumulative_pnl', {})
    print('📈 CUMULATIVE P&L:')
    print(f'• Current: ${cumulative.get("current", 0):.2f}')
    print(f'• Initial: ${cumulative.get("initial", 0):.2f}')
    print(f'• P&L: ${cumulative.get("pnl", 0):.2f}')
    print(f'• P&L %: {cumulative.get("pnl_percent", 0):.2f}%')
    print(f'• Recovery needed: ${cumulative.get("recovery_needed", 0):.2f}')
    print(f'• Recovery %: {cumulative.get("recovery_percent_needed", 0):.2f}%')
    print()
    
    # Check positions
    positions = data.get('current_positions', [])
    print(f'📊 POSITIONS: {len(positions)} open')
    
    total_position_value = 0
    for i, pos in enumerate(positions[:5]):  # Show first 5
        symbol = pos.get('symbol', 'unknown')
        amount = pos.get('amount', 0)
        price = pos.get('price', 0)
        value = pos.get('value', 0)
        side = pos.get('side', 'unknown')
        
        print(f'  {i+1}. {symbol} {side}:')
        print(f'     Amount: {amount:.6f}')
        print(f'     Price: ${price:.4f}')
        print(f'     Value: ${value:.2f}')
        total_position_value += value
    
    print(f'  Total position value: ${total_position_value:.2f}')
    print()
    
    # Check if P&L is updating
    print('🔄 CHECKING P&L UPDATE MECHANISM:')
    
    # Get current SOL price from Gemini API
    try:
        import ccxt
        exchange = ccxt.gemini()
        ticker = exchange.fetch_ticker('SOL/USD')
        current_price = ticker['last']
        print(f'• Current SOL price (Gemini): ${current_price:.4f}')
        
        # Calculate P&L for each position
        total_pl = 0
        for pos in positions:
            if pos.get('symbol') == 'SOL/USD':
                entry_price = pos.get('price', 0)
                amount = pos.get('amount', 0)
                position_pl = (current_price - entry_price) * amount
                total_pl += position_pl
                pl_percent = ((current_price / entry_price) - 1) * 100
                
                print(f'  Position P&L: ${position_pl:.4f} ({pl_percent:.4f}%)')
        
        print(f'• Total SOL positions P&L: ${total_pl:.4f}')
        print(f'• Should be updating with price: ${current_price:.4f}')
        
    except Exception as e:
        print(f'• Could not fetch current price: {e}')
    
    print()
    print('🔍 CHECKING DATA FRESHNESS:')
    last_updated = data.get('capital_allocation', {}).get('last_updated', '')
    print(f'• Last updated: {last_updated}')
    
    # Check if data is stale
    if last_updated:
        from datetime import datetime
        last_dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
        now = datetime.now()
        age = (now - last_dt).total_seconds() / 60  # minutes
        
        print(f'• Data age: {age:.1f} minutes')
        if age > 10:
            print('⚠️ WARNING: Data is stale (>10 minutes)')
            print('  • P&L may not be updating')
            print('  • Check if trading server is updating prices')
        else:
            print('✅ Data is fresh')
    
except Exception as e:
    print(f'❌ Error: {e}')

print()
print('🎯 NEXT STEPS:')
print('1. Check if trading server is fetching live prices')
print('2. Verify P&L calculation logic')
print('3. Ensure data updates are happening')
print('4. Remove any stale position data')