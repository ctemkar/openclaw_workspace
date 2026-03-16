import os
import subprocess
import json
import psutil
import signal
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, send_from_directory
import glob
import atexit
import traceback # Import traceback for better error logging

# --- Helper function for logging ---
def log_message(message):
    # Basic logging to stdout. For production, consider more robust logging.
    print(f"[LOG] {message}")

# --- Default configuration ---
DEFAULT_CONFIG = {
    'capital': 10000.0,  # Example default capital
    'trade_size_usd': 100.0, # Example default trade size in USD (using consistent naming)
    'stop_loss_pct': 0.01,   # Example default stop loss (1%)
    'take_profit_pct': 0.02  # Example default take profit (2%)
}

# Ensure the workspace directory exists
WORKSPACE_DIR = "/Users/chetantemkar/.openclaw/workspace"
APP_DIR = os.path.join(WORKSPACE_DIR, "app")
if not os.path.exists(APP_DIR):
    os.makedirs(APP_DIR)

# Paths for scripts and logs
TRADING_SCRIPT_PATH = os.path.join(APP_DIR, "crypto_trading_llm.sh")
LLM_GENERATOR_SCRIPT_PATH = os.path.join(APP_DIR, "llm_strategy_generator.py")
TRADING_LOG_FILE = os.path.join(APP_DIR, "logs", "trading.log")
LLM_GENERATOR_LOG_FILE = os.path.join(APP_DIR, "logs", "llm_generation.log")

# Create necessary directories if they don't exist
os.makedirs(os.path.join(APP_DIR, "static"), exist_ok=True)
os.makedirs(os.path.join(APP_DIR, "templates"), exist_ok=True)
os.makedirs(os.path.join(APP_DIR, "logs"), exist_ok=True)
os.makedirs(os.path.join(APP_DIR, "status"), exist_ok=True)

app = Flask(__name__, static_folder='static', template_folder='templates')

TASK_STATUS = {}
MANAGED_PROCESSES_HANDLES = {}
TASK_UPDATE_INTERVAL_SECONDS = 10

def get_process_info(script_name_pattern):
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            cmdline = proc.info.get('cmdline')
            # Check if the pattern is present in the command line arguments
            if cmdline and any(script_name_pattern in arg for arg in cmdline):
                processes.append({
                    'pid': proc.info['pid'],
                    'command': " ".join(cmdline),
                    'create_time': datetime.fromtimestamp(proc.info['create_time'])
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Ignore processes that can't be accessed
            pass
    return processes

def update_task_statuses():
    while True:
        current_time = datetime.now()

        # Update trading status
        trading_script_search_pattern = os.path.basename(TRADING_SCRIPT_PATH)
        trading_processes = []
        if TRADING_SCRIPT_PATH.endswith(".py"):
             python_processes = get_process_info("python3")
             for p in python_processes:
                 if TRADING_SCRIPT_PATH in p.get('command', ''):
                     trading_processes.append(p)
        else:
             trading_processes = get_process_info(trading_script_search_pattern)

        if trading_processes:
            pid = trading_processes[0]['pid']
            command = trading_processes[0]['command']
            if psutil.pid_exists(pid):
                TASK_STATUS['trading'] = {'pid': pid, 'status': 'running', 'last_update': current_time, 'command': command, 'is_running': True}
            else: 
                 if 'trading' in TASK_STATUS and TASK_STATUS['trading'].get('is_running'):
                     TASK_STATUS['trading']['status'] = 'stopped_unexpectedly'; TASK_STATUS['trading']['is_running'] = False
                     TASK_STATUS['trading']['end_time'] = current_time
                 else:
                     TASK_STATUS['trading'] = {'status': 'stopped', 'pid': None, 'last_update': current_time, 'command': '', 'is_running': False}
        else:
            if 'trading' in TASK_STATUS and TASK_STATUS['trading'].get('is_running'):
                TASK_STATUS['trading']['status'] = 'stopped_unexpectedly'; TASK_STATUS['trading']['is_running'] = False
                TASK_STATUS['trading']['end_time'] = current_time
            else:
                TASK_STATUS['trading'] = {'status': 'stopped', 'pid': None, 'last_update': current_time, 'command': '', 'is_running': False}

        # Update LLM generator status
        llm_gen_script_name = os.path.basename(LLM_GENERATOR_SCRIPT_PATH)
        llm_processes = []
        if LLM_GENERATOR_SCRIPT_PATH.endswith(".py"):
             python_processes = get_process_info("python3")
             for p in python_processes:
                 if LLM_GENERATOR_SCRIPT_PATH in p.get('command', ''):
                     llm_processes.append(p)
        else:
             llm_processes = get_process_info(llm_gen_script_name)

        if llm_processes:
            pid = llm_processes[0]['pid']
            command = llm_processes[0]['command']
            if psutil.pid_exists(pid):
                TASK_STATUS['llm_generator'] = {'pid': pid, 'status': 'running', 'last_update': current_time, 'command': command, 'is_running': True}
            else: 
                if 'llm_generator' in TASK_STATUS and TASK_STATUS['llm_generator'].get('is_running'):
                    TASK_STATUS['llm_generator']['status'] = 'stopped_unexpectedly'; TASK_STATUS['llm_generator']['is_running'] = False
                    TASK_STATUS['llm_generator']['end_time'] = current_time
                else:
                    TASK_STATUS['llm_generator'] = {'status': 'stopped', 'last_update': current_time, 'command': '', 'is_running': False} 
        else:
            if 'llm_generator' in TASK_STATUS and TASK_STATUS['llm_generator'].get('is_running'):
                TASK_STATUS['llm_generator']['status'] = 'stopped_unexpectedly'
                TASK_STATUS['llm_generator']['is_running'] = False
                TASK_STATUS['llm_generator']['end_time'] = current_time
            elif 'llm_generator' not in TASK_STATUS or TASK_STATUS['llm_generator'].get('status') != 'running':
                 TASK_STATUS['llm_generator'] = {'status': 'stopped', 'pid': None, 'last_update': current_time, 'command': '', 'is_running': False}

        time.sleep(TASK_UPDATE_INTERVAL_SECONDS)

status_thread = threading.Thread(target=update_task_statuses, daemon=True)
status_thread.start()

def start_script_process(script_path, log_file_path, task_key, task_name):
    if task_key in MANAGED_PROCESSES_HANDLES and MANAGED_PROCESSES_HANDLES[task_key] and MANAGED_PROCESSES_HANDLES[task_key].poll() is None:
        return {"message": f"{task_name} is already running.", "status": "running", "pid": MANAGED_PROCESSES_HANDLES[task_key].pid}, 409

    command = f"python3 {script_path}" if script_path.endswith(".py") else script_path
    
    try:
        process = subprocess.Popen(
            command,
            cwd=APP_DIR,
            shell=True,
            stdout=open(log_file_path, 'a'),
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid, # Create a new process group
            text=True
        )
        MANAGED_PROCESSES_HANDLES[task_key] = process
        TASK_STATUS[task_key] = {'pid': process.pid, 'status': 'running', 'last_update': datetime.now(), 'command': command, 'is_running': True}
        print(f"Started {task_name} with PID: {process.pid}")
        return {"message": f"{task_name} started.", "status": "running", "pid": process.pid}, 200
    except FileNotFoundError:
        log_message(f"Error: Script not found at {script_path}")
        return {"message": f"Error: Script not found at {script_path}", "status": "error"}, 500
    except Exception as e:
        log_message(f"Error starting {task_name}: {e}")
        print(traceback.format_exc()) # Log the full traceback for debugging
        TASK_STATUS[task_key] = {'status': 'error', 'pid': None, 'last_update': datetime.now(), 'command': command, 'is_running': False}
        return {"message": f"Error starting {task_name}: {e}", "status": "error"}, 500

def stop_process_async(task_key, task_name):
    process_handle = MANAGED_PROCESSES_HANDLES.get(task_key)
    
    if process_handle and process_handle.poll() is None: 
        try:
            os.killpg(os.getpgid(process_handle.pid), signal.SIGTERM) 
            process_handle.wait(timeout=5) 
            if task_key in TASK_STATUS: 
                TASK_STATUS[task_key]['status'] = 'stopped'; 
                TASK_STATUS[task_key]['is_running'] = False
                TASK_STATUS[task_key]['end_time'] = datetime.now()
            MANAGED_PROCESSES_HANDLES[task_key] = None
            print(f"Stopped {task_name} (Managed PID: {process_handle.pid}).")
            return {"message": f"Sent stop signal to {task_name} (PID: {process_handle.pid}).", "status": "stopped"}, 200
        except ProcessLookupError: 
            if task_key in TASK_STATUS: TASK_STATUS[task_key]['status'] = 'stopped'; TASK_STATUS[task_key]['is_running'] = False
            if task_key in MANAGED_PROCESSES_HANDLES: MANAGED_PROCESSES_HANDLES[task_key] = None
            return {"message": f"{task_name} process was already terminated.", "status": "stopped"}, 200
        except Exception as e:
            log_message(f"Error stopping managed {task_name} process {process_handle.pid}: {e}")
            return {"message": f"Error stopping {task_name} process {process_handle.pid}: {e}", "status": "error"}, 500
    else: 
        script_path = TRADING_SCRIPT_PATH if task_key == 'trading' else LLM_GENERATOR_SCRIPT_PATH
        script_name_pattern = os.path.basename(script_path)
        pids_to_kill = get_process_info(script_name_pattern)
        
        if pids_to_kill:
            killed_any = False
            for p_info in pids_to_kill:
                try:
                    os.killpg(os.getpgid(p_info['pid']), signal.SIGTERM) 
                    time.sleep(1) 
                    if psutil.pid_exists(p_info['pid']): 
                        os.killpg(os.getpgid(p_info['pid']), signal.SIGKILL) 
                    killed_any = True
                    print(f"Forcefully stopped {task_key} process (PID: {p_info['pid']}).")
                except Exception as e:
                    print(f"Error forcefully stopping {task_key} process {p_info['pid']}: {e}")
            
            if killed_any:
                 if task_key in TASK_STATUS: TASK_STATUS[task_key]['status'] = 'stopped'; TASK_STATUS[task_key]['is_running'] = False
                 return {"message": f"Stopped detected {task_key} processes.", "status": "stopped"}, 200
            else:
                 if task_key in TASK_STATUS: TASK_STATUS[task_key]['status'] = 'stopped'; TASK_STATUS[task_key]['is_running'] = False
                 return {"message": f"{task_key} process termination command failed, but it's no longer detected.", "status": "stopped"}, 200
        else:
             if task_key in TASK_STATUS: TASK_STATUS[task_key]['status'] = 'stopped'; TASK_STATUS[task_key]['is_running'] = False
             return {"message": f"{task_name} is not running.", "status": "stopped"}, 200

def cleanup_managed_processes():
    print("Cleaning up managed processes...")
    for task_key in list(MANAGED_PROCESSES_HANDLES.keys()):
        if MANAGED_PROCESSES_HANDLES[task_key] and MANAGED_PROCESSES_HANDLES[task_key].poll() is None:
            stop_process_async(task_key, task_key.replace('_',' ').title())
atexit.register(cleanup_managed_processes)

def get_script_logs(log_file_path):
    try:
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as f:
                return f.read()
        else:
            return "Log file not found yet."
    except Exception as e:
        return f"Error reading log file: {e}"

def get_latest_llm_strategies():
    try:
        list_of_files = glob.glob(os.path.join(APP_DIR, 'llm_strategies_*.json'))
        if not list_of_files:
            log_message("No LLM strategy files found.")
            return []
        latest_file = max(list_of_files, key=os.path.getctime)
        log_message(f"Loading strategies from: {latest_file}")
        with open(latest_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        log_message(f"Error reading latest LLM strategies: {e}")
        return []

def get_script_status(script_name):
    pids_info = get_process_info(script_name)
    return len(pids_info) > 0

def get_mock_market_data():
    prices = {
        "BTC/USD": 68500.50 + (time.time() % 100 - 50),
        "ETH/USD": 3500.25 + (time.time() % 50 - 25),
        "SOL/USD": 150.75 + (time.time() % 20 - 10),
    }
    return prices

def get_mock_price_history(symbol, period):
    now = time.time()
    data = []
    for i in range(60): 
        price_base = {"BTC/USD": 68500, "ETH/USD": 3500, "SOL/USD": 150}.get(symbol, 100)
        fluctuation = {"BTC/USD": 100, "ETH/USD": 20, "SOL/USD": 5}.get(symbol, 10)
        timestamp = (now - (60 - i) * 60) * 1000 
        price = price_base + fluctuation * ( (i / 60) - 0.5) + ( (now + i*60) % 1000 - 500) / 100 
        data.append({"timestamp": timestamp, "price": round(price, 2)})
    return data


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/trading/start', methods=['POST'])
def start_trading():
    if get_script_status(os.path.basename(TRADING_SCRIPT_PATH)):
        return jsonify({"message": "Trading script is already running.", "status": "running"}), 409
    success, code = start_script_process(TRADING_SCRIPT_PATH, TRADING_LOG_FILE, 'trading', 'Trading Script')
    return jsonify(success), code

@app.route('/api/trading/stop', methods=['POST'])
def stop_trading():
    success, code = stop_process_async('trading', 'Trading Script')
    return jsonify(success), code

@app.route('/api/trading/status', methods=['GET'])
def get_trading_status_route():
    status_info = TASK_STATUS.get('trading', {'status': 'stopped', 'pid': None, 'last_update': None, 'is_running': False})
    
    last_update_val = status_info.get('last_update')
    if isinstance(last_update_val, datetime):
        status_info['last_update'] = last_update_val.isoformat()
    elif not isinstance(last_update_val, str): 
        status_info['last_update'] = datetime.now().isoformat()
        
    if status_info['status'] == 'running' and status_info.get('pid'):
        if not psutil.pid_exists(status_info['pid']):
            status_info['status'] = 'stopped_unexpectedly'; status_info['is_running'] = False
            status_info['end_time'] = datetime.now().isoformat() 
    
    status_info['last_update'] = str(status_info.get('last_update')) 

    return jsonify(status_info)

@app.route('/api/trading/logs', methods=['GET'])
def get_trading_logs_route():
    logs = get_script_logs(TRADING_LOG_FILE)
    last_updated = datetime.now().isoformat()
    
    trading_status = TASK_STATUS.get('trading', {})
    last_update_val = trading_status.get('last_update')
    if isinstance(last_update_val, datetime):
        last_updated = last_update_val.isoformat()
    elif isinstance(last_update_val, str): 
        last_updated = last_update_val
    else: 
        last_updated = datetime.now().isoformat()

    return jsonify({"logs": logs, "last_updated": last_updated})

@app.route('/api/llm/generate', methods=['POST'])
def generate_llm_strategies():
    # Check if LLM generator is already running or has recently completed
    # If it has completed and we want to re-run, we might need a way to signal that.
    # For now, if it's detected as running, we return a conflict.
    if get_script_status(os.path.basename(LLM_GENERATOR_SCRIPT_PATH)):
         return jsonify({"message": "LLM generation is already running.", "status": "running"}), 409
    
    # Explicitly clear the 'llm_generator' status if it was previously stopped unexpectedly
    # to allow a fresh start detection.
    if 'llm_generator' in TASK_STATUS:
        del TASK_STATUS['llm_generator'] # Clear previous status to allow re-detection

    success, code = start_script_process(LLM_GENERATOR_SCRIPT_PATH, LLM_GENERATOR_LOG_FILE, 'llm_generator', 'LLM Generator Script')
    return jsonify(success), code

@app.route('/api/llm/strategies', methods=['GET'])
def get_llm_strategies_list():
    strategies = get_latest_llm_strategies()
    return jsonify(strategies)

@app.route('/api/llm/logs', methods=['GET'])
def get_llm_logs_route():
    logs = get_script_logs(LLM_GENERATOR_LOG_FILE)
    last_updated = datetime.now().isoformat()
    llm_status = TASK_STATUS.get('llm_generator', {})
    if llm_status.get('last_update'):
        if isinstance(llm_status['last_update'], datetime):
             last_updated = llm_status['last_update'].isoformat()
        else: 
             last_updated = llm_status['last_update']
    else: 
        last_updated = datetime.now().isoformat()

    return jsonify({"logs": logs, "last_updated": last_updated})

@app.route('/api/market/prices', methods=['GET'])
def get_market_prices():
    mock_data = get_mock_market_data()
    return jsonify(mock_data)

@app.route('/api/market/charts', methods=['GET'])
def get_market_charts():
    symbol = request.args.get('symbol', 'BTC/USD')
    period = request.args.get('period', '1h')
    mock_history = get_mock_price_history(symbol, period)
    return jsonify({"symbol": symbol, "period": period, "data": mock_history})

@app.route('/api/trading/configure', methods=['POST'])
def configure_trading():
    new_params = request.json
    config_path = os.path.join(APP_DIR, "trading_config.json")
    try:
        new_params['capital'] = float(new_params.get('capital', DEFAULT_CONFIG['capital']))
        new_params['trade_size_usd'] = float(new_params.get('trade_size_usd', DEFAULT_CONFIG['trade_size_usd']))
        new_params['stop_loss_pct'] = float(new_params.get('stop_loss_pct', DEFAULT_CONFIG['stop_loss_pct']))
        new_params['take_profit_pct'] = float(new_params.get('take_profit_pct', DEFAULT_CONFIG['take_profit_pct']))
        
        with open(config_path, 'w') as f:
            json.dump(new_params, f, indent=4)
        if 'trading' in TASK_STATUS:
            TASK_STATUS['trading']['status'] = 'config_updated'; TASK_STATUS['trading']['last_update'] = datetime.now()
        return jsonify({"message": "Configuration updated. Restart the trading script for changes to take effect.", "received": new_params}), 200
    except Exception as e:
        log_message(f"Failed to save configuration: {e}")
        traceback.print_exc() 
        return jsonify({"message": f"Failed to save configuration: {e}", "status": "error"}), 500

@app.route('/api/trading/progress', methods=['GET'])
def get_trading_progress():
    try:
        import requests
        
        response = requests.get('http://localhost:5001/api/trade_progress')
        
        if response.ok:
            return jsonify(response.json())
        else:
            log_message(f"Failed to fetch trade progress from live script: Status {response.status_code}, Response: {response.text}")
            return jsonify({"message": "Failed to get trade progress from live script.", "trades": []}), response.status_code

    except requests.exceptions.ConnectionError:
        log_message("Could not connect to the live trading script at http://localhost:5001/api/trade_progress.")
        return jsonify({"message": "Live trading script not running or inaccessible.", "trades": []}), 503
    except Exception as e:
        log_message(f"Error fetching trading progress: {e}")
        log_message(f"Traceback: {traceback.format_exc()}")
        return jsonify({"message": f"Server error fetching progress: {e}", "trades": []}), 500

@app.route('/api/status/all', methods=['GET'])
def get_all_statuses():
    serialized_task_status = {}
    for key, value in TASK_STATUS.items():
        serialized_task_status[key] = value.copy() 
        if 'last_update' in serialized_task_status[key] and isinstance(serialized_task_status[key]['last_update'], datetime):
            serialized_task_status[key]['last_update'] = serialized_task_status[key]['last_update'].isoformat()
        if 'end_time' in serialized_task_status[key] and isinstance(serialized_task_status[key]['end_time'], datetime):
            serialized_task_status[key]['end_time'] = serialized_task_status[key]['end_time'].isoformat()
            
    return jsonify(serialized_task_status)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/templates/<path:filename>')
def serve_templates(filename):
    return send_from_directory(app.template_folder, filename)

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=False, host='127.0.0.1', port=5001) 
