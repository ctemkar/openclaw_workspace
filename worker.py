import ccxt, ollama, pandas as pd, time, re, json, os
from datetime import datetime, timedelta
STATE_FILE = 'state.json'
STATUS_FILE = 'status.json'
LIVE_FILE = 'live_consensus.json'
MODELS = ['llama3', 'phi4', 'mistral', 'deepseek-r1:7b', 'qwen2.5:7b', 'gemma2:9b', 'llama3.2', 'llama3.1']
TOP_10 = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'DOGE/USDT', 'LINK/USDT', 'AVAX/USDT', 'DOT/USDT', 'MATIC/USDT']

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f: return json.load(f)
        except: pass
    return {"model_stats": {m: {"PL": 0.0, "Wins": 0, "Signals": 0} for m in MODELS}, "active_signals": [], "last_scan": (datetime.now() - timedelta(minutes=10)).isoformat()}

def save_state(s):
    with open(STATE_FILE, 'w') as f: json.dump(s, f)

def save_live(asset, votes, progress):
    with open(LIVE_FILE, 'w') as f:
        json.dump({"asset": asset, "votes": votes, "progress": progress, "time": datetime.now().strftime("%H:%M:%S")}, f)

def update_status(msg, asset=None):
    current = {"msg": msg, "asset": asset or "-", "time": datetime.now().strftime("%H:%M:%S")}
    if asset is None and os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, 'r') as f: current["asset"] = json.load(f).get("asset", "-")
        except: pass
    with open(STATUS_FILE, 'w') as f: json.dump(current, f)

def get_score(m, s, b, g, sp):
    try:
        res = ollama.chat(model=m, messages=[{'role': 'user', 'content': f"Asset:{s}, B:{b}, G:{g}, Spd:{sp}%. Score 1(Sell) to 10(Buy). 5 Neutral. Num only."}])
        t = re.sub(r'<think>.*?</think>', '', res['message']['content'], flags=re.DOTALL)
        n = re.findall(r"[-+]?\d*\.\d+|\d+", t)
        return min(max(float(n[-1]), 1.0), 10.0) if n else 5.0
    except: return 5.0

binance = ccxt.binance({'apiKey': 'ecTeKrOgmLbP1HspJsXCU5Wf6TKSlE6PmTNZfKWbmjFA9koTx3T29xvcDnguYaf6', 'secret': 'cLfkqqy4nLbp51Z8x4823FJ01317WwDTst8id2bMi5SEXJykiUag5IRn7kKhrilo', 'enableRateLimit': True})
binance.set_sandbox_mode(True)
gemini = ccxt.gemini({'enableRateLimit': True})

while True:
    try:
        s = load_state()
        now = datetime.now()
        rem = []
        for sig in s["active_signals"]:
            if now >= datetime.fromisoformat(sig['expiry']):
                curr = binance.fetch_ticker(sig['asset'])['last']
                diff = curr - sig['entry']
                is_win = (sig['score'] > 5.1 and diff > 0) or (sig['score'] < 4.9 and diff < 0)
                m = sig['model']
                s["model_stats"][m]["Signals"] += 1
                if is_win: s["model_stats"][m]["Wins"] += 1
                s["model_stats"][m]["PL"] += (diff * (25.0 / sig['entry'])) if sig['score'] > 5.1 else (-diff * (25.0 / sig['entry']))
            else: rem.append(sig)
        s["active_signals"] = rem
        
        ls = datetime.fromisoformat(s["last_scan"])
        if (now - ls).total_seconds() > 300:
            for sym in TOP_10:
                try:
                    update_status("🔍 ACTIVE SCAN", sym)
                    bt, gt = binance.fetch_ticker(sym), gemini.fetch_ticker(sym.replace('/USDT', '/USD'))
                    bp, gp = bt['last'], gt['last']
                    spd = round(((gp - bp) / bp) * 100, 4)
                    votes = {}
                    for i, m in enumerate(MODELS):
                        update_status(f"🔍 ANALYZING ({i+1}/8 Models)", sym)
                        score = get_score(m, sym, bp, gp, spd)
                        votes[m] = score
                        if score != 5.0:
                            s["active_signals"].append({"asset": sym, "model": m, "entry": bp, "expiry": (datetime.now() + timedelta(minutes=5)).isoformat(), "score": score})
                        save_live(sym, votes, f"{i+1}/8")
                    save_state(s)
                except: continue
            s["last_scan"] = datetime.now().isoformat()
        else:
            wait = int(300 - (now - ls).total_seconds())
            update_status(f"⏳ IDLE (Next scan in {wait}s)")
        save_state(s)
        time.sleep(10)
    except: time.sleep(10)
