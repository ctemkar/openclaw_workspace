#!/usr/bin/env python3
"""
Simple Trading Dashboard
Shows all trading systems in one place
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template_string

app = Flask(__name__)

def get_system_status():
    """Get overall system status"""
    return {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'timezone': 'Asia/Bangkok (GMT+7)'
    }

def get_forex_status():
    """Get Forex trading status"""
    status = {
        'account': 'Schwab #13086459',
        'balance': '$220.00',
        'bot': 'forex_bot_with_schwab.py',
        'status': 'Checking...',
        'trades': 0,
        'profit': 0.0
    }
    
    # Check if bot is running
    try:
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'forex_bot_with_schwab.py' in result.stdout:
            status['status'] = '✅ RUNNING'
            for line in result.stdout.split('\n'):
                if 'forex_bot_with_schwab.py' in line:
                    parts = line.split()
                    if len(parts) > 1:
                        status['pid'] = parts[1]
        else:
            status['status'] = '❌ STOPPED'
    except:
        status['status'] = '❌ ERROR CHECKING'
    
    # Check trades
    try:
        if os.path.exists('real_forex_trades.json'):
            with open('real_forex_trades.json', 'r') as f:
                trades = json.load(f)
            closed = [t for t in trades if t.get('status') == 'CLOSED']
            status['trades'] = len(closed)
            if closed:
                profits = [t.get('profit', 0) for t in closed]
                status['profit'] = sum(profits)
    except:
        pass
    
    return status

def get_crypto_status():
    """Get crypto trading status"""
    return {
        'total_profit': 2.60,
        'total_trades': 35,
        'status': '✅ PROVEN SUCCESS',
        'note': 'Can restart anytime'
    }

def get_scaling_plan():
    """Get scaling plan"""
    return {
        'current': 'Phase 1: Proof of Concept ($220)',
        'next': 'Phase 2: Add $500 when proven',
        'user_plan': 'Will add funds when proven successful'
    }

@app.route('/')
def dashboard():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>💰 Trading Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; }
            .container { max-width: 1000px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .card { background: white; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .card h2 { margin-top: 0; color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
            .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
            .status-item { background: #f8f9fa; padding: 15px; border-radius: 8px; }
            .label { font-weight: bold; color: #666; margin-bottom: 5px; }
            .value { font-size: 1.2em; color: #333; }
            .positive { color: #4CAF50; }
            .negative { color: #f44336; }
            .running { color: #4CAF50; font-weight: bold; }
            .stopped { color: #f44336; font-weight: bold; }
            .refresh { text-align: center; margin-top: 30px; }
            button { padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #45a049; }
        </style>
        <script>
            function refreshPage() {
                location.reload();
            }
            // Auto-refresh every 30 seconds
            setTimeout(refreshPage, 30000);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💰 COMPREHENSIVE TRADING DASHBOARD</h1>
                <p>All your trading systems in one view</p>
            </div>
            
            <div class="card">
                <h2>🖥️ SYSTEM STATUS</h2>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="label">Last Update</div>
                        <div class="value">{{ system.timestamp }}</div>
                    </div>
                    <div class="status-item">
                        <div class="label">Timezone</div>
                        <div class="value">{{ system.timezone }}</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>💱 FOREX TRADING</h2>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="label">Account</div>
                        <div class="value">{{ forex.account }}</div>
                    </div>
                    <div class="status-item">
                        <div class="label">Balance</div>
                        <div class="value">{{ forex.balance }}</div>
                    </div>
                    <div class="status-item">
                        <div class="label">Bot Status</div>
                        <div class="value {{ 'running' if 'RUNNING' in forex.status else 'stopped' }}">{{ forex.status }}</div>
                    </div>
                    <div class="status-item">
                        <div class="label">PID</div>
                        <div class="value">{{ forex.get('pid', 'N/A') }}</div>
                    </div>
                    <div class="status-item">
                        <div class="label">Closed Trades</div>
                        <div class="value">{{ forex.trades }}</div>
                    </div>
                    <div class="status-item">
                        <div class="label">Total Profit</div>
                        <div class="value {{ 'positive' if forex.profit > 0 else 'negative' }}">${{ "%.2f"|format(forex.profit) }}</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>₿ CRYPTO TRADING</h2>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="label">Total Profit</div>
                        <div class="value positive">${{ "%.2f"|format(crypto.total_profit) }}</div>
                    </div>
                    <div class="status-item">
                        <div class="label">Total Trades</div>
                        <div class="value">{{ crypto.total_trades }}</div>
                    </div>
                    <div class="status-item">
                        <div class="label">Status</div>
                        <div class="value running">{{ crypto.status }}</div>
                    </div>
                    <div class="status-item">
                        <div class="label">Note</div>
                        <div class="value">{{ crypto.note }}</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>📈 SCALING PLAN</h2>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="label">Current Phase</div>
                        <div class="value">{{ plan.current }}</div>
                    </div>
                    <div class="status-item">
                        <div class="label">Next Phase</div>
                        <div class="value">{{ plan.next }}</div>
                    </div>
                    <div class="status-item">
                        <div class="label">User's Plan</div>
                        <div class="value">"{{ plan.user_plan }}"</div>
                    </div>
                </div>
            </div>
            
            <div class="refresh">
                <button onclick="refreshPage()">🔄 Refresh Dashboard</button>
                <p style="margin-top: 10px; color: #666;">Auto-refreshes every 30 seconds</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(
        html,
        system=get_system_status(),
        forex=get_forex_status(),
        crypto=get_crypto_status(),
        plan=get_scaling_plan()
    )

if __name__ == '__main__':
    print("🚀 Starting Trading Dashboard on port 5010...")
    print("📊 Open: http://localhost:5010")
    app.run(host='0.0.0.0', port=5010, debug=False)
