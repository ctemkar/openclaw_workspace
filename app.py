from flask import Flask, jsonify, render_template, request
import socket, os, threading, time, psutil, json
from datetime import datetime

app = Flask(__name__)
BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

def get_task_status():
    try:
        found = any("crypto_trading_llm_live.py" in " ".join(p.cmdline()) 
                    for p in psutil.process_iter(['cmdline']) if p.info['cmdline'])
        return "running" if found else "stopped"
    except:
        return "unknown"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/status/all')
def get_status():
    trades_file = os.path.join(BASE_DIR, "completed_trades.json")
    trades = []
    if os.path.exists(trades_file):
        try:
            with open(trades_file, "r") as f:
                trades = json.load(f)
        except:
            pass
    return jsonify({"status": get_task_status(), "trades": trades})

@app.route('/api/llm/generate', methods=['POST', 'GET'])
def generate_strategies():
    try:
        strat_path = os.path.join(BASE_DIR, "llm_strategies.json")
        mock_strat = {
            "Gemini-Pro": {"symbol": "BTC/USD", "signal": "BUY"},
            "GPT-4o": {"symbol": "ETH/USD", "signal": "SELL"}
        }
        with open(strat_path, "w") as f:
            json.dump(mock_strat, f)
        return jsonify({"status": "success", "message": "Strategies queued"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/dashboard/tasks')
def get_dashboard_tasks():
    """Return dashboard tasks from memory files."""
    tasks_file = os.path.join(BASE_DIR, "dashboard_tasks.json")
    if os.path.exists(tasks_file):
        try:
            with open(tasks_file, "r") as f:
                tasks_data = json.load(f)
            return jsonify(tasks_data)
        except:
            pass
    return jsonify({"last_updated": datetime.now().isoformat(), "total_tasks": 0, "tasks": []})

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]
    
    with open(os.path.join(BASE_DIR, ".active_port"), 'w') as f:
        f.write(str(port))
        
    print(f"DASHBOARD ONLINE ON PORT: {port}")
    app.run(host='0.0.0.0', port=port)
