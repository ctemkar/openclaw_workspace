#!/usr/bin/env python3
"""
Update dashboard on port 5007 to show separate Gemini/Binance + totals
"""

import json
from datetime import datetime

def analyze_trades():
    """Analyze trades to get Gemini/Binance breakdown"""
    with open('trading_data/trades.json', 'r') as f:
        trades = json.load(f)
    
    data = {
        'total': {'investment': 0, 'current': 0, 'pnl': 0, 'pnl_percent': 0},
        'gemini': {'investment': 0, 'current': 0, 'pnl': 0, 'pnl_percent': 0, 'cash': 0, 'positions': []},
        'binance': {'investment': 0, 'current': 0, 'pnl': 0, 'pnl_percent': 0, 'cash': 0, 'positions': []}
    }
    
    for trade in trades:
        symbol = trade.get('symbol', '')
        exchange = trade.get('exchange', '')
        trade_type = trade.get('type', '')
        
        if symbol == 'INVESTMENT/SUMMARY':
            # Total summary
            data['total']['investment'] = trade.get('value', 0)
            data['total']['pnl'] = trade.get('pnl', 0)
            data['total']['current'] = trade.get('value', 0) + trade.get('pnl', 0)
            data['total']['pnl_percent'] = trade.get('pnl_percent', 0)
            
        elif symbol == 'GEMINI/INVESTMENT':
            # Gemini investment summary
            data['gemini']['investment'] = trade.get('value', 0)
            data['gemini']['pnl'] = trade.get('pnl', 0)
            data['gemini']['current'] = trade.get('value', 0) + trade.get('pnl', 0)
            data['gemini']['pnl_percent'] = trade.get('pnl_percent', 0)
            
        elif symbol == 'BINANCE/INVESTMENT':
            # Binance investment summary
            data['binance']['investment'] = trade.get('value', 0)
            data['binance']['pnl'] = trade.get('pnl', 0)
            data['binance']['current'] = trade.get('value', 0) + trade.get('pnl', 0)
            data['binance']['pnl_percent'] = trade.get('pnl_percent', 0)
            
        elif exchange == 'gemini' and trade_type == 'cash':
            # Gemini cash
            data['gemini']['cash'] = trade.get('value', 0)
            
        elif exchange == 'binance' and trade_type == 'cash':
            # Binance cash
            data['binance']['cash'] = trade.get('value', 0)
            
        elif exchange == 'gemini' and trade_type == 'spot':
            # Gemini positions
            data['gemini']['positions'].append({
                'symbol': trade.get('symbol', ''),
                'value': trade.get('value', 0),
                'pnl': trade.get('pnl', 0),
                'pnl_percent': trade.get('pnl_percent', 0)
            })
    
    # Calculate position totals
    data['gemini']['position_value'] = sum(p['value'] for p in data['gemini']['positions'])
    data['gemini']['position_pnl'] = sum(p['pnl'] for p in data['gemini']['positions'])
    
    # Calculate percentages
    total_current = data['total']['current']
    data['gemini']['percent_of_total'] = round((data['gemini']['current'] / total_current * 100), 1) if total_current > 0 else 0
    data['binance']['percent_of_total'] = round((data['binance']['current'] / total_current * 100), 1) if total_current > 0 else 0
    
    return data

def main():
    print("📊 Analyzing current portfolio...")
    data = analyze_trades()
    
    print(f"\n♊ GEMINI:")
    print(f"  Investment: ${data['gemini']['investment']:.2f}")
    print(f"  Current: ${data['gemini']['current']:.2f}")
    print(f"  P&L: ${data['gemini']['pnl']:+.2f} ({data['gemini']['pnl_percent']:+.1f}%)")
    print(f"  Cash: ${data['gemini']['cash']:.2f}")
    print(f"  Positions: ${data['gemini']['position_value']:.2f} ({len(data['gemini']['positions'])} positions)")
    
    print(f"\n₿ BINANCE:")
    print(f"  Investment: ${data['binance']['investment']:.2f}")
    print(f"  Current: ${data['binance']['current']:.2f}")
    print(f"  P&L: ${data['binance']['pnl']:+.2f} ({data['binance']['pnl_percent']:+.1f}%)")
    print(f"  Cash: ${data['binance']['cash']:.2f}")
    
    print(f"\n📊 TOTALS:")
    print(f"  Total Investment: ${data['total']['investment']:.2f}")
    print(f"  Total Current: ${data['total']['current']:.2f}")
    print(f"  Total P&L: ${data['total']['pnl']:+.2f} ({data['total']['pnl_percent']:+.1f}%)")
    print(f"  Total Positions: ${data['gemini']['position_value']:.2f}")
    print(f"  Total Cash: ${data['gemini']['cash'] + data['binance']['cash']:.2f}")
    
    print(f"\n📈 BREAKDOWN:")
    print(f"  Gemini: ${data['gemini']['current']:.2f} ({data['gemini']['percent_of_total']:.1f}% of portfolio)")
    print(f"  Binance: ${data['binance']['current']:.2f} ({data['binance']['percent_of_total']:.1f}% of portfolio)")
    
    print(f"\n🎯 Dashboard on port 5009 already shows this correctly:")
    print(f"   http://localhost:5009/")
    
    print(f"\n🔧 To update port 5007 dashboard, I need to:")
    print(f"   1. Stop the current dashboard (PID from port 5007)")
    print(f"   2. Update dashboard_with_cash_separate.py")
    print(f"   3. Restart it")
    
    return data

if __name__ == "__main__":
    main()