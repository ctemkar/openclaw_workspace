#!/usr/bin/env python3
"""
Trading Dashboard Monitor
Fetches data from http://localhost:5001/, logs to monitoring log,
detects critical conditions, and saves alerts.
"""

import json
import requests
import datetime
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5001"
MONITORING_LOG = Path("/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log")
CRITICAL_ALERTS_LOG = Path("/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log")

def fetch_data(endpoint):
    """Fetch JSON data from an endpoint."""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {endpoint}: {e}")
        return None

def fetch_summary():
    """Fetch the summary endpoint (returns HTML/text)."""
    try:
        response = requests.get(f"{BASE_URL}/summary", timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching summary: {e}")
        return None

def parse_trading_data():
    """Fetch and parse all trading data."""
    timestamp = datetime.datetime.now().isoformat()
    
    # Fetch status data
    status_data = fetch_data("/status")
    if not status_data:
        return None
    
    # Fetch trades data
    trades_data = fetch_data("/trades")
    
    # Fetch summary data
    summary_text = fetch_summary()
    
    # Extract risk parameters
    risk_params = status_data.get("risk_parameters", {})
    capital = status_data.get("capital", 0)
    stop_loss = risk_params.get("stop_loss", 0) * 100  # Convert to percentage
    take_profit = risk_params.get("take_profit", 0) * 100  # Convert to percentage
    
    # Parse trades for analysis
    trades = trades_data.get("trades", []) if trades_data else []
    total_trades = len(trades)
    
    # Calculate potential drawdown (simplified - would need actual P&L data)
    # For now, we'll check if there are any recent losses
    recent_losses = 0
    for trade in trades[:5]:  # Check last 5 trades
        # In a real system, we'd check actual P&L
        # For now, we'll just count trades
        pass
    
    # Check for critical conditions
    critical_conditions = []
    
    # Check if max daily trades reached (potential overtrading)
    max_trades_per_day = risk_params.get("max_trades_per_day", 2)
    if total_trades >= max_trades_per_day:
        critical_conditions.append(f"Max daily trades ({max_trades_per_day}) reached or exceeded")
    
    # Check if capital is below certain threshold (e.g., 80% of initial)
    initial_capital = 1000  # Assuming initial capital
    if capital < initial_capital * 0.8:
        critical_conditions.append(f"Capital below 80% of initial: ${capital:.2f}")
    
    # Check if system is not running
    if status_data.get("status") != "running":
        critical_conditions.append(f"System status: {status_data.get('status')}")
    
    # Prepare monitoring data
    monitoring_data = {
        "timestamp": timestamp,
        "status": status_data.get("status"),
        "capital": capital,
        "risk_parameters": risk_params,
        "total_trades": total_trades,
        "recent_trades_count": len(trades[:5]),
        "last_analysis": status_data.get("last_analysis"),
        "critical_conditions": critical_conditions,
        "trading_pairs": status_data.get("trading_pairs", [])
    }
    
    return monitoring_data, critical_conditions, summary_text

def log_monitoring_data(data):
    """Log monitoring data to file."""
    try:
        with open(MONITORING_LOG, "a") as f:
            f.write(json.dumps(data, indent=2) + "\n---\n")
        print(f"Logged monitoring data to {MONITORING_LOG}")
    except Exception as e:
        print(f"Error logging monitoring data: {e}")

def log_critical_alerts(critical_conditions, monitoring_data):
    """Log critical alerts to file."""
    if not critical_conditions:
        return
    
    alert_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "critical_conditions": critical_conditions,
        "monitoring_data": monitoring_data
    }
    
    try:
        with open(CRITICAL_ALERTS_LOG, "a") as f:
            f.write(json.dumps(alert_data, indent=2) + "\n---\n")
        print(f"Logged critical alerts to {CRITICAL_ALERTS_LOG}")
    except Exception as e:
        print(f"Error logging critical alerts: {e}")

def generate_summary(monitoring_data, critical_conditions, summary_text):
    """Generate a plain text summary."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary = f"TRADING MONITORING SUMMARY - {timestamp}\n"
    summary += "=" * 50 + "\n\n"
    
    # System status
    summary += f"System Status: {monitoring_data.get('status', 'unknown')}\n"
    summary += f"Capital: ${monitoring_data.get('capital', 0):.2f}\n"
    summary += f"Total Trades: {monitoring_data.get('total_trades', 0)}\n"
    summary += f"Trading Pairs: {', '.join(monitoring_data.get('trading_pairs', []))}\n\n"
    
    # Risk parameters
    risk_params = monitoring_data.get('risk_parameters', {})
    summary += "Risk Parameters:\n"
    summary += f"  Stop-loss: {risk_params.get('stop_loss', 0) * 100:.1f}%\n"
    summary += f"  Take-profit: {risk_params.get('take_profit', 0) * 100:.1f}%\n"
    summary += f"  Max trades/day: {risk_params.get('max_trades_per_day', 2)}\n\n"
    
    # Last analysis
    last_analysis = monitoring_data.get('last_analysis', 'N/A')
    summary += f"Last Analysis: {last_analysis}\n\n"
    
    # Critical conditions
    if critical_conditions:
        summary += "⚠️  CRITICAL ALERTS:\n"
        for condition in critical_conditions:
            summary += f"  • {condition}\n"
        summary += "\n"
    else:
        summary += "✅ No critical conditions detected\n\n"
    
    # Recent activity
    summary += f"Recent Trades (last 5): {monitoring_data.get('recent_trades_count', 0)}\n"
    
    # Add summary snippet if available
    if summary_text:
        # Extract key lines from summary
        lines = summary_text.split('\n')
        key_lines = [line for line in lines if any(keyword in line for keyword in 
                   ['Today\'s trades:', 'Total P&L:', 'Available capital:', 'Signal:'])]
        if key_lines:
            summary += "\nLatest Analysis Highlights:\n"
            for line in key_lines[:5]:  # Limit to 5 key lines
                summary += f"  {line.strip()}\n"
    
    summary += "\n" + "=" * 50 + "\n"
    
    return summary

def main():
    """Main monitoring function."""
    print("Starting trading dashboard monitor...")
    
    # Parse trading data
    result = parse_trading_data()
    if not result:
        print("Failed to parse trading data")
        return
    
    monitoring_data, critical_conditions, summary_text = result
    
    # Log monitoring data
    log_monitoring_data(monitoring_data)
    
    # Log critical alerts if any
    log_critical_alerts(critical_conditions, monitoring_data)
    
    # Generate and print summary
    summary = generate_summary(monitoring_data, critical_conditions, summary_text)
    print(summary)
    
    # Also write summary to stdout for cron delivery
    sys.stdout.write(summary)

if __name__ == "__main__":
    main()