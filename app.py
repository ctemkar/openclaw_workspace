from flask import Flask, jsonify, render_template
import socket, os, threading, time, psutil, json
from datetime import datetime

app = Flask(__name__)
BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

def get_task_status():
    found = any("crypto_trading_llm_live.py" in " ".join(p.cmdline()) 
                for p in psutil.process_iter(['cmdline']) if p.info['cmdline'])
    return "running" if found else "stopped"

@app.route('/')
def home():
    status = get_task_status()
    trades_file = os.path.join(BASE_DIR, "completed_trades.json")
    trades = []
    if os.path.exists(trades_file):
        try:
            with open(trades_file, "r") as f: trades = json.load(f)
        except: pass
    
    return f"""
    <html>
        <head><meta http-equiv="refresh" content="30"></head>
        <body style="font-family:sans-serif; text-align:center; padding:50px;">
            <h1>OpenClaw Trading Dashboard</h1>
            <div style="font-size:24px; color:{'green' if status=='running' else 'red'};">
                Bot Status: <strong>{status.upper()}</strong>
            </div>
            <p>Active Trades: {len(trades)}</p>
            <hr style="width:50%">
            <p><a href="/api/status/all">View API Data</a></p>
        </body>
    </html>
    """

@app.route('/api/status/all')
def get_status():
    trades_file = os.path.join(BASE_DIR, "completed_trades.json")
    trades = []
    if os.path.exists(trades_file):
        try:
            with open(trades_file, "r") as f: trades = json.load(f)
        except: pass
    return jsonify({"status": get_task_status(), "trades": trades})

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]
    with open(os.path.join(BASE_DIR, ".active_port"), 'w') as f:
        f.write(str(port))
    app.run(host='0.0.0.0', port=port)
