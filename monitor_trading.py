#!/usr/bin/env python3
import os
import json
import logging
from datetime import datetime, timedelta
import requests

# Setup logging
LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERT_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

# Configure main logger
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configure critical alert logger
critical_alert_logger = logging.getLogger('critical_alert_logger')
critical_alert_logger.setLevel(logging.CRITICAL)
critical_alert_handler = logging.FileHandler(CRITICAL_ALERT_LOG_FILE)
critical_alert_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
critical_alert_logger.addHandler(critical_alert_handler)

def load_json_file(filepath):
    """Load JSON file safely."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load {filepath}: {e}")
        return None

def analyze_trading_status():
    """Analyze trading status from status files."""
    summary = []
    
    # Check trading status
    status = load_json_file("./status/trading_status.json")
    if status:
        summary.append(f"Trading Status: {status.get('trading_status', 'unknown')}")
        summary.append(f"Is Running: {status.get('is_running', False)}")
        
        if status.get('trading_status') == 'error':
            error_msg = status.get('error_message', 'Unknown error')
            alert = f"CRITICAL: Trading bot error - {error_msg}"
            summary.append(f"ERROR: {error_msg}")
            critical_alert_logger.critical(alert)
        
        # Check last heartbeat
        last_heartbeat = status.get('last_heartbeat')
        if last_heartbeat:
            try:
                heartbeat_time = datetime.fromisoformat(last_heartbeat.replace('Z', '+00:00'))
                time_diff = datetime.now() - heartbeat_time
                if time_diff > timedelta(minutes=5):
                    alert = f"CRITICAL: Trading bot heartbeat stale ({time_diff.total_seconds()/60:.1f} minutes)"
                    summary.append(f"WARNING: Stale heartbeat ({time_diff.total_seconds()/60:.1f} minutes)")
                    critical_alert_logger.critical(alert)
            except Exception as e:
                logging.error(f"Error parsing heartbeat time: {e}")
    
    return summary

def analyze_trades():
    """Analyze completed trades."""
    summary = []
    
    trades = load_json_file("./completed_trades.json")
    if trades:
        total_trades = len(trades)
        buy_trades = sum(1 for t in trades if t.get('side') == 'buy')
        sell_trades = sum(1 for t in trades if t.get('side') == 'sell')
        
        summary.append(f"Total Completed Trades: {total_trades}")
        summary.append(f"Buy Trades: {buy_trades}, Sell Trades: {sell_trades}")
        
        # Check for recent trades
        recent_trades = []
        for trade in trades:
            if 'time' in trade:
                # Simple time check - if trade time looks recent
                try:
                    trade_time = datetime.strptime(trade['time'], "%H:%M:%S")
                    now = datetime.now()
                    # Assume today's trades
                    trade_datetime = datetime.combine(now.date(), trade_time.time())
                    if (now - trade_datetime) < timedelta(hours=24):
                        recent_trades.append(trade)
                except:
                    pass
        
        summary.append(f"Recent Trades (last 24h): {len(recent_trades)}")
        
        if len(recent_trades) == 0:
            summary.append("WARNING: No recent trades detected")
    
    return summary

def analyze_config():
    """Analyze trading configuration."""
    summary = []
    
    config = load_json_file("./trading_config.json")
    if config:
        capital = config.get('capital', 0)
        trade_size = config.get('trade_size_usd', 0)
        stop_loss = config.get('stop_loss_pct', 0)
        take_profit = config.get('take_profit_pct', 0)
        
        summary.append(f"Capital: ${capital:.2f}")
        summary.append(f"Trade Size: ${trade_size:.2f}")
        summary.append(f"Stop Loss: {stop_loss*100:.1f}%")
        summary.append(f"Take Profit: {take_profit*100:.1f}%")
        
        # Check for risky configuration
        if trade_size > capital * 0.5:
            alert = f"CRITICAL: Trade size (${trade_size:.2f}) exceeds 50% of capital (${capital:.2f})"
            summary.append(f"WARNING: Large trade size relative to capital")
            critical_alert_logger.critical(alert)
    
    return summary

def analyze_strategies():
    """Analyze LLM strategies."""
    summary = []
    
    # Find latest strategy file
    strategy_files = [f for f in os.listdir('.') if f.startswith('llm_strategies_') and f.endswith('.json')]
    if not strategy_files:
        summary.append("No strategy files found")
        return summary
    
    latest_file = max(strategy_files)
    strategies = load_json_file(latest_file)
    
    if strategies:
        summary.append(f"Active Strategies: {len(strategies)}")
        
        total_investment = sum(s.get('investment_usd', 0) for s in strategies)
        summary.append(f"Total Strategy Investment: ${total_investment:.2f}")
        
        # Check for high-risk strategies
        high_risk_strategies = []
        for strategy in strategies:
            risk_params = strategy.get('risk_parameters', {})
            stop_loss = risk_params.get('stop_loss_pct', 0)
            take_profit = risk_params.get('take_profit_pct', 0)
            
            if stop_loss > 0.1:  # > 10% stop loss
                high_risk_strategies.append(strategy['strategy_name'])
        
        if high_risk_strategies:
            alert = f"CRITICAL: High-risk strategies detected: {', '.join(high_risk_strategies)}"
            summary.append(f"WARNING: High-risk strategies: {', '.join(high_risk_strategies)}")
            critical_alert_logger.critical(alert)
    
    return summary

def check_dashboard():
    """Check if dashboard is accessible."""
    summary = []
    
    try:
        # Read port from .active_port
        with open(".active_port", "r") as f:
            port = f.read().strip()
        
        url = f"http://localhost:{port}/"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            summary.append(f"Dashboard accessible on port {port}")
        else:
            summary.append(f"Dashboard returned status {response.status_code}")
            logging.warning(f"Dashboard check failed: HTTP {response.status_code}")
    except Exception as e:
        summary.append(f"Dashboard check failed: {str(e)}")
        logging.error(f"Dashboard check error: {e}")
    
    return summary

def main():
    """Main monitoring function."""
    print(f"Trading Dashboard Monitor - {datetime.now().isoformat()}")
    print("=" * 50)
    
    all_summary = []
    
    # Run all analyses
    print("\n1. Trading Status Analysis:")
    status_summary = analyze_trading_status()
    for line in status_summary:
        print(f"   {line}")
        all_summary.append(line)
    
    print("\n2. Trade Analysis:")
    trade_summary = analyze_trades()
    for line in trade_summary:
        print(f"   {line}")
        all_summary.append(line)
    
    print("\n3. Configuration Analysis:")
    config_summary = analyze_config()
    for line in config_summary:
        print(f"   {line}")
        all_summary.append(line)
    
    print("\n4. Strategy Analysis:")
    strategy_summary = analyze_strategies()
    for line in strategy_summary:
        print(f"   {line}")
        all_summary.append(line)
    
    print("\n5. Dashboard Status:")
    dashboard_summary = check_dashboard()
    for line in dashboard_summary:
        print(f"   {line}")
        all_summary.append(line)
    
    print("\n" + "=" * 50)
    print("Monitoring complete.")
    
    # Log all summary lines
    for line in all_summary:
        logging.info(line)

if __name__ == "__main__":
    main()