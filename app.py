from flask import Flask, jsonify, render_template, request
import socket, os, json, psutil
from datetime import datetime

app = Flask(__name__)
BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

def get_bot_status():
    found = any("crypto_trading_llm_live.py" in " ".join(p.cmdline()) 
                for p in psutil.process_iter(['cmdline']) if p.info.get('cmdline'))
    return "RUNNING" if found else "STOPPED"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/trading/configure', methods=['GET', 'POST'])
def trading_config():
    return jsonify({
        "status": "success",
        "config": {
            "capital": 100.0,
            "trade_size": 10.0,
            "stop_loss": 0.03,
            "take_profit": 0.06
        }
    })

@app.route('/api/status/all')
@app.route('/api/trading/progress')
def status_all():
    trades_path = os.path.join(BASE_DIR, "completed_trades.json")
    trades = []
    if os.path.exists(trades_path):
        try:
            with open(trades_path, "r") as f: trades = json.load(f)
        except: pass
    return jsonify({
        "status": get_bot_status(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "trades": trades
    })

@app.route('/api/llm/strategies')
def get_llm_strategies():
    path = os.path.join(BASE_DIR, "llm_strategies.json")
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                strategies = json.load(f)
            return jsonify({
                "status": "success",
                "strategies": strategies
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "No strategies file found"}), 404

@app.route('/api/llm/generate', methods=['POST'])
def generate_llm_strategies():
    try:
        # Run the LLM analysis to generate real strategies
        import subprocess
        result = subprocess.run(
            ["./.nvenv/bin/python3", "llm_analysis.py"],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        
        if result.returncode == 0:
            # Read the generated strategies
            path = os.path.join(BASE_DIR, "llm_strategies.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    strategies = json.load(f)
                return jsonify({
                    "status": "success",
                    "strategies": strategies,
                    "log": result.stdout.strip()
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Strategies file not created",
                    "log": result.stderr.strip()
                }), 500
        else:
            return jsonify({
                "status": "error",
                "message": "LLM analysis failed",
                "log": result.stderr.strip()
            }), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]
    with open(os.path.join(BASE_DIR, ".active_port"), 'w') as f:
        f.write(str(port))
    app.run(host='0.0.0.0', port=port)
