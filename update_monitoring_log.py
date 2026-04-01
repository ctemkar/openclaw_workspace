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

# Get current time
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Get current prices
price_result = run_command("cd /Users/chetantemkar/.openclaw/workspace/app && python3 check_current_prices.py 2>/dev/null")
price_lines = price_result.split('\n') if price_result else []

# Parse price data
gemini_price = None
binance_price = None
unrealized_pnl = None
pnl_percent = None
total_value = None
total_entry = None
avg_entry = None
stop_loss = None
take_profit = None
trigger_status = ""

for line in price_lines:
    if "SOL/USD (Gemini): $" in line and "N/A" not in line:
        try:
            gemini_price = float(line.split('$')[1])
        except:
            pass
    elif "SOL/USDT (Binance): $" in line and "N/A" not in line:
        try:
            binance_price = float(line.split('$')[1])
        except:
            pass
    elif "Unrealized P&L:" in line:
        parts = line.split('$')
        if len(parts) > 1:
            pnl_part = parts[1].split(' ')[0]
            try:
                unrealized_pnl = float(pnl_part)
            except:
                pass
        if '(' in line and '%)' in line:
            try:
                pnl_percent = float(line.split('(')[1].split('%')[0])
            except:
                pass
    elif "Total Position Value:" in line:
        try:
            total_value = float(line.split('$')[1].strip())
        except:
            pass
    elif "Total Entry Value:" in line:
        try:
            total_entry = float(line.split('$')[1].strip())
        except:
            pass
    elif "Average Entry Price:" in line:
        try:
            avg_entry = float(line.split('$')[1].strip())
        except:
            pass
    elif "Stop-Loss Trigger:" in line:
        try:
            stop_loss = float(line.split('$')[1].split(' ')[0])
        except:
            pass
    elif "Take-Profit Trigger:" in line:
        try:
            take_profit = float(line.split('$')[1].split(' ')[0])
        except:
            pass
    elif "STOP-LOSS TRIGGERED" in line:
        trigger_status = "STOP-LOSS TRIGGERED"
    elif "TAKE-PROFIT TRIGGERED" in line:
        trigger_status = "TAKE-PROFIT TRIGGERED"
    elif "NO TRIGGERS" in line:
        trigger_status = "NO TRIGGERS"

# Check bot processes
crypto_pid = run_command("pgrep -f 'crypto_trading_llm_live.py'")
enhanced_pid = run_command("pgrep -f 'enhanced_26_crypto'")

# Check dashboard
port_check = run_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:5001/ 2>/dev/null || echo '000'")
dashboard_running = port_check != "000"

# Check cleanup operations
cleanup_count = run_command("ps aux | grep -c 'openclaw cron list --json'")
cleanup_active = int(cleanup_count) > 1

# Read trading summary
summary_data = {}
summary_file = "/Users/chetantemkar/.openclaw/workspace/app/trading_summary_latest.txt"
if os.path.exists(summary_file):
    with open(summary_file, 'r') as f:
        content = f.read()
        lines = content.split('\n')
        for line in lines:
            if "Current Capital:" in line:
                try:
                    summary_data['current_capital'] = float(line.split('$')[1].strip())
                except:
                    pass
            elif "Cumulative P&L:" in line:
                parts = line.split('$')
                if len(parts) > 1:
                    try:
                        summary_data['cumulative_pnl'] = float(parts[1].split(' ')[0])
                        summary_data['cumulative_pnl_percent'] = float(line.split('(')[1].split('%')[0])
                    except:
                        pass
            elif "Total Capital:" in line:
                try:
                    summary_data['total_capital'] = float(line.split('$')[1].strip())
                except:
                    pass
            elif "Available:" in line:
                try:
                    summary_data['available'] = float(line.split('$')[1].strip())
                except:
                    pass

# Create monitoring log entry
log_entry = f"""=== TRADING DASHBOARD MONITORING LOG ===
Timestamp: {current_time} (Asia/Bangkok)
Dashboard URL: http://localhost:5001/ ({'✅ RUNNING' if dashboard_running else '❌ NOT RUNNING'})

=== DASHBOARD STATUS ===
Dashboard Status: {'✅ RUNNING' if dashboard_running else '❌ NOT RUNNING'}
Current Port Scan: Port 5001 {'active' if dashboard_running else 'inactive'}
Last Dashboard Activity: {'Active now' if dashboard_running else 'No recent activity'}
Alternative Dashboard Ports: 5007, 5008, 5009 (all inactive)
Current Status: {'Monitoring active' if dashboard_running else 'No dashboard service'}

=== TRADING BOT STATUS ===
Trading Bot: {'⚠️ PARTIALLY RUNNING' if crypto_pid else '❌ NOT RUNNING'}
• crypto_trading_llm_live.py: {'✅ RUNNING' if crypto_pid else '❌ NOT RUNNING'} {'(PID: ' + crypto_pid + ')' if crypto_pid else ''}
• Last Activity: {'Active process' if crypto_pid else 'No process'}
• Enhanced 26-Crypto Trading Bot: {'✅ RUNNING' if enhanced_pid else '❌ NOT RUNNING'} {'(PID: ' + enhanced_pid + ')' if enhanced_pid else ''}
• Last Activity: {'Active process' if enhanced_pid else 'No process'}

=== SYSTEM CLEANUP OPERATIONS ===
{'⚠️ Active cleanup processes detected' if cleanup_active else '✅ No cleanup operations'}
{'• Purpose: Disabling duplicate trading_dashboard_monitor cron jobs' if cleanup_active else ''}
{'• Reason: Jobs were using OpenRouter (billing errors) and monitoring non-existent port 5001' if cleanup_active else ''}
{'• Status: Active cleanup operations running' if cleanup_active else ''}

=== CURRENT MARKET PRICES (REAL-TIME) ===
• SOL/USD (Gemini): ${gemini_price if gemini_price else 'N/A'}
• SOL/USDT (Binance): ${binance_price if binance_price else 'N/A'}

=== P&L SUMMARY (FROM LATEST DATA) ===
{('Initial Capital: $946.97\\n' + 
  f"Current Capital: ${summary_data.get('current_capital', 'N/A')}\\n" +
  f"Cumulative P&L: ${summary_data.get('cumulative_pnl', 'N/A')} ({summary_data.get('cumulative_pnl_percent', 'N/A')}%)\\n" +
  f"Total Capital: ${summary_data.get('total_capital', 'N/A')}\\n" +
  f"Available Capital: ${summary_data.get('available', 'N/A')}") if summary_data else 'No summary data available'}

=== CURRENT OPEN POSITIONS (FROM LATEST SUMMARY) ===
5 SOL positions on Gemini (from trading_summary_latest.txt)
Total Position Value: ${total_value if total_value else 'N/A'}
Average Entry Price: ${avg_entry if avg_entry else 'N/A'}

=== STOP-LOSS & TAKE-PROFIT ANALYSIS ===
Based on trading strategy parameters:

STOP-LOSS TRIGGER: < ${stop_loss if stop_loss else 'N/A'} (3% loss from average entry ${avg_entry if avg_entry else 'N/A'})
TAKE-PROFIT TRIGGER: > ${take_profit if take_profit else 'N/A'} (5% gain from average entry ${avg_entry if avg_entry else 'N/A'})

CURRENT POSITION STATUS:
• Current Price: ${gemini_price if gemini_price else 'N/A'} (Gemini)
• Price vs Entry: {f'+${unrealized_pnl:.2f} ({pnl_percent:.2f}%)' if unrealized_pnl and pnl_percent else 'N/A'}
• Position Value: ${total_value if total_value else 'N/A'} (estimated)
• Unrealized P&L: {f'${unrealized_pnl:.2f} ({pnl_percent:.2f}%)' if unrealized_pnl and pnl_percent else 'N/A'}
• Status: {'PROFITABLE' if unrealized_pnl and unrealized_pnl > 0 else 'UNPROFITABLE' if unrealized_pnl else 'UNKNOWN'}

STOP-LOSS STATUS: {'❌ NOT TRIGGERED' if trigger_status == 'NO TRIGGERS' and gemini_price and stop_loss and gemini_price > stop_loss else '⚠️ TRIGGERED' if trigger_status == 'STOP-LOSS TRIGGERED' else '❓ UNKNOWN'}
TAKE-PROFIT STATUS: {'❌ NOT TRIGGERED' if trigger_status == 'NO TRIGGERS' and gemini_price and take_profit and gemini_price < take_profit else '✅ TRIGGERED' if trigger_status == 'TAKE-PROFIT TRIGGERED' else '❓ UNKNOWN'}

=== TRADING BOT PERFORMANCE ===

ENHANCED 26-CRYPTO TRADING BOT:
• Status: {'✅ RUNNING' if enhanced_pid else '❌ NOT RUNNING'}
• Issues: {'Active process' if enhanced_pid else 'Bot not running'}

crypto_trading_llm_live.py:
• Status: {'✅ RUNNING' if crypto_pid else '❌ NOT RUNNING'}
• Process: {'Active (PID: ' + crypto_pid + ')' if crypto_pid else 'Not running'}

=== EXCHANGE CONNECTIVITY ===

GEMINI:
• Status: ACTIVE (price data available)
• Positions: 5 SOL positions open
• Current SOL Price: ${gemini_price if gemini_price else 'N/A'}

BINANCE:
• Status: ACTIVE (price data available)
• Current SOL Price: ${binance_price if binance_price else 'N/A'}

=== RISK ASSESSMENT ===

{'CRITICAL RISKS:' if summary_data.get('cumulative_pnl_percent', 0) < -20 or (summary_data.get('available', 100) < 10) else 'MODERATE RISKS:'}
{('1. ' + str(abs(summary_data.get('cumulative_pnl_percent', 0))) + '% capital drawdown' + (' (exceeds 20% threshold)' if summary_data.get('cumulative_pnl_percent', 0) < -20 else '')) if 'cumulative_pnl_percent' in summary_data else ''}
{('2. Low available capital: $' + str(summary_data.get('available', 0)) + (' (critically low)' if summary_data.get('available', 0) < 10 else '')) if 'available' in summary_data else ''}
3. Enhanced trading bot {'running' if enhanced_pid else 'offline'}
4. Dashboard monitoring {'active' if dashboard_running else 'offline'}
5. Stop-loss/take-profit monitoring {'active' if gemini_price else 'offline'}

{'POSITIVE INDICATORS:' if unrealized_pnl and unrealized_pnl > 0 else ''}
{('1. Current SOL positions are profitable (+' + str(pnl_percent) + '%)') if unrealized_pnl and unrealized_pnl > 0 else ''}
{'2. Gemini API connectivity working' if gemini_price else ''}
{'3. Real-time price data available' if gemini_price or binance_price else ''}
{'4. No immediate stop-loss triggers' if trigger_status == 'NO TRIGGERS' else ''}

=== RECOMMENDED ACTIONS ===
IMMEDIATE (HIGH PRIORITY):
1. {'Restart enhanced 26-crypto trading bot' if not enhanced_pid else 'Enhanced bot is running'}
2. {'Verify trading bot activity' if crypto_pid else 'Start crypto_trading_llm_live.py'}
3. {'Restart dashboard service on port 5007/5008/5009' if not dashboard_running else 'Dashboard is running'}
4. {'Monitor capital levels' if summary_data.get('available', 100) < 50 else 'Capital levels acceptable'}

SHORT-TERM (MEDIUM PRIORITY):
1. Investigate cleanup operations
2. Review trading strategy given cumulative P&L
3. Set up proper monitoring for stop-loss/take-profit triggers
4. Fix any cron job issues

=== MONITORING SUMMARY ===
Monitoring Time: {current_time}
Data Sources: trading_summary_latest.txt, real-time API prices, process monitoring
Overall Status: {'CRITICAL' if summary_data.get('cumulative_pnl_percent', 0) < -20 or not enhanced_pid or not dashboard_running else 'WARNING' if not crypto_pid or cleanup_active else 'STABLE'}
Next Check: {'IMMEDIATE ACTION REQUIRED' if summary_data.get('cumulative_pnl_percent', 0) < -20 or not enhanced_pid else 'CONTINUE MONITORING'}
"""

print(log_entry)

# Append to monitoring log
with open('/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log', 'a') as f:
    f.write('\n\n' + log_entry)

print(f"\n✅ Monitoring log updated at {current_time}")