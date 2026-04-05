import subprocess
import json
import os
from datetime import datetime

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except:
        return ""

print("=" * 80)
print("TRADING DASHBOARD MONITORING REPORT")
print("=" * 80)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Asia/Bangkok)")
print(f"Dashboard URL: http://localhost:5001/")
print()

# Check if dashboard is running
print("=== DASHBOARD STATUS ===")
port_check = run_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:5001/ 2>/dev/null || echo '000'")
if port_check == "000":
    print("❌ Dashboard Status: NOT RUNNING (Port 5001 inactive)")
else:
    print(f"✅ Dashboard Status: RUNNING (HTTP {port_check})")

# Check for other dashboard ports
print("\n=== ALTERNATIVE DASHBOARD PORTS ===")
for port in [5007, 5008, 5009, 5000, 5002, 5003, 5004, 5005, 5006, 5010]:
    status = run_command(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{port}/ 2>/dev/null || echo '000'")
    if status != "000":
        print(f"Port {port}: HTTP {status}")

# Check trading bot processes
print("\n=== TRADING BOT PROCESSES ===")
processes = run_command("ps aux | grep -E '(crypto_trading|enhanced_26_crypto|trading_bot)' | grep -v grep")
if processes:
    print("✅ Trading bots detected:")
    for line in processes.split('\n'):
        if line:
            print(f"  • {line[:100]}...")
else:
    print("❌ No active trading bot processes found")

# Check specific bot status
print("\n=== SPECIFIC BOT STATUS ===")
# Check crypto_trading_llm_live.py
crypto_pid = run_command("pgrep -f 'crypto_trading_llm_live.py'")
if crypto_pid:
    print(f"✅ crypto_trading_llm_live.py: RUNNING (PID: {crypto_pid})")
    # Check last activity
    last_log = run_command("tail -5 /Users/chetantemkar/.openclaw/workspace/app/crypto_trading_llm_live.log 2>/dev/null | tail -1 || echo ''")
    if last_log:
        print(f"  Last log entry: {last_log[:80]}...")
else:
    print("❌ crypto_trading_llm_live.py: NOT RUNNING")

# Check enhanced bot
enhanced_pid = run_command("pgrep -f 'enhanced_26_crypto'")
if enhanced_pid:
    print(f"✅ enhanced_26_crypto_trading.py: RUNNING (PID: {enhanced_pid})")
    last_log = run_command("tail -5 /Users/chetantemkar/.openclaw/workspace/app/enhanced_26_crypto_trading.log 2>/dev/null | tail -1 || echo ''")
    if last_log:
        print(f"  Last log entry: {last_log[:80]}...")
else:
    print("❌ enhanced_26_crypto_trading.py: NOT RUNNING")

# Check current prices
print("\n=== CURRENT MARKET PRICES ===")
price_result = run_command("cd /Users/chetantemkar/.openclaw/workspace/app && python3 check_current_prices.py 2>/dev/null")
if price_result:
    for line in price_result.split('\n'):
        if line and not line.startswith('Current Time'):
            print(line)

# Check trading summary
print("\n=== LATEST TRADING SUMMARY ===")
summary_file = "/Users/chetantemkar/.openclaw/workspace/app/trading_summary_latest.txt"
if os.path.exists(summary_file):
    with open(summary_file, 'r') as f:
        lines = f.readlines()
        # Get key metrics
        for line in lines:
            if "Current Capital:" in line:
                print(line.strip())
            elif "Cumulative P&L:" in line:
                print(line.strip())
            elif "Total Capital:" in line:
                print(line.strip())
            elif "Available:" in line:
                print(line.strip())
            elif "Total Open Positions:" in line:
                print(line.strip())
else:
    print("❌ No trading summary file found")

# Check critical alerts
print("\n=== SYSTEM STATUS ===")
critical_file = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
if os.path.exists(critical_file):
    with open(critical_file, 'r') as f:
        content = f.read()
        # Count critical alerts
        critical_count = content.count("CRITICAL ALERT:")
        warning_count = content.count("SYSTEM CLEANUP") + content.count("POSITION STATUS")
        
        print(f"Active Critical Alerts: {critical_count}")
        print(f"Active Warnings: {warning_count}")
        
        # Get latest alert
        alerts = content.split("=== CRITICAL ALERT:")
        if len(alerts) > 1:
            latest = alerts[1].split('\n')[0].strip()
            print(f"Latest Critical: {latest}")
else:
    print("❌ No critical alerts file found")

# Check cleanup operations
print("\n=== CLEANUP OPERATIONS ===")
cleanup_count = run_command("ps aux | grep -c 'openclaw cron list --json'")
if int(cleanup_count) > 1:
    print(f"⚠️  Active cleanup processes: {int(cleanup_count)-1}")
    print("  Purpose: Disabling duplicate trading_dashboard_monitor cron jobs")
    print("  Issue: OpenRouter billing errors, monitoring non-existent port 5001")
else:
    print("✅ No active cleanup operations")

print("\n" + "=" * 80)
print("MONITORING COMPLETE")
print("=" * 80)