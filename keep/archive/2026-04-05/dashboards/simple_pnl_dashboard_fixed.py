#!/usr/bin/env python3
"""
SIMPLE P&L DASHBOARD - FIXED VERSION
Shows P&L information as requested
"""

from flask import Flask, jsonify, render_template_string
import json
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📊 P&L DASHBOARD - Most Important</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f0f0f0;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .section {
            margin: 30px 0;
            padding: 20px;
            border-radius: 8px;
            background: #f8f9fa;
        }
        .section-title {
            color: #34495e;
            margin-top: 0;
            font-size: 1.4em;
        }
        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .data-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .data-card h3 {
            margin-top: 0;
            color: #2c3e50;
            font-size: 1em;
        }
        .data-value {
            font-size: 1.8em;
            font-weight: bold;
            margin: 10px 0;
        }
        .positive {
            color: #27ae60;
        }
        .negative {
            color: #e74c3c;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f8f9fa;
            font-weight: bold;
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .timestamp {
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 P&L INFORMATION - MOST IMPORTANT</h1>
        <p><em>Updated: {{ timestamp }}</em></p>
        
        <div class="section">
            <h2 class="section-title">🔴 CUMULATIVE P&L (NEVER RESETS)</h2>
            <div class="data-grid">
                <div class="data-card">
                    <h3>Initial Capital</h3>
                    <div class="data-value">${{ "%.2f"|format(initial) }}</div>
                    <p>Total BTC purchases</p>
                </div>
                <div class="data-card">
                    <h3>Current Capital</h3>
                    <div class="data-value">${{ "%.2f"|format(current) }}</div>
                    <p>Real current value</p>
                </div>
                <div class="data-card">
                    <h3>Cumulative P&L</h3>
                    <div class="data-value {{ 'positive' if pnl >= 0 else 'negative' }}">
                        ${{ "%+.2f"|format(pnl) }} ({{ "%+.2f"|format(pnl_percent) }}%)
                    </div>
                    <p>Never resets</p>
                </div>
                <div class="data-card">
                    <h3>Recovery Needed</h3>
                    <div class="data-value">
                        +{{ "%.1f"|format(recovery_percent) }}%
                    </div>
                    <p>${{ "%.2f"|format(recovery_needed) }}</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">💰 CURRENT STATUS</h2>
            <table>
                <tr>
                    <td>Trading Bot</td>
                    <td><strong>{{ bot_status }}</strong></td>
                </tr>
                <tr>
                    <td>Gemini Status</td>
                    <td>{{ gemini_status }}</td>
                </tr>
                <tr>
                    <td>Binance Status</td>
                    <td>{{ binance_status }}</td>
                </tr>
                <tr>
                    <td>Available Capital</td>
                    <td><strong>${{ "%.2f"|format(available_capital) }}</strong></td>
                </tr>
            </table>
        </div>
        
        <div class="timestamp">
            Generated: {{ timestamp }} | Simple Fixed Dashboard
        </div>
    </div>
</body>
</html>
'''

def load_system_status():
    """Load system status from file"""
    try:
        with open('system_status.json', 'r') as f:
            return json.load(f)
    except:
        return {}

@app.route('/')
def dashboard():
    """Main dashboard with P&L information"""
    system_status = load_system_status()
    capital = system_status.get('capital', {})
    
    # Get current bot status
    import subprocess
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'real_26_crypto_trader.py' in result.stdout:
            bot_status = '✅ RUNNING'
        else:
            bot_status = '❌ STOPPED'
    except:
        bot_status = 'UNKNOWN'
    
    # Exchange status from system_status
    exchange_status = system_status.get('exchange_status', {})
    gemini_status = exchange_status.get('gemini', 'UNKNOWN')
    binance_status = exchange_status.get('binance', 'UNKNOWN')
    
    # If Binance is blocked, show the error
    if binance_status == 'BLOCKED_GEOGRAPHIC_RESTRICTIONS':
        binance_status = '❌ BLOCKED (Geographic restrictions)'
    
    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        initial=capital.get('initial', 946.97),
        current=capital.get('current', 531.65),
        pnl=capital.get('pnl', -415.32),
        pnl_percent=capital.get('pnl_percent', -43.86),
        recovery_needed=capital.get('recovery_needed', 415.32),
        recovery_percent=capital.get('recovery_percent_needed', 78.1),
        bot_status=bot_status,
        gemini_status=gemini_status,
        binance_status=binance_status,
        available_capital=capital.get('free_usd', 134.27)
    )

@app.route('/api/pnl')
def api_pnl():
    """JSON P&L data"""
    system_status = load_system_status()
    capital = system_status.get('capital', {})
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'initial_capital': capital.get('initial', 946.97),
        'current_capital': capital.get('current', 531.65),
        'cumulative_pnl': capital.get('pnl', -415.32),
        'cumulative_pnl_percent': capital.get('pnl_percent', -43.86),
        'recovery_needed': capital.get('recovery_needed', 415.32),
        'recovery_percent_needed': capital.get('recovery_percent_needed', 78.1),
        'available_capital': capital.get('free_usd', 134.27)
    })

if __name__ == '__main__':
    print('🚀 STARTING SIMPLE P&L DASHBOARD (FIXED VERSION)')
    print('   • Port: 5008')
    print('   • Shows: P&L information as requested')
    print('   • Priority: Cumulative P&L first')
    print('   • Access: http://localhost:5008/')
    print()
    app.run(host='0.0.0.0', port=5008, debug=False)