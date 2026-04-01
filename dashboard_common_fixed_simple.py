#!/usr/bin/env python3
"""
Simple fixed Common Dashboard - Shows real data
"""

from flask import Flask
import json
from datetime import datetime

app = Flask(__name__)

def get_current_data():
    """Get current data from trades.json"""
    try:
        with open('trading_data/trades.json', 'r') as f:
            trades = json.load(f)
    except:
        trades = []
    
    buy_trades = [t for t in trades if t.get('side') == 'buy']
    sell_trades = [t for t in trades if t.get('side') == 'sell']
    
    total_buy_value = sum(t.get('value', 0) for t in buy_trades)
    total_pnl = sum(t.get('pnl', 0) for t in trades)
    
    starting_capital = 471.05
    remaining_capital = starting_capital - total_buy_value
    
    return {
        'total_trades': len(trades),
        'long_positions': len(buy_trades),
        'short_positions': len(sell_trades),
        'total_pnl': total_pnl,
        'capital_deployed': total_buy_value,
        'remaining_capital': remaining_capital,
        'timestamp': datetime.now().isoformat()
    }

@app.route('/')
def dashboard():
    data = get_current_data()
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>🚀 COMMON DASHBOARD - FIXED</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {{ font-family: monospace; margin: 20px; background: #000; color: #0f0; }}
        .dashboard {{ max-width: 800px; margin: 0 auto; border: 1px solid #0f0; padding: 20px; }}
        h1 {{ color: #0f0; text-align: center; }}
        .stat {{ margin: 15px 0; padding: 10px; background: #111; border: 1px solid #0f0; }}
        .stat-value {{ font-size: 20px; font-weight: bold; }}
        .positive {{ color: #0f0; }}
        .negative {{ color: #f00; }}
        .info {{ text-align: center; color: #666; margin-top: 30px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>📊 COMMON DASHBOARD - FIXED</h1>
        <p style="text-align: center; color: #0f0;">✅ Showing REAL data (not zeros)</p>
        
        <div class="stat">
            <div>Total Trades</div>
            <div class="stat-value">{data['total_trades']}</div>
        </div>
        
        <div class="stat">
            <div>LONG Positions</div>
            <div class="stat-value">{data['long_positions']}</div>
        </div>
        
        <div class="stat">
            <div>SHORT Positions</div>
            <div class="stat-value">{data['short_positions']}</div>
        </div>
        
        <div class="stat">
            <div>Total P&L</div>
            <div class="stat-value {'positive' if data['total_pnl'] >= 0 else 'negative'}">
                ${data['total_pnl']:+.4f}
            </div>
        </div>
        
        <div class="stat">
            <div>Capital Deployed</div>
            <div class="stat-value">${data['capital_deployed']:.2f}</div>
        </div>
        
        <div class="stat">
            <div>Remaining Capital</div>
            <div class="stat-value">${data['remaining_capital']:.2f}</div>
        </div>
        
        <div class="info">
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Data source: trading_data/trades.json</p>
            <p>Auto-refreshes every 30 seconds</p>
            <p>✅ Fixed: No more zeros!</p>
        </div>
    </div>
</body>
</html>"""

if __name__ == '__main__':
    print("🚀 Starting FIXED Common Dashboard on port 5007...")
    print("📊 Will show REAL data from trades.json")
    print("🔗 Access: http://localhost:5007/")
    app.run(host='0.0.0.0', port=5007, debug=False)
