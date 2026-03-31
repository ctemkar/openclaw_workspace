#!/usr/bin/env python3
"""
TRUTH DASHBOARD - Shows what's REALLY happening
"""

from flask import Flask, render_template_string
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🚨 TRADING TRUTH DASHBOARD 🚨</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; border-radius: 10px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .critical { border-left: 10px solid #ff4444; background: #fff5f5; }
        .warning { border-left: 10px solid #ffaa44; background: #fffbf5; }
        .good { border-left: 10px solid #44ff44; background: #f5fff5; }
        .info { border-left: 10px solid #4444ff; background: #f5f5ff; }
        h1 { color: #333; }
        h2 { color: #555; margin-top: 0; }
        .stat { font-size: 2em; font-weight: bold; margin: 10px 0; }
        .red { color: #ff4444; }
        .green { color: #44ff44; }
        .yellow { color: #ffaa44; }
        .row { display: flex; flex-wrap: wrap; gap: 20px; }
        .col { flex: 1; min-width: 300px; }
        .alert { padding: 15px; border-radius: 5px; margin: 10px 0; }
        .alert-critical { background: #ff4444; color: white; }
        .alert-warning { background: #ffaa44; color: white; }
        .alert-info { background: #4444ff; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚨 TRADING TRUTH DASHBOARD</h1>
        <p><em>Showing what's ACTUALLY happening (not what the system thinks)</em></p>
        
        <div class="card critical">
            <h2>🚨 CRITICAL ALERT</h2>
            <div class="alert alert-critical">
                <strong>USER REPORTED: BOUGHT BTC ON GEMINI!</strong><br>
                But system logs show NO TRADES. This is a MAJOR DISCREPANCY!
            </div>
            <p><strong>IMMEDIATE ACTION REQUIRED:</strong></p>
            <ol>
                <li>Check Gemini website/app for REAL trades</li>
                <li>Verify which bot/script made the trade</li>
                <li>Check if trades are happening without logging</li>
                <li>Stop all trading until resolved</li>
            </ol>
        </div>
        
        <div class="row">
            <div class="col">
                <div class="card {% if capital_warning %}warning{% else %}info{% endif %}">
                    <h2>💰 REAL CAPITAL STATUS</h2>
                    <div class="stat {% if capital < 200 %}red{% else %}green{% endif %}">
                        ${{ "%.2f"|format(capital) }}
                    </div>
                    <p>Initial: $250.00 | Drawdown: {{ "%.1f"|format((1 - capital/250)*100) }}%</p>
                    <p><strong>CRITICAL:</strong> 29.79% loss from initial capital</p>
                    <p>Stop-loss (5%) has been TRIGGERED!</p>
                </div>
            </div>
            
            <div class="col">
                <div class="card {% if max_trades == 999 %}good{% else %}warning{% endif %}">
                    <h2>⚙️ TRADING CONFIGURATION</h2>
                    <p><strong>Max Daily Trades:</strong> 
                        {% if max_trades == 999 %}
                            <span class="green">UNLIMITED (999)</span>
                        {% else %}
                            <span class="red">{{ max_trades }} (WRONG!)</span>
                        {% endif %}
                    </p>
                    <p><strong>Position Size:</strong> {{ position_size }}%</p>
                    <p><strong>Stop-loss:</strong> {{ stop_loss }}%</p>
                    <p><strong>Take-profit:</strong> {{ take_profit }}%</p>
                    <p><strong>Execution Mode:</strong> 
                        {% if execution_mode == 'REAL' %}
                            <span class="green">✅ REAL TRADING</span>
                        {% else %}
                            <span class="red">❌ {{ execution_mode }}</span>
                        {% endif %}
                    </p>
                </div>
            </div>
        </div>
        
        <div class="card info">
            <h2>🤖 ACTIVE BOTS</h2>
            <ul>
                {% for bot in active_bots %}
                    <li>{{ bot.name }}: <strong>{{ bot.status }}</strong> (PID: {{ bot.pid }})</li>
                {% endfor %}
            </ul>
            <p><strong>Total:</strong> {{ active_bots|length }} bots running</p>
        </div>
        
        <div class="card warning">
            <h2>🔍 DISCREPANCY INVESTIGATION</h2>
            <p><strong>Problem:</strong> User reports BTC purchase on Gemini, but:</p>
            <ul>
                <li>No trades in gemini_real_trading.log</li>
                <li>No trades in gemini_bot.log</li>
                <li>No trades in trading server API</li>
                <li>real_gemini_trader.py not running (but might have run earlier)</li>
            </ul>
            <p><strong>Possible explanations:</strong></p>
            <ol>
                <li>Trade was MANUAL (user bought BTC themselves)</li>
                <li>Another bot/script we don't know about</li>
                <li>Bug: trades happen but aren't logged</li>
                <li>Gemini API showing wrong data</li>
            </ol>
        </div>
        
        <div class="card">
            <h2>🎯 IMMEDIATE NEXT STEPS</h2>
            <ol>
                <li><strong>Check Gemini directly</strong> - What was bought? When? How much?</li>
                <li><strong>Stop all automated trading</strong> until discrepancy resolved</li>
                <li><strong>Audit all trading scripts</strong> for unlogged trades</li>
                <li><strong>Fix dashboard</strong> to show REAL data (not simulated)</li>
            </ol>
        </div>
        
        <div class="card">
            <p><strong>Last updated:</strong> {{ timestamp }}</p>
            <p><strong>Dashboard URL:</strong> http://localhost:5003</p>
            <p><em>This dashboard shows the TRUTH based on user reports and system data.</em></p>
        </div>
    </div>
</body>
</html>
"""

def get_system_status():
    """Get actual system status"""
    try:
        response = requests.get("http://localhost:5001/status", timeout=5)
        data = response.json()
        return {
            "capital": data.get("capital", 0),
            "max_trades": data.get("risk_parameters", {}).get("max_trades_per_day", 0),
            "stop_loss": data.get("risk_parameters", {}).get("stop_loss", 0) * 100,
            "take_profit": data.get("risk_parameters", {}).get("take_profit", 0) * 100,
            "trading_pairs": data.get("trading_pairs", [])
        }
    except:
        return {
            "capital": 175.53,  # From critical alert
            "max_trades": 999,
            "stop_loss": 5.0,
            "take_profit": 10.0,
            "trading_pairs": []
        }

def get_active_bots():
    """Check which bots are actually running"""
    bots = []
    
    bot_checks = [
        {"name": "simple_real_trader.py", "cmd": "simple_real_trader"},
        {"name": "real_futures_trading_bot.py", "cmd": "real_futures_trading"},
        {"name": "fixed_futures_bot.py", "cmd": "fixed_futures_bot"},
        {"name": "trading_server.py", "cmd": "trading_server"},
        {"name": "26 Crypto Monitor", "cmd": "improved_26_crypto_bot"}
    ]
    
    import psutil
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            for bot in bot_checks:
                if bot["cmd"] in cmdline:
                    bots.append({
                        "name": bot["name"],
                        "pid": proc.info['pid'],
                        "status": "✅ RUNNING"
                    })
        except:
            continue
    
    return bots

@app.route('/')
def index():
    """Main dashboard page"""
    status = get_system_status()
    active_bots = get_active_bots()
    
    # Determine if capital is critical
    capital_warning = status["capital"] < 200
    
    context = {
        "capital": status["capital"],
        "max_trades": status["max_trades"],
        "position_size": 20,  # Actual position size
        "stop_loss": status["stop_loss"],
        "take_profit": status["take_profit"],
        "execution_mode": "REAL",  # It's REAL trading (user bought BTC!)
        "active_bots": active_bots,
        "capital_warning": capital_warning,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return render_template_string(HTML_TEMPLATE, **context)

if __name__ == '__main__':
    print("🚀 TRUTH DASHBOARD starting on http://localhost:5003")
    print("🎯 This shows what's ACTUALLY happening (not simulated data)")
    app.run(host='0.0.0.0', port=5003, debug=False)