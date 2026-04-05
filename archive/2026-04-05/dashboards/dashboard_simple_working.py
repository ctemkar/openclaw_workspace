#!/usr/bin/env python3
"""
SIMPLE WORKING DASHBOARD - No mess, just works
Shows real trading data clearly
"""

from flask import Flask
import json
from datetime import datetime
import os

app = Flask(__name__)

def get_trading_data():
    """Get real trading data from trades.json"""
    try:
        with open('trading_data/trades.json', 'r') as f:
            trades = json.load(f)
    except Exception as e:
        print(f"Error loading trades: {e}")
        trades = []
    
    # Calculate stats
    total_trades = len(trades)
    long_trades = len([t for t in trades if t.get('side') == 'buy'])
    short_trades = len([t for t in trades if t.get('side') == 'sell'])
    
    # Calculate P&L
    total_pnl = sum(t.get('pnl', 0) for t in trades)
    
    # Calculate capital deployed (value of LONG positions)
    capital_deployed = sum(t.get('value', 0) for t in trades if t.get('side') == 'buy')
    
    # Starting capital
    starting_capital = 471.05
    remaining_capital = starting_capital - capital_deployed
    
    return {
        'total_trades': total_trades,
        'long_trades': long_trades,
        'short_trades': short_trades,
        'total_pnl': total_pnl,
        'capital_deployed': capital_deployed,
        'remaining_capital': remaining_capital,
        'starting_capital': starting_capital,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

@app.route('/')
def dashboard():
    data = get_trading_data()
    
    # Determine P&L color
    pnl_color = "green" if data['total_pnl'] >= 0 else "red"
    pnl_sign = "+" if data['total_pnl'] >= 0 else ""
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>✅ SIMPLE WORKING DASHBOARD</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .success-banner {{
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border: 1px solid #c3e6cb;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            border-left: 5px solid #3498db;
        }}
        .stat-label {{
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 5px;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #212529;
        }}
        .pnl-value {{
            color: {pnl_color};
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
            font-size: 14px;
            text-align: center;
        }}
        .data-source {{
            background: #e9ecef;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-family: monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>✅ SIMPLE WORKING DASHBOARD</h1>
        
        <div class="success-banner">
            <strong>✓ This dashboard WORKS - No mess, just data</strong>
            <p>Showing real trading data from trades.json</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Trades</div>
                <div class="stat-value">{data['total_trades']}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">LONG Positions</div>
                <div class="stat-value">{data['long_trades']}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">SHORT Positions</div>
                <div class="stat-value">{data['short_trades']}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Total P&L</div>
                <div class="stat-value pnl-value">${pnl_sign}{data['total_pnl']:.4f}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Capital Deployed</div>
                <div class="stat-value">${data['capital_deployed']:.2f}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Remaining Capital</div>
                <div class="stat-value">${data['remaining_capital']:.2f}</div>
            </div>
        </div>
        
        <div class="data-source">
            <strong>Data Source:</strong> trading_data/trades.json ({data['total_trades']} trades loaded)
        </div>
        
        <div class="footer">
            <p>Last updated: {data['timestamp']}</p>
            <p>Auto-refreshes every 10 seconds • Simple & Working</p>
            <p>Starting Capital: ${data['starting_capital']:.2f}</p>
        </div>
    </div>
</body>
</html>'''

if __name__ == '__main__':
    print("🚀 Starting SIMPLE WORKING DASHBOARD on port 5008...")
    print("✅ This dashboard WILL work - no mess")
    print("🔗 Access: http://localhost:5008/")
    app.run(host='0.0.0.0', port=5008, debug=False)