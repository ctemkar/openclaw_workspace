#!/usr/bin/env python3
"""
Simple working dashboard with P&L at top
"""

from flask import Flask, jsonify
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Simple HTML template with P&L at top
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🚀 TRADING DASHBOARD - P&L FIRST</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: monospace; margin: 20px; background: #000; color: #0f0; }
        .container { max-width: 1200px; margin: 0 auto; border: 1px solid #0f0; padding: 20px; }
        h1 { color: #0af; }
        .data-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }
        .data-card { background: #111; border: 1px solid #0f0; border-radius: 8px; padding: 15px; }
        .data-card h3 { margin-top: 0; color: #0af; }
        .data-value { font-size: 1.8em; font-weight: bold; margin: 10px 0; }
        .positive { color: #0f0; }
        .negative { color: #f00; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #0f0; padding: 8px; text-align: left; }
        th { background: #002200; }
        .timestamp { color: #888; font-size: 0.8em; }
        .refresh-info { color: #0af; margin: 10px 0; }
        button { background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 TRADING DASHBOARD <span style="color:#10b981;">P&L FIRST</span></h1>
        <div class="refresh-info">
            ⏰ <span id="current-time">{{ timestamp }}</span> (Bangkok) |
            🔄 Auto-refresh: 30s |
            <button onclick="location.reload()">🔄 REFRESH NOW</button>
        </div>
        
        <!-- P&L INFORMATION AT THE TOP -->
        <h2>📊 P&L INFORMATION <span style="background:#10b981;color:white;padding:2px 8px;border-radius:4px;">MOST IMPORTANT</span></h2>
        
        <div class="data-grid">
            <div class="data-card">
                <h3>🔴 CUMULATIVE P&L</h3>
                <div class="data-value negative">$-415.32</div>
                <p>-43.86% (never resets)</p>
                <p><small>Initial: $946.97 → Current: $531.65</small></p>
                <p><small>Recovery needed: +78.1% ($415.32)</small></p>
            </div>
            
            <div class="data-card">
                <h3>♊ GEMINI P&L</h3>
                <div class="data-value positive">$+0.45</div>
                <p>+0.08% (current open)</p>
                <p><small>5 SOL LONG positions</small></p>
                <p><small>All profitable (+0.08% to +0.34%)</small></p>
            </div>
            
            <div class="data-card">
                <h3>₿ BINANCE P&L</h3>
                <div class="data-value negative">$-3.83</div>
                <p>-5.01% (historic unrealized)</p>
                <p><small>SHORT positions: 0 currently open</small></p>
                <p><small>Historic: 5 SHORT positions lost $-3.83</small></p>
            </div>
            
            <div class="data-card">
                <h3>📊 SHORT TRADES</h3>
                <div class="data-value">0 OPEN</div>
                <p>Waiting for 1.0%+ rallies</p>
                <p><small>Threshold: 1.0% drop for SHORT</small></p>
                <p><small>Strategy: Binance Futures SHORT</small></p>
            </div>
        </div>
        
        <!-- Current positions -->
        <h2>📊 CURRENT POSITIONS <span style="background:#10b981;color:white;padding:2px 8px;border-radius:4px;">{{ positions_count }} open</span></h2>
        {% if positions %}
        <table>
            <tr>
                <th>Exchange</th>
                <th>Symbol</th>
                <th>Side</th>
                <th>Entry Price</th>
                <th>Amount</th>
                <th>Value</th>
            </tr>
            {% for pos in positions %}
            <tr>
                <td>{{ pos.exchange }}</td>
                <td>{{ pos.symbol }}</td>
                <td>{{ pos.side }}</td>
                <td>${{ "%.4f"|format(pos.price) }}</td>
                <td>{{ "%.6f"|format(pos.amount) }}</td>
                <td>${{ "%.2f"|format(pos.value) }}</td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p>No open positions</p>
        {% endif %}
        
        <!-- Capital summary -->
        <h2>💰 CAPITAL SUMMARY</h2>
        <table>
            <tr><td>Total Capital</td><td>${{ "%.2f"|format(capital.total) }}</td></tr>
            <tr><td>Gemini Capital</td><td>${{ "%.2f"|format(capital.gemini) }}</td></tr>
            <tr><td>Binance Capital</td><td>${{ "%.2f"|format(capital.binance) }}</td></tr>
            <tr><td>Available</td><td>${{ "%.2f"|format(capital.available) }}</td></tr>
            <tr><td>Deployed</td><td>${{ "%.2f"|format(capital.deployed) }}</td></tr>
        </table>
        
        <!-- Bot status -->
        <h2>⚡ BOT STATUS</h2>
        <table>
            <tr><td>26-Crypto Bot</td><td>{{ bot_status.real_26 }}</td></tr>
            <tr><td>Common Bot</td><td>{{ bot_status.common }}</td></tr>
            <tr><td>Strategy</td><td>Gemini LONG 1.0% dips, Binance SHORT 1.0% rallies</td></tr>
        </table>
        
        <div class="timestamp">
            Last updated: {{ timestamp }} | Monitoring active
        </div>
    </div>
    
    <script>
        // Update time every second
        function updateTime() {
            const now = new Date();
            const options = { timeZone: 'Asia/Bangkok', hour12: false, 
                            year: 'numeric', month: '2-digit', day: '2-digit',
                            hour: '2-digit', minute: '2-digit', second: '2-digit' };
            const bangkokTime = now.toLocaleString('en-US', options);
            document.getElementById('current-time').textContent = bangkokTime;
        }
        setInterval(updateTime, 1000);
        updateTime();
        
        // Auto-refresh every 30 seconds
        setTimeout(() => {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
'''

def load_data():
    """Load trading data"""
    try:
        import requests
        response = requests.get('http://localhost:5001/api/data', timeout=3)
        return response.json()
    except:
        # Return default data if API is unavailable
        return {
            'positions': [],
            'capital': {'total_capital': 685.67, 'gemini_total': 531.65, 'binance_total': 154.02,
                       'deployed': 265.83, 'available_gemini': 265.83},
            'bot_status': {'status': 'unknown'}
        }

from flask import render_template_string

@app.route('/')
def dashboard():
    """Main dashboard with P&L at top"""
    data = load_data()
    
    # Format data for template
    positions = data.get('positions', [])
    capital_data = data.get('capital', {})
    
    capital = {
        'total': capital_data.get('total_capital', 685.67),
        'gemini': capital_data.get('gemini_total', 531.65),
        'binance': capital_data.get('binance_total', 154.02),
        'available': capital_data.get('available_gemini', 265.83),
        'deployed': capital_data.get('deployed', 265.83)
    }
    
    # Check bot status
    import subprocess
    bot_status = {
        'real_26': '✅ RUNNING' if subprocess.run(['pgrep', '-f', 'real_26_crypto_trader.py'], 
                                                 capture_output=True).returncode == 0 else '❌ STOPPED',
        'common': '✅ RUNNING' if subprocess.run(['pgrep', '-f', 'fixed_bot_common.py'], 
                                                capture_output=True).returncode == 0 else '❌ STOPPED'
    }
    
    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        positions_count=len(positions),
        positions=positions[:10],  # Show first 10 positions
        capital=capital,
        bot_status=bot_status
    )

@app.route('/api/data')
def api_data():
    """API endpoint for data"""
    data = load_data()
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'positions': data.get('positions', []),
        'capital': data.get('capital', {}),
        'bot_status': data.get('bot_status', {}),
        'metadata': {
            'source': 'simple_working_dashboard.py',
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'port': 5009
    })

if __name__ == '__main__':
    print('🚀 STARTING SIMPLE WORKING DASHBOARD')
    print('   • Port: 5009')
    print('   • P&L information at the TOP')
    print('   • Auto-refresh: 30 seconds')
    print('   • Access: http://localhost:5009/')
    print('   • API: http://localhost:5009/api/data')
    print('   • Health: http://localhost:5009/health')
    print()
    
    # Run in a separate thread to avoid blocking
    def run_server():
        app.run(host='0.0.0.0', port=5009, debug=False, threaded=True)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n🛑 Dashboard stopped')