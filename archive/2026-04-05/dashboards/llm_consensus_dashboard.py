#!/usr/bin/env python3
"""
LLM CONSENSUS DASHBOARD
Shows real-time analysis from all LLMs and final decisions
"""

from flask import Flask, render_template_string, jsonify
import json
import os
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Read LLM consensus log and parse it
def parse_llm_log():
    """Parse the LLM consensus log file"""
    log_file = "llm_consensus.log"
    if not os.path.exists(log_file):
        return {"error": "Log file not found"}
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    # Parse last complete cycle
    analysis = {
        "last_updated": datetime.now().isoformat(),
        "cryptos": {},
        "cycle_info": {}
    }
    
    current_crypto = None
    current_cycle = None
    
    for line in lines[-200:]:  # Last 200 lines
        if "CYCLE" in line and "STARTING" in line:
            # Extract cycle number
            parts = line.split("CYCLE")
            if len(parts) > 1:
                cycle_part = parts[1].split("STARTING")[0].strip()
                current_cycle = f"Cycle {cycle_part}"
                analysis["cycle_info"]["current"] = current_cycle
        
        elif "Getting LLM consensus for" in line:
            parts = line.split("Getting LLM consensus for")
            if len(parts) > 1:
                current_crypto = parts[1].split("...")[0].strip()
                if current_crypto not in analysis["cryptos"]:
                    analysis["cryptos"][current_crypto] = {
                        "models": [],
                        "consensus": {},
                        "signal": "PENDING"
                    }
        
        elif "glm-4.7-flash:" in line or "llama3.1:" in line or "llama3:" in line or "qwen2.5-coder:" in line:
            if current_crypto:
                # Parse model response
                parts = line.strip().split(":")
                if len(parts) >= 2:
                    model_name = parts[0].strip()
                    rest = ":".join(parts[1:]).strip()
                    
                    # Extract scores
                    buy_score = 5
                    sell_score = 5
                    reason = "No reason provided"
                    
                    if "BUY=" in rest and "SELL=" in rest:
                        buy_part = rest.split("BUY=")[1].split(",")[0]
                        sell_part = rest.split("SELL=")[1]
                        buy_score = int(buy_part.strip())
                        sell_score = int(sell_part.strip())
                    
                    analysis["cryptos"][current_crypto]["models"].append({
                        "name": model_name,
                        "buy_score": buy_score,
                        "sell_score": sell_score,
                        "reason": reason
                    })
        
        elif "consensus:" in line and current_crypto:
            # Parse consensus result
            if "BUY=" in line and "SELL=" in line and "Signal=" in line:
                buy_part = line.split("BUY=")[1].split(",")[0]
                sell_part = line.split("SELL=")[1].split(",")[0]
                signal_part = line.split("Signal=")[1].strip()
                
                analysis["cryptos"][current_crypto]["consensus"] = {
                    "buy_score": float(buy_part.strip()),
                    "sell_score": float(sell_part.strip()),
                    "signal": signal_part
                }
                analysis["cryptos"][current_crypto]["signal"] = signal_part
        
        elif "TRADE DECISIONS:" in line:
            analysis["cycle_info"]["trade_decisions"] = []
            in_decisions = True
    
    return analysis

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🧠 LLM Consensus Trading Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #0f0f23; color: #ccc; }
        .dashboard { max-width: 1400px; margin: 0 auto; }
        h1 { color: #00ff9d; text-align: center; }
        .header { 
            background: #1a1a2e; 
            padding: 15px; 
            border-radius: 8px;
            margin: 20px 0;
            border: 1px solid #00ff9d;
        }
        .cycle-info {
            background: #16213e;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .crypto-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .crypto-card {
            background: #1a1a2e;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #2d2d4d;
        }
        .crypto-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #2d2d4d;
        }
        .crypto-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #00ff9d;
        }
        .signal {
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: bold;
        }
        .signal-buy { background: #00ff9d22; color: #00ff9d; border: 1px solid #00ff9d; }
        .signal-sell { background: #ff006622; color: #ff0066; border: 1px solid #ff0066; }
        .signal-neutral { background: #66666622; color: #999; border: 1px solid #666; }
        .model-list {
            margin-top: 10px;
        }
        .model-item {
            background: #0f0f1a;
            padding: 8px;
            margin: 5px 0;
            border-radius: 4px;
            border-left: 3px solid #00ff9d;
        }
        .model-name {
            font-weight: bold;
            color: #66ccff;
        }
        .scores {
            display: flex;
            gap: 15px;
            margin-top: 5px;
        }
        .buy-score { color: #00ff9d; }
        .sell-score { color: #ff0066; }
        .consensus {
            margin-top: 10px;
            padding: 10px;
            background: #0f0f1a;
            border-radius: 4px;
            border: 1px solid #00ff9d;
        }
        .timestamp {
            color: #666;
            font-size: 0.9em;
            text-align: right;
            margin-top: 20px;
        }
        .no-data {
            text-align: center;
            padding: 40px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>🧠 LLM Consensus Trading Dashboard</h1>
        
        <div class="header">
            <h2>🤖 Multi-AI Voting System</h2>
            <p>DeepSeek (coordinator) + 4 Ollama LLMs consensus trading</p>
            <p>Auto-refreshes every 10 seconds</p>
        </div>
        
        <div class="cycle-info">
            <h3>🔄 {{ analysis.cycle_info.current or "Current Cycle" }}</h3>
            <p>Last updated: {{ analysis.last_updated }}</p>
        </div>
        
        {% if analysis.cryptos %}
        <div class="crypto-grid">
            {% for crypto, data in analysis.cryptos.items() %}
            <div class="crypto-card">
                <div class="crypto-header">
                    <div class="crypto-name">{{ crypto }}</div>
                    <div class="signal signal-{{ data.signal.lower().replace('strong_', '').replace(' ', '-') }}">
                        {{ data.signal }}
                    </div>
                </div>
                
                <div class="model-list">
                    <h4>🤖 LLM Analysis:</h4>
                    {% for model in data.models %}
                    <div class="model-item">
                        <div class="model-name">{{ model.name }}</div>
                        <div class="scores">
                            <span class="buy-score">BUY: {{ model.buy_score }}/10</span>
                            <span class="sell-score">SELL: {{ model.sell_score }}/10</span>
                        </div>
                        <div class="reason">{{ model.reason }}</div>
                    </div>
                    {% endfor %}
                </div>
                
                {% if data.consensus %}
                <div class="consensus">
                    <h4>📊 FINAL CONSENSUS:</h4>
                    <div class="scores">
                        <span class="buy-score">BUY: {{ data.consensus.buy_score }}/10</span>
                        <span class="sell-score">SELL: {{ data.consensus.sell_score }}/10</span>
                    </div>
                    <div><strong>Decision:</strong> {{ data.consensus.signal }}</div>
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="no-data">
            <h3>⏳ Waiting for LLM analysis...</h3>
            <p>The LLM consensus bot is running but no analysis data yet.</p>
            <p>Check back in 1-2 minutes for real-time consensus data.</p>
        </div>
        {% endif %}
        
        <div class="timestamp">
            Last updated: {{ analysis.last_updated }}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def dashboard():
    analysis = parse_llm_log()
    return render_template_string(HTML_TEMPLATE, analysis=analysis)

@app.route('/api/consensus')
def api_consensus():
    analysis = parse_llm_log()
    return jsonify(analysis)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5012, debug=False)