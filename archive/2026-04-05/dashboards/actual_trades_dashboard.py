#!/usr/bin/env python3
"""
ACTUAL TRADES DASHBOARD - Shows real trade rows with actual data
"""

from flask import Flask, render_template_string, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📊 ACTUAL TRADES DASHBOARD</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="30">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 20px;
            background: #0f172a;
            color: #e2e8f0;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: #1e293b;
            border-radius: 10px;
            border: 1px solid #334155;
        }
        h1 {
            color: #00ff9d;
            margin: 0;
            font-size: 2.5em;
        }
        .subtitle {
            color: #94a3b8;
            margin: 10px 0 20px 0;
        }
        .exchange-summary {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
        }
        .exchange-card {
            background: #1e293b;
            padding: 15px 25px;
            border-radius: 8px;
            border: 1px solid #334155;
            min-width: 200px;
            text-align: center;
        }
        .exchange-card.gemini {
            border-color: #3b82f6;
        }
        .exchange-card.binance {
            border-color: #f59e0b;
        }
        .exchange-name {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .exchange-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #00ff9d;
        }
        .trades-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: #1e293b;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #334155;
        }
        .trades-table th {
            background: #334155;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #cbd5e1;
            border-bottom: 2px solid #475569;
        }
        .trades-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #334155;
        }
        .trades-table tr:hover {
            background: #2d3748;
        }
        .positive {
            color: #10b981;
            font-weight: bold;
        }
        .negative {
            color: #ef4444;
            font-weight: bold;
        }
        .neutral {
            color: #94a3b8;
        }
        .status-open {
            color: #10b981;
            background: rgba(16, 185, 129, 0.1);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.9em;
        }
        .status-closed {
            color: #94a3b8;
            background: rgba(148, 163, 184, 0.1);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.9em;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
            margin-right: 5px;
        }
        .badge-gemini {
            background: rgba(59, 130, 246, 0.2);
            color: #3b82f6;
            border: 1px solid #3b82f6;
        }
        .badge-binance {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
            border: 1px solid #f59e0b;
        }
        .last-updated {
            text-align: center;
            margin-top: 20px;
            color: #94a3b8;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 ACTUAL TRADES DASHBOARD</h1>
            <div class="subtitle">Real trade rows from Gemini and Binance</div>
            
            <div class="exchange-summary">
                <div class="exchange-card gemini">
                    <div class="exchange-name">🔵 GEMINI</div>
                    <div class="exchange-value">${{ gemini_total }}</div>
                    <div>{{ gemini_trades }} trades</div>
                </div>
                <div class="exchange-card binance">
                    <div class="exchange-name">🟡 BINANCE</div>
                    <div class="exchange-value">${{ binance_total }}</div>
                    <div>{{ binance_trades }} trades</div>
                </div>
            </div>
        </div>
        
        <h2>💱 ACTUAL TRADE ROWS</h2>
        
        <table class="trades-table">
            <thead>
                <tr>
                    <th>Exchange</th>
                    <th>Symbol</th>
                    <th>Side</th>
                    <th>Entry Price</th>
                    <th>Current Price</th>
                    <th>P&L</th>
                    <th>P&L %</th>
                    <th>Status</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                {% for trade in trades %}
                <tr>
                    <td>
                        <span class="badge badge-{{ trade.exchange }}">
                            {{ trade.exchange|upper }}
                        </span>
                    </td>
                    <td><strong>{{ trade.symbol }}</strong></td>
                    <td>
                        {% if trade.side == 'buy' %}
                        <span class="positive">▲ BUY</span>
                        {% else %}
                        <span class="negative">▼ SELL</span>
                        {% endif %}
                    </td>
                    <td>${{ "%.4f"|format(trade.entry_price) }}</td>
                    <td>${{ "%.4f"|format(trade.current_price) }}</td>
                    <td class="{{ 'positive' if trade.pnl >= 0 else 'negative' }}">
                        ${{ "%.2f"|format(trade.pnl) }}
                    </td>
                    <td class="{{ 'positive' if trade.pnl_percent >= 0 else 'negative' }}">
                        {{ "%.2f"|format(trade.pnl_percent) }}%
                    </td>
                    <td>
                        {% if trade.status == 'open' %}
                        <span class="status-open">OPEN</span>
                        {% else %}
                        <span class="status-closed">CLOSED</span>
                        {% endif %}
                    </td>
                    <td>{{ trade.timestamp }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="last-updated">
            Last updated: {{ last_updated }}
        </div>
    </div>
</body>
</html>
'''

def load_trade_history():
    """Load and process actual trade history"""
    trades = []
    
    # Try to load corrected trade history
    trade_files = [
        '26_crypto_trade_history_CORRECTED.json',
        '26_crypto_trade_history.json',
        'daily_trades.json'
    ]
    
    all_trades = []
    
    for file in trade_files:
        if os.path.exists(file):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    all_trades.extend(data)
                elif isinstance(data, dict) and 'trades' in data:
                    all_trades.extend(data['trades'])
            except Exception as e:
                print(f"Error loading {file}: {e}")
    
    # Process trades
    for trade in all_trades:
        # Skip trades with zero entry price (invalid)
        if trade.get('entry_price', 0) <= 0:
            continue
            
        # Calculate P&L percentage if not present
        entry_price = trade.get('entry_price', 0)
        current_price = trade.get('current_price', entry_price)
        pnl = trade.get('pnl', 0)
        
        if entry_price > 0:
            pnl_percent = ((current_price - entry_price) / entry_price) * 100
            if trade.get('side') == 'sell':
                pnl_percent = -pnl_percent  # Inverse for sells
        else:
            pnl_percent = 0
        
        processed_trade = {
            'exchange': trade.get('exchange', 'unknown'),
            'symbol': trade.get('symbol', 'unknown'),
            'side': trade.get('side', 'unknown'),
            'entry_price': entry_price,
            'current_price': current_price,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'status': trade.get('status', 'closed'),
            'timestamp': trade.get('timestamp', trade.get('time', 'unknown'))
        }
        
        trades.append(processed_trade)
    
    # Sort by timestamp (newest first)
    trades.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return trades

def calculate_exchange_totals(trades):
    """Calculate totals per exchange"""
    gemini_trades = [t for t in trades if t['exchange'] == 'gemini']
    binance_trades = [t for t in trades if t['exchange'] == 'binance']
    
    # Calculate approximate totals based on trade sizes
    # Assuming average position size of $30 per trade
    gemini_total = len(gemini_trades) * 30
    binance_total = len(binance_trades) * 30
    
    # If we have actual capital data, use it
    try:
        with open('real_26_crypto_trader.py', 'r') as f:
            content = f.read()
            import re
            
            # Get Gemini capital
            gemini_match = re.search(r'GEMINI_CAPITAL\s*=\s*([\d.]+)', content)
            if gemini_match:
                gemini_total = float(gemini_match.group(1))
            
            # Get Binance capital
            binance_match = re.search(r'BINANCE_CAPITAL\s*=\s*([\d.]+)', content)
            if binance_match:
                binance_total = float(binance_match.group(1))
    except:
        pass
    
    return {
        'gemini_total': gemini_total,
        'binance_total': binance_total,
        'gemini_trades': len(gemini_trades),
        'binance_trades': len(binance_trades)
    }

@app.route('/')
def index():
    """Main dashboard page"""
    trades = load_trade_history()
    exchange_totals = calculate_exchange_totals(trades)
    
    return render_template_string(
        HTML_TEMPLATE,
        trades=trades[:50],  # Show last 50 trades max
        gemini_total=f"{exchange_totals['gemini_total']:.2f}",
        binance_total=f"{exchange_totals['binance_total']:.2f}",
        gemini_trades=exchange_totals['gemini_trades'],
        binance_trades=exchange_totals['binance_trades'],
        last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.route('/api/trades')
def api_trades():
    """API endpoint for trades data"""
    trades = load_trade_history()
    return jsonify({
        'trades': trades[:100],
        'count': len(trades),
        'last_updated': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("="*70)
    print("📊 ACTUAL TRADES DASHBOARD")
    print("="*70)
    print("Shows real trade rows from Gemini and Binance")
    print(f"Dashboard: http://localhost:5012")
    print(f"API: http://localhost:5012/api/trades")
    print("="*70)
    
    app.run(host='0.0.0.0', port=5012, debug=False)