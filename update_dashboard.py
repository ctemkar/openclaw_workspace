#!/usr/bin/env python3
"""
Update dashboard with latest trading data.
"""

import json
import os
from datetime import datetime

def update_dashboard():
    """Update dashboard with latest data."""
    
    # Read latest report
    reports_dir = "reports"
    latest_report = None
    
    if os.path.exists(reports_dir):
        report_files = [f for f in os.listdir(reports_dir) if f.startswith("trading_report_")]
        if report_files:
            latest_report = sorted(report_files)[-1]
    
    # Read trading state
    trading_state = {}
    if os.path.exists("trading_state.json"):
        with open("trading_state.json", "r") as f:
            trading_state = json.load(f)
    
    # Read real trading state
    real_trading_state = {}
    if os.path.exists("real_trading_state.json"):
        with open("real_trading_state.json", "r") as f:
            real_trading_state = json.load(f)
    
    # Create dashboard data
    dashboard_data = {
        "last_updated": datetime.now().isoformat(),
        "status": "active",
        "report_available": latest_report is not None,
        "latest_report": latest_report,
        "trading_state": {
            "system_status": trading_state.get("system_status", "unknown"),
            "capital": trading_state.get("capital", 0),
            "open_positions": trading_state.get("open_positions", 0),
            "total_trades": trading_state.get("total_trades", 0)
        },
        "real_trading": {
            "enabled": real_trading_state.get("real_trading_enabled", False),
            "exchange_connections": real_trading_state.get("exchange_connections", {}),
            "capital_allocation": real_trading_state.get("capital_allocation", {}),
            "current_positions": len(real_trading_state.get("current_positions", []))
        },
        "next_update": "hourly",
        "alerts": []
    }
    
    # Add alerts if needed
    if trading_state.get("open_positions", 0) == 0:
        dashboard_data["alerts"].append("No open positions - ready for new trades")
    
    if real_trading_state.get("real_trading_enabled", False):
        dashboard_data["alerts"].append("Real trading mode is enabled")
    
    # Write dashboard data
    with open("dashboard_latest.json", "w") as f:
        json.dump(dashboard_data, f, indent=2)
    
    # Also update dashboard_status.json
    with open("dashboard_status.json", "w") as f:
        status_data = {
            "last_updated": datetime.now().isoformat(),
            "status": "active",
            "report_generated": True,
            "next_update": "hourly"
        }
        json.dump(status_data, f, indent=2)
    
    print(f"Dashboard updated at {dashboard_data['last_updated']}")
    print(f"Latest report: {latest_report}")
    print(f"Trading state: {dashboard_data['trading_state']['system_status']}")
    print(f"Real trading enabled: {dashboard_data['real_trading']['enabled']}")
    print(f"Open positions: {dashboard_data['real_trading']['current_positions']}")
    
    return dashboard_data

if __name__ == "__main__":
    update_dashboard()