#!/usr/bin/env python3
"""
Enhanced Trading Dashboard
Real-time monitoring of all trading bots and activities
"""

import json
import requests
import subprocess
import time
import os
from datetime import datetime
from flask import Flask, render_template_string, jsonify
import threading
import psutil

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# HTML template for dashboard
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Enhanced Trading Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #fff;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .card h3 {
            margin-top: 0;
            color: #4fc3f7;
            border-bottom: 2px solid #4fc3f7;
            padding-bottom: 10px;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin: 5px;
        }
        .status-running { background: #4caf50; color: white; }
        .status-stopped { background: #f44336; color: white; }
        .status-warning { background: #ff9800; color: white; }
        .trade-list {
            max-height: 300px;
            overflow-y: auto;
        }
        .trade-item {
            background: rgba(255, 255, 255, 0.05);
            margin: 5px 0;
            padding: 10px;
            border-radius: 8px;
            border-left: 4px solid;
        }
        .trade-buy { border-left-color: #4caf50; }
        .trade-sell { border-left-color: #f44336; }
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        .stat-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #4fc3f7;
        }
        .stat-label {
            font-size: 12px;
            color: #aaa;
            text-transform: uppercase;
        }
        .refresh-info {
            text-align: center;
            color: #aaa;
            font-size: 12px;
            margin-top: 20px;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn-primary { background: #2196f3; color: white; }
        .btn-success { background: #4caf50; color: white; }
        .btn-danger { background: #f44336; color: white; }
        .btn:hover { opacity: 0.9; transform: translateY(-2px); }
    </style>
    <script>
        function refreshDashboard() {
            location.reload();
        }
        
        function runAnalysis() {
            fetch('/api/run_analysis')
                .then(response => response.json())
                .then(data => {
                    alert('Analysis started: ' + data.message);
                    setTimeout(refreshDashboard, 2000);
                });
        }
        
        function checkBotStatus() {
            fetch('/api/bot_status')
                .then(response => response.json())
                .then(data => {
                    alert('Bot Status:\\n' + 
                          'Real Gemini Trader: ' + data.real_gemini_trader + '\\n' +
                          'Trading Server: ' + data.trading_server + '\\n' +
                          '26 Crypto Bot: ' + data.crypto_bot);
                });
        }
        
        // Auto-refresh every 30 seconds
        setTimeout(refreshDashboard, 30000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Enhanced Trading Dashboard</h1>
            <p>Real-time monitoring of crypto trading system</p>
            <div class="controls">
                <button class="btn btn-primary" onclick="refreshDashboard()">🔄 Refresh</button>
                <button class="btn btn-success" onclick="runAnalysis()">📊 Run Analysis</button>
                <button class="btn" onclick="checkBotStatus()">🤖 Check Bots</button>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <!-- System Status Card -->
            <div class="card">
                <h3>📈 System Status</h3>
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="stat-value">{{ system_status.capital }}$</div>
                        <div class="stat-label">Total Capital</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{{ system_status.active_bots }}</div>
                        <div class="stat-label">Active Bots</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{{ system_status.trades_today }}</div>
                        <div class="stat-label">Trades Today</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{{ system_status.max_trades }}</div>
                        <div class="stat-label">Max/Day</div>
                    </div>
                </div>
                <p><strong>Status:</strong> 
                    <span class="status-badge status-running">{{ system_status.overall_status }}</span>
                </p>
                <p><strong>Last Analysis:</strong> {{ system_status.last_analysis }}</p>
                <p><strong>Trading Pairs:</strong> {{ system_status.trading_pairs|join(', ') }}</p>
            </div>
            
            <!-- Bot Status Card -->
            <div class="card">
                <h3>🤖 Bot Status</h3>
                {% for bot in bot_status %}
                <div style="margin-bottom: 15px;">
                    <strong>{{ bot.name }}</strong>
                    <span class="status-badge {{ 'status-running' if bot.running else 'status-stopped' }}">
                        {{ 'RUNNING' if bot.running else 'STOPPED' }}
                    </span>
                    {% if bot.pid %}<small>(PID: {{ bot.pid }})</small>{% endif %}
                    <div style="font-size: 12px; color: #aaa;">
                        Uptime: {{ bot.uptime }} | CPU: {{ bot.cpu }}% | Mem: {{ bot.memory }}MB
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <!-- Recent Trades Card -->
            <div class="card">
                <h3>💰 Recent Trades</h3>
                <div class="trade-list">
                    {% if recent_trades %}
                        {% for trade in recent_trades %}
                        <div class="trade-item {{ 'trade-buy' if trade.side|lower == 'buy' else 'trade-sell' }}">
                            <strong>{{ trade.symbol }}</strong> - {{ trade.side|upper }}
                            <div style="float: right;">${{ trade.price }}</div>
                            <div style="clear: both; font-size: 12px; color: #aaa;">
                                {{ trade.time }} | {{ trade.model if trade.model else 'Unknown' }}
                                {% if trade.status %}| Status: {{ trade.status }}{% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    {% else %}
                        <p>No recent trades found.</p>
                    {% endif %}
                </div>
                <p><strong>Total Trades:</strong> {{ total_trades }}</p>
            </div>
            
            <!-- Risk Parameters Card -->
            <div class="card">
                <h3>⚖️ Risk Management</h3>
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="stat-value">{{ risk_params.stop_loss }}%</div>
                        <div class="stat-label">Stop Loss</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{{ risk_params.take_profit }}%</div>
                        <div class="stat-label">Take Profit</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{{ risk_params.position_size }}%</div>
                        <div class="stat-label">Position Size</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{{ risk_params.max_daily_trades }}</div>
                        <div class="stat-label">Max Daily Trades</div>
                    </div>
                </div>
                <p><strong>Strategy:</strong> {{ risk_params.strategy }}</p>
                <p><strong>Execution Mode:</strong> 
                    <span class="status-badge {{ 'status-running' if risk_params.real_trading else 'status-warning' }}">
                        {{ 'REAL TRADING' if risk_params.real_trading else 'SIMULATION' }}
                    </span>
                </p>
            </div>
            
            <!-- Market Data Card -->
            <div class="card">
                <h3>📊 Market Overview</h3>
                {% if market_data %}
                    {% for market in market_data %}
                    <div style="margin-bottom: 10px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                        <strong>{{ market.symbol }}</strong>: ${{ market.price }}
                        <span style="float: right; color: {{ 'green' if market.change >= 0 else 'red' }};">
                            {{ market.change }}%
                        </span>
                        <div style="font-size: 12px; color: #aaa;">
                            Volume: ${{ market.volume }} | 24h Change
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p>Market data unavailable</p>
                {% endif %}
            </div>
            
            <!-- Logs & Alerts Card -->
            <div class="card">
                <h3>📝 Recent Logs</h3>
                <div style="max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 12px;">
                    {% for log in recent_logs %}
                    <div style="margin: 2px 0; padding: 3px; background: rgba(255,255,255,0.05);">
                        {{ log }}
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <div class="refresh-info">
            Last updated: {{ current_time }} | Auto-refresh in 30 seconds
        </div>
    </div>
</body>
</html>
'''

def get_bot_status():
    """Check status of all trading bots"""
    bots = []
    
    # Bot definitions - UPDATED to match actual running bots
    bot_definitions = [
        {"name": "Gemini Long Trader", "process_name": "simple_real_trader.py"},
        {"name": "Trading Server", "process_name": "trading_server.py"},
        {"name": "26 Crypto Monitor", "process_name": "improved_26_crypto_bot.py"},
        {"name": "Binance Futures Bot", "process_name": "fixed_futures_bot.py"},
        {"name": "Binance Futures Bot 2", "process_name": "real_futures_trading_bot.py"},
    ]
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            for bot_def in bot_definitions:
                if bot_def["process_name"] in cmdline:
                    # Calculate uptime
                    create_time = datetime.fromtimestamp(proc.create_time())
                    uptime = datetime.now() - create_time
                    uptime_str = str(uptime).split('.')[0]  # Remove microseconds
                    
                    bots.append({
                        "name": bot_def["name"],
                        "running": True,
                        "pid": proc.info['pid'],
                        "cpu": round(proc.info['cpu_percent'], 1),
                        "memory": round(proc.info['memory_info'].rss / 1024 / 1024, 1),  # MB
                        "uptime": uptime_str
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Add missing bots as stopped
    found_names = [bot["name"] for bot in bots]
    for bot_def in bot_definitions:
        if bot_def["name"] not in found_names:
            bots.append({
                "name": bot_def["name"],
                "running": False,
                "pid": None,
                "cpu": 0,
                "memory": 0,
                "uptime": "N/A"
            })
    
    return bots

def get_system_status():
    """Get overall system status"""
    try:
        response = requests.get('http://localhost:5001/status', timeout=5)
        status_data = response.json()
        
        # Count active bots
        active_bots = len([b for b in get_bot_status() if b["running"]])
        
        return {
            "capital": status_data.get("capital", 0),
            "active_bots": active_bots,
            "trades_today": 0,  # Would need to track this
            "max_trades": status_data.get("risk_parameters", {}).get("max_trades_per_day", 2),
            "overall_status": "Running" if active_bots > 0 else "Stopped",
            "last_analysis": status_data.get("last_analysis", "N/A").replace("T", " ").split(".")[0],
            "trading_pairs": status_data.get("trading_pairs", [])
        }
    except:
        return {
            "capital": 0,
            "active_bots": 0,
            "trades_today": 0,
            "max_trades": 0,
            "overall_status": "Error",
            "last_analysis": "N/A",
            "trading_pairs": []
        }

def get_recent_trades():
    """Get recent trades from API"""
    try:
        response = requests.get('http://localhost:5001/trades', timeout=5)
        trades_data = response.json()
        return trades_data.get("trades", []), trades_data.get("count", 0)
    except:
        return [], 0

def get_risk_parameters():
    """Get risk parameters"""
    try:
        response = requests.get('http://localhost:5001/status', timeout=5)
        status_data = response.json()
        risk_params = status_data.get("risk_parameters", {})
        
        return {
            "stop_loss": round(risk_params.get("stop_loss", 0.05) * 100, 1),
            "take_profit": round(risk_params.get("take_profit", 0.1) * 100, 1),
            "position_size": 50,  # Default
            "max_daily_trades": risk_params.get("max_trades_per_day", 2),
            "strategy": "Conservative Dip Buying",
            "real_trading": True  # Check if real trading is enabled
        }
    except:
        return {
            "stop_loss": 5.0,
            "take_profit": 10.0,
            "position_size": 50,
            "max_daily_trades": 2,
            "strategy": "Unknown",
            "real_trading": False
        }

def get_market_data():
    """Get market data (simulated for now)"""
    # In a real implementation, this would fetch from exchange APIs
    return [
        {"symbol": "BTC/USD", "price": 66611.07, "change": 1.2, "volume": 19676176},
        {"symbol": "ETH/USD", "price": 2021.77, "change": 0.8, "volume": 9652782},
        {"symbol": "SOL/USD", "price": 145.32, "change": 2.5, "volume": 3245678},
    ]

def get_recent_logs():
    """Get recent logs from trading system"""
    logs = []
    log_files = [
        "26_crypto_live_trading.log",
        "real_trading.log",
        "critical_alerts.log"
    ]
    
    for log_file in log_files:
        log_path = os.path.join(BASE_DIR, log_file)
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r') as f:
                    lines = f.readlines()[-10:]  # Last 10 lines
                    for line in lines:
                        logs.append(f"{log_file}: {line.strip()}")
            except:
                pass
    
    return logs[-20:] if logs else ["No logs available"]

@app.route('/')
def dashboard():
    """Render the main dashboard"""
    context = {
        "system_status": get_system_status(),
        "bot_status": get_bot_status(),
        "recent_trades": get_recent_trades()[0][:10],  # Last 10 trades
        "total_trades": get_recent_trades()[1],
        "risk_params": get_risk_parameters(),
        "market_data": get_market_data(),
        "recent_logs": get_recent_logs(),
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return render_template_string(DASHBOARD_TEMPLATE, **context)

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return jsonify({
        "system": get_system_status(),
        "bots": get_bot_status(),
        "trades": get_recent_trades()[0][:5],
        "risk": get_risk_parameters(),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/run_analysis')
def api_run_analysis():
    """Run trading analysis"""
    try:
        result = subprocess.run(
            ["python3", os.path.join(BASE_DIR, "conservative_crypto_trading.py")],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        return jsonify({
            "success": True,
            "message": "Analysis completed",
            "output": result.stdout[:500]  # First 500 chars
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Analysis failed: {str(e)}"
        })

@app.route('/api/bot_status')
def api_bot_status():
    """Check bot status"""
    bots = get_bot_status()
    status = {}
    for bot in bots:
        status[bot["name"].lower().replace(" ", "_")] = "RUNNING" if bot["running"] else "STOPPED"
    
    return jsonify(status)

def start_dashboard():
    """Start the enhanced dashboard"""
    print("="*70)
    print("🚀 ENHANCED TRADING DASHBOARD")
    print("="*70)
    print(f"📊 Dashboard URL: http://localhost:5002")
    print(f"📈 Trading Server: http://localhost:5001")
    print(f"📁 Working directory: {BASE_DIR}")
    print("="*70)
    
    # Run in background
    import webbrowser
    webbrowser.open("http://localhost:5002")
    
    app.run(host='0.0.0.0', port=5002, debug=False)

if __name__ == '__main__':
    start_dashboard()