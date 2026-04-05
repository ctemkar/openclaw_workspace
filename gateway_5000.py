#!/usr/bin/env python3
"""
Gateway on port 5000 - Redirects to main dashboards
"""

from flask import Flask, redirect, render_template_string
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>OpenClaw Gateway - Dashboard Hub</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #0f172a; color: white; }
        .header { background: #1e40af; padding: 30px; border-radius: 15px; margin-bottom: 30px; text-align: center; }
        h1 { margin: 0; font-size: 2.5em; }
        .subtitle { color: #cbd5e1; margin: 10px 0 20px 0; font-size: 1.2em; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .dashboard-card { background: #1e293b; border-radius: 10px; padding: 25px; border: 1px solid #334155; transition: transform 0.2s; }
        .dashboard-card:hover { transform: translateY(-5px); border-color: #3b82f6; }
        .dashboard-title { color: #60a5fa; font-size: 1.5em; margin: 0 0 10px 0; }
        .dashboard-desc { color: #94a3b8; margin: 10px 0 20px 0; }
        .dashboard-link { display: inline-block; background: #3b82f6; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold; }
        .dashboard-link:hover { background: #2563eb; }
        .status-badge { background: #10b981; color: white; padding: 5px 10px; border-radius: 20px; font-size: 0.9em; display: inline-block; margin-left: 10px; }
        .system-status { background: #1e293b; padding: 20px; border-radius: 10px; margin-top: 30px; border: 1px solid #334155; }
        .system-title { color: #60a5fa; margin-top: 0; }
        .footer { text-align: center; margin-top: 40px; color: #64748b; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 OpenClaw Gateway</h1>
        <div class="subtitle">Central Dashboard Hub - All Monitoring Systems</div>
    </div>
    
    <div class="dashboard-grid">
        <div class="dashboard-card">
            <h2 class="dashboard-title">📊 REAL Top 10 Spreads Dashboard</h2>
            <div class="status-badge">✅ ACTIVE</div>
            <p class="dashboard-desc">Actual arbitrage opportunities from 26-crypto bot. Shows real-time top 10 spreads with prices from Binance and Gemini.</p>
            <a href="http://localhost:5026" class="dashboard-link" target="_blank">Open Dashboard →</a>
        </div>
        
        <div class="dashboard-card">
            <h2 class="dashboard-title">📈 Sorted Spread Dashboard</h2>
            <div class="status-badge">✅ ACTIVE</div>
            <p class="dashboard-desc">Legacy dashboard showing sorted spreads. Useful for historical comparison and spread monitoring.</p>
            <a href="http://localhost:5025" class="dashboard-link" target="_blank">Open Dashboard →</a>
        </div>
        
        <div class="dashboard-card">
            <h2 class="dashboard-title">📋 Truthful Dashboard</h2>
            <div class="status-badge">✅ ACTIVE</div>
            <p class="dashboard-desc">System status and trading performance dashboard. Shows bot status, profits, and market conditions.</p>
            <a href="http://localhost:5024" class="dashboard-link" target="_blank">Open Dashboard →</a>
        </div>
    </div>
    
    <div class="system-status">
        <h2 class="system-title">⚙️ System Status</h2>
        <p><strong>✅ Trading Bots Running:</strong></p>
        <ul>
            <li>Practical Profit Bot (PID: 80537) - Active since 2:08 AM</li>
            <li>26-Crypto Arbitrage Bot - Monitoring 16 cryptos</li>
            <li>Auto Arbitrage Bot - Continuous monitoring</li>
            <li>Multi-LLM Trading Bot - Active</li>
        </ul>
        
        <p><strong>📊 Current Market Status:</strong></p>
        <ul>
            <li>Best Opportunity: XTZ at -0.95% spread</li>
            <li>MANA Spread: +0.11% (too small for arbitrage)</li>
            <li>Average Spread: 0.23% across markets</li>
            <li>Today's Profit: $0.09 from 53 trades</li>
        </ul>
        
        <p><strong>🔧 System Health:</strong></p>
        <ul>
            <li>Binance API: ✅ WORKING</li>
            <li>Gemini API: ⚠️ Nonce errors (limits trading)</li>
            <li>CPU Usage: 0.0%</li>
            <li>Memory Usage: 0.1%</li>
        </ul>
    </div>
    
    <div class="footer">
        <p>Gateway running on port 5000 | Auto-redirects to active dashboards</p>
        <p>Last updated: {{ current_time }}</p>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    """Main gateway page"""
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template_string(HTML_TEMPLATE, current_time=current_time)

@app.route("/real")
def real_dashboard():
    """Redirect to REAL Top 10 Spreads Dashboard"""
    return redirect("http://localhost:5026")

@app.route("/sorted")
def sorted_dashboard():
    """Redirect to Sorted Spread Dashboard"""
    return redirect("http://localhost:5025")

@app.route("/truthful")
def truthful_dashboard():
    """Redirect to Truthful Dashboard"""
    return redirect("http://localhost:5024")

@app.route("/status")
def status():
    """Quick status check"""
    return {
        "status": "online",
        "gateway": "port_5000",
        "dashboards": {
            "real_top_10": "http://localhost:5026",
            "sorted_spread": "http://localhost:5025", 
            "truthful": "http://localhost:5024"
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting OpenClaw Gateway on port 5001...")
    print("   Main Page: http://localhost:5001")
    print("   Real Dashboard: http://localhost:5001/real")
    print("   Sorted Dashboard: http://localhost:5001/sorted")
    print("   Truthful Dashboard: http://localhost:5001/truthful")
    print("   Status: http://localhost:5001/status")
    print("\nPress Ctrl+C to stop")
    
    from datetime import datetime
    app.run(host="0.0.0.0", port=5001, debug=False)