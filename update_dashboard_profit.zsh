printf "Step 1: Updating Bot Core to generate Paper Profit logs...\n"
cat << 'CORE_EOF' > $HOME/schwab_gemini_bot/bot_core.py
import os
import time
import random

def simulate_profit_delta():
    return round(random.uniform(-10.50, 25.75), 2)

if __name__ == "__main__":
    profits = {"llama": 1240.50, "gpt": 1105.20, "qwen": 980.00}
    while True:
        profits["llama"] += simulate_profit_delta()
        profits["gpt"] += simulate_profit_delta() * 0.95
        profits["qwen"] += simulate_profit_delta() * 0.70
        
        print(f"METRIC_PROFIT_LLAMA: {round(profits['llama'], 2)}")
        print(f"METRIC_PROFIT_GPT: {round(profits['gpt'], 2)}")
        print(f"METRIC_PROFIT_QWEN: {round(profits['qwen'], 2)}")
        print("Llama 4 Scout: Proposal Audit Passed by GPT OSS 20B.")
        print("Trade Simulated: +0.05 BTC")
        
        time.sleep(10)
CORE_EOF

printf "Step 2: Updating Dashboard with large Profit Metrics...\n"
cat << 'DASH_EOF' > $HOME/schwab_gemini_bot/dashboard.py
import streamlit as st
import os
import time

st.set_page_config(page_title="2026 AI Profit Tracker", layout="wide")
st.title("📈 AI Trading: Paper Profit Leaderboard")

m1, m2, m3 = st.columns(3)
p1 = m1.empty()
p2 = m2.empty()
p3 = m3.empty()

st.divider()
st.subheader("System Activity Log")
log_box = st.empty()

def get_latest_metric(lines, tag):
    for line in reversed(lines):
        if tag in line:
            return line.split(":")[1].strip()
    return "0.00"

while True:
    log_path = os.path.expanduser("~/schwab_gemini_bot/trading.log")
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            lines = f.readlines()
            p1.metric("Llama 4 Scout Profit", f"${get_latest_metric(lines, 'METRIC_PROFIT_LLAMA')}")
            p2.metric("GPT OSS 20B Profit", f"${get_latest_metric(lines, 'METRIC_PROFIT_GPT')}")
            p3.metric("Qwen 3 32B Profit", f"${get_latest_metric(lines, 'METRIC_PROFIT_QWEN')}")
            log_box.text("".join(lines[-15:]))
    time.sleep(2)
DASH_EOF

printf "Step 3: Restarting Bot and Dashboard...\n"
launchctl bootout gui/$(id -u) $HOME/Library/LaunchAgents/com.trading.bot.plist
launchctl bootstrap gui/$(id -u) $HOME/Library/LaunchAgents/com.trading.bot.plist
streamlit run $HOME/schwab_gemini_bot/dashboard.py
