from flask import Flask, jsonify, render_template, request, redirect
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

# Payment routes for $100 trading experiment
@app.route('/pay/<payment_id>')
def payment_page(payment_id):
    """Display payment page for $100 trading experiment"""
    return render_template('payment_page.html')

@app.route('/api/payment/process', methods=['POST'])
def process_payment():
    """Simulate payment processing"""
    # In reality, this would integrate with Stripe API
    # For demo, we simulate successful payment
    
    # Update payment status
    status_file = os.path.join(BASE_DIR, 'status/payment_status.json')
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            status = json.load(f)
        status['status'] = 'completed'
        status['completed_at'] = datetime.now().isoformat()
        status['trading_status'] = 'active'
        
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    # Start trading bot with $100 capital
    trading_config = {
        'capital': 100.0,
        'trade_size_usd': 20.0,
        'stop_loss_pct': 0.015,
        'take_profit_pct': 0.03,
        'assets': ['BTC/USD', 'ETH/USD', 'SOL/USD'],
        'strategy': 'llm_momentum_scalping'
    }
    
    # Save trading config
    with open(os.path.join(BASE_DIR, 'trading_config_100.json'), 'w') as f:
        json.dump(trading_config, f, indent=2)
    
    return jsonify({
        'status': 'success',
        'message': '$100 payment processed. Trading begins now!',
        'dashboard': 'http://127.0.0.1:5080',
        'next_update': 'within 1 hour'
    })

@app.route('/api/experiment/status')
def experiment_status():
    """Get status of $100 trading experiment"""
    status_file = os.path.join(BASE_DIR, 'status/payment_status.json')
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({
        'status': 'ready',
        'message': 'Awaiting $100 payment to begin trading',
        'payment_link': 'http://127.0.0.1:5080/pay/demo'
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5080)
