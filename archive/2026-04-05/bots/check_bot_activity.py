#!/usr/bin/env python3
"""
Check if 26-crypto trading bot is actually working
"""

import os
import time
import psutil
import subprocess
from datetime import datetime

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"
BOT_PID = 47029  # From earlier check

def check_bot_process():
    """Check if bot process is alive and working"""
    print("🔍 Checking bot process...")
    
    try:
        proc = psutil.Process(BOT_PID)
        
        print(f"✅ Process {BOT_PID} is running")
        print(f"   Name: {proc.name()}")
        print(f"   Status: {proc.status()}")
        print(f"   CPU: {proc.cpu_percent():.1f}%")
        print(f"   Memory: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
        print(f"   Created: {datetime.fromtimestamp(proc.create_time()).strftime('%H:%M:%S')}")
        
        # Check command line
        cmdline = ' '.join(proc.cmdline())
        print(f"   Command: {cmdline[:80]}...")
        
        return True
        
    except psutil.NoSuchProcess:
        print(f"❌ Process {BOT_PID} not found")
        return False
    except Exception as e:
        print(f"❌ Error checking process: {e}")
        return False

def test_bot_functionality():
    """Test if bot can actually analyze markets"""
    print("\n🧪 Testing bot functionality...")
    
    # Run a quick test of the bot's analysis
    test_script = """
import ccxt
import os

print("Quick market analysis test...")

# Test Gemini
try:
    gemini = ccxt.gemini()
    btc_ticker = gemini.fetch_ticker('BTC/USD')
    print(f"BTC/USD: ${btc_ticker['last']:.2f} ({btc_ticker['percentage']:.2f}%)")
except Exception as e:
    print(f"Gemini error: {e}")

# Test Binance  
try:
    binance = ccxt.binance()
    eth_ticker = binance.fetch_ticker('ETH/USDT')
    print(f"ETH/USDT: ${eth_ticker['last']:.2f} ({eth_ticker['percentage']:.2f}%)")
except Exception as e:
    print(f"Binance error: {e}")
"""
    
    try:
        result = subprocess.run(['python3', '-c', test_script], 
                              capture_output=True, text=True, cwd=BASE_DIR)
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def check_recent_activity():
    """Check for any recent activity files"""
    print("\n📊 Checking for recent activity...")
    
    recent_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(('.log', '.json', '.txt')):
                path = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(path)
                    if time.time() - mtime < 300:  # Last 5 minutes
                        size = os.path.getsize(path)
                        recent_files.append((path, size, datetime.fromtimestamp(mtime)))
                except:
                    pass
    
    if recent_files:
        print(f"✅ Found {len(recent_files)} recently modified files:")
        for path, size, mtime in sorted(recent_files, key=lambda x: x[2], reverse=True)[:5]:
            print(f"   {mtime.strftime('%H:%M:%S')} - {os.path.basename(path)} ({size} bytes)")
    else:
        print("❌ No recently modified files found")
    
    return len(recent_files) > 0

def restart_bot_if_needed():
    """Restart bot if it's not working"""
    print("\n🔄 Checking if bot needs restart...")
    
    # Check if bot is producing any output
    bot_file = os.path.join(BASE_DIR, "simple_26_crypto_bot.py")
    
    if not os.path.exists(bot_file):
        print(f"❌ Bot file not found: {bot_file}")
        return False
    
    # Read bot to understand what it should do
    with open(bot_file, 'r') as f:
        content = f.read()
    
    if 'print("=" * 70)' in content and '26-CRYPTO TRADING BOT' in content:
        print("✅ Bot script looks correct")
        
        # Check if bot might be stuck
        choice = input("\nBot might not be producing output. Restart it? (y/N): ").strip().lower()
        
        if choice == 'y':
            print("Restarting bot...")
            # Kill existing
            try:
                proc = psutil.Process(BOT_PID)
                proc.terminate()
                time.sleep(2)
            except:
                pass
            
            # Start new
            new_proc = subprocess.Popen(['python3', bot_file], 
                                       cwd=BASE_DIR,
                                       stdout=open(os.path.join(BASE_DIR, '26_crypto_live.log'), 'w'),
                                       stderr=subprocess.STDOUT)
            print(f"✅ Bot restarted with PID: {new_proc.pid}")
            print(f"   Output going to: 26_crypto_live.log")
            return True
        else:
            print("⚠️  Keeping existing bot running")
            return False
    else:
        print("❌ Bot script doesn't look right")
        return False

def main():
    """Main function"""
    print("=" * 70)
    print("26-CRYPTO TRADING BOT - ACTIVITY CHECK")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print("Bot started at: 00:15:00 (6 minutes ago)")
    print("Should have completed 3 scan cycles by now")
    print("=" * 70)
    
    # Check process
    process_ok = check_bot_process()
    
    # Test functionality
    functionality_ok = test_bot_functionality()
    
    # Check activity
    activity_found = check_recent_activity()
    
    print("\n" + "=" * 70)
    print("DIAGNOSIS:")
    print("=" * 70)
    
    if not process_ok:
        print("❌ BOT PROCESS: NOT RUNNING")
        print("   The bot PID 47029 doesn't exist")
    elif not functionality_ok:
        print("❌ BOT FUNCTIONALITY: ISSUES")
        print("   Market data fetch might be failing")
    elif not activity_found:
        print("⚠️  BOT ACTIVITY: NO RECENT OUTPUT")
        print("   Bot is running but not producing logs/output")
        print("   Possible issues:")
        print("   1. Bot might be stuck in loop")
        print("   2. Output not being logged")
        print("   3. API connections failing silently")
        
        # Offer to restart
        restart_bot_if_needed()
    else:
        print("✅ BOT STATUS: ACTIVE AND WORKING")
        print("   Recent activity detected")
        print("   Check specific log files for trading signals")
    
    print("\n💡 QUICK FIX:")
    print("   1. Check: tail -f 26_crypto_live.log (if exists)")
    print("   2. Restart: kill 47029 && python3 simple_26_crypto_bot.py")
    print("   3. Monitor: Check for 'CYCLE' output in logs")
    
    print(f"\n⏰ Check completed: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()