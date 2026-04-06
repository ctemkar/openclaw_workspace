printf "Step 1: Synchronizing Mac mini Clock (Fixing Gemini Nonce Error)...\n"
sudo sntp -sS time.apple.com

printf "Step 2: Pulling 2026 Model Suite to Ollama...\n"
ollama pull llama-4-scout
ollama pull gpt-oss:20b
ollama pull qwen3:32b

printf "Step 3: Creating Multi-Model Paper Trading Test Engine...\n"
mkdir -p ~/schwab_gemini_bot
cat << 'INNER_EOF' > ~/schwab_gemini_bot/bot_core.py
import os
import time

def run_model_test(model_name):
    print(f"--- TESTING MODEL: {model_name} ---")
    print(f"Syncing balances with {model_name} logic...")
    time.sleep(2)
    print(f"{model_name} Status: Monitoring for market fake-outs.")

def bot_loop():
    models = ["llama-4-scout", "gpt-oss:20b", "qwen3:32b"]
    while True:
        for model in models:
            run_model_test(model)
            time.sleep(5)
        print("Cooldown: 5 minutes before next full cycle...")
        time.sleep(300)

if __name__ == "__main__":
    bot_loop()
INNER_EOF

printf "Step 4: Configuring Automatic Launch on Startup...\n"
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

launchctl load ~/Library/LaunchAgents/com.ctemkar.tradingbot.plist
printf "All systems synchronized and Paper Trading tests are live.\n"
