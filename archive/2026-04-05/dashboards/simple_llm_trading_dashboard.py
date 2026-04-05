#!/usr/bin/env python3
"""
Simple Real-Time LLM Trading Dashboard
Shows consensus signals and any executed trades
"""

from flask import Flask, render_template_string, jsonify
import json
import os
from datetime import datetime
import time

app = Flask(__name__)

def get_llm_data():
    """Get LLM consensus and trade data"""
    data = {
        "last_updated": datetime.now().strftime("%H:%M:%S"),
        "bot_status": "Checking...",
        "current_cycle": "Unknown",
        "consensus_signals": [],
        "recent_trades": [],
        "balances": {}
    }
    
    # Check if bot is running
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['cmdline'] and 'llm_consensus_bot.py' in ' '.join(proc.info['cmdline']):
                data["bot_status"] = f"✅ RUNNING (PID: {proc.info['pid']})"
                break
        else:
            data["bot_status"] = "❌ NOT RUNNING"
    except:
        data["bot_status"] = "⚠️ Status unknown"
    
    # Read consensus log
    log_file = "llm_consensus.log"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()[-50:]  # Last 50 lines
        
        for line in lines:
            if "consensus:" in line:
                parts = line.split("consensus:")
                if len(parts) > 1:
                    consensus_text = parts[1].strip()
                    if "BUY=" in consensus_text and "SELL=" in consensus_text:
                        # Parse crypto and signal
                        crypto = line.split("📊 ")[1].split(" consensus")[0] if "📊 " in line else "Unknown"
                        buy_match = consensus_text.split("BUY=")[1].split(",")[0]
                        sell_match = consensus_text.split("SELL=")[1].split(",")[0]
                        signal_match = consensus_text.split("Signal=")[1] if "Signal=" in consensus_text else "NEUTRAL"
                        
                        data["consensus_signals"].append({
                            "crypto": crypto,
                            "buy_score": float(buy_match),
                            "sell_score": float(sell_match),
                            "signal": signal_match,
                            "time": line.split(" - INFO - ")[0] if " - INFO - " in line else ""
                        })
    
    # Read trading log
    trade_log = "llm_trading.log"
    if os.path.exists(trade_log):
        with open(trade_log, 'r') as f:
            lines = f.readlines()[-20:]  # Last 20 lines
        
        for line in lines:
            if "EXECUTING" in line or "Order placed" in line:
                data["recent_trades"].append({
                    "action": line.split(" - INFO - ")[1] if " - INFO - " in line else line.strip(),
                    "time": line.split(" - INFO - ")[0] if " - INFO - " in line else ""
                })
    
    return data

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🧠 LLM Real-Time Trading</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #0f0f23; color: #ccc; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #00ff9d; text-align: center; }
        .status-box { 
            background: #1a1a2e; 
            padding: 15px; 
            border-radius: 8px;
            margin: 20px 0;
            border: 1px solid #00ff9d;
        }
        .signal-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }
        .signal-card { background: #1a1a2e; padding: 15px; border-radius: 6px; border: 1px solid #2d2d4d; }
        .signal-buy { border-left: 4px solid #00ff9d; }
        .signal-sell { border-left: 4px solid #ff0066; }
        .signal-neutral { border-left: 4px solid #666; }
        .crypto-name { font-weight: bold; color: #66ccff; }
        .trade-log { background: #0f0f1a; padding: 10px; border-radius: 6px; margin-top: 20px; }
        .trade-item { padding: 5px; border-bottom: 1px solid #2d2d4d; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 LLM Real-Time Trading Dashboard</h1>
        
        <div class="status-box">
            <h2>🤖 Bot Status: {{ data.bot_status }}</h2>
            <p>Last updated: {{ data.last_updated }} (auto-refresh every 5s)</p>
            <p>💰 Trade size: $15-25 per trade | Strategy: LLM Consensus Voting</p>
        </div>
        
        <h2>📊 Current LLM Consensus Signals</h2>
        {% if data.consensus_signals %}
        <div class="signal-grid">
            {% for signal in data.consensus_signals[-10:] %}
            <div class="signal-card signal-{{ signal.signal.lower().replace('strong_', '').replace(' ', '-') }}">
                <div class="crypto-name">{{ signal.crypto }}</div>
                <div>BUY: {{ signal.buy_score }}/10</div>
                <div>SELL: {{ signal.sell_score }}/10</div>
                <div><strong>Signal:</strong> {{ signal.signal }}</div>
                <div class="timestamp">{{ signal.time }}</div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <p>⏳ Waiting for LLM consensus data...</p>
        {% endif %}
        
        <h2>💸 Recent Trade Activity</h2>
        <div class="trade-log">
            {% if data.recent_trades %}
                {% for trade in data.recent_trades[-10:] %}
                <div class="trade-item">
                    {{ trade.action }} <span class="timestamp">{{ trade.time }}</span>
                </div>
                {% endfor %}
            {% else %}
                <p>⏳ No trades executed yet. Waiting for strong consensus signals...</p>
                <p>Next analysis cycle in ~10 minutes</p>
            {% endif %}
        </div>
        
        <div style="margin-top: 30px; text-align: center; color: #666;">
            <p>🧠 Multi-LLM Voting System: DeepSeek + 4 Ollama models</p>
            <p>⚡ Real trades enabled: $15-25 per position</p>
            <p>🔄 Auto-refreshing...</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def dashboard():
    data = get_llm_data()
    return render_template_string(HTML_TEMPLATE, data=data)

@app.route('/api/data')
def api_data():
    data = get_llm_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5013, debug=False)
