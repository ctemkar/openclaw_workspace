import json
import requests
from datetime import datetime
import sys

def fetch_data():
    """Fetch data from trading dashboard"""
    try:
        # Fetch status
        status_response = requests.get('http://localhost:5001/status', timeout=10)
        status = status_response.json()
        
        # Fetch trades
        trades_response = requests.get('http://localhost:5001/trades', timeout=10)
        trades = trades_response.json()
        
        return status, trades
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None

def analyze_trading(status, trades):
    """Analyze trading data for risks and alerts"""
    if not status or not trades:
        return "Failed to fetch trading data"
    
    report = []
    report.append("=== TRADING DASHBOARD MONITORING REPORT ===")
    report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Capital: ${status['capital']:.2f}")
    report.append(f"Open Positions: {status['pnl']['total']['open_positions']}")
    report.append(f"Total P&L: ${status['pnl']['total']['total']:.4f}")
    report.append(f"Unrealized P&L: ${status['pnl']['total']['unrealized']:.4f}")
    report.append(f"Realized P&L: ${status['pnl']['total']['realized']:.4f}")
    
    report.append("\n=== RISK PARAMETERS ===")
    report.append(f"Stop-loss: {status['risk_parameters']['stop_loss']*100}%")
    report.append(f"Take-profit: {status['risk_parameters']['take_profit']*100}%")
    report.append(f"Max trades/day: {status['risk_parameters']['max_trades_per_day']}")
    
    report.append("\n=== TRADING ACTIVITY ===")
    report.append(f"Total trades recorded: {trades['count']}")
    report.append("Recent trades:")
    for i, trade in enumerate(trades['trades'][:5], 1):
        report.append(f"{i}. {trade['symbol']} - {trade['side']} @ ${trade['price']:.2f} ({trade['time']})")
    
    report.append("\n=== RISK ANALYSIS ===")
    # Calculate drawdown
    initial_capital = 250.00
    current_capital = status['capital']
    drawdown = ((initial_capital - current_capital) / initial_capital) * 100
    
    report.append(f"Initial Capital: ${initial_capital:.2f}")
    report.append(f"Current Capital: ${current_capital:.2f}")
    report.append(f"Capital Drawdown: {drawdown:.2f}%")
    
    # Check Binance performance
    binance_pnl = status['pnl']['binance']['total']
    gemini_pnl = status['pnl']['gemini']['total']
    report.append(f"Binance P&L: ${binance_pnl:.4f}")
    report.append(f"Gemini P&L: ${gemini_pnl:.4f}")
    
    report.append("\n=== ALERT STATUS ===")
    alerts = []
    
    # Capital drawdown alerts
    if drawdown > 10:
        alerts.append("🚨 CRITICAL: Capital drawdown > 10%!")
    elif drawdown > 5:
        alerts.append("⚠️  WARNING: Capital drawdown > 5%")
    else:
        alerts.append("✅ Capital drawdown within acceptable range (<5%)")
    
    # Check if system is actively trading
    if status['pnl']['total']['open_positions'] == 0:
        alerts.append("ℹ️  No open positions - system may be waiting for signals")
    
    # Check last analysis time
    last_analysis = datetime.fromisoformat(status['last_analysis'].replace('Z', '+00:00'))
    time_since_analysis = (datetime.now() - last_analysis).total_seconds() / 3600
    if time_since_analysis > 2:
        alerts.append(f"⚠️  Last analysis was {time_since_analysis:.1f} hours ago")
    
    for alert in alerts:
        report.append(alert)
    
    report.append("\n=== RECOMMENDATIONS ===")
    if drawdown > 5:
        report.append("1. Consider reducing position sizes or pausing trading")
        report.append("2. Review stop-loss levels - consider tightening to 3-4%")
    else:
        report.append("1. Continue current strategy with monitoring")
    
    report.append("2. Ensure real-time price monitoring for SL/TP triggers")
    report.append("3. Review trade frequency and success rate")
    
    return "\n".join(report)

def log_to_file(report, log_file, alert_file):
    """Log report to files"""
    try:
        # Log to monitoring log
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Monitoring Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
            f.write(report + "\n")
        
        # Check for critical alerts and log to alert file
        if "CRITICAL" in report or "drawdown > 10%" in report:
            with open(alert_file, 'a') as f:
                f.write(f"\n{'!'*60}\n")
                f.write(f"CRITICAL ALERT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'!'*60}\n")
                f.write(report + "\n")
            return True
        return False
    except Exception as e:
        print(f"Error logging to file: {e}")
        return False

def main():
    # File paths
    monitoring_log = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
    alert_log = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
    
    # Fetch and analyze data
    status, trades = fetch_data()
    report = analyze_trading(status, trades)
    
    # Print report
    print(report)
    
    # Log to files
    has_critical = log_to_file(report, monitoring_log, alert_log)
    
    if has_critical:
        print("\n⚠️  Critical alert logged to critical_alerts.log")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())