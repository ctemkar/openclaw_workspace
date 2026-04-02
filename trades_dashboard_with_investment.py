#!/usr/bin/env python3
"""
Trades Dashboard with TOTAL INVESTMENT and CUMULATIVE P&L
"""

from flask import Flask, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📈 Trades Dashboard - TOTAL INVESTMENT & P&L</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="30">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 20px;
            background: #f8f9fa;
            color: #212529;
        }
        .dashboard { 
            max-width: 1400px; 
            margin: 0 auto; 
        }
        h1 { 
            color: #2c3e50; 
            margin-bottom: 10px;
        }
        
        /* INVESTMENT SUMMARY - PROMINENT */
        .investment-summary {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .investment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }
        .investment-card {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .investment-value {
            font-size: 1.8em;
            font-weight: bold;
            margin: 10px 0;
        }
        .investment-label {
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 5px;
        }
        
        /* CASH SECTION */
        .cash-section {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            color: white;
            text-align: center;
        }
        .cash-amount {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        
        /* POSITIONS SUMMARY */
        .summary {
            background: #ffffff;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border: 1px solid #dee2e6;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .summary-card {
            text-align: center;
            padding: 10px;
        }
        .summary-value {
            font-size: 1.5em;
            font-weight: bold;
            margin: 5px 0;
        }
        .summary-label {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .positive { color: #28a745; font-weight: bold; }
        .negative { color: #dc3545; font-weight: bold; }
        .neutral { color: #6c757d; }
        
        /* TRADES TABLE */
        table { 
            border-collapse: collapse; 
            width: 100%; 
            margin: 20px 0;
            font-size: 14px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        th, td { 
            border: 1px solid #dee2e6; 
            padding: 12px; 
            text-align: right;
        }
        th { 
            background-color: #2c3e50; 
            color: white; 
            text-align: center;
            font-weight: 600;
        }
        tr:nth-child(even) { background-color: #f8f9fa; }
        tr:hover { background-color: #e9ecef; }
        
        .exchange-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 5px;
        }
        .binance { background: #f0b90b; color: black; }
        .gemini { background: #00d2ff; color: black; }
        .system { background: #6c757d; color: white; }
        
        .last-updated {
            color: #6c757d;
            font-size: 12px;
            margin-top: 20px;
            text-align: center;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin: 15px 0;
            flex-wrap: wrap;
        }
        .control-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
        }
        .control-btn:hover {
            background: #2980b9;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>📈 Trades Dashboard - TOTAL INVESTMENT & CUMULATIVE P&L</h1>
        <p><strong>Live prices with complete investment tracking</strong></p>
        
        <div class="controls">
            <a href="http://localhost:5007" class="control-btn" target="_blank">🏠 Main Dashboard</a>
            <a href="http://localhost:5014" class="control-btn" target="_blank">🔄 Real-Time Prices</a>
            <a href="#positions" class="control-btn">📊 Positions</a>
        </div>
        
        <!-- INVESTMENT SUMMARY -->
        <div class="investment-summary">
            <h2 style="margin-top: 0; color: white;">💰 TOTAL INVESTMENT SUMMARY</h2>
            <div class="investment-grid">
                <div class="investment-card">
                    <div class="investment-label">Total Money Invested</div>
                    <div class="investment-value">${{ "%.2f"|format(total_investment) }}</div>
                </div>
                <div class="investment-card">
                    <div class="investment-label">Current Portfolio Value</div>
                    <div class="investment-value">${{ "%.2f"|format(total_portfolio) }}</div>
                </div>
                <div class="investment-card">
                    <div class="investment-label">Cumulative P&L</div>
                    <div class="investment-value {{ 'positive' if cumulative_pnl >= 0 else 'negative' }}">
                        ${{ "%+.2f"|format(cumulative_pnl) }}
                    </div>
                    <div class="{{ 'positive' if cumulative_pnl_percent >= 0 else 'negative' }}">
                        {{ "%+.1f"|format(cumulative_pnl_percent) }}%
                    </div>
                </div>
                <div class="investment-card">
                    <div class="investment-label">Recovery Needed</div>
                    <div class="investment-value">
                        {% if cumulative_pnl < 0 %}
                        ${{ "%.2f"|format(-cumulative_pnl) }}
                        {% else %}
                        $0.00
                        {% endif %}
                    </div>
                </div>
            </div>
            {% if investment_note %}
            <div style="margin-top: 15px; font-size: 0.9em; opacity: 0.9; font-style: italic;">
                {{ investment_note }}
            </div>
            {% endif %}
        </div>
        
        <!-- CASH SECTION -->
        <div class="cash-section">
            <div style="font-size: 1.1em; margin-bottom: 10px;">💵 AVAILABLE CASH FOR TRADING</div>
            <div class="cash-amount">${{ "%.2f"|format(available_cash) }}</div>
            <div style="font-size: 0.9em; opacity: 0.9;">
                Cash on hand - NOT included in investment positions
            </div>
        </div>
        
        <!-- POSITIONS SUMMARY -->
        <div class="summary">
            <h2 style="margin-top: 0; color: #2c3e50;">📊 CURRENT POSITIONS SUMMARY</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="summary-label">Total Positions</div>
                    <div class="summary-value">{{ total_positions }}</div>
                </div>
                <div class="summary-card">
                    <div class="summary-label">Positions Value</div>
                    <div class="summary-value">${{ "%.2f"|format(positions_value) }}</div>
                </div>
                <div class="summary-card">
                    <div class="summary-label">Positions P&L</div>
                    <div class="summary-value {{ 'positive' if positions_pnl >= 0 else 'negative' }}">
                        ${{ "%+.2f"|format(positions_pnl) }}
                    </div>
                </div>
                <div class="summary-card">
                    <div class="summary-label">Win Rate</div>
                    <div class="summary-value">{{ win_rate }}%</div>
                </div>
            </div>
        </div>
        
        <!-- POSITIONS TABLE -->
        <a name="positions"></a>
        <h2>💱 INVESTMENT POSITIONS</h2>
        <table>
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
            {% for trade in positions %}
            <tr>
                <td>
                    <span class="exchange-badge {{ trade.exchange }}">
                        {{ trade.exchange|upper }}
                    </span>
                </td>
                <td><strong>{{ trade.symbol }}</strong></td>
                <td class="{{ 'positive' if trade.side == 'buy' else 'negative' }}">
                    {{ trade.side|upper }}
                </td>
                <td>${{ "%.2f"|format(trade.price) }}</td>
                <td>${{ "%.2f"|format(trade.current_price) }}</td>
                <td class="{{ 'positive' if trade.pnl > 0 else 'negative' if trade.pnl < 0 else 'neutral' }}">
                    ${{ "%+.2f"|format(trade.pnl) }}
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
            <p>Dashboard updated: {{ update_time }}</p>
            <p>Total Portfolio: ${{ "%.2f"|format(total_portfolio) }} = Positions (${{ "%.2f"|format(positions_value) }}) + Cash (${{ "%.2f"|format(available_cash) }})</p>
            <p>Cumulative P&L: ${{ "%+.2f"|format(cumulative_pnl) }} ({{ "%+.1f"|format(cumulative_pnl_percent) }}%) from ${{ "%.2f"|format(total_investment) }} investment</p>
            <p>Auto-refreshes every 30 seconds</p>
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
def trades_dashboard():
    try:
        # Load trades
        trades_file = os.path.join(BASE_DIR, "trading_data", "trades.json")
        with open(trades_file, 'r') as f:
            trades = json.load(f)
        
        # Load available cash
        available_cash = load_available_cash()
        
        # Separate investment summary from positions
        investment_summary = [t for t in trades if t.get('symbol') == 'INVESTMENT/SUMMARY']
        positions = [t for t in trades if t.get('symbol') != 'INVESTMENT/SUMMARY']
        
        # Get investment data
        if investment_summary:
            investment_data = investment_summary[0]
            total_investment = investment_data.get('value', 0)
            cumulative_pnl = investment_data.get('pnl', 0)
            cumulative_pnl_percent = investment_data.get('pnl_percent', 0)
            investment_note = investment_data.get('note', '')
        else:
            # Calculate from positions if no summary
            total_investment = sum(t.get('value', 0) for t in positions)
            cumulative_pnl = sum(t.get('pnl', 0) for t in positions)
            cumulative_pnl_percent = (cumulative_pnl / total_investment * 100) if total_investment > 0 else 0
            investment_note = ''
        
        # Calculate positions statistics
        total_positions = len(positions)
        positions_value = sum(t.get('value', 0) for t in positions)
        positions_pnl = sum(t.get('pnl', 0) for t in positions)
        
        # Total portfolio = positions + cash
        total_portfolio = positions_value + available_cash
        
        # Win rate
        winning_positions = sum(1 for t in positions if t.get('pnl', 0) > 0)
        win_rate = (winning_positions / total_positions * 100) if total_positions > 0 else 0
        
        # Prepare template data
        data = {
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'positions': positions,
            'total_positions': total_positions,
            'positions_value': positions_value,
            'positions_pnl': positions_pnl,
            'win_rate': round(win_rate, 1),
            'available_cash': available_cash,
            'total_investment': total_investment,
            'total_portfolio': total_portfolio,
            'cumulative_pnl': cumulative_pnl,
            'cumulative_pnl_percent': cumulative_pnl_percent,
            'investment_note': investment_note
        }
        
        return render_template_string(HTML_TEMPLATE, **data)
        
    except Exception as e:
        return f"Error loading trades dashboard: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=False)