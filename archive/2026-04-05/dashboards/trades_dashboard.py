#!/usr/bin/env python3
"""
Dashboard showing trades with REAL current prices and P&L
"""

from flask import Flask, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Real-Time Trades Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .dashboard { max-width: 1400px; margin: 0 auto; }
        h1 { color: #333; }
        .summary { 
            background: #f5f5f5; 
            padding: 15px; 
            border-radius: 5px;
            margin: 20px 0;
        }
        table { 
            border-collapse: collapse; 
            width: 100%; 
            margin: 20px 0;
            font-size: 14px;
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 8px; 
            text-align: right;
        }
        th { 
            background-color: #4CAF50; 
            color: white; 
            text-align: center;
        }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .positive { color: green; font-weight: bold; }
        .negative { color: red; font-weight: bold; }
        .neutral { color: #666; }
        .exchange-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 5px;
        }
        .binance { background: #f0b90b; color: black; }
        .gemini { background: #00d2ff; color: black; }
        .last-updated {
            color: #666;
            font-size: 12px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>📈 Real-Time Trades Dashboard</h1>
        <p><strong>Live prices and P&L</strong> - Updated: {{ update_time }}</p>
        
        <div class="summary">
            <h2>📊 Trading Summary</h2>
            <p><strong>Total Trades:</strong> {{ total_trades }}</p>
            <p><strong>Total P&L:</strong> <span class="{{ 'positive' if total_pnl >= 0 else 'negative' }}">
                ${{ "%+.2f"|format(total_pnl) }}
            </span></p>
            <p><strong>Win Rate:</strong> {{ win_rate }}% ({{ winning_trades }}/{{ total_trades }} profitable)</p>
            <p><strong>Avg Trade Size:</strong> ${{ "%.2f"|format(avg_trade_size) }}</p>
        </div>
        
        <h2>💱 Recent Trades</h2>
        <table>
            <tr>
                <th>Exchange</th>
                <th>Symbol</th>
                <th>Type</th>
                <th>Side</th>
                <th>Entry Price</th>
                <th>Current Price</th>
                <th>P&L</th>
                <th>P&L %</th>
                <th>Amount</th>
                <th>Value</th>
                <th>Time</th>
            </tr>
            {% for trade in trades %}
            <tr>
                <td>
                    <span class="exchange-badge {{ 'binance' if trade.exchange == 'binance' else 'gemini' }}">
                        {{ trade.exchange|upper }}
                    </span>
                </td>
                <td><strong>{{ trade.symbol }}</strong></td>
                <td>{{ trade.type if trade.type else 'SPOT' }}</td>
                <td>{{ trade.side|upper }}</td>
                <td>${{ "%.4f"|format(trade.price) }}</td>
                <td>${{ "%.4f"|format(trade.current_price) }}</td>
                <td class="{{ 'positive' if trade.pnl > 0 else 'negative' if trade.pnl < 0 else 'neutral' }}">
                    ${{ "%+.4f"|format(trade.pnl) }}
                </td>
                <td class="{{ 'positive' if trade.pnl_percent > 0 else 'negative' if trade.pnl_percent < 0 else 'neutral' }}">
                    {{ "%+.2f"|format(trade.pnl_percent) }}%
                </td>
                <td>{{ "%.6f"|format(trade.amount) }}</td>
                <td>${{ "%.2f"|format(trade.value) }}</td>
                <td>{{ trade.timestamp[:19].replace('T', ' ') }}</td>
            </tr>
            {% endfor %}
        </table>
        
        <div class="last-updated">
            <p>Data loaded from: trading_data/trades.json</p>
            <p>Prices updated: {{ price_update_time }}</p>
            <p>Dashboard auto-refreshes every 30 seconds</p>
        </div>
        
        <script>
            // Auto-refresh every 30 seconds
            setTimeout(function() {
                location.reload();
            }, 30000);
        </script>
    </div>
</body>
</html>
'''

@app.route('/')
def trades_dashboard():
    try:
        # Load updated trades
        with open('trading_data/trades.json', 'r') as f:
            trades = json.load(f)
        
        # Calculate summary statistics
        total_trades = len(trades)
        total_pnl = sum(t.get('pnl', 0) for t in trades)
        winning_trades = sum(1 for t in trades if t.get('pnl', 0) > 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate value for each trade (price * amount) if not present
        for trade in trades:
            if 'value' not in trade:
                trade['value'] = trade.get('price', 0) * trade.get('amount', 0)
        
        avg_trade_size = sum(t.get('value', 0) for t in trades) / total_trades if total_trades > 0 else 0
        
        # Add trade type (SHORT for sell, LONG for buy)
        for trade in trades:
            trade['type'] = 'SHORT' if trade['side'] == 'sell' else 'LONG'
        
        # Prepare template data
        data = {
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'price_update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'trades': trades,
            'total_trades': total_trades,
            'total_pnl': total_pnl,
            'winning_trades': winning_trades,
            'win_rate': round(win_rate, 1),
            'avg_trade_size': avg_trade_size
        }
        
        return render_template_string(HTML_TEMPLATE, **data)
        
    except Exception as e:
        return f"Error loading trades dashboard: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=False)
