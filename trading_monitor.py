#!/usr/bin/env python3
"""
Trading Dashboard Monitor
Monitors the trading system at http://localhost:5001/
Logs trading data and alerts on critical conditions
"""

import json
import requests
import time
from datetime import datetime
import sys
import os

# Configuration
DASHBOARD_URL = "http://localhost:5001"
MONITORING_LOG = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

def fetch_endpoint(endpoint):
    """Fetch data from a dashboard endpoint"""
    try:
        url = f"{DASHBOARD_URL}{endpoint}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            if endpoint == "/summary":
                return response.text
            else:
                return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def parse_trading_data():
    """Parse all trading data from the dashboard"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "status": None,
        "trades": None,
        "summary": None,
        "strategy": None,
        "alerts": []
    }
    
    # Fetch status
    status_data = fetch_endpoint("/status")
    if "error" not in status_data:
        data["status"] = status_data
    else:
        data["alerts"].append(f"Failed to fetch status: {status_data['error']}")
    
    # Fetch trades
    trades_data = fetch_endpoint("/trades")
    if "error" not in trades_data:
        data["trades"] = trades_data
    else:
        data["alerts"].append(f"Failed to fetch trades: {trades_data['error']}")
    
    # Fetch summary
    summary_data = fetch_endpoint("/summary")
    if not isinstance(summary_data, dict) or "error" not in summary_data:
        data["summary"] = summary_data
    else:
        data["alerts"].append(f"Failed to fetch summary: {summary_data.get('error', 'Unknown error')}")
    
    # Fetch strategy
    strategy_data = fetch_endpoint("/strategy")
    if "error" not in strategy_data:
        data["strategy"] = strategy_data
    else:
        # Strategy endpoint returns error when no strategy file exists, which is normal
        pass
    
    return data

def analyze_risk(data):
    """Analyze trading data for risk indicators"""
    alerts = []
    
    # Check if system is running
    if data.get("status") and data["status"].get("status") != "running":
        alerts.append(f"System status is {data['status'].get('status')}, expected 'running'")
    
    # Check capital
    if data.get("status") and data["status"].get("capital"):
        capital = data["status"]["capital"]
        if capital < 900:  # 10% drawdown from $1000
            alerts.append(f"Capital drawdown: ${capital:.2f} (below 90% of initial $1000)")
    
    # Analyze trades for stop-loss/take-profit triggers
    if data.get("trades") and "trades" in data["trades"]:
        trades = data["trades"]["trades"]
        if trades:
            # Check for recent trades
            latest_trade = trades[0]
            # In a real system, we would check current prices against entry prices
            # For now, just log trade activity
            if len(trades) > 8:  # High trade frequency
                alerts.append(f"High trade frequency: {len(trades)} trades in history")
    
    # Parse summary for alerts
    if data.get("summary"):
        summary = data["summary"]
        if "ALERT STATUS" in summary:
            alert_section = summary.split("ALERT STATUS")[1].split("RECOMMENDED ACTIONS")[0]
            if "critical alerts" in alert_section.lower() and "No new" not in alert_section:
                alerts.append("Critical alerts detected in summary")
    
    return alerts

def log_monitoring_data(data, risk_alerts):
    """Log monitoring data to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare log entry
    log_entry = f"\n{'='*60}\n"
    log_entry += f"MONITORING CHECK: {timestamp}\n"
    log_entry += f"{'='*60}\n"
    
    # System status
    if data.get("status"):
        status = data["status"]
        log_entry += f"System Status: {status.get('status', 'unknown')}\n"
        log_entry += f"Capital: ${status.get('capital', 0):.2f}\n"
        log_entry += f"Last Analysis: {status.get('last_analysis', 'unknown')}\n"
        log_entry += f"Trading Pairs: {', '.join(status.get('trading_pairs', []))}\n"
        
        risk_params = status.get('risk_parameters', {})
        log_entry += f"Risk Parameters:\n"
        log_entry += f"  Stop-loss: {risk_params.get('stop_loss', 0)*100:.1f}%\n"
        log_entry += f"  Take-profit: {risk_params.get('take_profit', 0)*100:.1f}%\n"
        log_entry += f"  Max trades/day: {risk_params.get('max_trades_per_day', 0)}\n"
    
    # Trade activity
    if data.get("trades") and "trades" in data["trades"]:
        trades = data["trades"]["trades"]
        log_entry += f"\nTrade Activity: {len(trades)} trades in history\n"
        if trades:
            log_entry += f"Latest trade: {trades[0].get('side', 'unknown')} {trades[0].get('symbol', trades[0].get('model', 'unknown'))} "
            log_entry += f"at ${trades[0].get('price', 0):.2f} ({trades[0].get('time', 'unknown')})\n"
    
    # Risk alerts
    if risk_alerts:
        log_entry += f"\nRISK ALERTS ({len(risk_alerts)}):\n"
        for i, alert in enumerate(risk_alerts, 1):
            log_entry += f"  {i}. {alert}\n"
    else:
        log_entry += f"\nNo risk alerts detected\n"
    
    # System alerts (connection issues, etc.)
    if data.get("alerts"):
        log_entry += f"\nSYSTEM ALERTS ({len(data['alerts'])}):\n"
        for i, alert in enumerate(data["alerts"], 1):
            log_entry += f"  {i}. {alert}\n"
    
    # Write to monitoring log
    with open(MONITORING_LOG, "a") as f:
        f.write(log_entry)
    
    # Write critical alerts to separate log
    critical_alerts = []
    for alert in risk_alerts:
        if any(keyword in alert.lower() for keyword in ["critical", "drawdown", "stop-loss", "take-profit", "failed"]):
            critical_alerts.append(alert)
    
    if critical_alerts:
        alert_entry = f"\n{'='*60}\n"
        alert_entry += f"CRITICAL ALERT: {timestamp}\n"
        alert_entry += f"{'='*60}\n"
        for i, alert in enumerate(critical_alerts, 1):
            alert_entry += f"{i}. {alert}\n"
        
        # Include relevant data
        if data.get("status"):
            alert_entry += f"\nSystem State:\n"
            alert_entry += f"  Capital: ${data['status'].get('capital', 0):.2f}\n"
            alert_entry += f"  Status: {data['status'].get('status', 'unknown')}\n"
        
        with open(CRITICAL_ALERTS_LOG, "a") as f:
            f.write(alert_entry)
        
        # Return True if critical alerts were logged
        return True
    
    return False

def main():
    """Main monitoring function"""
    print(f"Starting trading dashboard monitor at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Parse trading data
    data = parse_trading_data()
    
    # Analyze for risk
    risk_alerts = analyze_risk(data)
    
    # Log data
    has_critical_alerts = log_monitoring_data(data, risk_alerts)
    
    # Print summary
    print(f"Monitoring check completed")
    print(f"  System status: {data.get('status', {}).get('status', 'unknown')}")
    print(f"  Capital: ${data.get('status', {}).get('capital', 0):.2f}")
    print(f"  Trades in history: {len(data.get('trades', {}).get('trades', [])) if data.get('trades') else 0}")
    print(f"  Risk alerts: {len(risk_alerts)}")
    print(f"  Critical alerts logged: {'Yes' if has_critical_alerts else 'No'}")
    
    return has_critical_alerts

if __name__ == "__main__":
    try:
        critical = main()
        sys.exit(1 if critical else 0)
    except Exception as e:
        print(f"Error in monitoring: {e}")
        sys.exit(1)