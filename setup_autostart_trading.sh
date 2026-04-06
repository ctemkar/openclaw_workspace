printf "Creating macOS LaunchAgent for auto-startup...\n"
mkdir -p ~/Library/LaunchAgents
cat << 'PLIST_EOF' > ~/Library/LaunchAgents/com.ctemkar.tradingbot.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ctemkar.tradingbot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$HOME/schwab_gemini_bot/bot_core.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
PLIST_EOF

printf "Configuring Paper Trading Core with 5-minute cooldown...\n"
mkdir -p ~/schwab_gemini_bot
cat << 'CORE_EOF' > ~/schwab_gemini_bot/bot_core.py
import time
import os

def paper_trade_cycle():
    mock_schwab = "https://api.sandbox.schwab.com"
    mock_gemini = "https://api.sandbox.gemini.com"
    print(f"Simulation Mode Active: Polling {mock_gemini}...")
    
    kill_switch_active = False 
    if kill_switch_active:
        print("VOICE ABORT DETECTED. PAUSING FOR 5 MINUTES.")
        os.system("say 'Trades paused for 5 minutes'")
        time.sleep(300)
        os.system("say 'Resuming paper trading'")

if __name__ == "__main__":
    while True:
        paper_trade_cycle()
        time.sleep(60)
CORE_EOF

launchctl load ~/Library/LaunchAgents/com.ctemkar.tradingbot.plist
printf "LaunchAgent loaded. Bot will now run automatically on login.\n"
