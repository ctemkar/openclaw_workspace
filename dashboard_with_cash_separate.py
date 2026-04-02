#!/usr/bin/env python3
"""
DASHBOARD WITH SEPARATE CASH DISPLAY
Shows investment positions AND available cash separately
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
    <title>📊 Trading System Dashboard - CASH SEPARATE</title>
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
            margin-bottom: 20px;
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
        
        /* CASH SECTION - PROMINENT */
        .cash-section {
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 25px;
            border: 2px solid #3b82f6;
            text-align: center;
        }
        .cash-amount {
            font-size: 3em;
            font-weight: bold;
            color: #ffffff;
            margin: 10px 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .cash-label {
            color: #bfdbfe;
            font-size: 1.2em;
            margin-bottom: 10px;
        }
        .cash-note {
            color: #93c5fd;
            font-size: 0.9em;
            font-style: italic;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        .summary-card {
            background: #1e293b;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #334155;
            text-align: center;
        }
        .summary-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #00ff9d;
            margin: 10px 0;
        }
        .summary-label {
            color: #94a3b8;
            font-size: 0.9em;
        }
        .positive {
            color: #10b981;
        }
        .negative {
            color: #ef4444;
        }
        
        .section {
            margin-top: 30px;
        }
        .section-title {
            color: #cbd5e1;
            font-size: 1.3em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #334155;
        }
        
        .trade-table {
            width: 100%;
            border-collapse: collapse;
            background: #1e293b;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #334155;
            margin-bottom: 20px;
        }
        .trade-table th {
            background: #334155;
            padding: 12px;
            text-align: left;
            color: #e2e8f0;
            font-weight: 600;
        }
        .trade-table td {
            padding: 12px;
            border-bottom: 1px solid #475569;
        }
        .trade-table tr:hover {
            background: #2d3748;
        }
        
        .exchange-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .exchange-badge.gemini {
            background: #00dc82;
            color: #000;
        }
        .exchange-badge.binance {
            background: #f0b90b;
            color: #000;
        }
        
        .side-buy { color: #10b981; }
        .side-sell { color: #ef4444; }
        
        .last-updated {
            text-align: center;
            color: #94a3b8;
            font-size: 0.9em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #334155;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin: 20px 0;
        }
        .control-btn {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .control-btn:hover {
            background: #2563eb;
        }
        
        .status-badge {
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.9em;
            margin: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Trading System Dashboard</h1>
            <p class="subtitle">Investment positions + Available cash separately | {{ total_trades }} positions, {{ win_rate }}% win rate</p>
            
            <div class="controls">
                <a href="http://localhost:5011" class="control-btn" target="_blank">📈 Trades Dashboard</a>
                <a href="http://localhost:5014" class="control-btn" target="_blank">🔄 Real-Time Prices</a>
                <a href="#llm-reports" class="control-btn">🧠 LLM Reports</a>
            </div>
        </div>
        
        <!-- CASH SECTION - PROMINENT -->
        <div class="cash-section">
            <div class="cash-label">💰 AVAILABLE CASH FOR TRADING</div>
            <div class="cash-amount">${{ "%.2f"|format(available_cash) }}</div>
            <div class="cash-note">Cash on hand - NOT an investment position | Ready for Gemini-only trading bot</div>
        </div>
        
        <!-- INVESTMENT SUMMARY -->
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-label">Total Investment</div>
                <div class="summary-value">${{ "%.2f"|format(total_investment) }}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Current Portfolio</div>
                <div class="summary-value">${{ "%.2f"|format(total_portfolio) }}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Cumulative P&L</div>
                <div class="summary-value {{ 'positive' if total_pnl > 0 else 'negative' }}">
                    ${{ "%+.2f"|format(total_pnl) }} ({{ "%+.1f"|format(total_pnl_percent) }}%)
                </div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Positions Value</div>
                <div class="summary-value">${{ "%.2f"|format(positions_value) }}</div>
            </div>
        </div>
        
        <!-- INVESTMENT POSITIONS TABLE -->
        <div class="section">
            <div class="section-title">📈 INVESTMENT POSITIONS (NOT including cash)</div>
            <table class="trade-table">
                <thead>
                    <tr>
                        <th>Exchange</th>
                        <th>Symbol</th>
                        <th>Side</th>
                        <th>Entry Price</th>
                        <th>Current Price</th>
                        <th>P&L</th>
                        <th>P&L %</th>
                        <th>Amount</th>
                        <th>Value</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    {% for trade in trades %}
                    {% if trade.symbol != 'INVESTMENT/SUMMARY' %}
                    <tr>
                        <td>
                            <span class="exchange-badge {{ trade.exchange }}">
                                {{ trade.exchange|upper }}
                            </span>
                        </td>
                        <td><strong>{{ trade.symbol }}</strong></td>
                        <td class="side-{{ trade.side }}">{{ trade.side|upper }}</td>
                        <td>${{ "%.2f"|format(trade.price) }}</td>
                        <td>{% if 'current_price' in trade %}${{ "%.2f"|format(trade.current_price) }}{% else %}N/A{% endif %}</td>
                        <td class="{% if 'pnl' in trade %}{{ 'positive' if trade.pnl > 0 else 'negative' if trade.pnl < 0 else '' }}{% endif %}">
                            {% if 'pnl' in trade %}${{ "%+.2f"|format(trade.pnl) }}{% else %}N/A{% endif %}
                        </td>
                        <td class="{% if 'pnl_percent' in trade %}{{ 'positive' if trade.pnl_percent > 0 else 'negative' if trade.pnl_percent < 0 else '' }}{% endif %}">
                            {% if 'pnl_percent' in trade %}{{ "%+.2f"|format(trade.pnl_percent) }}%{% else %}N/A{% endif %}
                        </td>
                        </td>
                        <td>{{ "%.6f"|format(trade.amount) }}</td>
                        <td>${{ "%.2f"|format(trade.value) }}</td>
                        <td>{{ trade.timestamp[:19].replace('T', ' ') }}</td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <!-- INVESTMENT SUMMARY DETAIL -->
        {% for trade in trades %}
        {% if trade.symbol == 'INVESTMENT/SUMMARY' %}
        <div class="section">
            <div class="section-title">📋 INVESTMENT SUMMARY</div>
            <div class="summary-card" style="text-align: left; padding: 20px;">
                <div style="color: #cbd5e1; margin-bottom: 10px; font-size: 1.1em;">
                    {{ trade.note }}
                </div>
                <div style="color: #94a3b8; font-size: 0.9em;">
                    Total money invested: ${{ "%.2f"|format(trade.value) }} | 
                    Real cumulative P&L: ${{ "%+.2f"|format(trade.pnl) }} ({{ "%+.2f"|format(trade.pnl_percent) }}%)
                </div>
            </div>
        </div>
        {% endif %}
        {% endfor %}
        
        <div class="last-updated">
            <p>Dashboard updated: {{ update_time }}</p>
            <p>Auto-refreshes every 30 seconds</p>
            <p>Cash: ${{ "%.2f"|format(available_cash) }} | Positions: ${{ "%.2f"|format(positions_value) }} | Total: ${{ "%.2f"|format(total_portfolio) }}</p>
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

def load_available_cash():
    """Load available cash from separate file"""
    cash_file = os.path.join(BASE_DIR, "trading_data", "available_cash.json")
    
    try:
        with open(cash_file, 'r') as f:
            cash_data = json.load(f)
        return cash_data.get('available_cash_usd', 0)
    except:
        return 0

@app.route('/')
def dashboard():
    try:
        # Load trades
        trades_file = os.path.join(BASE_DIR, "trading_data", "trades.json")
        with open(trades_file, 'r') as f:
            trades = json.load(f)
        
        # Load available cash separately
        available_cash = load_available_cash()
        
        # Calculate statistics (EXCLUDING cash from trades)
        investment_trades = [t for t in trades if t.get('symbol') != 'INVESTMENT/SUMMARY']
        total_trades = len(investment_trades)
        
        # Get investment summary
        investment_summary = [t for t in trades if t.get('symbol') == 'INVESTMENT/SUMMARY']
        if investment_summary:
            total_investment = investment_summary[0].get('value', 0)
            total_pnl = investment_summary[0].get('pnl', 0)
            total_pnl_percent = investment_summary[0].get('pnl_percent', 0)
        else:
            total_investment = sum(t.get('value', 0) for t in investment_trades)
            total_pnl = sum(t.get('pnl', 0) for t in investment_trades)
            total_pnl_percent = (total_pnl / total_investment * 100) if total_investment > 0 else 0
        
        # Calculate positions value (EXCLUDING cash)
        positions_value = sum(t.get('value', 0) for t in investment_trades)
        
        # Total portfolio = positions + cash
        total_portfolio = positions_value + available_cash
        
        # Win rate
        winning_trades = sum(1 for t in investment_trades if t.get('pnl', 0) > 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Prepare template data
        data = {
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'trades': trades,
            'total_trades': total_trades,
            'win_rate': round(win_rate, 1),
            'available_cash': available_cash,
            'total_investment': total_investment,
            'total_portfolio': total_portfolio,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'positions_value': positions_value
        }
        
        return render_template_string(HTML_TEMPLATE, **data)
        
    except Exception as e:
        return f"Error loading dashboard: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=False)