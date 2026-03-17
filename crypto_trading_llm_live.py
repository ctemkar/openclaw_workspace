import ccxt
import os
import time
import json
from datetime import datetime

STRATEGY_FILE = "/Users/chetantemkar/.openclaw/workspace/app/llm_strategies.json"
LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_bot_clean.log"

def log_action(message):
    with open(LOG_FILE, "a") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ts}] {message}\n")

def check_signals():
    if os.path.exists(STRATEGY_FILE):
        try:
            with open(STRATEGY_FILE, 'r') as f:
                data = json.load(f)
                signal = data.get('signal')
                symbol = data.get('symbol', 'BTC/USD')
                amount = data.get('amount', 0.001)
                
                if signal in ['BUY', 'SELL']:
                    log_action(f"SIGNAL DETECTED: {signal} {symbol}")
                    # In a real scenario, we would call place_market_order here
                    return True
        except Exception as e:
            log_action(f"ERROR READING STRATEGY: {e}")
    return False

if __name__ == "__main__":
    log_action("BOT ACTIVE: Using CCXT Gemini Driver.")
    while True:
        if check_signals():
            log_action("HEARTBEAT: Signal processed.")
        else:
            log_action("HEARTBEAT: Waiting for trade signals...")
        time.sleep(60)
