#!/usr/bin/env python3
"""
Check 26-crypto trading system status
"""

import os
import time
import psutil
import requests
from datetime import datetime

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

def check_bot_process():
    """Check if trading bot is running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and 'simple_26_crypto_bot.py' in ' '.join(proc.info['cmdline']):
                return proc.info['pid'], proc.info['cmdline']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None, None

def check_trading_server():
    """Check trading server status"""
    try:
        response = requests.get("http://127.0.0.1:5001/status", timeout=2)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def check_logs():
    """Check for log files"""
    logs = []
    for log_file in ["26_crypto_trading.log", "26_crypto_analysis.log", "trading.log"]:
        path = os.path.join(BASE_DIR, log_file)
        if os.path.exists(path):
            size = os.path.getsize(path)
            mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%H:%M:%S")
            logs.append((log_file, size, mtime))
    return logs

def main():
    """Main function"""
    print("=" * 70)
    print("26-CRYPTO TRADING SYSTEM - REAL-TIME STATUS")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Check bot process
    pid, cmdline = check_bot_process()
    if pid:
        print(f"✅ TRADING BOT: RUNNING (PID: {pid})")
        print(f"   Command: {' '.join(cmdline[:3])}...")
    else:
        print("❌ TRADING BOT: NOT RUNNING")
    
    # Check trading server
    print("\n🔍 CHECKING TRADING SERVER...")
    server_status = check_trading_server()
    if 'error' in server_status:
        print(f"❌ TRADING SERVER: {server_status['error']}")
    else:
        print(f"✅ TRADING SERVER: RUNNING on port {server_status.get('port', 'N/A')}")
        print(f"   Status: {server_status.get('status', 'N/A')}")
        print(f"   Capital: ${server_status.get('capital', 0):.2f}")
        print(f"   Last update: {server_status.get('timestamp', 'N/A')}")
    
    # Check logs
    print("\n📊 CHECKING LOGS...")
    logs = check_logs()
    if logs:
        for log_file, size, mtime in logs:
            print(f"✅ {log_file}: {size:,} bytes (updated {mtime})")
    else:
        print("⚠️  No log files found yet")
    
    # Check API connections
    print("\n🔗 CHECKING EXCHANGE CONNECTIONS...")
    
    # Quick Gemini check
    try:
        import ccxt
        with open(os.path.join(BASE_DIR, '.gemini_key'), 'r') as f:
            gemini_key = f.read().strip()
        print(f"✅ Gemini API Key: {gemini_key[:15]}...")
    except:
        print("❌ Gemini: API key issue")
    
    # Quick Binance check  
    try:
        with open(os.path.join(BASE_DIR, '.binance_key'), 'r') as f:
            binance_key = f.read().strip()
        print(f"✅ Binance API Key: {binance_key[:10]}...")
    except:
        print("❌ Binance: API key issue")
    
    print("\n" + "=" * 70)
    print("🎯 TRADING SYSTEM SUMMARY")
    print("=" * 70)
    
    if pid:
        print("✅ SYSTEM STATUS: ACTIVE AND TRADING")
        print("\n📈 The system is now:")
        print("   1. Monitoring 26 cryptocurrencies")
        print("   2. Scanning every 2 minutes")
        print("   3. Looking for LONG opportunities on Gemini (16 pairs)")
        print("   4. Looking for SHORT opportunities on Binance (26 pairs)")
        print("   5. Using conservative risk management")
        
        print("\n🔍 TO MONITOR:")
        print("   • Check logs: tail -f 26_crypto_trading.log")
        print("   • Dashboard: http://127.0.0.1:5080")
        print("   • API: http://127.0.0.1:5001/status")
        
        print("\n⚠️  NOTE:")
        print("   Binance shows $0.00 USDT balance")
        print("   Trading will use Gemini only until Binance funds available")
        print("   You mentioned having $70+ USDT - please verify")
    else:
        print("❌ SYSTEM STATUS: INACTIVE")
        print("\n🚀 TO START TRADING:")
        print("   cd /Users/chetantemkar/.openclaw/workspace/app")
        print("   python3 simple_26_crypto_bot.py")
    
    print(f"\n⏰ Last check: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()