from flask import Flask, jsonify, render_template, request
import os, json, psutil, subprocess
from datetime import datetime
app = Flask(__name__, template_folder='templates', static_folder='static')
BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

def get_status():
    try:
        for p in psutil.process_iter(['cmdline']):
            if "crypto_trading_llm_live.py" in " ".join(p.info.get('cmdline', [])): return "RUNNING"
        return "STOPPED"
    except: return "STOPPED"

@app.route('/')
def home(): return render_template('index.html')

@app.route('/api/status/all')
@app.route('/api/trading/progress')
def get_all_status():
    return jsonify({
        "status": get_status(),
        "llm_status": "READY",
        "trades": [],
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

@app.route('/api/trading/configure', methods=['GET'])
def get_config():
    return jsonify({"status": "success", "config": {"capital": 10000.0, "trade_size": 10.0, "stop_loss": 0.01, "take_profit": 0.02}})

@app.route('/api/llm/strategies', methods=['GET'])
def get_strats():
    path = os.path.join(BASE_DIR, "llm_strategies.json")
    if os.path.exists(path):
        with open(path, "r") as f: return jsonify(json.load(f))
    return jsonify({"Gemini-Pro": {"symbol": "BTC/USD", "signal": "WAITING"}})

@app.route('/api/trading/logs')
@app.route('/api/llm/logs')
def get_logs():
    return jsonify({"logs": [f"[{datetime.now().strftime('%H:%M:%S')}] Dashboard active on port 5080"]})

@app.route('/api/trading/start', methods=['POST'])
def start_bot():
    if get_status() == "STOPPED":
        subprocess.Popen(["/Users/chetantemkar/.openclaw/workspace/app/venv/bin/python", os.path.join(BASE_DIR, "crypto_trading_llm_live.py")])
    return jsonify({"status": "success"})

@app.route('/api/llm/generate', methods=['POST'])
def generate_strat():
    with open(os.path.join(BASE_DIR, "llm_strategies.json"), "w") as f:
        json.dump({"Gemini-Pro": {"symbol": "BTC/USD", "signal": "BUY"}}, f)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5080)
