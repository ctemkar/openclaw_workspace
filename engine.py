import streamlit as st
import ccxt
import ollama
import pandas as pd
import time
import re
from datetime import datetime, timedelta

st.set_page_config(page_title="AI Shadow Engine", layout="wide")
st.title("🕵️‍♂️ AI SHADOW ATTRIBUTION ENGINE (5-MIN WINDOW)")

binance = ccxt.binance({
    'apiKey': 'ecTeKrOgmLbP1HspJsXCU5Wf6TKSlE6PmTNZfKWbmjFA9koTx3T29xvcDnguYaf6',
    'secret': 'cLfkqqy4nLbp51Z8x4823FJ01317WwDTst8id2bMi5SEXJykiUag5IRn7kKhrilo',
    'enableRateLimit': True
})
binance.set_sandbox_mode(True)
gemini = ccxt.gemini({'enableRateLimit': True})

MODELS = ['llama3', 'phi4', 'mistral', 'deepseek-r1:7b', 'qwen2.5:7b', 'gemma2:9b', 'llama3.2', 'llama3.1']

if 'model_stats' not in st.session_state:
    st.session_state.model_stats = {m: {"Shadow_PL": 0.0, "Accuracy": 0.0, "Signals": 0} for m in MODELS}
if 'active_signals' not in st.session_state:
    st.session_state.active_signals = []

m1, m2, m3, m4 = st.columns(4)
b_metric = m1.empty()
g_metric = m2.empty()
s_metric = m3.empty()
a_metric = m4.empty()

st.divider()
st.subheader("🗳️ Current Consensus Vote (Real-Time)")
votes_display = st.empty()

st.divider()
col_lead, col_active = st.columns([1, 1])

with col_lead:
    st.subheader("🏆 Shadow Leaderboard")
    leaderboard_display = st.empty()

with col_active:
    st.subheader("⏱️ Pending Signal Evaluation (5-Min Wait)")
    pending_display = st.empty()

def get_model_vote(model_name, bp, gp, spd):
    prompt = f"Price B:{bp}, G:{gp}, Spread:{spd}%. Score 1-10 on Buy Binance. Number only."
    try:
        res = ollama.chat(model=model_name, messages=[{'role': 'user', 'content': prompt}])
        score_text = res['message']['content']
        score = float(re.findall(r"[-+]?\d*\.\d+|\d+", score_text)[0])
        return min(max(score, 1.0), 10.0)
    except:
        return 5.0

while True:
    try:
        btick = binance.fetch_ticker('BTC/USDT')
        gtick = gemini.fetch_ticker('BTC/USD')
        bp, gp = btick['last'], gtick['last']
        spd = round(((gp - bp) / bp) * 100, 4)
        
        b_metric.metric("Binance BTC", f"${bp}")
        g_metric.metric("Gemini BTC", f"${gp}")
        s_metric.metric("Spread %", f"{spd}%")
        
        votes = {m: get_model_vote(m, bp, gp, spd) for m in MODELS}
        a_metric.metric("Avg Score", round(sum(votes.values())/8, 2))

        votes_df = pd.DataFrame([votes])
        votes_display.dataframe(votes_df)

        for m, score in votes.items():
            if score >= 7.0:
                st.session_state.active_signals.append({
                    "model": m,
                    "entry_price": bp,
                    "expiry": datetime.now() + timedelta(minutes=5),
                    "score": score
                })
        
        current_time = datetime.now()
        remaining_signals = []
        for sig in st.session_state.active_signals:
            if current_time >= sig['expiry']:
                profit = (bp - sig['entry_price']) * (25.0 / sig['entry_price'])
                st.session_state.model_stats[sig['model']]["Shadow_PL"] += profit
                st.session_state.model_stats[sig['model']]["Signals"] += 1
                wins = 1 if profit > 0 else 0
                total_sigs = st.session_state.model_stats[sig['model']]["Signals"]
                current_acc = st.session_state.model_stats[sig['model']]["Accuracy"]
                st.session_state.model_stats[sig['model']]["Accuracy"] = round(((current_acc * (total_sigs - 1)) + wins) / total_sigs, 4)
            else:
                remaining_signals.append(sig)
        
        st.session_state.active_signals = remaining_signals

        leader_df = pd.DataFrame.from_dict(st.session_state.model_stats, orient='index').astype(float)
        leaderboard_display.table(leader_df.sort_values(by="Shadow_PL", ascending=False))
        
        if st.session_state.active_signals:
            pending_df = pd.DataFrame(st.session_state.active_signals)
            pending_display.dataframe(pending_df[['model', 'entry_price', 'score', 'expiry']])
        else:
            pending_display.write("Waiting for high-confidence signals to enter waitlist...")

        time.sleep(20)
    except Exception as e:
        time.sleep(10)
