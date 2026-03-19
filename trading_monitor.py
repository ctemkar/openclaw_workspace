#!/usr/bin/env python3
"""
Trading Dashboard Monitor
Fetches data from localhost:5001, parses trading data, and logs alerts.
"""

import json
import requests
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BASE_URL = "http://localhost:5001"
MONITORING_LOG = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

def fetch_endpoint(endpoint: str) -> Optional[Dict[str, Any]]:
    """Fetch data from an endpoint, handling both JSON and text responses."""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        response.raise_for_status()
        
        # Try to parse as JSON first
        try:
            return response.json()
        except json.JSONDecodeError:
            # Return as text if not JSON
            return {"text": response.text}
            
    except requests.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
        return None

def parse_summary_text(summary_text: str) -> Dict[str, Any]:
    """Parse the trading summary text into structured data."""
    data = {
        "capital": None,
        "stop_loss": None,
        "take_profit": None,
        "today_trades": None,
        "total_trades": None,
        "total_pnl": None,
        "available_capital": None,
        "signals": []
    }
    
    lines = summary_text.split('\n')
    for line in lines:
        line = line.strip()
        
        # Extract capital, stop-loss, take-profit
        if "Capital:" in line and "Stop-loss:" in line:
            parts = line.split('|')
            for part in parts:
                if "Capital:" in part:
                    try:
                        data["capital"] = float(part.split('$')[1].replace(',', ''))
                    except:
                        pass
                elif "Stop-loss:" in part:
                    try:
                        data["stop_loss"] = float(part.split(':')[1].replace('%', '').strip()) / 100
                    except:
                        pass
                elif "Take-profit:" in part:
                    try:
                        data["take_profit"] = float(part.split(':')[1].replace('%', '').strip()) / 100
                    except:
                        pass
        
        # Extract today's trades
        elif "Today's trades:" in line:
            try:
                parts = line.split(':')[1].strip()
                current, max_trades = parts.split('/')
                data["today_trades"] = int(current.strip())
            except:
                pass
        
        # Extract total trades and P&L
        elif "Total trades:" in line:
            try:
                data["total_trades"] = int(line.split(':')[1].strip())
            except:
                pass
        elif "Total P&L:" in line:
            try:
                data["total_pnl"] = float(line.split('$')[1].strip())
            except:
                pass
        elif "Available capital:" in line:
            try:
                data["available_capital"] = float(line.split('$')[1].strip())
            except:
                pass
        
        # Extract trading signals
        elif "Signal:" in line and "Confidence:" in line:
            try:
                symbol_line = lines[lines.index(line) - 2] if lines.index(line) > 1 else ""
                symbol = symbol_line.split()[1].replace('...', '') if '...' in symbol_line else ""
                signal = line.split('Signal:')[1].split('(')[0].strip()
                confidence = float(line.split('Confidence:')[1].replace('%)', '').strip())
                data["signals"].append({
                    "symbol": symbol,
                    "signal": signal,
                    "confidence": confidence
                })
            except:
                pass
    
    return data

def calculate_drawdown(current_value: float, peak_value: float) -> float:
    """Calculate drawdown percentage."""
    if peak_value <= 0:
        return 0
    return (peak_value - current_value) / peak_value * 100

def check_critical_conditions(status_data: Dict, summary_data: Dict, trades_data: Dict) -> List[str]:
    """Check for critical conditions requiring alerts."""
    alerts = []
    
    # Check if system is not running
    if status_data.get("status") != "running":
        alerts.append(f"⚠️ System status: {status_data.get('status')}")
    
    # Extract risk parameters
    risk_params = status_data.get("risk_parameters", {})
    stop_loss_pct = risk_params.get("stop_loss", 0.05) * 100  # Convert to percentage
    take_profit_pct = risk_params.get("take_profit", 0.10) * 100
    
    # Check capital
    capital = summary_data.get("capital")
    available_capital = summary_data.get("available_capital")
    
    if capital and available_capital:
        # Calculate drawdown from initial capital
        drawdown = calculate_drawdown(available_capital, capital)
        
        # Check for critical drawdown (more than half of stop-loss threshold)
        if drawdown > (stop_loss_pct / 2):
            alerts.append(f"⚠️ Significant drawdown: {drawdown:.2f}% (available: ${available_capital:.2f} of ${capital:.2f})")
        
        # Check if approaching stop-loss
        if drawdown > (stop_loss_pct * 0.8):  # 80% of stop-loss threshold
            alerts.append(f"🚨 Approaching stop-loss! Drawdown: {drawdown:.2f}% (stop-loss: {stop_loss_pct:.1f}%)")
        
        # Check if stop-loss triggered
        if drawdown >= stop_loss_pct:
            alerts.append(f"🔴 STOP-LOSS TRIGGERED! Drawdown: {drawdown:.2f}% (threshold: {stop_loss_pct:.1f}%)")
    
    # Check P&L for take-profit
    total_pnl = summary_data.get("total_pnl", 0)
    if total_pnl > 0:
        # Calculate return percentage
        return_pct = (total_pnl / capital * 100) if capital else 0
        
        # Check if approaching take-profit
        if return_pct > (take_profit_pct * 0.8):  # 80% of take-profit threshold
            alerts.append(f"📈 Approaching take-profit! Return: {return_pct:.2f}% (target: {take_profit_pct:.1f}%)")
        
        # Check if take-profit triggered
        if return_pct >= take_profit_pct:
            alerts.append(f"🟢 TAKE-PROFIT TRIGGERED! Return: {return_pct:.2f}% (target: {take_profit_pct:.1f}%)")
    
    # Check max trades per day
    max_trades = risk_params.get("max_trades_per_day", 2)
    today_trades = summary_data.get("today_trades", 0)
    
    if today_trades >= max_trades:
        alerts.append(f"📊 Max daily trades reached: {today_trades}/{max_trades}")
    
    # Check recent trades for any failed trades
    trades = trades_data.get("trades", [])
    failed_trades = [t for t in trades if t.get("status") == "failed"]
    if failed_trades:
        alerts.append(f"❌ {len(failed_trades)} failed trade(s) detected")
    
    return alerts

def log_data(timestamp: str, status_data: Dict, summary_data: Dict, trades_data: Dict):
    """Log extracted data to monitoring log."""
    log_entry = {
        "timestamp": timestamp,
        "status": status_data,
        "summary": summary_data,
        "trades_count": trades_data.get("count", 0),
        "recent_trades": trades_data.get("trades", [])[:3]  # Last 3 trades
    }
    
    with open(MONITORING_LOG, 'a') as f:
        f.write(json.dumps(log_entry, indent=2) + '\n')

def log_critical_alerts(timestamp: str, alerts: List[str]):
    """Log critical alerts to alerts log."""
    if not alerts:
        return
    
    alert_entry = {
        "timestamp": timestamp,
        "alerts": alerts
    }
    
    with open(CRITICAL_ALERTS_LOG, 'a') as f:
        f.write(json.dumps(alert_entry, indent=2) + '\n')
    
    # Also print alerts to stdout for cron delivery
    print(f"\n{'='*60}")
    print(f"TRADING ALERTS - {timestamp}")
    print('='*60)
    for alert in alerts:
        print(f"• {alert}")
    print('='*60)

def main():
    """Main monitoring function."""
    timestamp = datetime.now().isoformat()
    
    print(f"Starting trading dashboard monitor at {timestamp}")
    
    # Fetch data from all endpoints
    print("Fetching data from endpoints...")
    status_data = fetch_endpoint("/status")
    summary_response = fetch_endpoint("/summary")
    trades_data = fetch_endpoint("/trades")
    
    if not all([status_data, summary_response, trades_data]):
        print("Error: Failed to fetch data from one or more endpoints")
        sys.exit(1)
    
    # Parse summary data
    summary_text = summary_response.get("text", "") if isinstance(summary_response, dict) and "text" in summary_response else ""
    summary_data = parse_summary_text(summary_text)
    
    # Log extracted data
    print("Logging extracted data...")
    log_data(timestamp, status_data, summary_data, trades_data)
    
    # Check for critical conditions
    print("Checking for critical conditions...")
    alerts = check_critical_conditions(status_data, summary_data, trades_data)
    
    # Log critical alerts
    if alerts:
        print(f"Found {len(alerts)} critical condition(s)")
        log_critical_alerts(timestamp, alerts)
    else:
        print("No critical conditions detected")
    
    # Print summary for cron delivery
    print(f"\nMonitoring complete at {timestamp}")
    print(f"Status: {status_data.get('status', 'unknown')}")
    print(f"Capital: ${summary_data.get('capital', 0):.2f}")
    print(f"Available: ${summary_data.get('available_capital', 0):.2f}")
    print(f"Today's trades: {summary_data.get('today_trades', 0)}")
    print(f"Total P&L: ${summary_data.get('total_pnl', 0):.2f}")
    
    if alerts:
        return 1  # Non-zero exit code if alerts were found
    
    return 0

if __name__ == "__main__":
    sys.exit(main())