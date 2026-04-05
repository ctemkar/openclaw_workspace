#!/usr/bin/env python3
"""
DASHBOARD TRUTH - Shows ONLY REAL Gemini data, no simulations
"""

from flask import Flask, render_template_string, jsonify
import json
import os
import time
import ccxt
from datetime import datetime
import threading

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>💰 Trading Truth Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 20px;
            background: #0f172a;
            color: #e2e8f0;
        }
        .container {
            max-width: 800px;
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
        .truth-card {
            background: #1e293b;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            border: 2px solid #334155;
        }
        .truth-card h2 {
            margin-top: 0;
            color: #60a5fa;
            border-bottom: 2px solid #334155;
            padding-bottom: 10px;
        }
        .data-row {
            display: flex;
            justify-content: space-between;
            margin: 12px 0;
            padding: 10px;
            background: #0f172a;
            border-radius: 5px;
            border: 1px solid #334155;
        }
        .label {
            color: #94a3b8;
        }
        .value {
            font-weight: bold;
            font-size: 1.1em;
        }
        .positive { color: #4ade80; }
        .negative { color: #f87171; }
        .neutral { color: #e2e8f0; }
        .warning {
            background: #7f1d1d;
            border: 2px solid #f87171;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        .refresh {
            text-align: center;
            margin: 20px 0;
        }
        button {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background: #2563eb;
        }
        .last-updated {
            text-align: center;
            color: #64748b;
            font-size: 0.8em;
            margin-top: 30px;
        }
    </style>
    <script>
        function refreshData() {
            fetch('/api/truth')
                .then(response => response.json())
                .then(data => {
                    // Update timestamp
                    document.getElementById('timestamp').textContent = new Date(data.timestamp).toLocaleString();
                    
                    // Update Gemini data
                    document.getElementById('gemini-total').textContent = '$' + data.gemini.total_value.toFixed(2);
                    document.getElementById('gemini-usd').textContent = '$' + data.gemini.usd.toFixed(2);
                    document.getElementById('gemini-eth').textContent = data.gemini.eth_amount.toFixed(8) + ' ETH ($' + data.gemini.eth_value.toFixed(2) + ')';
                    document.getElementById('gemini-sol').textContent = data.gemini.sol_amount.toFixed(8) + ' SOL ($' + data.gemini.sol_value.toFixed(2) + ')';
                    
                    // Update trading status
                    document.getElementById('trading-status').textContent = data.trading.status;
                    document.getElementById('trading-cycles').textContent = data.trading.cycles;
                    document.getElementById('trading-opportunities').textContent = data.trading.opportunities;
                    
                    // Update P&L
                    const pnlEl = document.getElementById('total-pnl');
                    pnlEl.textContent = '$' + data.pnl.total.toFixed(2);
                    pnlEl.className = 'value ' + (data.pnl.total >= 0 ? 'positive' : 'negative');
                    
                    const pnlPercentEl = document.getElementById('pnl-percent');
                    pnlPercentEl.textContent = data.pnl.percent.toFixed(2) + '%';
                    pnlPercentEl.className = 'value ' + (data.pnl.percent >= 0 ? 'positive' : 'negative');
                    
                    // Update warnings
                    const warningsEl = document.getElementById('warnings');
                    warningsEl.innerHTML = '';
                    data.warnings.forEach(warning => {
                        const div = document.createElement('div');
                        div.className = 'warning';
                        div.textContent = '⚠️ ' + warning;
                        warningsEl.appendChild(div);
                    });
                })
                .catch(error => {
                    console.error('Error refreshing data:', error);
                });
        }
        
        // Refresh every 60 seconds
        setInterval(refreshData, 60000);
        
        // Initial load
        document.addEventListener('DOMContentLoaded', refreshData);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 TRADING TRUTH DASHBOARD</h1>
            <p>Showing ONLY REAL Gemini data - No simulations, no stale data</p>
        </div>
        
        <div id="warnings">
            <!-- Warnings will appear here -->
        </div>
        
        <div class="truth-card">
            <h2>📊 REAL GEMINI BALANCE</h2>
            <div class="data-row">
                <span class="label">Total Portfolio Value</span>
                <span class="value" id="gemini-total">$---</span>
            </div>
            <div class="data-row">
                <span class="label">USD Balance</span>
                <span class="value" id="gemini-usd">$---</span>
            </div>
            <div class="data-row">
                <span class="label">ETH Holdings</span>
                <span class="value" id="gemini-eth">---</span>
            </div>
            <div class="data-row">
                <span class="label">SOL Holdings</span>
                <span class="value" id="gemini-sol">---</span>
            </div>
        </div>
        
        <div class="truth-card">
            <h2>🎯 TRADING STATUS</h2>
            <div class="data-row">
                <span class="label">Bot Status</span>
                <span class="value" id="trading-status">---</span>
            </div>
            <div class="data-row">
                <span class="label">Cycles Completed</span>
                <span class="value" id="trading-cycles">---</span>
            </div>
            <div class="data-row">
                <span class="label">Opportunities Found</span>
                <span class="value" id="trading-opportunities">---</span>
            </div>
        </div>
        
        <div class="truth-card">
            <h2>📈 REAL P&L (From $946.97 initial)</h2>
            <div class="data-row">
                <span class="label">Total P&L</span>
                <span class="value neutral" id="total-pnl">$---</span>
            </div>
            <div class="data-row">
                <span class="label">P&L %</span>
                <span class="value neutral" id="pnl-percent">---%</span>
            </div>
        </div>
        
        <div class="refresh">
            <button onclick="refreshData()">🔄 Refresh Now</button>
            <p>Auto-refreshes every 60 seconds</p>
        </div>
        
        <div class="last-updated">
            Last updated: <span id="timestamp">---</span>
        </div>
    </div>
</body>
</html>
'''

# Cache for truth data
truth_cache = {
    'timestamp': datetime.now().isoformat(),
    'gemini': {
        'total_value': 0,
        'usd': 0,
        'eth_amount': 0,
        'eth_value': 0,
        'sol_amount': 0,
        'sol_value': 0
    },
    'trading': {
        'status': 'unknown',
        'cycles': 0,
        'opportunities': 0
    },
    'pnl': {
        'total': 0,
        'percent': 0
    },
    'warnings': []
}

def get_real_gemini_data():
    """Get REAL Gemini balance - no simulations"""
    try:
        with open(os.path.join(BASE_DIR, 'secure_keys/.gemini_key'), 'r') as f:
            key = f.read().strip()
        with open(os.path.join(BASE_DIR, 'secure_keys/.gemini_secret'), 'r') as f:
            secret = f.read().strip()
        
        exchange = ccxt.gemini({
            'apiKey': key,
            'secret': secret,
            'enableRateLimit': True
        })
        
        balance = exchange.fetch_balance()
        usd = balance['total'].get('USD', 0)
        eth = balance['total'].get('ETH', 0)
        sol = balance['total'].get('SOL', 0)
        
        # Get current prices
        if eth > 0:
            eth_ticker = exchange.fetch_ticker('ETH/USD')
            eth_value = eth * eth_ticker['last']
        else:
            eth_value = 0
        
        if sol > 0:
            sol_ticker = exchange.fetch_ticker('SOL/USD')
            sol_value = sol * sol_ticker['last']
        else:
            sol_value = 0
        
        total_value = usd + eth_value + sol_value
        
        return {
            'total_value': total_value,
            'usd': usd,
            'eth_amount': eth,
            'eth_value': eth_value,
            'sol_amount': sol,
            'sol_value': sol_value
        }
        
    except Exception as e:
        print(f"❌ Error getting Gemini data: {e}")
        return None

def get_trading_status():
    """Get REAL trading bot status"""
    try:
        # Check if trader is running
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        trader_running = 'real_26_crypto_trader.py' in result.stdout
        
        # Read trader log
        cycles = 0
        opportunities = 0
        log_path = os.path.join(BASE_DIR, 'trader.log')
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                lines = f.readlines()[-50:]  # Last 50 lines
                for line in lines:
                    if 'CYCLE' in line and 'STARTING' in line:
                        cycles += 1
                    if 'opportunities found' in line.lower():
                        import re
                        match = re.search(r'(\d+)\s+opportunities', line.lower())
                        if match:
                            opportunities = int(match.group(1))
        
        status = 'ACTIVE' if trader_running else 'STOPPED'
        
        return {
            'status': status,
            'cycles': cycles,
            'opportunities': opportunities
        }
        
    except Exception as e:
        print(f"❌ Error getting trading status: {e}")
        return {'status': 'ERROR', 'cycles': 0, 'opportunities': 0}

def calculate_real_pnl(current_value):
    """Calculate REAL P&L from initial $946.97"""
    initial = 946.97
    pnl = current_value - initial
    pnl_percent = (pnl / initial) * 100
    
    return {
        'total': pnl,
        'percent': pnl_percent
    }

def get_warnings(gemini_data, trading_data):
    """Get warnings about discrepancies"""
    warnings = []
    
    # Check if trading bot is finding opportunities
    if trading_data['opportunities'] == 0 and trading_data['cycles'] > 10:
        warnings.append(f"Trading bot found 0 opportunities in {trading_data['cycles']} cycles")
    
    # Check Gemini balance
    if gemini_data['total_value'] < 500:
        warnings.append(f"Low Gemini balance: ${gemini_data['total_value']:.2f}")
    
    # Check if there are other dashboards showing fake data
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5012))
        if result == 0:
            warnings.append("Port 5012 dashboard showing simulated/old trades")
    except:
        pass
    
    return warnings

def update_truth_cache():
    """Update cache with REAL data"""
    global truth_cache
    
    # Get REAL Gemini data
    gemini_data = get_real_gemini_data()
    if gemini_data:
        truth_cache['gemini'] = gemini_data
    
    # Get trading status
    trading_data = get_trading_status()
    truth_cache['trading'] = trading_data
    
    # Calculate REAL P&L
    current_value = gemini_data['total_value'] if gemini_data else 0
    truth_cache['pnl'] = calculate_real_pnl(current_value)
    
    # Get warnings
    truth_cache['warnings'] = get_warnings(gemini_data, trading_data)
    
    # Update timestamp
    truth_cache['timestamp'] = datetime.now().isoformat()

def cache_updater_thread():
    """Thread to periodically update cache"""
    while True:
        update_truth_cache()
        time.sleep(60)  # Update every 60 seconds

@app.route('/')
def dashboard():
    """Main truth dashboard page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/truth')
def api_truth():
    """API endpoint for truth data"""
    return jsonify(truth_cache)

if __name__ == '__main__':
    # Start cache updater thread
    updater = threading.Thread(target=cache_updater_thread, daemon=True)
    updater.start()
    
    # Initial cache update
    update_truth_cache()
    
    print("="*70)
    print("💰 TRADING TRUTH DASHBOARD")
    print("="*70)
    print("Showing ONLY REAL Gemini data - No simulations, no stale data")
    print(f"📊 Dashboard available at: http://localhost:5015")
    print(f"📈 API endpoint: http://localhost:5015/api/truth")
    print("="*70)
    
    # Show initial data
    print(f"\n📊 INITIAL TRUTH DATA:")
    print(f"  Gemini Total: ${truth_cache['gemini']['total_value']:.2f}")
    print(f"  USD: ${truth_cache['gemini']['usd']:.2f}")
    print(f"  ETH: {truth_cache['gemini']['eth_amount']:.8f} (${truth_cache['gemini']['eth_value']:.2f})")
    print(f"  SOL: {truth_cache['gemini']['sol_amount']:.8f} (${truth_cache['gemini']['sol_value']:.2f})")
    print(f"  P&L: ${truth_cache['pnl']['total']:.2f} ({truth_cache['pnl']['percent']:.2f}%)")
    
    if truth_cache['warnings']:
        print(f"\n⚠️  WARNINGS:")
        for warning in truth_cache['warnings']:
            print(f"  • {warning}")
    
    app.run(host='0.0.0.0', port=5015, debug=False)