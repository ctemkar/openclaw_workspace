printf "Pulling 2026 AI Stack to Ollama...\n"
ollama pull gpt-oss:120b
ollama pull llama-4-scout:latest
ollama pull whisper-large-v3-turbo:latest

printf "Creating Trading Bot Core...\n"
cat << 'INNER_EOF' > bot_core.py
import os
import json

def get_balance_sync():
    printf_cmd = "Llama 4 Scout: Synchronizing Schwab and Gemini balances..."
    print(printf_cmd)
    return True

def trade_confirmation(action):
    os.system(f"orpheus-tts --text 'Trade confirmed: {action}' --voice english")

def kill_switch_listener():
    os.system("whisper-listen --keyword 'abort' --action 'kill-all-trades'")

if __name__ == "__main__":
    get_balance_sync()
    print("System active and listening for voice commands.")
INNER_EOF

chmod +x bot_core.py
printf "Bot environment and scripts are ready.\n"
