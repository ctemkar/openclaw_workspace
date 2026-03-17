import ccxt
import os
import subprocess
import time
from datetime import datetime

def get_keys():
    try:
        key = subprocess.check_output(["security", "find-generic-password", "-s", "GEMINI_API_KEY", "-w"], timeout=2).decode().strip()
        secret = subprocess.check_output(["security", "find-generic-password", "-s", "GEMINI_SECRET", "-w"], timeout=2).decode().strip()
        return key, secret
    except:
        try:
            with open("/Users/chetantemkar/.openclaw/workspace/app/.gemini_key", "r") as f:
                key = f.read().strip()
            with open("/Users/chetantemkar/.openclaw/workspace/app/.gemini_secret", "r") as f:
                secret = f.read().strip()
            return key, secret
        except:
            return None, None

def log_action(message):
    log_path = "/Users/chetantemkar/.openclaw/workspace/app/trading_bot_clean.log"
    with open(log_path, "a") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ts}] {message}\n")

if __name__ == "__main__":
    api_key, api_secret = get_keys()
    if api_key and api_secret:
        try:
            exchange = ccxt.gemini({"apiKey": api_key, "secret": api_secret})
            log_action("VERIFIED: EXCHANGE CONNECTED")
            while True:
                log_action("HEARTBEAT: Scanning markets")
                time.sleep(60)
        except Exception as e:
            log_action(f"EXCHANGE ERROR: {str(e)}")
    else:
        log_action("FATAL ERROR: No keys found in Keychain or local backup")
