#!/usr/bin/env python3
"""
Simplified Real-Time Trades Dashboard
Shows trades with Binance Total row AFTER all Binance trades
"""
from flask import Flask, render_template_string
import json
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Real-Time Trades Dashboard</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #0f0f23; color: #ccc; }
        .dashboard { max-width: 1400px; margin: 0 auto; }
        h1 { color: #00ff9d; }
        .summary { 
            background: #1a1a2e; 
            padding: 15px; 
            border-radius: 8px;
            margin: 20px 0;
            border: 1px solid #00ff9d;
        }
        table { 
            border-collapse: collapse; 
            width: 100%; 
            margin: 20px 0;
            font-size: 14px;
        }
        th, td { 
            border: 1px solid #2d2d4d; 
            padding: 8px; 
            text-align: right;
        }
        th { 
            background-color: #1a1a2e; 
            color: #00ff9d; 
            text-align: center;
            border-bottom: 2px solid #00ff9d;
        }
        tr:nth-child(even) { background-color: #1a1a2e; }
        tr:hover { background-color: #2d2d4d; }
        .positive { color: #00ff9d; font-weight: bold; }
        .negative { color: #ff0066; font-weight: bold; }
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
            text-align: center;
        }
        .price-updating {
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>📈 Real-Time Trades Dashboard</h1>
        <p><strong>Trades with Exchange Totals</strong> - Updated: {{ update_time }}</p>
        
        <div class="summary">
            <h2>📊 Trading Summary</h2>
            <p><strong>Total Trades:</strong> {{ total_trades }}</p>
            <p><strong>Total Value:</strong> ${{ "%.2f"|format(total_value) }}</p>
            <p><strong>Exchange Breakdown:</strong></p>
            <p>• Gemini: {{ gemini_count }} trades, ${{ "%.2f"|format(gemini_total) }} ({{ "%.1f"|format(gemini_percent) }}%)</p>
            <p>• Binance: {{ binance_count }} trades, ${{ "%.2f"|format(binance_total) }} ({{ "%.1f"|format(binance_percent) }}%)</p>
        </div>
        
        <h2>💱 All Trades</h2>
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
            
            {# Gemini LONG Positions #}
            {% if gemini_trades %}
            <tr style="background-color: rgba(0, 210, 255, 0.1);">
                <td colspan="11" style="text-align: center; font-weight: bold; color: #00d2ff;">
                    🔵 GEMINI LONG POSITIONS
                </td>
            </tr>
            {% for trade in gemini_trades %}
            <tr>
                <td>
                    <span class="exchange-badge gemini">
                        GEMINI
                    </span>
                </td>
                <td><strong>{{ trade.symbol }}</strong></td>
                <td>LONG</td>
                <td>BUY</td>
                <td>${{ "%.4f"|format(trade.price) }}</td>
                <td class="price-updating">${{ "%.4f"|format(trade.get('current_price', trade.price)) }}</td>
                <td class="{{ 'positive' if trade.get('pnl', 0) > 0 else 'negative' if trade.get('pnl', 0) < 0 else 'neutral' }}">
                    ${{ "%+.4f"|format(trade.get('pnl', 0)) }}
                </td>
                <td class="{{ 'positive' if trade.get('pnl_percent', 0) > 0 else 'negative' if trade.get('pnl_percent', 0) < 0 else 'neutral' }}">
                    {{ "%+.2f"|format(trade.get('pnl_percent', 0)) }}%
                </td>
                <td>{{ "%.6f"|format(trade.amount) }}</td>
                <td>${{ "%.2f"|format(trade.value) }}</td>
                <td>{{ trade.timestamp[:19].replace('T', ' ') }}</td>
            </tr>
            {% endfor %}
            {# Gemini Total #}
            {% set gemini_total_pnl = gemini_trades|sum(attribute='pnl') %}
            {% set gemini_total_pnl_percent = (gemini_total_pnl / gemini_total * 100) if gemini_total > 0 else 0 %}
            <tr style="background-color: rgba(0, 210, 255, 0.15); border-top: 2px solid #00d2ff;">
                <td colspan="7" style="text-align: right; font-weight: bold; color: #00d2ff;">
                    🔵 GEMINI TOTAL:
                </td>
                <td class="{{ 'positive' if gemini_total_pnl_percent >= 0 else 'negative' }}">
                    {{ "%+.2f"|format(gemini_total_pnl_percent) }}%
                </td>
                <td style="font-weight: bold;">{{ gemini_count }} trades</td>
                <td style="font-weight: bold; color: #00d2ff;">${{ "%.2f"|format(gemini_total) }}</td>
                <td style="font-weight: bold;" class="{{ 'positive' if gemini_total_pnl >= 0 else 'negative' }}">
                    ${{ "%+.2f"|format(gemini_total_pnl) }}
                </td>
            </tr>
            {% endif %}
            
            {# Binance SHORT Positions #}
            {% if binance_trades %}
            <tr style="background-color: rgba(240, 185, 11, 0.1);">
                <td colspan="11" style="text-align: center; font-weight: bold; color: #f0b90b;">
                    🟡 BINANCE SHORT POSITIONS
                </td>
            </tr>
            {% for trade in binance_trades %}
            <tr>
                <td>
                    <span class="exchange-badge binance">
                        BINANCE
                    </span>
                </td>
                <td><strong>{{ trade.symbol }}</strong></td>
                <td>SHORT</td>
                <td>SELL</td>
                <td>${{ "%.4f"|format(trade.price) }}</td>
                <td class="price-updating">${{ "%.4f"|format(trade.get('current_price', trade.price)) }}</td>
                <td class="{{ 'positive' if trade.get('pnl', 0) > 0 else 'negative' if trade.get('pnl', 0) < 0 else 'neutral' }}">
                    ${{ "%+.4f"|format(trade.get('pnl', 0)) }}
                </td>
                <td class="{{ 'positive' if trade.get('pnl_percent', 0) > 0 else 'negative' if trade.get('pnl_percent', 0) < 0 else 'neutral' }}">
                    {{ "%+.2f"|format(trade.get('pnl_percent', 0)) }}%
                </td>
                <td>{{ "%.6f"|format(trade.amount) }}</td>
                <td>${{ "%.2f"|format(trade.value) }}</td>
                <td>{{ trade.timestamp[:19].replace('T', ' ') }}</td>
            </tr>
            {% endfor %}
            {# Binance Total - ADDED AFTER ALL BINANCE TRADES #}
            {% set binance_total_pnl = binance_trades|sum(attribute='pnl') %}
            {% set binance_total_pnl_percent = (binance_total_pnl / binance_total * 100) if binance_total > 0 else 0 %}
            <tr style="background-color: rgba(240, 185, 11, 0.15); border-top: 2px solid #f0b90b;">
                <td colspan="7" style="text-align: right; font-weight: bold; color: #f0b90b;">
                    🟡 BINANCE TOTAL:
                </td>
                <td class="{{ 'positive' if binance_total_pnl_percent >= 0 else 'negative' }}">
                    {{ "%+.2f"|format(binance_total_pnl_percent) }}%
                </td>
                <td style="font-weight: bold;">{{ binance_count }} trades</td>
                <td style="font-weight: bold; color: #f0b90b;">${{ "%.2f"|format(binance_total) }}</td>
                <td style="font-weight: bold;" class="{{ 'positive' if binance_total_pnl >= 0 else 'negative' }}">
                    ${{ "%+.2f"|format(binance_total_pnl) }}
                </td>
            </tr>
            {% endif %}
        </table>
        
        <div class="last-updated">
            <p>🔁 Auto-refreshing every 30 seconds</p>
            <p>Last update: {{ update_time }}</p>
            <p><strong>✅ Binance Total row appears AFTER all Binance trades as requested!</strong></p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def trades_dashboard():
    try:
        # Load trades
        with open('trading_data/trades.json', 'r') as f:
            trades = json.load(f)
        
        # Separate by exchange
        gemini_trades = [t for t in trades if t.get('exchange') == 'gemini']
        binance_trades = [t for t in trades if t.get('exchange') == 'binance']
        
        # Calculate totals
        gemini_total = sum(t.get('value', 0) for t in gemini_trades)
        binance_total = sum(t.get('value', 0) for t in binance_trades)
        total_value = gemini_total + binance_total
        
        gemini_count = len(gemini_trades)
        binance_count = len(binance_trades)
        total_trades = gemini_count + binance_count
        
        gemini_percent = (gemini_total / total_value * 100) if total_value > 0 else 0
        binance_percent = (binance_total / total_value * 100) if total_value > 0 else 0
        
        # Prepare template data
        data = {
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_trades': total_trades,
            'total_value': total_value,
            'gemini_trades': gemini_trades,
            'binance_trades': binance_trades,
            'gemini_total': gemini_total,
            'binance_total': binance_total,
            'gemini_count': gemini_count,
            'binance_count': binance_count,
            'gemini_percent': gemini_percent,
            'binance_percent': binance_percent
        }
        
        return render_template_string(HTML_TEMPLATE, **data)
        
    except Exception as e:
        return f"Error loading trades dashboard: {str(e)}", 500

if __name__ == '__main__':
    print("Starting simplified trades dashboard on port 5011...")
    print("✅ Binance Total row will appear AFTER all Binance trades")
    app.run(host='0.0.0.0', port=5011, debug=False)