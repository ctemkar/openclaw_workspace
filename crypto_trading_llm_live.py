import sys, ccxt, numpy
import sys, ccxt, numpy
import sys, ccxt, numpy
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
import traceback

# --- Global Variables and Configuration ---
# Ensure these are accessible across the module
TASK_STATUS = {} # Global dictionary to store task statuses
DEFAULT_CONFIG = { # Default configurations
    "capital": 100.00,
    "trade_size_usd": 10.00, # Default trade size per strategy if not specified
    "stop_loss_pct": 0.03,
    "take_profit_pct": 0.06
}

# --- File Paths ---
WORKSPACE_DIR = "/Users/chetantemkar/.openclaw/workspace"
APP_DIR = os.path.join(WORKSPACE_DIR, "app")
CONFIG_PATH = os.path.join(APP_DIR, "trading_config.json")
LOG_FILE = os.path.join(APP_DIR, "logs", "trading.log")
STATUS_FILE = os.path.join(APP_DIR, "status", "trading_status.json")
STRATEGIES_DIR = APP_DIR 

# Create necessary directories if they don't exist
os.makedirs(os.path.join(APP_DIR, "static"), exist_ok=True)
os.makedirs(os.path.join(APP_DIR, "templates"), exist_ok=True)
os.makedirs(os.path.join(APP_DIR, "logs"), exist_ok=True)
os.makedirs(os.path.join(APP_DIR, "status"), exist_ok=True)

# Flask App Initialization
app = Flask(__name__, static_folder='static', template_folder='templates')

PROCESS_PID = os.getpid()
TASK_UPDATE_INTERVAL_SECONDS = 10

# --- Logging Function ---
# Defined at the top level to be globally accessible
def log_message(message):
    """Logs a message to both stdout and the log file, accessible globally."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}][{PROCESS_PID}] {message}\n"
    print(message) # Print to stdout for server logs
    try:
        with open(LOG_FILE, "a") as f:
            f.write(full_message)
    except IOError as e:
        print(f"Error writing to log file {LOG_FILE}: {e}")
    # Update status file with last log message
    update_status_file({"last_log": timestamp, "last_message": message})

# --- Status File Management ---
def update_status_file(status_data):
    """Updates the status file with new data, preserving existing info."""
    try:
        existing_status = {}
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r') as f:
                existing_status = json.load(f)
        
        existing_status.update(status_data)
        existing_status["pid"] = PROCESS_PID
        existing_status["last_heartbeat"] = datetime.now().isoformat()

        with open(STATUS_FILE, 'w') as f:
            json.dump(existing_status, f, indent=4)
    except Exception as e:
        print(f"Error updating status file: {e}")

# --- Configuration Loading ---
def load_config():
    """Loads configuration from trading_config.json or uses defaults."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            log_message("Loading configuration from trading_config.json")
            return json.load(f)
    else:
        log_message("trading_config.json not found, using default configuration.")
        return DEFAULT_CONFIG

# --- Keychain Credential Retrieval ---
def get_keychain_credential(keychain_item_name):
    """Retrieves credentials from macOS Keychain securely."""
    log_message(f"Attempting to retrieve '{keychain_item_name}' from Keychain...")
    try:
        command = f"/usr/bin/security find-generic-password -w -s '{keychain_item_name}'"
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        credential = result.stdout.strip()
        if not credential:
            raise ValueError(f"Credential '{keychain_item_name}' not found in Keychain or is empty.")
        log_message(f"Successfully retrieved '{keychain_item_name}' (length: {len(credential)}).")
        return credential
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else "Unknown error"
        log_message(f"Error executing security command for '{keychain_item_name}': Command='{e.cmd}', ExitCode={e.returncode}, Stderr='{error_message}'")
        if "The specified item could not be found in the keychain" in error_message or "Code=-25292" in error_message:
            raise ValueError(f"Credential '{keychain_item_name}' not found in Keychain. Please ensure it's added and accessible.") from e
        else:
            raise ValueError(f"Could not retrieve '{keychain_item_name}' from Keychain due to an error: {error_message}") from e
    except FileNotFoundError:
        log_message("Error: The '/usr/bin/security' command was not found. Ensure it's in your PATH.")
        raise ValueError("The '/usr/bin/security' command is not available.") from None
    except Exception as e:
        log_message(f"An unexpected error occurred accessing Keychain for '{keychain_item_name}': {e}")
        log_message(f"Traceback: {traceback.format_exc()}")
        raise ValueError(f"Unexpected error accessing Keychain for '{keychain_item_name}'.") from e

# --- Exchange Initialization ---
def get_exchange():
    """Initializes and returns the CCXT exchange object, falling back to env vars for secret."""
    config = load_config() # Uses global DEFAULT_CONFIG if file not found
    api_key = None
    secret = None

    try:
        api_key_name = 'GEMINI_API_KEY'
        api_key = get_keychain_credential(api_key_name)
    except ValueError as e:
        log_message(f"Failed to retrieve '{api_key_name}' from Keychain: {e}. This key is required.")
        raise 

    try:
        secret_name = 'GEMINI_SECRET'
        secret = get_keychain_credential(secret_name)
        log_message(f"Successfully retrieved '{secret_name}' from Keychain.")
    except ValueError as e:
        log_message(f"Failed to retrieve '{secret_name}' from Keychain: {e}. Attempting to read from environment variable.")
        secret = os.environ.get(secret_name) 
        if not secret:
            log_message(f"'{secret_name}' not found in Keychain and not set as environment variable.")
            raise ValueError(f"'{secret_name}' is required but not found in Keychain or environment.") from e
        else:
            log_message(f"Successfully retrieved '{secret_name}' from environment variable.")

    if not api_key or not secret:
        raise ValueError("Required API credentials (API Key and Secret) are missing or could not be retrieved.")

    try:
        exchange_class = getattr(ccxt, 'gemini')
        exchange = exchange_class({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True, 
        })
        exchange.load_markets() 
        log_message("Gemini Exchange markets loaded successfully. Credentials appear valid.")
        return exchange, config
    except ccxt.AuthenticationError as e:
        log_message(f"Authentication failed with Gemini API: {e}")
        raise ValueError(f"Gemini API authentication failed. Please check your API key and secret. Error: {e}") from e
    except ccxt.NetworkError as e:
        log_message(f"Network error during exchange setup: {e}")
        raise ValueError(f"Could not connect to Gemini exchange. Please check your network connection. Error: {e}") from e
    except Exception as e:
        log_message(f"An unexpected error occurred during exchange initialization: {e}")
        log_message(f"Traceback: {traceback.format_exc()}")
        raise 

def get_latest_llm_strategies():
    """Finds and loads the most recent LLM strategy JSON file."""
    try:
        list_of_files = glob.glob(os.path.join(STRATEGIES_DIR, 'llm_strategies_*.json'))
        if not list_of_files:
            log_message("No LLM strategy files found.")
            return []
        latest_file = max(list_of_files, key=os.path.getctime)
        log_message(f"Loading strategies from: {latest_file}")
        with open(latest_file, 'r') as f:
            strategies = json.load(f)
            for i, strategy in enumerate(strategies):
                if 'strategy_name' not in strategy:
                    strategy['strategy_name'] = f"Strategy_{i+1}_from_{os.path.basename(latest_file)}"
            return strategies
    except Exception as e:
        log_message(f"Error reading latest LLM strategies: {e}")
        log_message(f"Traceback: {traceback.format_exc()}")
        return []

def calculate_order_size(balance, price, strategy_investment_usd, global_trade_size_usd, stop_loss_pct):
    target_size_usd = float(strategy_investment_usd) if isinstance(strategy_investment_usd, (int, float)) else float(global_trade_size_usd)
    if target_size_usd <= 0:
        log_message(f"Invalid target_size_usd ({target_size_usd}). Using global default.")
        target_size_usd = float(global_trade_size_usd)

    available_quote_value = balance 
    effective_trade_size_usd = min(target_size_usd, available_quote_value) 
    
    if effective_trade_size_usd <= 0:
        log_message(f"Effective trade size is zero or negative after capping by balance ({effective_trade_size_usd:.2f} $). Skipping order.")
        return None
    
    size = effective_trade_size_usd / price
    min_order_size_base = 0.00001 
    if size < min_order_size_base:
        log_message(f"Calculated order size ({size:.8f} {base_currency}) is smaller than minimum ({min_order_size_base:.8f} {base_currency}). Skipping.")
        return None
    return size

def place_limit_order(exchange, symbol, order_type, size, price, strategy_name=None):
    base_currency = symbol.split('/')[0]
    try:
        log_message(f"Attempting to place {order_type} order: {size:.8f} {base_currency} at {price:.2f} for strategy '{strategy_name or 'N/A'}'")
        order = exchange.create_order(symbol, order_type, size, price)
        log_message(f"Order placed successfully: ID {order['id']} for strategy '{strategy_name or 'N/A'}'. Order details: {order}")
        return order
    except ccxt.InsufficientFunds:
        log_message(f"Insufficient funds to place order for strategy '{strategy_name or 'N/A'}'. Available quote balance might be too low.")
        return None
    except ccxt.NetworkError as e:
        log_message(f"Network error placing order for strategy '{strategy_name or 'N/A'}': {e}")
        log_message(f"Traceback: {traceback.format_exc()}")
        return None
    except ccxt.ExchangeError as e:
        log_message(f"Exchange error placing order for strategy '{strategy_name or 'N/A'}': {e}")
        log_message(f"Traceback: {traceback.format_exc()}")
        return None
    except Exception as e:
        log_message(f"An unexpected error occurred placing order for strategy '{strategy_name or 'N/A'}': {e}")
        log_message(f"Traceback: {traceback.format_exc()}")
        return None

def get_current_price(exchange, symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        if ticker and 'last' in ticker and ticker['last']:
            return ticker['last']
        else:
            log_message(f"Could not retrieve 'last' price for {symbol} from ticker.")
            return None
    except ccxt.NetworkError as e:
        log_message(f"Network error fetching ticker for {symbol}: {e}")
        return None
    except ccxt.ExchangeError as e:
        log_message(f"Exchange error fetching ticker for {symbol}: {e}")
        return None
    except Exception as e:
        log_message(f"Unexpected error fetching ticker for {symbol}: {e}")
        return None

def execute_trade(exchange, symbol, config, strategy=None):
    strategy_name = strategy.get('strategy_name', 'DefaultStrategy') if strategy else 'DefaultStrategy'
    log_message(f"Executing trade logic for {symbol} using strategy: '{strategy_name}'...")
    
    try:
        quote_currency = symbol.split('/')[1]
        balance_info = exchange.fetch_balance()
        available_quote_balance = balance_info.get('free', {}).get(quote_currency, 0)
        
        if available_quote_balance == 0:
            log_message(f"No free balance in quote currency '{quote_currency}' for strategy '{strategy_name}'. Skipping.")
            return

        current_price = get_current_price(exchange, symbol)
        if not current_price:
            log_message(f"Could not get current price for {symbol}, skipping trade for strategy '{strategy_name}'.")
            return

        log_message(f"Current price for {symbol}: {current_price:.2f}")

        strategy_investment_usd_raw = strategy.get('investment_usd', config['trade_size_usd']) if strategy else config['trade_size_usd']
        
        try:
            strategy_investment_usd = float(strategy_investment_usd_raw)
            if strategy_investment_usd <= 0:
                 log_message(f"Strategy '{strategy_name}' investment_usd ({strategy_investment_usd_raw}) is non-positive. Using global default.")
                 strategy_investment_usd = float(config['trade_size_usd'])
        except (ValueError, TypeError):
            log_message(f"Invalid 'investment_usd' ({strategy_investment_usd_raw}) in strategy '{strategy_name}'. Using global default: ${config['trade_size_usd']:.2f}.")
            strategy_investment_usd = float(config['trade_size_usd'])

        trade_size_usd_for_this_trade = min(float(config['trade_size_usd']), strategy_investment_usd)
        trade_size_usd_for_this_trade = min(trade_size_usd_for_this_trade, available_quote_balance) 

        if trade_size_usd_for_this_trade < 1.00: 
            log_message(f"Effective trade size for '{strategy_name}' ({trade_size_usd_for_this_trade:.2f}$) is too small, skipping.")
            return

        stop_loss_pct = float(strategy.get('risk_parameters', {}).get('stop_loss_pct', config['stop_loss_pct'])) if strategy else float(config['stop_loss_pct'])
        take_profit_pct = float(strategy.get('risk_parameters', {}).get('take_profit_pct', config['take_profit_pct'])) if strategy else float(config['take_profit_pct'])
        
        # --- BUY LOGIC ---
        buy_entry_price_target = current_price * (1 - 0.01) 
        
        if current_price <= buy_entry_price_target and available_quote_balance >= trade_size_usd_for_this_trade:
            order_size = calculate_order_size(available_quote_balance, current_price, trade_size_usd_for_this_trade, config['trade_size_usd'], stop_loss_pct)
            if order_size:
                buy_price = current_price * (1 - 0.005) 
                
                order = place_limit_order(exchange, symbol, 'limit', order_size, buy_price, strategy_name=strategy_name)
                if order:
                    log_message(f"BUY order placed for {strategy_name}: {order['id']}")
                    
                    stop_loss_price = buy_price * (1 - stop_loss_pct)
                    take_profit_price = buy_price * (1 + take_profit_pct)
                    
                    log_message(f"Setting STOP LOSS order at ${stop_loss_price:.2f} for {strategy_name}")
                    place_limit_order(exchange, symbol, 'limit', order_size, stop_loss_price, strategy_name=strategy_name) 
                    
                    log_message(f"Setting TAKE PROFIT order at ${take_profit_price:.2f} for {strategy_name}")
                    place_limit_order(exchange, symbol, 'limit', order_size, take_profit_price, strategy_name=strategy_name)
        else:
            log_message(f"Buy conditions not met for '{strategy_name}' on {symbol} or insufficient funds for trade size {trade_size_usd_for_this_trade:.2f}$. Current price condition not met: {current_price} > {buy_entry_price_target}.")

    except Exception as e:
        log_message(f"An error occurred during trade execution for strategy '{strategy_name}' on {symbol}: {e}")
        log_message(f"Traceback: {traceback.format_exc()}")

# --- Main Trading Loop ---
def main_trading_loop(exchange, config):
    symbols_to_trade = set()
    last_loaded_strategies_json = "" # Store string representation to detect changes

    while True:
        log_message("--- Starting trade cycle ---")
        strategies = get_latest_llm_strategies() # Uses global log_message
        current_strategies_json = json.dumps(strategies, sort_keys=True)

        if current_strategies_json != last_loaded_strategies_json:
            log_message(f"Detected change in LLM strategies or first run. Found {len(strategies)} strategies.")
            last_loaded_strategies_json = current_strategies_json

            symbols_to_trade.clear()
            if strategies:
                for strategy in strategies:
                    if strategy.get('symbol'):
                        symbols_to_trade.add(strategy['symbol'])
                
                if not symbols_to_trade: 
                    symbols_to_trade.update(["BTC/USD", "ETH/USD"])
                    log_message("LLM strategies found, but no symbols specified. Using default symbols.")
                else:
                     log_message(f"Trading symbols based on strategies: {', '.join(symbols_to_trade)}")
            else: 
                symbols_to_trade.update(["BTC/USD", "ETH/USD"]) 
                log_message("No LLM strategies found. Trading default symbols: BTC/USD, ETH/USD.")
        else:
            log_message("LLM strategies unchanged. Proceeding with existing symbols.")
            if not symbols_to_trade: 
                symbols_to_trade.update(["BTC/USD", "ETH/USD"])
                log_message("Re-ensuring default symbols as none were processed.")

        for symbol in symbols_to_trade:
            current_strategy = None
            if strategies: 
                for strategy in strategies:
                    if strategy.get('symbol', '').lower() == symbol.lower():
                        current_strategy = strategy
                        break 
            
            execute_trade(exchange, symbol, config, strategy=current_strategy)

        update_status_file({"trading_cycle_complete": datetime.now().isoformat()})
        log_message("Trade cycle finished. Sleeping for 5 minutes.")
        time.sleep(300) 

def signal_handler(sig, frame):
    log_message('Received termination signal, shutting down gracefully...')
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    log_message("Crypto Trading LLM Bot - Live Trading Script Started within virtual environment.")
    try:
        # Initialize TASK_STATUS for the trading process before get_exchange
        TASK_STATUS['trading'] = {'status': 'initializing', 'pid': PROCESS_PID, 'start_time': datetime.now().isoformat()}
        
        exchange, config = get_exchange() # This now uses Keychain or Env Var for secret and has better error handling
        
        # Update status to running after successful initialization
        TASK_STATUS['trading'] = {'status': 'running', 'pid': PROCESS_PID, 'start_time': datetime.now().isoformat(), 'config_loaded': config, 'is_running': True}
        
        main_trading_loop(exchange, config) 
        
    except ValueError as e: 
        log_message(f"Initialization error: {e}")
        update_status_file({"trading_status": "error", "error_message": str(e), "is_running": False})
        sys.exit(1)
    except Exception as e:
        log_message(f"An unexpected critical error occurred in the main script: {e}")
        log_message(f"Traceback:\n{traceback.format_exc()}") 
        update_status_file({"trading_status": "error", "error_message": str(e), "is_running": False})
        sys.exit(1)
