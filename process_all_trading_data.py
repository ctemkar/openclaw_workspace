#!/usr/bin/env python3
"""
Comprehensive trading data processing script.
Fetches data from all trading systems and generates a unified report.
"""

import json
import requests
import os
import subprocess
from datetime import datetime
import sys

def get_trading_server_status():
    """Get status from the main trading server."""
    try:
        response = requests.get("http://localhost:5001/status", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching trading server status: {e}")
        return None

def get_trading_server_trades():
    """Get trades from the main trading server."""
    try:
        response = requests.get("http://localhost:5001/trades", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching trading server trades: {e}")
        return None

def analyze_log_file(log_file, bot_name):
    """Analyze a log file for a specific bot."""
    if not os.path.exists(log_file):
        return {"status": "log_not_found", "bot": bot_name}
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            return {"status": "empty_log", "bot": bot_name}
        
        # Get last 20 lines
        last_lines = lines[-20:] if len(lines) > 20 else lines
        
        # Look for key patterns
        status = "unknown"
        last_activity = None
        errors = []
        trades_executed = 0
        balance_info = None
        
        for line in reversed(last_lines):
            line_lower = line.lower()
            
            # Extract timestamp
            if not last_activity and '2026-' in line:
                parts = line.split()
                for part in parts:
                    if '2026-' in part:
                        last_activity = part
                        break
            
            # Check for errors
            if 'error' in line_lower or 'failed' in line_lower:
                errors.append(line.strip())
            
            # Check for trade execution
            if 'trade' in line_lower and ('executed' in line_lower or 'placed' in line_lower):
                trades_executed += 1
            
            # Check for balance info
            if 'balance' in line_lower or 'usdt' in line.lower():
                balance_info = line.strip()
            
            # Determine status
            if 'running' in line_lower or 'cycle' in line_lower:
                status = "running"
            elif 'stopped' in line_lower or 'exited' in line_lower:
                status = "stopped"
            elif 'error' in line_lower:
                status = "error"
        
        return {
            "status": status,
            "bot": bot_name,
            "last_activity": last_activity,
            "errors_count": len(errors),
            "recent_errors": errors[:3],  # Last 3 errors
            "trades_executed": trades_executed,
            "balance_info": balance_info,
            "log_file": log_file,
            "log_size_kb": os.path.getsize(log_file) / 1024
        }
    
    except Exception as e:
        return {"status": "analysis_error", "bot": bot_name, "error": str(e)}

def check_bot_process(bot_name, process_keyword):
    """Check if a bot process is running."""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        lines = result.stdout.split('\n')
        process_count = 0
        
        for line in lines:
            if process_keyword in line and 'grep' not in line:
                process_count += 1
        
        return {
            "bot": bot_name,
            "running": process_count > 0,
            "process_count": process_count
        }
    
    except Exception as e:
        return {"bot": bot_name, "running": False, "error": str(e)}

def get_market_data():
    """Get current market prices."""
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd',
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "btc_usd": data.get('bitcoin', {}).get('usd'),
            "eth_usd": data.get('ethereum', {}).get('usd'),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None

def generate_comprehensive_report(all_data):
    """Generate a comprehensive trading report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    
    report = f"""
COMPREHENSIVE TRADING DATA PROCESSING REPORT
============================================
Generated: {timestamp}

SYSTEM OVERVIEW
---------------
"""
    
    # Trading server status
    server_status = all_data.get('trading_server_status', {})
    if server_status:
        report += f"Trading Server: {server_status.get('status', 'unknown')}\n"
        report += f"Capital: ${server_status.get('capital', 0):.2f}\n"
        report += f"Last Analysis: {server_status.get('last_analysis', 'unknown')}\n"
        report += f"Trading Pairs: {', '.join(server_status.get('trading_pairs', []))}\n"
    else:
        report += "Trading Server: UNAVAILABLE\n"
    
    # Market data
    market_data = all_data.get('market_data', {})
    if market_data:
        report += f"\nMARKET DATA\n"
        report += f"-----------\n"
        report += f"BTC/USD: ${market_data.get('btc_usd', 'N/A'):,.2f}\n" if isinstance(market_data.get('btc_usd'), (int, float)) else f"BTC/USD: {market_data.get('btc_usd', 'N/A')}\n"
        report += f"ETH/USD: ${market_data.get('eth_usd', 'N/A'):,.2f}\n" if isinstance(market_data.get('eth_usd'), (int, float)) else f"ETH/USD: {market_data.get('eth_usd', 'N/A')}\n"
    
    # Bot status
    report += f"\nTRADING BOTS STATUS\n"
    report += f"------------------\n"
    
    bots_status = all_data.get('bots_status', [])
    for bot in bots_status:
        report += f"{bot.get('bot', 'Unknown')}:\n"
        report += f"  • Status: {bot.get('status', 'unknown')}\n"
        report += f"  • Last Activity: {bot.get('last_activity', 'unknown')}\n"
        report += f"  • Trades Executed: {bot.get('trades_executed', 0)}\n"
        report += f"  • Errors: {bot.get('errors_count', 0)}\n"
        if bot.get('balance_info'):
            report += f"  • Balance: {bot.get('balance_info')}\n"
    
    # Process status
    report += f"\nPROCESS STATUS\n"
    report += f"--------------\n"
    
    processes = all_data.get('process_status', [])
    for proc in processes:
        status = "✅ RUNNING" if proc.get('running') else "❌ STOPPED"
        report += f"{proc.get('bot', 'Unknown')}: {status} ({proc.get('process_count', 0)} processes)\n"
    
    # Trading activity analysis
    report += f"\nTRADING ACTIVITY ANALYSIS\n"
    report += f"-------------------------\n"
    
    trades_data = all_data.get('trading_server_trades', {})
    if trades_data and 'trades' in trades_data:
        trades = trades_data['trades']
        total_trades = len(trades)
        
        if total_trades > 0:
            buy_count = sum(1 for t in trades if t.get('side', '').lower() == 'buy')
            sell_count = sum(1 for t in trades if t.get('side', '').lower() == 'sell')
            filled_count = sum(1 for t in trades if t.get('status', '').lower() == 'filled')
            
            report += f"Total Trades: {total_trades}\n"
            report += f"Buy Orders: {buy_count}\n"
            report += f"Sell Orders: {sell_count}\n"
            report += f"Filled Orders: {filled_count}\n"
            report += f"Pending Orders: {total_trades - filled_count}\n"
        else:
            report += "No trades recorded in trading server.\n"
    else:
        report += "Trading activity data unavailable.\n"
    
    # Issues and recommendations
    report += f"\nISSUES AND RECOMMENDATIONS\n"
    report += f"--------------------------\n"
    
    issues = []
    recommendations = []
    
    # Check for stopped bots
    stopped_bots = [p for p in processes if not p.get('running')]
    if stopped_bots:
        issues.append(f"{len(stopped_bots)} trading bot(s) not running")
        recommendations.append(f"Restart stopped bots: {', '.join([b.get('bot') for b in stopped_bots])}")
    
    # Check for bots with errors
    error_bots = [b for b in bots_status if b.get('errors_count', 0) > 0]
    if error_bots:
        issues.append(f"{len(error_bots)} bot(s) have errors")
        for bot in error_bots[:2]:  # Show first 2 bots with errors
            recommendations.append(f"Check {bot.get('bot')} for errors: {', '.join(bot.get('recent_errors', [])[:2])}")
    
    # Check trading server
    if not server_status:
        issues.append("Trading server unavailable")
        recommendations.append("Check if trading server is running on port 5001")
    
    # Check for no trading activity
    trades_data = all_data.get('trading_server_trades', {})
    if trades_data and 'trades' in trades_data:
        if len(trades_data['trades']) == 0:
            issues.append("No trading activity recorded")
            recommendations.append("Review trading strategy and market conditions")
    
    if issues:
        report += "ISSUES DETECTED:\n"
        for i, issue in enumerate(issues, 1):
            report += f"  {i}. {issue}\n"
        
        report += "\nRECOMMENDATIONS:\n"
        for i, rec in enumerate(recommendations, 1):
            report += f"  {i}. {rec}\n"
    else:
        report += "✅ All systems operational\n"
        report += "✅ Trading activity normal\n"
        recommendations.append("Continue monitoring - system healthy")
    
    # System health summary
    report += f"\nSYSTEM HEALTH SUMMARY\n"
    report += f"---------------------\n"
    
    total_bots = len(processes)
    running_bots = len([p for p in processes if p.get('running')])
    bots_with_errors = len(error_bots)
    
    report += f"Total Bots: {total_bots}\n"
    report += f"Running Bots: {running_bots}/{total_bots} ({running_bots/total_bots*100:.1f}%)\n"
    report += f"Bots with Errors: {bots_with_errors}\n"
    report += f"Trading Server: {'✅ ONLINE' if server_status else '❌ OFFLINE'}\n"
    report += f"Market Data: {'✅ AVAILABLE' if market_data else '❌ UNAVAILABLE'}\n"
    
    # Next actions
    report += f"\nNEXT ACTIONS\n"
    report += f"------------\n"
    report += f"1. Review this report for any issues\n"
    report += f"2. Check critical_alerts.log for urgent alerts\n"
    report += f"3. Monitor trading_monitoring.log for detailed analysis\n"
    report += f"4. Next scheduled check: In 1 hour\n"
    
    return report

def main():
    """Main function to process all trading data."""
    print("Processing all trading data...")
    
    all_data = {}
    
    # Get trading server data
    print("Fetching trading server status...")
    all_data['trading_server_status'] = get_trading_server_status()
    
    print("Fetching trading server trades...")
    all_data['trading_server_trades'] = get_trading_server_trades()
    
    # Get market data
    print("Fetching market data...")
    all_data['market_data'] = get_market_data()
    
    # Analyze bot logs
    print("Analyzing bot logs...")
    bots_to_check = [
        ("26 Crypto Bot", "26_crypto_live_trading.log"),
        ("Binance Futures Short Bot", "binance_futures_trading.log"),
        ("Fixed Futures Bot", "fixed_futures_trading.log"),
        ("Real Futures Bot", "real_futures_trading.log"),
        ("Real Trading Bot", "real_trading.log"),
    ]
    
    bots_status = []
    for bot_name, log_file in bots_to_check:
        print(f"  Analyzing {bot_name}...")
        status = analyze_log_file(log_file, bot_name)
        bots_status.append(status)
    
    all_data['bots_status'] = bots_status
    
    # Check bot processes
    print("Checking bot processes...")
    processes_to_check = [
        ("26 Crypto Bot", "improved_26_crypto_bot.py"),
        ("Binance Futures Short Bot", "binance_futures_short_bot.py"),
        ("Fixed Futures Bot", "fixed_futures_bot.py"),
        ("Real Futures Bot", "real_futures_trading_bot.py"),
        ("Trading Server", "trading_server.py"),
    ]
    
    process_status = []
    for bot_name, process_keyword in processes_to_check:
        print(f"  Checking {bot_name} process...")
        status = check_bot_process(bot_name, process_keyword)
        process_status.append(status)
    
    all_data['process_status'] = process_status
    
    # Generate report
    print("Generating comprehensive report...")
    report = generate_comprehensive_report(all_data)
    
    # Print report
    print(report)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comprehensive_trading_report_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to: {filename}")
    
    # Also save as latest report
    latest_filename = "latest_trading_analysis.txt"
    with open(latest_filename, 'w') as f:
        f.write(report)
    
    print(f"Latest analysis saved to: {latest_filename}")
    
    # Save data as JSON for programmatic access
    json_filename = f"trading_data_snapshot_{timestamp}.json"
    with open(json_filename, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"Data snapshot saved to: {json_filename}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())