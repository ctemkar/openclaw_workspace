#!/usr/bin/env python3
"""
INSTANT STATUS CHECK - Quick overview of ALL systems
"""
import os
import subprocess
import requests
from datetime import datetime

print("🚀 INSTANT STATUS CHECK - ALL TRADING SYSTEMS")
print("=" * 60)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

def check_process(name, pattern):
    """Check if process is running"""
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    return pattern in result.stdout

def get_pid(pattern):
    """Get PID of process"""
    result = subprocess.run(['pgrep', '-f', pattern], capture_output=True, text=True)
    pids = result.stdout.strip().split()
    return pids[0] if pids else 'NOT FOUND'

# 1. FOREX BOT
print("💰 FOREX TRADING BOT:")
forex_running = check_process('Forex', 'forex_bot_with_schwab.py')
forex_pid = get_pid('forex_bot_with_schwab.py')
if forex_running:
    print(f"  ✅ RUNNING (PID: {forex_pid})")
    # Check if it's real or simulated
    if os.path.exists('real_forex_trading.log'):
        with open('real_forex_trading.log', 'r') as f:
            lines = f.readlines()[-3:]
            for line in lines:
                if 'SIMULATED' in line or 'PLACEHOLDER' in line:
                    print("  ⚠️  SIMULATED (needs Access Token)")
                    break
                elif 'REAL' in line and 'API' in line:
                    print("  ✅ REAL TRADING (API calls)")
                    break
else:
    print("  ❌ NOT RUNNING")

# 2. 26-CRYPTO BOT
print("\n⚡ 26-CRYPTO ARBITRAGE BOT:")
crypto_running = check_process('26-crypto', 'real_26_crypto_trader.py')
crypto_pid = get_pid('real_26_crypto_trader.py')
if crypto_running:
    print(f"  ✅ RUNNING (PID: {crypto_pid})")
else:
    print("  ❌ NOT RUNNING")

# 3. PRACTICAL PROFIT BOT
print("\n📈 PRACTICAL PROFIT BOT:")
profit_running = check_process('practical', 'practical_profit_bot.py')
profit_pid = get_pid('practical_profit_bot.py')
if profit_running:
    print(f"  ✅ RUNNING (PID: {profit_pid})")
    # Check for errors
    if os.path.exists('practical_profit_output.log'):
        with open('practical_profit_output.log', 'r') as f:
            content = f.read()[-500:]
            if 'NOTIONAL' in content:
                print("  ⚠️  HAS NOTIONAL ERROR (trade size too small)")
            elif 'ERROR' in content:
                print("  ⚠️  HAS ERRORS")
            else:
                print("  ✅ NO ERRORS")
else:
    print("  ❌ NOT RUNNING")

# 4. DASHBOARD
print("\n📊 TRADING DASHBOARD:")
try:
    response = requests.get('http://localhost:5020', timeout=5)
    if response.status_code == 200:
        print("  ✅ RUNNING (HTTP 200)")
        # Check clicking functionality
        if 'cursor: pointer' in response.text:
            print("  ✅ CLICK FUNCTIONALITY ENABLED")
        else:
            print("  ⚠️  Click functionality missing")
    else:
        print(f"  ❌ ERROR: HTTP {response.status_code}")
except:
    print("  ❌ NOT RESPONDING")

# 5. EXCHANGE APIS
print("\n🌐 EXCHANGE APIS:")
try:
    b_resp = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=5)
    print(f"  ✅ Binance: {'OK' if b_resp.status_code == 200 else 'ERROR'}")
except:
    print("  ❌ Binance: FAILED")

try:
    g_resp = requests.get('https://api.gemini.com/v1/pubticker/btcusd', timeout=5)
    print(f"  ✅ Gemini: {'OK' if g_resp.status_code == 200 else 'ERROR'}")
except:
    print("  ❌ Gemini: FAILED")

# 6. ARBITRAGE OPPORTUNITY
print("\n💰 ARBITRAGE OPPORTUNITY:")
try:
    b = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=MANAUSDT', timeout=5).json()
    g = requests.get('https://api.gemini.com/v1/pubticker/manausd', timeout=5).json()
    bp = float(b['price'])
    gp = float(g['last'])
    spread = ((gp - bp) / bp) * 100
    
    print(f"  Binance: ${bp:.4f}")
    print(f"  Gemini:  ${gp:.4f}")
    print(f"  Spread:  {spread:.2f}%")
    
    if spread > 0.5:
        print(f"  ✅ PROFITABLE! ${gp-bp:.4f} per MANA")
    else:
        print(f"  ⚠️  Not profitable (need >0.5%)")
        
except Exception as e:
    print(f"  ❌ Can't check: {e}")

# 7. OVERALL STATUS
print("\n" + "=" * 60)
print("🎯 OVERALL SYSTEM STATUS:")

systems = [
    ('Forex Bot', forex_running),
    ('26-Crypto Bot', crypto_running),
    ('Profit Bot', profit_running),
    ('Dashboard', 'dashboard_running' in locals() and dashboard_running),
    ('Exchange APIs', 'b_resp' in locals() and b_resp.status_code == 200 and g_resp.status_code == 200)
]

running = sum(1 for name, status in systems if status)
total = len(systems)

print(f"  Systems running: {running}/{total}")
print(f"  Health: {'✅ GOOD' if running >= 4 else '⚠️  NEEDS ATTENTION' if running >= 2 else '❌ CRITICAL'}")

# 8. IMMEDIATE ACTIONS
print("\n🔧 IMMEDIATE ACTIONS NEEDED:")
if not forex_running:
    print("  • Start Forex bot")
if not crypto_running:
    print("  • Start 26-crypto bot")
if not profit_running:
    print("  • Start practical profit bot")

# Check for Access Token
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        env_content = f.read()
        if 'SCHWAB_ACCESS_TOKEN' not in env_content:
            print("  • Get Schwab Access Token for REAL Forex trading")

print("\n🔄 Run this anytime: python3 instant_status_check.py")
print("📊 Dashboard: http://localhost:5020")
print("🔍 Detailed monitor: python3 proactive_monitor.py")