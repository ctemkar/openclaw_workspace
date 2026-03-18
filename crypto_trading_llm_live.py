import ccxt
import os
import json
import subprocess
import time
from datetime import datetime

TRADE_SIZE_USD = 10.0
STRATEGY_FILE = "/Users/chetantemkar/.openclaw/workspace/app/llm_strategies.json"
TRADES_LOG = "/Users/chetantemkar/.openclaw/workspace/app/completed_trades.json"
BOT_LOG = "/Users/chetantemkar/.openclaw/workspace/app/trading_bot_clean.log"

def get_keys():
    try:
        key = subprocess.check_output(["security", "find-generic-password", "-s", "GEMINI_API_KEY", "-w"], timeout=2).decode().strip()
        sec = subprocess.check_output(["security", "find-generic-password", "-s", "GEMINI_SECRET", "-w"], timeout=2).decode().strip()
        return key, sec
    except:
        try:
            with open("/Users/chetantemkar/.openclaw/workspace/app/.gemini_key", "r") as f: k = f.read().strip()
            with open("/Users/chetantemkar/.openclaw/workspace/app/.gemini_secret", "r") as f: s = f.read().strip()
            return k, s
        except: return None, None

def log_bot(msg):
    with open(BOT_LOG, "a") as f: f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def record_trade(trade_data):
    trades = []
    if os.path.exists(TRADES_LOG):
        try:
            with open(TRADES_LOG, "r") as f: trades = json.load(f)
        except: trades = []
    trades.insert(0, trade_data)
    with open(TRADES_LOG, "w") as f: json.dump(trades[:50], f)

def execute_trade(exchange, symbol, side, model_name):
    try:
        ticker = exchange.fetch_ticker(symbol)
        price = ticker["last"]
        limit_price = price * 1.01 if side == "buy" else price * 0.99
        amount = TRADE_SIZE_USD / price
        params = {'options': ['immediate-or-cancel']}
        exchange.create_order(symbol, 'limit', side, amount, limit_price, params)
        record_trade({"time": datetime.now().strftime("%H:%M:%S"), "model": model_name, "side": side, "price": price, "amount": amount, "status": "filled"})
        log_bot(f"SUCCESS: {model_name} {side} filled.")
    except Exception as e: log_bot(f"TRADE FAILURE: {str(e)}")

if __name__ == "__main__":
    k, s = get_keys()
    if not k: exit()
    exchange = ccxt.gemini({"apiKey": k, "secret": s})
    while True:
        if os.path.exists(STRATEGY_FILE):
            try:
                with open(STRATEGY_FILE, "r") as f: strategies = json.load(f)
                for model, data in strategies.items():
                    sig = data.get("signal", "").lower()
                    if sig in ["buy", "sell"]: execute_trade(exchange, data.get("symbol", "BTC/USD"), sig, model)
                os.remove(STRATEGY_FILE)
            except: pass
        time.sleep(10)
