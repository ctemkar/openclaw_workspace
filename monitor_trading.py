#!/usr/bin/env python3
import json
import requests
import time
from datetime import datetime
import re

# Configuration
BASE_URL = "http://localhost:5001"
GENERAL_LOG = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_LOG = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

def fetch_data(endpoint):
    """Fetch data from an endpoint"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"ERROR: {str(e)}"

def parse_summary(summary_text):
    """Parse the summary text to extract key metrics"""
    metrics = {}
    
    # Extract P&L
    pnl_match = re.search(r'Total P&L:\s*\$([\d\.\-]+)', summary_text)
    if pnl_match:
        metrics['pnl'] = float(pnl_match.group(1))
    
    # Extract available capital
    capital_match = re.search(r'Available capital:\s*\$([\d\.]+)', summary_text)
    if capital_match:
        metrics['available_capital'] = float(capital_match.group(1))
    
    # Extract today's trades
    trades_match = re.search(r"Today's trades:\s*(\d+)/(\d+)", summary_text)
    if trades_match:
        metrics['trades_today'] = int(trades_match.group(1))
        metrics['max_trades_today'] = int(trades_match.group(2))
    
    # Extract total trades
    total_trades_match = re.search(r'Total trades:\s*(\d+)', summary_text)
    if total_trades_match:
        metrics['total_trades'] = int(total_trades_match.group(1))
    
    # Check for stop-loss/take-profit triggers in the text
    metrics['stop_loss_triggered'] = 'STOP-LOSS' in summary_text.upper()
    metrics['take_profit_triggered'] = 'TAKE-PROFIT' in summary_text.upper() or 'PROFIT TAKEN' in summary_text.upper()
    
    # Check for drawdown warnings
    metrics['drawdown_warning'] = 'DRAWDOWN' in summary_text.upper() or 'LOSS' in summary_text.upper()
    
    return metrics

def check_critical_conditions(metrics, status_data):
    """Check for critical trading conditions"""
    alerts = []
    
    # Check if P&L is negative beyond a threshold (e.g., -5% of capital)
    if 'pnl' in metrics and 'available_capital' in metrics:
        initial_capital = 1000.0  # From configuration
        current_total = metrics['available_capital'] + abs(min(metrics['pnl'], 0))
        drawdown_percent = ((initial_capital - current_total) / initial_capital) * 100
        
        if drawdown_percent >= 5:  # 5% drawdown threshold
            alerts.append(f"Critical drawdown detected: {drawdown_percent:.1f}%")
    
    # Check for stop-loss triggers
    if metrics.get('stop_loss_triggered'):
        alerts.append("Stop-loss order triggered")
    
    # Check for take-profit triggers
    if metrics.get('take_profit_triggered'):
        alerts.append("Take-profit order triggered")
    
    # Check if system is not running
    if status_data and 'status' in status_data and status_data['status'] != 'running':
        alerts.append(f"System status: {status_data['status']}")
    
    return alerts

def log_general_data(timestamp, status_data, summary_text, metrics):
    """Log general data to the monitoring log"""
    log_entry = {
        'timestamp': timestamp,
        'status': status_data if isinstance(status_data, dict) else {'raw': status_data},
        'summary_metrics': metrics,
        'summary_preview': summary_text[:500] + "..." if len(summary_text) > 500 else summary_text
    }
    
    with open(GENERAL_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def log_critical_alerts(timestamp, alerts):
    """Log critical alerts to the alerts log"""
    if alerts:
        with open(CRITICAL_LOG, 'a') as f:
            for alert in alerts:
                alert_entry = {
                    'timestamp': timestamp,
                    'alert': alert,
                    'type': 'CRITICAL'
                }
                f.write(json.dumps(alert_entry) + '\n')

def main():
    timestamp = datetime.now().isoformat()
    
    # Fetch data
    print(f"[{timestamp}] Monitoring trading dashboard...")
    
    status_text = fetch_data('/status')
    summary_text = fetch_data('/summary')
    
    # Parse JSON status
    status_data = {}
    if status_text and not status_text.startswith('ERROR'):
        try:
            status_data = json.loads(status_text)
        except:
            status_data = {'raw': status_text}
    
    # Parse summary for metrics
    metrics = parse_summary(summary_text)
    
    # Log general data
    log_general_data(timestamp, status_data, summary_text, metrics)
    
    # Check for critical conditions
    alerts = check_critical_conditions(metrics, status_data)
    
    # Log critical alerts
    log_critical_alerts(timestamp, alerts)
    
    # Generate summary
    summary_lines = []
    summary_lines.append(f"Trading Dashboard Monitor - {timestamp}")
    summary_lines.append("=" * 50)
    
    if status_data and isinstance(status_data, dict):
        summary_lines.append(f"Status: {status_data.get('status', 'unknown')}")
        summary_lines.append(f"Capital: ${status_data.get('capital', 0):.2f}")
        if 'risk_parameters' in status_data:
            rp = status_data['risk_parameters']
            summary_lines.append(f"Stop-loss: {rp.get('stop_loss', 0)*100:.1f}%")
            summary_lines.append(f"Take-profit: {rp.get('take_profit', 0)*100:.1f}%")
    
    summary_lines.append("")
    summary_lines.append("Metrics from summary:")
    for key, value in metrics.items():
        if key not in ['stop_loss_triggered', 'take_profit_triggered', 'drawdown_warning']:
            summary_lines.append(f"  {key}: {value}")
    
    summary_lines.append("")
    if alerts:
        summary_lines.append("⚠️ CRITICAL ALERTS:")
        for alert in alerts:
            summary_lines.append(f"  • {alert}")
    else:
        summary_lines.append("✅ No critical alerts detected.")
    
    summary = '\n'.join(summary_lines)
    print(summary)
    
    # Write summary to a file for cron job to read
    summary_file = "/tmp/trading_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(summary)
    
    return summary

if __name__ == "__main__":
    main()