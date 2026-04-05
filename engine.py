import streamlit as st
import ccxt
import ollama
import pandas as pd
import time
import re
import json
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="AI CIO Terminal", layout="wide")
st.title("⚖️ THE CIO ENSEMBLE: 50-ASSET SHADOW TERMINAL")

STATE_FILE = 'state.json'
MODELS = ['llama3', 'phi4', 'mistral', 'deepseek-r1:7b', 'qwen2.5:7b', 'gemma2:9b', 'llama3.2', 'llama3.1']
TOP_10 = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'DOGE/USDT', 'LINK/USDT', 'AVAX/USDT', 'DOT/USDT', 'MATIC/USDT']

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                if "model_stats" in data: return data
        except: pass
    return {
        "model_stats": {m: {"PL": 0.0, "Wins": 0, "Signals": 0} for m in MODELS},
        "active_signals": [],
        "last_scan": (datetime.now() - timedelta(minutes=10)).isoformat()
    }

def save_state(s):
    with open(STATE_FILE, 'w') as f:
        json.dump(s, f)

binance = ccxt.binance({'apiKey': 'ecTeKrOgmLbP1HspJsXCU5Wf6TKSlE6PmTNZfKWbmjFA9koTx3T29xvcDnguYaf6', 'secret': 'cLfkqqy4nLbp51Z8x4823FJ01317WwDTst8id2bMi5SEXJykiUag5IRn7kKhrilo', 'enableRateLimit': True})
binance.set_sandbox_mode(True)
gemini = ccxt.gemini({'enableRateLimit': True})

state = load_state()

m1, m2, m3 = st.columns(3)
scan_status = m1.empty()
active_ticker = m2.empty()
spread_ticker = m3.empty()

st.divider()
col_lead, col_active = st.columns([3, 2])
lead_table = col_lead.empty()
active_df_display = col_active.empty()

def get_clean_score(model, symbol, bp, gp, spd):
    try:
        res = ollama.chat(model=model, messages=[{'role': 'user', 'content': f"Asset:{symbol}, B:{bp}, G:{gp}, Spread:{spd}%. Score 1-10. Number only."}])
        text = re.sub(r'<think>.*?</think>', '', res['message']['content'], flags=re.DOTALL)
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        return min(max(float(nums[-1]), 1.0), 10.0) if nums else 5.0
    except: return 5.0

def render_ui(s):
    df = pd.DataFrame.from_dict(s["model_stats"], orient='index')
    df['Accuracy'] = (df['Wins'] / df['Signals']).fillna(0.0).round(4)
    lead_table.table(df[['PL', 'Accuracy', 'Signals']].sort_values(by="PL", ascending=False))
    if s["active_signals"]:
        active_df_display.dataframe(pd.DataFrame(s["active_signals"])[['asset', 'model', 'expiry']])
    else:
        active_df_display.info("No active signals maturing.")

while True:
    try:
        now = datetime.now()
        render_ui(state)
        
        matured = False
        remaining = []
        for sig in state["active_signals"]:
            if now >= datetime.fromisoformat(sig['expiry']):
                matured = True
                curr = binance.fetch_ticker(sig['asset'])['last']
                profit = (curr - sig['entry']) * (25.0 / sig['entry'])
                m = sig['model']
                state["model_stats"][m]["PL"] += profit
                state["model_stats"][m]["Signals"] += 1
                if profit > 0: state["model_stats"][m]["Wins"] += 1
            else:
                remaining.append(sig)
        state["active_signals"] = remaining
        if matured: 
            save_state(state)
            render_ui(state)

        last_scan = datetime.fromisoformat(state["last_scan"])
        if (now - last_scan).total_seconds() > 300:
            with st.status("🚀 Scanning Markets...", expanded=True) as status:
                for symbol in TOP_10:
                    try:
                        status.write(f"Analyzing {symbol}...")
                        bt = binance.fetch_ticker(symbol)
                        gt = gemini.fetch_ticker(symbol.replace('/USDT', '/USD'))
                        bp, gp = bt['last'], gt['last']
                        spd = round(((gp - bp) / bp) * 100, 4)
                        active_ticker.metric("Active Asset", symbol)
                        spread_ticker.metric("Current Spread", f"{spd}%")
                        if abs(spd) > 0.05:
                            for m in MODELS:
                                score = get_clean_score(m, symbol, bp, gp, spd)
                                if score >= 7.0:
                                    state["active_signals"].append({
                                        "asset": symbol, "model": m, "entry": bp,
                                        "expiry": (datetime.now() + timedelta(minutes=5)).isoformat(), "score": score
                                    })
                                    render_ui(state)
                        save_state(state)
                    except: continue
                state["last_scan"] = datetime.now().isoformat()
                save_state(state)
                status.update(label="✅ Scan Complete", state="complete")
        else:
            scan_status.warning(f"⏳ IDLE: Next scan in {int(300 - (now - last_scan).total_seconds())}s")

        time.sleep(10)
    except Exception as e:
        time.sleep(10)
