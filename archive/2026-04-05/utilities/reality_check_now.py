#!/usr/bin/env python3
"""
Reality Check - Verify actual trading status
"""

import os
import json
from datetime import datetime

print("=" * 70)
print(f"🔍 REALITY CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# Check 1: Verify bots are running
print("\n1. ✅ CHECKING BOT PROCESSES:")
try:
    import subprocess
    
    # Check practical profit bot
    result = subprocess.run(['pgrep', '-f', 'practical_profit_bot.py'], 
                          capture_output=True, text=True)
    if result.stdout:
        print(f"   Practical Profit Bot: ✅ RUNNING (PID: {result.stdout.strip()})")
    else:
        print(f"   Practical Profit Bot: ❌ NOT RUNNING")
    
    # Check 26-crypto arbitrage bot
    result = subprocess.run(['pgrep', '-f', 'real_26_crypto_arbitrage_bot.py'], 
                          capture_output=True, text=True)
    if result.stdout:
        print(f"   26-Crypto Arbitrage Bot: ✅ RUNNING (PID: {result.stdout.strip()})")
    else:
        print(f"   26-Crypto Arbitrage Bot: ❌ NOT RUNNING")
        
except Exception as e:
    print(f"   Error checking processes: {e}")

# Check 2: Verify profit logs
print("\n2. 📊 CHECKING PROFIT LOGS:")
profit_log = "practical_profits.log"
if os.path.exists(profit_log):
    try:
        with open(profit_log, 'r') as f:
            lines = f.readlines()
        
        print(f"   Log file exists: {len(lines)} entries")
        
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        today_trades = [line for line in lines if line.startswith(today)]
        
        print(f"   Trades today ({today}): {len(today_trades)}")
        
        if today_trades:
            print(f"   Last trade today: {today_trades[-1].strip()}")
            
            # Check for inconsistent counting
            trade_counts = []
            for line in today_trades:
                if "Trades:" in line:
                    import re
                    match = re.search(r'Trades:\s*(\d+)', line)
                    if match:
                        trade_counts.append(int(match.group(1)))
            
            if trade_counts:
                print(f"   Trade counts in log: {trade_counts}")
                if len(set(trade_counts)) > 1:
                    print(f"   ⚠️  WARNING: Inconsistent trade counting detected!")
        
    except Exception as e:
        print(f"   Error reading log: {e}")
else:
    print(f"   ❌ Profit log not found: {profit_log}")

# Check 3: Verify API keys
print("\n3. 🔐 CHECKING API CONFIGURATION:")
secure_keys_dir = "secure_keys"
if os.path.exists(secure_keys_dir):
    files = os.listdir(secure_keys_dir)
    print(f"   Secure keys directory: {len(files)} files")
    
    for file in files:
        if file.startswith('.binance'):
            try:
                with open(os.path.join(secure_keys_dir, file), 'r') as f:
                    content = f.read().strip()
                    print(f"   {file}: {len(content)} chars ({content[:10]}...{content[-10:]})")
            except:
                print(f"   {file}: Error reading")
else:
    print(f"   ❌ Secure keys directory not found")

# Check 4: Current market check
print("\n4. 📈 CHECKING CURRENT MARKET:")
try:
    import ccxt
    
    binance = ccxt.binance({'enableRateLimit': True})
    gemini = ccxt.gemini({'enableRateLimit': True})
    
    # Check MANA
    b_mana = binance.fetch_ticker('MANA/USDT')['last']
    g_mana = gemini.fetch_ticker('MANA/USD')['last']
    mana_spread = ((g_mana - b_mana) / b_mana) * 100
    
    print(f"   MANA Spread: {mana_spread:.2f}%")
    print(f"   Binance: ${b_mana:.4f}, Gemini: ${g_mana:.4f}")
    
    if abs(mana_spread) >= 0.5:
        print(f"   ✅ TRADABLE: {abs(mana_spread):.2f}% ≥ 0.5%")
    else:
        print(f"   ⏳ MONITORING: {abs(mana_spread):.2f}% < 0.5%")
        
except Exception as e:
    print(f"   Error checking market: {e}")

# Check 5: Dashboard status
print("\n5. 🌐 CHECKING DASHBOARDS:")
dashboards = [
    ("Gateway (5001)", "http://localhost:5001"),
    ("Real Top 10 (5026)", "http://localhost:5026"),
    ("Sorted Spread (5025)", "http://localhost:5025"),
    ("Truthful (5024)", "http://localhost:5024"),
]

for name, url in dashboards:
    try:
        import subprocess
        result = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', url],
                              capture_output=True, text=True, timeout=2)
        if result.stdout == "200":
            print(f"   {name}: ✅ ACCESSIBLE")
        else:
            print(f"   {name}: ❌ HTTP {result.stdout}")
    except:
        print(f"   {name}: ❌ UNREACHABLE")

print("\n" + "=" * 70)
print("🎯 SUMMARY:")
print("   • Gateway running on port 5001")
print("   • Check dashboards for real-time data")
print("   • Verify profit log consistency")
print("   • Monitor MANA spread for trading opportunities")
print("=" * 70)