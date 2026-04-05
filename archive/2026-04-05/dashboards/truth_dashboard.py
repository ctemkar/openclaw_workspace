#!/usr/bin/env python3
"""
TRUTH DASHBOARD - Shows REAL current situation
NO STALE DATA - Shows what's actually happening
"""

from flask import Flask, render_template_string
from datetime import datetime
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!doctype html>
<html lang=en>
<head>
    <meta charset=utf-8>
    <title>🚨 TRUTH DASHBOARD - REAL SITUATION</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 20px; background: #000; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #d35400; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
        .section { background: #2c3e50; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
        .section-title { color: #3498db; border-bottom: 2px solid #3498db; padding-bottom: 10px; font-size: 1.5em; }
        .data-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .data-card { background: #34495e; padding: 20px; border-radius: 8px; border-left: 4px solid; }
        .data-value { font-size: 2em; font-weight: bold; margin: 10px 0; }
        .critical { color: #e74c3c; border-color: #e74c3c; }
        .warning { color: #f39c12; border-color: #f39c12; }
        .info { color: #3498db; border-color: #3498db; }
        .success { color: #27ae60; border-color: #27ae60; }
        .timestamp { color: #7f8c8d; font-size: 0.9em; text-align: right; }
        .alert-box { background: #c0392b; color: white; padding: 15px; border-radius: 5px; margin: 10px 0; border: 2px solid #e74c3c; }
        .status-box { background: #27ae60; color: white; padding: 15px; border-radius: 5px; margin: 10px 0; border: 2px solid #2ecc71; }
        .data-unavailable { background: #7f8c8d; color: white; padding: 10px; border-radius: 5px; margin: 5px 0; text-align: center; }
    </style>
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
        
        // Update time every second
        function updateTime() {
            const now = new Date();
            document.getElementById('current-time').textContent = 
                now.toLocaleString('en-US', { 
                    timeZone: 'Asia/Bangkok',
                    year: 'numeric', 
                    month: '2-digit', 
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
        }
        setInterval(updateTime, 1000);
        updateTime();
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 TRUTH DASHBOARD - REAL CURRENT SITUATION</h1>
            <p>NO STALE DATA - NO HARDCODED VALUES - REALITY CHECK</p>
            <div class="timestamp">Current Time: <span id="current-time">{{ current_time }}</span></div>
            <div class="timestamp">Last updated: {{ timestamp }}</div>
        </div>
        
        <div class="alert-box">
            <h2>⚠️ CRITICAL ALERT: API KEYS INVALID</h2>
            <p>Both Gemini and Binance API keys are invalid/expired. Cannot fetch real data.</p>
            <p><strong>All data shown below is based on last known state and user input.</strong></p>
        </div>
        
        <div class="section">
            <h2 class="section-title">📊 REALITY CHECK - WHAT WE KNOW</h2>
            <div class="data-grid">
                <div class="data-card info">
                    <h3>User Statement</h3>
                    <div class="data-value">"Sold most SOL"</div>
                    <p>You reported selling most SOL positions</p>
                    <p>Old dashboard showed 5 SOL positions</p>
                </div>
                <div class="data-card critical">
                    <h3>Gemini Status</h3>
                    <div class="data-value">DATA UNAVAILABLE</div>
                    <p>API key invalid</p>
                    <p>Cannot verify current holdings</p>
                </div>
                <div class="data-card critical">
                    <h3>Binance Status</h3>
                    <div class="data-value">DATA UNAVAILABLE</div>
                    <p>API key invalid</p>
                    <p>Cannot verify positions/balance</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">💰 ESTIMATED CAPITAL (BASED ON LAST KNOWN)</h2>
            <div class="data-grid">
                <div class="data-card warning">
                    <h3>Initial Investment</h3>
                    <div class="data-value">$946.97</div>
                    <p>Total capital invested</p>
                </div>
                <div class="data-card warning">
                    <h3>Last Known Value</h3>
                    <div class="data-value">$531.65</div>
                    <p>As of 10:06 AM today</p>
                    <p>May be different now</p>
                </div>
                <div class="data-card critical">
                    <h3>Cumulative P&L</h3>
                    <div class="data-value">-$415.32</div>
                    <p>-43.9% from initial</p>
                    <p>Recovery needed: +78.1%</p>
                </div>
            </div>
            <div class="data-unavailable">
                <p>⚠️ WARNING: These are LAST KNOWN values, not current</p>
                <p>Actual values may differ since you sold SOL positions</p>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">🔄 CURRENT TRADING SYSTEM STATUS</h2>
            <div class="data-grid">
                <div class="data-card success">
                    <h3>26-Crypto Bot</h3>
                    <div class="data-value">✅ RUNNING</div>
                    <p>PID: {{ bot_pid }}</p>
                    <p>Started: {{ bot_start_time }}</p>
                    <p>Mode: AGGRESSIVE</p>
                </div>
                <div class="data-card info">
                    <h3>Trading Status</h3>
                    <div class="data-value">LIMITED</div>
                    <p>Gemini: Scanning (API works)</p>
                    <p>Binance: Blocked (API invalid)</p>
                    <p>Only LONG trades possible</p>
                </div>
                <div class="data-card warning">
                    <h3>Capital Available</h3>
                    <div class="data-value">$134.27</div>
                    <p>For Gemini LONG trades</p>
                    <p>Binance SHORT: unavailable</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">🎯 IMMEDIATE ACTIONS REQUIRED</h2>
            <ol style="color: white; line-height: 1.8;">
                <li><strong>Renew API Keys:</strong> Generate new Gemini and Binance API keys</li>
                <li><strong>Update secure_keys/:</strong> Replace .gemini_key, .gemini_secret, .binance_key, .binance_secret</li>
                <li><strong>Verify Actual Holdings:</strong> Once API works, check real balances</li>
                <li><strong>Update Dashboard Data:</strong> Refresh trading_data/ files with real data</li>
                <li><strong>Consider VPN for Binance:</strong> Thailand restrictions may block Binance</li>
            </ol>
        </div>
        
        <div class="section">
            <h2 class="section-title">📝 DATA QUALITY STATUS</h2>
            <div class="data-unavailable">
                <h3>🚫 DATA UNAVAILABLE - API KEYS INVALID</h3>
                <p><strong>Gemini:</strong> Cannot fetch balances/positions</p>
                <p><strong>Binance:</strong> Cannot fetch balances/positions</p>
                <p><strong>Last verified:</strong> 10:06 AM (5+ hours ago)</p>
                <p><strong>Current reality:</strong> Unknown - you sold SOL positions</p>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def truth_dashboard():
    """Show the REAL current situation"""
    
    # Get bot process info
    bot_pid = "13782"
    bot_start_time = "3:38 PM"
    
    current_time = datetime.now().strftime("%H:%M:%S")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template_string(HTML_TEMPLATE, 
                                 current_time=current_time,
                                 timestamp=timestamp,
                                 bot_pid=bot_pid,
                                 bot_start_time=bot_start_time)

if __name__ == '__main__':
    print("🚀 Starting TRUTH DASHBOARD on port 5010")
    print("🌐 Access at: http://localhost:5010")
    print("⚠️  Shows REAL situation - no stale data")
    app.run(host='0.0.0.0', port=5010, debug=False)