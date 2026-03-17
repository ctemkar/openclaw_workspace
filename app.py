from flask import Flask, jsonify, render_template, send_from_directory, request, Blueprint
import socket, os, threading, time, psutil, json
from datetime import datetime
import random

app = Flask(__name__)
TASK_STATUS = {"trading": "stopped", "last_update": "never"}

MOCK_TRADING_CONFIG = {
    "capital": 10000.0,
    "trade_size_usd": 10.0,
    "stop_loss_pct": 0.01,
    "take_profit_pct": 0.02
}

MOCK_TRADES = []
# Real data only - no mock strategies
MOCK_TRADING_LOGS = ["Initial log entry."]
MOCK_LLM_LOGS = ["Initial LLM log entry."]
MOCK_MARKET_PRICES = {"BTC/USDT": 40000.0, "ETH/USDT": 3000.0, "SOL/USDT": 100.0}

LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_bot_clean.log"
STRATEGY_FILE = "/Users/chetantemkar/.openclaw/workspace/app/llm_strategies.json"
COMPLETED_TRADES_FILE = "/Users/chetantemkar/.openclaw/workspace/app/completed_trades.json"

def log_action(message):
    with open(LOG_FILE, "a") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ts}] {message}\n")

def update_task_statuses():
    while True:
        try:
            found = any("crypto_trading_llm_live.py" in " ".join(p.cmdline()) 
                        for p in psutil.process_iter(['cmdline']) if p.info['cmdline'])
            TASK_STATUS["trading"] = "running" if found else "stopped"
            TASK_STATUS["last_update"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as e: 
            print(f"Error in update_task_statuses: {e}")
            pass 
        time.sleep(5)

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/status/all')
def get_status():
    return jsonify(TASK_STATUS)

@api_bp.route('/trading/status')
def get_trading_status():
    return jsonify(TASK_STATUS)

@api_bp.route('/trading/progress')
def get_trading_progress():
    trades = []
    if os.path.exists(COMPLETED_TRADES_FILE):
        try:
            with open(COMPLETED_TRADES_FILE, "r") as f: trades = json.load(f)
        except json.JSONDecodeError:
            log_action("ERROR decoding completed_trades.json, file might be empty or corrupted.")
            trades = []
    return jsonify({"trades": trades})

@api_bp.route('/llm/strategies')
def get_llm_strategies():
    strategies = []
    strategy_file = "llm_strategies.json"
    if os.path.exists(strategy_file):
        try:
            with open(strategy_file, "r") as f:
                data = json.load(f)
                # Convert the strategy dictionary to a list format for the dashboard
                for model_name, strategy_data in data.items():
                    strategy = {
                        "strategy_name": f"{model_name} Strategy",
                        "symbol": strategy_data.get("symbol", "Unknown"),
                        "llm_provider": model_name.split("-")[0] if "-" in model_name else model_name,
                        "model": model_name,
                        "description": f"{strategy_data.get('signal', 'UNKNOWN')} signal for {strategy_data.get('symbol', 'Unknown')}",
                        "profit_rationale": "Based on LLM analysis",
                        "risk_parameters": {"stop_loss_pct": 0.01, "take_profit_pct": 0.02},
                        "buy_signal_details": strategy_data.get("signal") if strategy_data.get("signal") == "BUY" else "",
                        "sell_signal_details": strategy_data.get("signal") if strategy_data.get("signal") == "SELL" else ""
                    }
                    strategies.append(strategy)
        except json.JSONDecodeError:
            log_action("ERROR decoding llm_strategies.json")
            strategies = []
    return jsonify(strategies)

@api_bp.route('/trading/configure', methods=['GET', 'POST', 'PUT'])
def configure_trading():
    if request.method == 'GET':
        return jsonify(MOCK_TRADING_CONFIG)
    elif request.method == 'POST' or request.method == 'PUT':
        data = request.get_json()
        if data:
            MOCK_TRADING_CONFIG.update(data)
            log_action(f"Trading configuration updated: {MOCK_TRADING_CONFIG}")
            return jsonify({"message": "Configuration updated successfully.", "config": MOCK_TRADING_CONFIG})
        return jsonify({"message": "Invalid input."}), 400
    else:
        return jsonify({"message": "Method not allowed."}), 405

@api_bp.route('/trading/logs')
def get_trading_logs():
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                logs = f.readlines()
        except Exception as e:
            log_action(f"Could not read trading logs: {e}")
    return jsonify({"logs": "".join(logs[-50:]), "last_updated": datetime.now().isoformat() + "Z"})

@api_bp.route('/llm/logs')
def get_llm_logs():
    llm_logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                llm_logs = f.readlines()
        except Exception as e:
            log_action(f"Could not read LLM logs: {e}")
    return jsonify({"logs": "".join(llm_logs[-50:]), "last_updated": datetime.now().isoformat() + "Z"})

@api_bp.route('/market/prices')
def get_market_prices():
    for symbol in MOCK_MARKET_PRICES:
        change = random.uniform(-0.01, 0.01) * MOCK_MARKET_PRICES[symbol]
        MOCK_MARKET_PRICES[symbol] += change
        MOCK_MARKET_PRICES[symbol] = max(MOCK_MARKET_PRICES[symbol], 0.01)
    return jsonify(MOCK_MARKET_PRICES)

@api_bp.route('/market/charts')
def get_market_charts():
    symbol = request.args.get('symbol', 'BTC/USDT')
    period = request.args.get('period', '1h')
    
    now = time.time() * 1000
    data = []
    base_price = MOCK_MARKET_PRICES.get(symbol, 40000.0)
    
    for i in range(60): 
        ts = now - (60 - i) * 60 * 1000 
        price_fluctuation = random.uniform(-0.005, 0.005) * base_price
        price = base_price + price_fluctuation
        data.append({"timestamp": ts, "price": price})
        
    return jsonify({"symbol": symbol, "period": period, "data": data})

@api_bp.route('/trading/start', methods=['POST'])
def start_trading_script():
    log_action("API: Received request to start trading script.")
    TASK_STATUS["trading"] = "running" 
    MOCK_TRADING_LOGS.append("Trading script started via API.")
    return jsonify({"message": "Trading script start command simulated."})

@api_bp.route('/trading/stop', methods=['POST'])
def stop_trading_script():
    log_action("API: Received request to stop trading script.")
    TASK_STATUS["trading"] = "stopped"
    MOCK_TRADING_LOGS.append("Trading script stop command simulated.")
    return jsonify({"message": "Trading script stop command simulated."})

@api_bp.route('/llm/generate', methods=['POST'])
def generate_llm_strategies():
    log_action("API: Received request to generate LLM strategies.")
    MOCK_LLM_STRATEGIES.clear()
    MOCK_LLM_STRATEGIES.extend([
        {"strategy_name": "GeneratedStrategy_ETH_SELL_Gemini","symbol": "ETH/USDT","llm_provider": "Gemini","model": "gemini-pro","description": "A mock strategy for selling ETH.","profit_rationale": "Based on mock indicators.","risk_parameters": {"stop_loss_pct": 0.015, "take_profit_pct": 0.025},"sell_signal_details": "Mock sell signal generated."},
        {"strategy_name": "GeneratedStrategy_BTC_BUY_Qwen","symbol": "BTC/USDT","llm_provider": "Qwen","model": "qwen-turbo","description": "A mock strategy for buying BTC.","profit_rationale": "Based on mock technical indicators.","risk_parameters": {"stop_loss_pct": 0.01, "take_profit_pct": 0.02},"buy_signal_details": "Mock buy signal generated."},
        {"strategy_name": "GeneratedStrategy_SOL_SELL_Deepseek","symbol": "SOL/USDT","llm_provider": "Deepseek","model": "deepseek-coder","description": "A mock strategy for selling SOL.","profit_rationale": "Based on mock news sentiment.","risk_parameters": {"stop_loss_pct": 0.008, "take_profit_pct": 0.015},"sell_signal_details": "Mock sell signal generated."}
    ])
    MOCK_LLM_LOGS.append("LLM strategies generated via API.")
    return jsonify({"message": "LLM strategies generated. Check LLM Strategies tab."})

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_bot_clean.log"
    STRATEGY_FILE = "/Users/chetantemkar/.openclaw/workspace/app/llm_strategies.json"

    if not os.path.exists(os.path.dirname(LOG_FILE)):
        os.makedirs(os.path.dirname(LOG_FILE))
    with open(LOG_FILE, 'a') as f: pass 
    if not os.path.exists(STRATEGY_FILE):
        with open(STRATEGY_FILE, 'w') as f:
            json.dump({"strategy": "initialize", "message": "Waiting for AI signals..."}, f)

    monitor_thread = threading.Thread(target=update_task_statuses, daemon=True)
    monitor_thread.start()
    
    port = 5001
    
    with open('/Users/chetantemkar/.openclaw/workspace/app/.active_port', 'w') as f:
        f.write(str(port))
        
    app.register_blueprint(api_bp)

    app.run(host='0.0.0.0', port=port, debug=False) 
