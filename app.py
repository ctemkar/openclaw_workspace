from flask import Flask, jsonify, render_template, request
import socket, os, json, psutil
from datetime import datetime

app = Flask(__name__)
BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

def get_status():
    found = any("crypto_trading_llm_live.py" in " ".join(p.cmdline()) 
                for p in psutil.process_iter(['cmdline']) if p.info.get('cmdline'))
    return "RUNNING" if found else "STOPPED"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/trading/configure', methods=['GET', 'POST'])
def config():
    return jsonify({
        "status": "success",
        "config": {"capital": 10000, "trade_size": 10, "stop_loss": 0.03}
    })

@app.route('/api/trading/progress', methods=['GET'])
def progress():
    trades_file = os.path.join(BASE_DIR, "completed_trades.json")
    trades = []
    if os.path.exists(trades_file):
        try:
            with open(trades_file, "r") as f: trades = json.load(f)
        except: pass
    return jsonify({"status": get_status(), "trades": trades})

@app.route('/api/llm/generate', methods=['POST'])
def generate():
    try:
        path = os.path.join(BASE_DIR, "llm_strategies.json")
        with open(path, "w") as f:
            json.dump({"Gemini": {"symbol": "BTC/USD", "signal": "BUY"}}, f)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]
    with open(os.path.join(BASE_DIR, ".active_port"), 'w') as f:
        f.write(str(port))
    app.run(host='0.0.0.0', port=port)
