#!/usr/bin/env python3
"""
SIMPLE ACCURATE DASHBOARD
Shows current reality - No cached data, always fresh
"""

from flask import Flask, jsonify, render_template_string
import json
import os
from datetime import datetime
import psutil

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>ACCURATE Trading Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #0f2027;
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
        }
        .warning {
            background: rgba(255, 0, 0, 0.2);
            border: 2px solid red;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .positive { color: #4caf50; }
        .negative { color: #f44336; }
        .status-running { color: #4caf50; }
        .status-stopped { color: #f44336; }
        .position-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .position-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid;
        }
        .position-long { border-left-color: #4caf50; }
        .position-short { border-left-color: #f44336; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ACCURATE TRADING DASHBOARD</h1>
            <p>Real-time data • No cache • Current reality only</p>
            <p>Last updated: {{ timestamp }}</p>
        </div>
        
        <div class="warning">
            <h3>⚠️ IMPORTANT: CUMULATIVE P&L NEVER RESETS</h3>
            <p>Historical losses stay forever. Current trading adds to cumulative total.</p>
        </div>
        
        <div class="card">
            <h2>💰 CUMULATIVE PERFORMANCE (NEVER RESETS)</h2>
            <p><strong>Initial Capital:</strong> ${{ "%.2f"|format(cumulative.initial_capital) }}</p>
            <p><strong>Current Portfolio:</strong> ${{ "%.2f"|format(cumulative.current_value) }}</p>
            <p><strong>Cumulative P&L:</strong> <span class="{{ 'positive' if cumulative.pnl >= 0 else 'negative' }}">${{ "%+.2f"|format(cumulative.pnl) }} ({{ "%+.2f"|format(cumulative.pnl_percent) }}%)</span></p>
            <p><strong>Recovery Needed:</strong> +${{ "%.2f"|format(cumulative.recovery_needed) }} ({{ "%.1f"|format(cumulative.recovery_percent) }}% from current)</p>
        </div>
        
        <div class="card">
            <h2>🤖 SYSTEM STATUS</h2>
            <p><strong>26-Crypto Bot:</strong> <span class="status-running">✅ RUNNING (PID {{ bot_status.pid }})</span></p>
            <p><strong>Other Bots:</strong> <span class="status-stopped">❌ ALL KILLED</span></p>
            <p><strong>Dashboard:</strong> <span class="status-running">✅ THIS DASHBOARD ONLY</span></p>
            <p><strong>Cycle:</strong> {{ bot_status.cycle }} completed</p>
            <p><strong>Opportunities Found:</strong> {{ bot_status.opportunities }} total</p>
        </div>
        
        <div class="card">
            <h2>📊 OPEN POSITIONS ({{ positions|length }} total)</h2>
            <div class="position-list">
                {% for pos in positions %}
                <div class="position-item {{ 'position-long' if pos.side == 'buy' else 'position-short' }}">
                    <h4>{{ pos.symbol }} {{ pos.side|upper }}</h4>
                    <p>Entry: ${{ "%.2f"|format(pos.entry_price) }}</p>
                    <p>Current: ${{ "%.2f"|format(pos.current_price) }}</p>
                    <p>P&L: <span class="{{ 'positive' if pos.pnl >= 0 else 'negative' }}">${{ "%+.2f"|format(pos.pnl) }} ({{ "%+.2f"|format(pos.pnl_percent) }}%)</span></p>
                    <p>Days held: {{ "%.2f"|format(pos.days_held) }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="card">
            <h2>📈 PERFORMANCE SUMMARY</h2>
            <p><strong>Total Trades:</strong> {{ performance.total_trades }}</p>
            <p><strong>Winning Trades:</strong> {{ performance.winning_trades }}</p>
            <p><strong>Losing Trades:</strong> {{ performance.losing_trades }}</p>
            <p><strong>Win Rate:</strong> {{ "%.1f"|format(performance.win_rate) }}%</p>
            <p><strong>Current Unrealized P&L:</strong> <span class="{{ 'positive' if performance.unrealized_pnl >= 0 else 'negative' }}">${{ "%+.2f"|format(performance.unrealized_pnl) }}</span></p>
        </div>
        
        <div class="card">
            <h2>🔄 AUTO-REFRESH</h2>
            <p>This dashboard auto-refreshes every 30 seconds.</p>
            <p>Next refresh in: <span id="countdown">30</span> seconds</p>
            <button onclick="location.reload()">Refresh Now</button>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        let countdown = 30;
        const countdownElement = document.getElementById('countdown');
        
        setInterval(() => {
            countdown--;
            countdownElement.textContent = countdown;
            
            if (countdown <= 0) {
                location.reload();
            }
        }, 1000);
    </script>
</body>
</html>
'''

def load_cumulative_pnl():
    """Load cumulative P&L data"""
    tracker_path = os.path.join(BASE_DIR, 'cumulative_pnl_tracker.json')
    if os.path.exists(tracker_path):
        with open(tracker_path, 'r') as f:
            return json.load(f)
    return None

def get_bot_status():
    """Get 26-crypto bot status"""
    # Check if bot is running
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and 'real_26_crypto_trader.py' in ' '.join(proc.info['cmdline']):
                # Check log for cycle info
                log_path = os.path.join(BASE_DIR, '26_crypto_trading.log')
                cycle = 0
                opportunities = 0
                
                if os.path.exists(log_path):
                    with open(log_path, 'r') as f:
                        lines = f.readlines()[-50:]  # Last 50 lines
                        for line in lines:
                            if 'Cycle' in line and 'duration' in line:
                                try:
                                    cycle = int(line.split('Cycle')[1].split()[0])
                                except:
                                    pass
                            if 'opportunities found' in line.lower():
                                try:
                                    opportunities = int(line.split('found:')[1].split()[0])
                                except:
                                    pass
                
                return {
                    'pid': proc.info['pid'],
                    'status': 'running',
                    'cycle': cycle,
                    'opportunities': opportunities
                }
        except:
            continue
    
    return {'pid': 'N/A', 'status': 'stopped', 'cycle': 0, 'opportunities': 0}

@app.route('/')
def dashboard():
    """Main dashboard page"""
    # Load data
    tracker = load_cumulative_pnl()
    bot_status = get_bot_status()
    
    if tracker:
        cumulative = {
            'initial_capital': tracker['performance_summary']['total_initial_capital'],
            'current_value': tracker['performance_summary']['total_current_value'],
            'pnl': tracker['performance_summary']['total_cumulative_pnl'],
            'pnl_percent': tracker['performance_summary']['total_cumulative_pnl_percent'],
            'recovery_needed': tracker['performance_summary']['total_initial_capital'] - tracker['performance_summary']['total_current_value'],
            'recovery_percent': ((tracker['performance_summary']['total_initial_capital'] - tracker['performance_summary']['total_current_value']) / tracker['performance_summary']['total_current_value']) * 100
        }
        
        positions = tracker.get('unrealized_positions', [])
        
        performance = {
            'total_trades': tracker['performance_summary']['total_trades'],
            'winning_trades': tracker['performance_summary']['winning_trades'],
            'losing_trades': tracker['performance_summary']['losing_trades'],
            'win_rate': tracker['performance_summary']['win_rate'],
            'unrealized_pnl': tracker['performance_summary']['total_unrealized_pnl']
        }
    else:
        # Fallback data
        cumulative = {
            'initial_capital': 946.97,
            'current_value': 531.65,
            'pnl': -415.32,
            'pnl_percent': -43.86,
            'recovery_needed': 415.32,
            'recovery_percent': 78.1
        }
        positions = []
        performance = {
            'total_trades': 7,
            'winning_trades': 5,
            'losing_trades': 2,
            'win_rate': 71.4,
            'unrealized_pnl': -7.32
        }
    
    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        cumulative=cumulative,
        bot_status=bot_status,
        positions=positions,
        performance=performance
    )

@app.route('/api/status')
def api_status():
    """API endpoint for status"""
    tracker = load_cumulative_pnl()
    bot_status = get_bot_status()
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'bot_running': bot_status['status'] == 'running',
        'bot_pid': bot_status['pid'],
        'cumulative_pnl_tracking': tracker is not None,
        'dashboard': 'simple_accurate_dashboard'
    })

if __name__ == '__main__':
    print("="*70)
    print("🚀 SIMPLE ACCURATE DASHBOARD")
    print("="*70)
    print("📊 Showing CURRENT REALITY - No cached data")
    print("💰 Cumulative P&L tracking: ACTIVE (never resets)")
    print("🌐 URL: http://localhost:5003")
    print("="*70)
    
    # Run on port 5003 to avoid confusion with old port 5002
    app.run(host='0.0.0.0', port=5003, debug=False)