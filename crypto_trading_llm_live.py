import ccxt, os, json, time
from datetime import datetime
STRATEGY_FILE = "/Users/chetantemkar/.openclaw/workspace/app/llm_strategies.json"
TRADES_LOG = "/Users/chetantemkar/.openclaw/workspace/app/completed_trades.json"
def get_keys():
    try:
        with open("/Users/chetantemkar/.openclaw/workspace/app/.gemini_key", "r") as f: k = f.read().strip()
        with open("/Users/chetantemkar/.openclaw/workspace/app/.gemini_secret", "r") as f: s = f.read().strip()
        return k, s
    except: return None, None
def log_bot(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
if __name__ == "__main__":
    log_bot("🚀 STARTING GEMINI TRADING ENGINE...")
    k, s = get_keys()
    if not k:
        log_bot("❌ ERROR: No API keys found in .gemini_key file.")
        exit()
    exchange = ccxt.gemini({"apiKey": k, "secret": s})
    log_bot("✅ Connected to Gemini. Entering watch loop...")
    while True:
        if os.path.exists(STRATEGY_FILE):
            log_bot("📂 New strategy detected! Processing...")
            try:
                with open(STRATEGY_FILE, "r") as f: strategies = json.load(f)
                log_bot(f"🎯 Action: {strategies}")
                os.remove(STRATEGY_FILE)
            except Exception as e: log_bot(f"⚠️ Strategy Error: {e}")
        else:
            print(".", end="", flush=True)
        time.sleep(10)
