#!/usr/bin/env python3
"""
Generate real trading reports from trading data.
"""

import json
import requests
from datetime import datetime
import os
import sys

BASE_URL = "http://localhost:5001"
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

def fetch_trading_data():
    """Fetch all trading data from the API."""
    endpoints = {
        'status': '/status',
        'trades': '/trades',
        'positions': '/positions',
        'capital': '/capital'
    }
    
    data = {}
    for name, endpoint in endpoints.items():
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                data[name] = response.json()
            else:
                data[name] = {"error": f"Failed to fetch {endpoint}"}
        except Exception as e:
            data[name] = {"error": str(e)}
    
    return data

def load_json_file(filename):
    """Load JSON data from a file."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    return {}

def generate_report(trading_data, history_data, real_trading_state):
    """Generate a comprehensive trading report."""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_filename = f"{REPORTS_DIR}/trading_report_{timestamp}.txt"
    
    status = trading_data.get('status', {})
    trades = trading_data.get('trades', {})
    positions = trading_data.get('positions', {})
    capital = trading_data.get('capital', {})
    
    # Calculate statistics
    total_trades = 0
    open_trades = 0
    closed_trades = 0
    total_pnl = 0.0
    
    if 'trades' in trades:
        total_trades = len(trades['trades'])
        open_trades = sum(1 for t in trades['trades'] if t.get('status') == 'OPEN')
        closed_trades = total_trades - open_trades
    
    # Read trading history
    daily_trades = history_data.get('daily_trades', {})
    history_total_trades = history_data.get('total_trades', 0)
    history_capital = history_data.get('capital', 0)
    
    # Generate report content
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append(f"TRADING REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 60)
    report_lines.append("")
    
    # System Status
    report_lines.append("SYSTEM STATUS")
    report_lines.append("-" * 40)
    report_lines.append(f"Status: {status.get('status', 'Unknown')}")
    report_lines.append(f"Last Analysis: {status.get('last_analysis', 'N/A')}")
    report_lines.append(f"Capital: ${status.get('capital', 0):.2f}")
    report_lines.append(f"Trading Pairs: {', '.join(status.get('trading_pairs', []))}")
    report_lines.append("")
    
    # Risk Parameters
    risk_params = status.get('risk_parameters', {})
    report_lines.append("RISK PARAMETERS")
    report_lines.append("-" * 40)
    report_lines.append(f"Stop Loss: {risk_params.get('stop_loss', 0)*100:.1f}%")
    report_lines.append(f"Take Profit: {risk_params.get('take_profit', 0)*100:.1f}%")
    report_lines.append(f"Max Trades/Day: {risk_params.get('max_trades_per_day', 0)}")
    report_lines.append("")
    
    # Trading Statistics
    report_lines.append("TRADING STATISTICS")
    report_lines.append("-" * 40)
    report_lines.append(f"Total Trades (Current): {total_trades}")
    report_lines.append(f"Open Trades: {open_trades}")
    report_lines.append(f"Closed Trades: {closed_trades}")
    report_lines.append(f"Total Trades (History): {history_total_trades}")
    report_lines.append(f"Historical Capital: ${history_capital:.2f}")
    report_lines.append("")
    
    # Daily Trades Summary
    report_lines.append("DAILY TRADES SUMMARY")
    report_lines.append("-" * 40)
    for date, trades_list in daily_trades.items():
        report_lines.append(f"{date}: {len(trades_list)} trades")
        for trade in trades_list:
            symbol = trade.get('symbol', 'Unknown')
            side = trade.get('side', 'Unknown')
            price = trade.get('entry_price', 0)
            status = trade.get('status', 'Unknown')
            report_lines.append(f"  - {symbol} {side} @ ${price:.2f} ({status})")
    report_lines.append("")
    
    # Real Trading State
    report_lines.append("REAL TRADING STATE")
    report_lines.append("-" * 40)
    if real_trading_state:
        for key, value in real_trading_state.items():
            report_lines.append(f"{key}: {value}")
    else:
        report_lines.append("No real trading state data available")
    report_lines.append("")
    
    # Recommendations
    report_lines.append("RECOMMENDATIONS")
    report_lines.append("-" * 40)
    if open_trades > 0:
        report_lines.append("✓ Monitor open positions for stop-loss/take-profit triggers")
    else:
        report_lines.append("✓ No open positions - system ready for new trades")
    
    if total_trades < risk_params.get('max_trades_per_day', 2):
        report_lines.append(f"✓ Can execute {risk_params.get('max_trades_per_day', 2) - total_trades} more trades today")
    
    report_lines.append("✓ Ensure stop-loss orders are in place for all open positions")
    report_lines.append("")
    
    report_lines.append("=" * 60)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 60)
    
    # Write report to file
    report_content = "\n".join(report_lines)
    with open(report_filename, 'w') as f:
        f.write(report_content)
    
    # Also update latest summary
    with open(f"{REPORTS_DIR}/trading_summary_latest.txt", 'w') as f:
        f.write(report_content)
    
    return report_filename, report_content

def update_dashboard():
    """Update dashboard with fresh data."""
    try:
        # Create a simple dashboard update
        dashboard_file = "dashboard_status.json"
        dashboard_data = {
            "last_updated": datetime.now().isoformat(),
            "status": "active",
            "report_generated": True,
            "next_update": "hourly"
        }
        
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        print(f"Dashboard updated: {dashboard_file}")
        return True
    except Exception as e:
        print(f"Error updating dashboard: {e}")
        return False

def main():
    print("Generating real trading reports...")
    
    # Fetch trading data
    print("Fetching trading data from API...")
    trading_data = fetch_trading_data()
    
    # Load historical data
    print("Loading trading history...")
    history_data = load_json_file("trading_history.json")
    
    # Load real trading state (if exists)
    print("Loading real trading state...")
    real_trading_state = {}
    
    # Try to load real_trading_state.json
    if os.path.exists("real_trading_state.json"):
        real_trading_state = load_json_file("real_trading_state.json")
    elif os.path.exists("trading_state.json"):
        real_trading_state = load_json_file("trading_state.json")
    
    # Generate report
    print("Generating report...")
    report_file, report_content = generate_report(trading_data, history_data, real_trading_state)
    
    # Update dashboard
    print("Updating dashboard...")
    dashboard_updated = update_dashboard()
    
    # Print summary
    print("\n" + "=" * 60)
    print("REPORT GENERATION COMPLETE")
    print("=" * 60)
    print(f"Report saved to: {report_file}")
    print(f"Dashboard updated: {dashboard_updated}")
    print(f"Report size: {len(report_content)} characters")
    print("=" * 60)
    
    # Print first few lines of report
    print("\nReport preview:")
    print("-" * 40)
    lines = report_content.split('\n')[:15]
    for line in lines:
        print(line)

if __name__ == "__main__":
    main()