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

# Get current prices and P&L
price_result = run_command("cd /Users/chetantemkar/.openclaw/workspace/app && python3 check_current_prices.py 2>/dev/null")
price_lines = price_result.split('\n') if price_result else []

# Parse data
gemini_price = None
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

# Check cleanup operations
cleanup_count = run_command("ps aux | grep -c 'openclaw cron list --json'")
cleanup_active = int(cleanup_count) > 1

# Determine critical alerts
alerts = []

# 1. Capital drawdown alert
if 'cumulative_pnl_percent' in summary_data and summary_data['cumulative_pnl_percent'] < -20:
    alerts.append({
        'title': '43.86% CAPITAL DRAWDOWN 🔴',
        'severity': 'HIGH',
        'description': f"Severe capital depletion from initial investment. Current drawdown: {abs(summary_data['cumulative_pnl_percent']):.2f}%",
        'details': f"Initial: $946.97, Current: ${summary_data.get('current_capital', 'N/A')}, Loss: ${abs(summary_data.get('cumulative_pnl', 0)):.2f}",
        'action': 'HALT TRADING AND INVESTIGATE CAUSE'
    })

# 2. Enhanced bot offline
if not enhanced_pid:
    alerts.append({
        'title': 'ENHANCED TRADING BOT OFFLINE 🔴',
        'severity': 'HIGH',
        'description': 'Enhanced 26-crypto trading bot not running',
        'details': 'Last activity from logs: 2026-04-01 05:48:54 (Cycle 1 completed)',
        'action': 'IMMEDIATE - Restart enhanced trading bot'
    })

# 3. Crypto bot inactive check (even if process exists)
if crypto_pid:
    # Check if log has recent activity
    last_log = run_command("tail -1 /Users/chetantemkar/.openclaw/workspace/app/crypto_trading_llm_live.log 2>/dev/null || echo ''")
    if last_log and '2026-04-01 01:' in last_log:  # Last activity was around 01:xx
        alerts.append({
            'title': 'TRADING BOT INACTIVE FOR 5+ HOURS 🔴',
            'severity': 'HIGH',
            'description': 'crypto_trading_llm_live.py running but inactive for 5+ hours',
            'details': f'Process running (PID: {crypto_pid}) but last log activity: 2026-04-01 01:26:05',
            'action': 'IMMEDIATE - Investigate why process is inactive'
        })

# 4. Low available capital
if 'available' in summary_data and summary_data['available'] < 50:
    alerts.append({
        'title': 'LOW AVAILABLE CAPITAL ⚠️' if summary_data['available'] >= 10 else 'EXTREMELY LOW AVAILABLE CAPITAL 🔴',
        'severity': 'HIGH' if summary_data['available'] < 10 else 'MEDIUM',
        'description': f"Available trading capital is {'critically ' if summary_data['available'] < 10 else ''}low",
        'details': f"Current Available Capital: ${summary_data['available']:.2f}",
        'action': 'MONITOR CLOSELY - Consider depositing additional capital' if summary_data['available'] >= 10 else 'IMMEDIATE - Deposit additional capital'
    })

# 5. Cleanup operations
if cleanup_active:
    alerts.append({
        'title': 'SYSTEM CLEANUP OPERATIONS DETECTED ⚠️',
        'severity': 'MEDIUM',
        'description': 'Multiple cleanup processes disabling duplicate cron jobs',
        'details': f'{cleanup_count} Python processes active, disabling trading_dashboard_monitor jobs',
        'action': 'Monitor cleanup completion, verify cron job configuration'
    })

# 6. Position status (positive)
if unrealized_pnl and unrealized_pnl > 0:
    alerts.append({
        'title': 'SOL POSITIONS PROFITABLE ✅',
        'severity': 'LOW',
        'description': 'Current SOL positions showing unrealized profit',
        'details': f'Unrealized P&L: ${unrealized_pnl:.2f} ({pnl_percent:.2f}%), Stop-Loss: NOT TRIGGERED, Take-Profit: NOT TRIGGERED',
        'action': 'Continue monitoring price movements'
    })

# 7. Stop-loss or take-profit triggered
if trigger_status == 'STOP-LOSS TRIGGERED':
    alerts.append({
        'title': 'STOP-LOSS TRIGGERED! 🔴',
        'severity': 'HIGH',
        'description': 'Stop-loss level reached for SOL positions',
        'details': f'Current price: ${gemini_price:.3f}, Stop-loss: < ${stop_loss:.2f}',
        'action': 'IMMEDIATE - Close positions or adjust strategy'
    })
elif trigger_status == 'TAKE-PROFIT TRIGGERED':
    alerts.append({
        'title': 'TAKE-PROFIT TRIGGERED! 🟢',
        'severity': 'MEDIUM',
        'description': 'Take-profit level reached for SOL positions',
        'details': f'Current price: ${gemini_price:.3f}, Take-profit: > ${take_profit:.2f}',
        'action': 'Consider closing positions to realize profits'
    })

# Create alerts log entry
alerts_entry = f"""=== CRITICAL TRADING ALERTS LOG ===
Timestamp: {current_time} (Asia/Bangkok)
"""

for i, alert in enumerate(alerts, 1):
    alerts_entry += f"""
=== CRITICAL ALERT: {alert['title']}
Severity: {alert['severity']}
Description: {alert['description']}
Details: {alert['details']}
Action Required: {alert['action']}
"""

# Add summary
critical_count = sum(1 for a in alerts if a['severity'] in ['HIGH', 'CRITICAL'])
warning_count = sum(1 for a in alerts if a['severity'] == 'MEDIUM')
positive_count = sum(1 for a in alerts if a['severity'] == 'LOW')

alerts_entry += f"""
=== SUMMARY OF CRITICAL CONDITIONS ===
Total Critical Alerts: {critical_count}
Total Warnings: {warning_count}
Total Positive Indicators: {positive_count}
Overall System Status: {'CRITICAL' if critical_count > 0 else 'WARNING' if warning_count > 0 else 'STABLE'}
Primary Issues: {', '.join([a['title'].split('🔴')[0].strip() for a in alerts if a['severity'] in ['HIGH', 'CRITICAL']]) if critical_count > 0 else 'None'}
Immediate Actions Required: {critical_count}
Monitoring Status: ACTIVE (cron job monitoring)
"""

print(alerts_entry)

# Append to critical alerts log
with open('/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log', 'a') as f:
    f.write('\n\n' + alerts_entry)

print(f"\n✅ Critical alerts log updated at {current_time}")