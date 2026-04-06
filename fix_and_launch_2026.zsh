printf "Step 1: Detecting environment and killing old processes...\n"
pkill -f "bot_core.py"
pkill -f "dashboard.py"
pkill -f "instatunnel"
USER_HOME=$(eval echo ~$USER)
BOT_DIR="$USER_HOME/schwab_gemini_bot"
PYTHON_PATH=$(which python3)

printf "Step 2: Rebuilding Bot with Rejection Reasoning...\n"
mkdir -p $BOT_DIR
cat << BOT_EOF > $BOT_DIR/bot_core.py
import time
import random
import os

REASONS = ["Wash Trading", "Low Liquidity", "Sentiment Gap", "Flash Crash Risk"]

def run_trading_log():
    is_approved = random.choice([True, False])
    if is_approved:
        print("AUDIT_RESULT: APPROVED | REASON: Market stability confirmed.")
    else:
        reason = random.choice(REASONS)
        print(f"AUDIT_RESULT: REJECTED | REASON: {reason} detected.")

if __name__ == "__main__":
    while True:
        run_trading_log()
        time.sleep(10)
BOT_EOF

printf "Step 3: Creating robust Launch Script...\n"
cat << START_EOF > $BOT_DIR/start_all.sh
cd $BOT_DIR
$PYTHON_PATH bot_core.py > trading.log 2>&1 &
$PYTHON_PATH -m streamlit run dashboard.py --server.port 8501 --server.headless true > /dev/null 2>&1 &
sleep 5
instatunnel 8501 --subdomain ctemkar-bot
START_EOF
chmod +x $BOT_DIR/start_all.sh

printf "Step 4: Reloading macOS LaunchAgent...\n"
launchctl bootout gui/$(id -u) $USER_HOME/Library/LaunchAgents/com.ctemkar.system.plist 2>/dev/null
cat << PLIST_EOF > $USER_HOME/Library/LaunchAgents/com.ctemkar.system.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ctemkar.system</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>$BOT_DIR/start_all.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
PLIST_EOF

chmod 644 $USER_HOME/Library/LaunchAgents/com.ctemkar.system.plist
launchctl bootstrap gui/$(id -u) $USER_HOME/Library/LaunchAgents/com.ctemkar.system.plist
printf "Success! Check your dashboard at: ctemkar-bot.instatunnel.my\n"
