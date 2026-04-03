#!/usr/bin/env python3
print("=== QUICK STATUS ===")
import subprocess
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
bots = [
    ('Forex', 'forex_bot_with_schwab.py'),
    ('26-Crypto', 'real_26_crypto_trader.py'),
    ('Profit Bot', 'practical_profit_bot.py'),
    ('Dashboard', 'arbitration_trading_dashboard.py'),
    ('Monitor', 'proactive_monitor.py')
]
for name, pattern in bots:
    if pattern in result.stdout:
        print(f"✅ {name}: RUNNING")
    else:
        print(f"❌ {name}: NOT RUNNING")
print("\n📊 Dashboard: http://localhost:5020")
print("🔄 Quick check: python3 instant_status_check.py")