printf "Ensuring Streamlit is installed for your Mac mini...\n"
pip install streamlit pandas --quiet

printf "Updating Bot to log all activity to ~/schwab_gemini_bot/trading.log...\n"
mkdir -p $HOME/schwab_gemini_bot
launchctl bootout gui/$(id -u) $HOME/Library/LaunchAgents/com.trading.bot.plist

cat << 'PLIST_EOF' > $HOME/Library/LaunchAgents/com.trading.bot.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.trading.bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$HOME/schwab_gemini_bot/bot_core.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/schwab_gemini_bot/trading.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/schwab_gemini_bot/trading.log</string>
</dict>
</plist>
PLIST_EOF

launchctl bootstrap gui/$(id -u) $HOME/Library/LaunchAgents/com.trading.bot.plist

printf "Creating the Dashboard script...\n"
cat << 'DASH_EOF' > $HOME/schwab_gemini_bot/dashboard.py
import streamlit as st
import os
import time

st.set_page_config(page_title="2026 AI Trading Dashboard", layout="wide")
st.title("🤖 Master Auditor Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.header("Llama 4 Scout")
    st.info("Execution Agent")

with col2:
    st.header("GPT OSS 20B")
    st.success("Master Auditor")

with col3:
    st.header("Qwen 3 32B")
    st.warning("High Latency Strategist")

st.subheader("Live Feed")
log_box = st.empty()

while True:
    if os.path.exists(os.path.expanduser("~/schwab_gemini_bot/trading.log")):
        with open(os.path.expanduser("~/schwab_gemini_bot/trading.log"), "r") as f:
            logs = f.readlines()
            log_box.text("".join(logs[-20:]))
    time.sleep(2)
DASH_EOF

printf "Launching Dashboard! View it at http://localhost:8501\n"
streamlit run $HOME/schwab_gemini_bot/dashboard.py
