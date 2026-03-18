#!/usr/bin/env python3
"""
Fetch and process trading data from the Conservative Crypto Trading System.
"""

import json
import requests
from datetime import datetime
import sys

BASE_URL = "http://localhost:5001"

def fetch_status():
    """Fetch system status."""
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching status: {e}")
        return None

def fetch_trades():
    """Fetch recent trades."""
    try:
        response = requests.get(f"{BASE_URL}/trades", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching trades: {e}")
        return None

def analyze_trades(trades_data):
    """Analyze trading data."""
    if not trades_data or 'trades' not in trades_data:
        return None
    
    trades = trades_data['trades']
    total_trades = len(trades)
    
    # Count buys and sells
    buy_count = 0
    sell_count = 0
    filled_trades = 0
    pending_trades = 0
    
    # Analyze by model/strategy
    model_stats = {}
    
    for trade in trades:
        side = trade.get('side', '').lower()
        if side == 'buy':
            buy_count += 1
        elif side == 'sell':
            sell_count += 1
        
        status = trade.get('status', '').lower()
        if status == 'filled':
            filled_trades += 1
        else:
            pending_trades += 1
        
        # Track model usage
        model = trade.get('model', 'unknown')
        if model not in model_stats:
            model_stats[model] = {'buy': 0, 'sell': 0, 'total': 0}
        
        model_stats[model]['total'] += 1
        if side == 'buy':
            model_stats[model]['buy'] += 1
        elif side == 'sell':
            model_stats[model]['sell'] += 1
    
    # Calculate percentages
    buy_percentage = (buy_count / total_trades * 100) if total_trades > 0 else 0
    sell_percentage = (sell_count / total_trades * 100) if total_trades > 0 else 0
    filled_percentage = (filled_trades / total_trades * 100) if total_trades > 0 else 0
    
    return {
        'total_trades': total_trades,
        'buy_count': buy_count,
        'sell_count': sell_count,
        'buy_percentage': buy_percentage,
        'sell_percentage': sell_percentage,
        'filled_trades': filled_trades,
        'pending_trades': pending_trades,
        'filled_percentage': filled_percentage,
        'model_stats': model_stats,
        'timestamp': trades_data.get('timestamp', datetime.now().isoformat())
    }

def generate_report(status_data, trade_analysis):
    """Generate a comprehensive trading report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    
    report = f"""
TRADING SYSTEM DATA REPORT
==========================
Generated: {timestamp}

SYSTEM STATUS
-------------
"""
    
    if status_data:
        report += f"Status: {status_data.get('status', 'unknown')}\n"
        report += f"Capital: ${status_data.get('capital', 0):.2f}\n"
        report += f"Last Analysis: {status_data.get('last_analysis', 'unknown')}\n"
        report += f"Analysis Schedule: {status_data.get('analysis_scheduled', 'unknown')}\n"
        report += f"Trading Pairs: {', '.join(status_data.get('trading_pairs', []))}\n"
        
        risk = status_data.get('risk_parameters', {})
        report += f"Risk Parameters:\n"
        report += f"  • Stop-loss: {risk.get('stop_loss', 0)*100:.1f}%\n"
        report += f"  • Take-profit: {risk.get('take_profit', 0)*100:.1f}%\n"
        report += f"  • Max trades/day: {risk.get('max_trades_per_day', 0)}\n"
    else:
        report += "Status: UNAVAILABLE\n"
    
    report += f"""
TRADING ACTIVITY
----------------
"""
    
    if trade_analysis:
        report += f"Total Trades: {trade_analysis['total_trades']}\n"
        report += f"Buy Trades: {trade_analysis['buy_count']} ({trade_analysis['buy_percentage']:.1f}%)\n"
        report += f"Sell Trades: {trade_analysis['sell_count']} ({trade_analysis['sell_percentage']:.1f}%)\n"
        report += f"Filled Trades: {trade_analysis['filled_trades']} ({trade_analysis['filled_percentage']:.1f}%)\n"
        report += f"Pending Trades: {trade_analysis['pending_trades']}\n"
        
        if trade_analysis['model_stats']:
            report += f"\nMODEL/STRATEGY BREAKDOWN\n"
            report += f"-----------------------\n"
            for model, stats in trade_analysis['model_stats'].items():
                report += f"{model}:\n"
                report += f"  • Total: {stats['total']}\n"
                report += f"  • Buys: {stats['buy']}\n"
                report += f"  • Sells: {stats['sell']}\n"
    else:
        report += "Trading Data: UNAVAILABLE\n"
    
    report += f"""
HEALTH ASSESSMENT
-----------------
"""
    
    # Health checks
    issues = []
    
    if status_data and status_data.get('status') != 'running':
        issues.append("System status is not 'running'")
    
    if trade_analysis:
        if trade_analysis['total_trades'] == 0:
            issues.append("No trades recorded")
        
        if trade_analysis['filled_percentage'] < 80 and trade_analysis['total_trades'] > 5:
            issues.append(f"Low fill rate ({trade_analysis['filled_percentage']:.1f}%)")
        
        if trade_analysis['buy_percentage'] > 80:
            issues.append(f"Heavy buy bias ({trade_analysis['buy_percentage']:.1f}%)")
        elif trade_analysis['sell_percentage'] > 80:
            issues.append(f"Heavy sell bias ({trade_analysis['sell_percentage']:.1f}%)")
    
    if issues:
        report += "ISSUES DETECTED:\n"
        for i, issue in enumerate(issues, 1):
            report += f"  {i}. {issue}\n"
    else:
        report += "✓ System appears healthy\n"
    
    report += f"""
RECOMMENDATIONS
---------------
"""
    
    recommendations = []
    
    if not status_data:
        recommendations.append("Check if trading server is running")
    
    if trade_analysis and trade_analysis['total_trades'] == 0:
        recommendations.append("Review trading strategy - no trades executed")
    
    if issues:
        recommendations.append("Address the issues listed above")
    else:
        recommendations.append("Continue monitoring - system operational")
    
    for i, rec in enumerate(recommendations, 1):
        report += f"{i}. {rec}\n"
    
    return report

def main():
    """Main function to fetch and process trading data."""
    print("Fetching trading data...")
    
    # Fetch data
    status_data = fetch_status()
    trades_data = fetch_trades()
    
    # Analyze trades
    trade_analysis = analyze_trades(trades_data) if trades_data else None
    
    # Generate report
    report = generate_report(status_data, trade_analysis)
    
    # Print report
    print(report)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trading_report_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to: {filename}")
    
    # Also update the summary endpoint file
    summary_file = "trading_summary_latest.txt"
    with open(summary_file, 'w') as f:
        f.write(report)
    
    print(f"Latest summary saved to: {summary_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())