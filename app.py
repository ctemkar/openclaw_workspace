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
@app.route('/favicon.ico')
def favicon(): return '', 204
@app.route('/api/trading/configure')
def config():
    return jsonify({"status": "success", "config": {"capital": 100.0, "trade_size": 10.0, "stop_loss": 0.03, "take_profit": 0.06}})
@app.route('/api/status/all')
@app.route('/api/trading/progress')
@app.route('/api/llm/strategies')
def status_data():
    trades = []
    if os.path.exists(os.path.join(BASE_DIR, "completed_trades.json")):
        with open(os.path.join(BASE_DIR, "completed_trades.json"), "r") as f: trades = json.load(f)
    strategies = {}
    if os.path.exists(os.path.join(BASE_DIR, "llm_strategies.json")):
        with open(os.path.join(BASE_DIR, "llm_strategies.json"), "r") as f: strategies = json.load(f)
    return jsonify({"status": get_status(), "trades": trades, "strategies": strategies, "timestamp": datetime.now().strftime("%H:%M:%S")})
@app.route('/api/llm/generate', methods=['POST'])
def generate():
    with open(os.path.join(BASE_DIR, "llm_strategies.json"), "w") as f: json.dump({"Gemini-Pro": {"symbol": "BTC/USD", "signal": "BUY"}}, f)
    return jsonify({"status": "success"})
@app.route('/api/trading/start', methods=['POST'])
def start_t():
    if get_status() == "STOPPED":
        subprocess.Popen(["/Users/chetantemkar/.openclaw/workspace/app/venv/bin/python", os.path.join(BASE_DIR, "crypto_trading_llm_live.py")])
    return jsonify({"status": "success"})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
