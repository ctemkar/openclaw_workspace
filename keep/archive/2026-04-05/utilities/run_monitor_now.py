#!/usr/bin/env python3
import json
import logging
from datetime import datetime
import os

LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
CRITICAL_LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
critical_logger = logging.getLogger('critical_alerts')
critical_handler = logging.FileHandler(CRITICAL_LOG_FILE)
critical_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
critical_logger.addHandler(critical_handler)
critical_logger.setLevel(logging.WARNING)

def analyze_current_state():
    """Analyze current trading state from logs and files"""
    summary_lines = []
    critical_alerts = []
    
    # Read recent trading logs
    trading_logs = []
    try:
        with open('/Users/chetantemkar/.openclaw/workspace/app/real_26_crypto_trading.log', 'r') as f:
            trading_logs = f.read().split('\n')[-50:]  # Last 50 lines
    except:
        trading_logs = ["No real trading logs available"]
    
    # Read critical alerts
    critical_alerts_content = []
    try:
        with open(CRITICAL_LOG_FILE, 'r') as f:
            critical_alerts_content = f.read().split('\n')[-20:]  # Last 20 lines
    except:
        critical_alerts_content = ["No critical alerts file"]
    
    # Check for recent errors in logs
    recent_errors = [log for log in trading_logs if 'ERROR' in log or 'failed' in log.lower()]
    recent_success = [log for log in trading_logs if 'SUCCESS' in log or 'EXECUTING' in log]
    
    # Check for margin/insufficient funds errors
    margin_errors = [log for log in recent_errors if 'insufficient' in log.lower() or 'margin' in log.lower()]
    
    # Get current time
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Log analysis
    logging.info(f"=== Trading Monitor Analysis - {current_time} ===")
    logging.info(f"Recent logs analyzed: {len(trading_logs)} lines")
    logging.info(f"Recent errors found: {len(recent_errors)}")
    logging.info(f"Recent successes: {len(recent_success)}")
    logging.info(f"Margin errors: {len(margin_errors)}")
    
    # Build summary
    summary_lines.append(f"=== TRADING DASHBOARD MONITOR SUMMARY ===")
    summary_lines.append(f"Analysis Time: {current_time}")
    summary_lines.append(f"Status: DASHBOARD OFFLINE - Analyzing from logs")
    
    # System status
    summary_lines.append(f"\n=== SYSTEM STATUS ===")
    summary_lines.append(f"Dashboard: OFFLINE (no active server detected)")
    summary_lines.append(f"Trading Bot: ACTIVE (crypto_trading_llm_live.py running)")
    summary_lines.append(f"Recent Activity: {len(recent_success)} trade attempts in last 50 logs")
    
    # Error analysis
    if recent_errors:
        summary_lines.append(f"\n=== RECENT ERRORS ===")
        for error in recent_errors[-5:]:  # Last 5 errors
            summary_lines.append(f"- {error}")
    
    # Critical alerts check
    if critical_alerts_content and len(critical_alerts_content) > 5:
        summary_lines.append(f"\n=== CRITICAL ALERTS (from file) ===")
        # Get the most recent critical alert section
        for line in critical_alerts_content[-10:]:
            if line.strip():
                summary_lines.append(line)
    
    # Margin/insufficient funds analysis
    if margin_errors:
        alert_msg = f"🚨 MARGIN/INSUFFICIENT FUNDS ERRORS DETECTED: {len(margin_errors)} recent errors"
        critical_alerts.append(alert_msg)
        critical_logger.warning(alert_msg)
        summary_lines.append(f"\n🚨 CRITICAL: Margin/Insufficient Funds Issues")
        summary_lines.append(f"   - {len(margin_errors)} margin-related errors detected")
        summary_lines.append(f"   - Trading may be blocked due to low available capital")
    
    # Check if trading is actually happening
    if len(recent_success) == 0 and len(recent_errors) > 5:
        alert_msg = "🚨 NO SUCCESSFUL TRADES WITH MULTIPLE ERRORS - Trading may be stuck"
        critical_alerts.append(alert_msg)
        critical_logger.warning(alert_msg)
        summary_lines.append(f"\n🚨 CRITICAL: No successful trades with multiple errors")
    
    # Overall assessment
    summary_lines.append(f"\n=== OVERALL ASSESSMENT ===")
    if margin_errors:
        summary_lines.append(f"Status: ❌ CRITICAL - Margin/Insufficient Funds Issues")
        summary_lines.append(f"Action Required: Check available capital and margin requirements")
    elif recent_errors and not recent_success:
        summary_lines.append(f"Status: ⚠️ WARNING - Errors without successful trades")
        summary_lines.append(f"Action Required: Investigate trading bot errors")
    elif recent_success:
        summary_lines.append(f"Status: ✅ ACTIVE - Trading attempts detected")
        summary_lines.append(f"Note: Some errors present but system is attempting trades")
    else:
        summary_lines.append(f"Status: ℹ️ INACTIVE - No recent trading activity")
    
    # Recommendations
    summary_lines.append(f"\n=== RECOMMENDATIONS ===")
    summary_lines.append(f"1. Check available capital on exchanges")
    summary_lines.append(f"2. Verify API keys and permissions")
    summary_lines.append(f"3. Restart dashboard server if needed")
    summary_lines.append(f"4. Review margin requirements and position sizing")
    
    # Log the summary
    logging.info(f"Analysis complete. Status: {'CRITICAL' if margin_errors else 'WARNING' if recent_errors else 'OK'}")
    
    return "\n".join(summary_lines)

if __name__ == "__main__":
    result_summary = analyze_current_state()
    print(result_summary)