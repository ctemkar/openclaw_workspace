import requests
import json
import logging
from datetime import datetime

LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
CRITICAL_LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'

# Read the active port from .active_port file
try:
    with open('/Users/chetantemkar/.openclaw/workspace/app/.active_port', 'r') as f:
        PORT = f.read().strip()
except:
    PORT = '5001'  # fallback

DATA_URL = f'http://localhost:{PORT}/api/trading/progress'

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
critical_logger = logging.getLogger('critical_alerts')
critical_handler = logging.FileHandler(CRITICAL_LOG_FILE)
critical_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
critical_logger.addHandler(critical_handler)
critical_logger.setLevel(logging.WARNING)

def fetch_data():
    try:
        response = requests.get(DATA_URL, timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            
            # Read trading logs
            trading_logs = []
            try:
                with open('/Users/chetantemkar/.openclaw/workspace/app/trading_bot_clean.log', 'r') as f:
                    trading_logs = f.read().split('\n')[-20:]  # Last 20 lines
            except:
                trading_logs = ["No trading logs available"]
            
            # Mock prices based on recent trades
            prices_data = {"BTC/USD": 74800.0, "ETH/USD": 2317.71}
            
            # Combine all data
            combined_data = {
                'status': status_data,
                'logs': {"logs": "\n".join(trading_logs)},
                'prices': prices_data,
                'capital': 10000.0,
                'stop_loss': 0.01,
                'take_profit': 0.02,
                'trading_logs': trading_logs,
                'status_updates': [f"Trading: {status_data.get('status', 'unknown')} - Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
            }
            
            return combined_data
        else:
            logging.error(f"Failed to fetch data: HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data from dashboard: {e}")
        return None

def analyze_data(data):
    if not data:
        return "No data received for analysis."

    summary_lines = []
    critical_alerts = []

    capital = data.get('capital', 'N/A')
    stop_loss = data.get('stop_loss', 'N/A')
    take_profit = data.get('take_profit', 'N/A')
    trading_logs = data.get('trading_logs', [])
    status_updates = data.get('status_updates', [])
    prices = data.get('prices', {})
    status_data = data.get('status', {})
    
    # Check for strategy errors in logs
    strategy_errors = [log for log in trading_logs if 'STRATEGY ERROR' in log]
    recent_logs = trading_logs[-10:] if len(trading_logs) > 10 else trading_logs

    # Log extracted data
    logging.info(f"Fetched data: Capital=${capital}, StopLoss={stop_loss}, TakeProfit={take_profit}")
    logging.info(f"Trading Status: {status_data.get('status', 'unknown')}")
    logging.info(f"Completed Trades: {len(status_data.get('trades', []))}")
    logging.info(f"Market Prices: {prices}")
    for log in recent_logs:
        logging.info(f"Trading Log: {log}")
    for status in status_updates:
        logging.info(f"Status Update: {status}")

    summary_lines.append(f"--- Trading Dashboard Monitor Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    summary_lines.append(f"Trading Status: {status_data.get('status', 'unknown')}")
    summary_lines.append(f"Capital: ${capital}")
    summary_lines.append(f"Stop Loss: {float(stop_loss)*100}%")
    summary_lines.append(f"Take Profit: {float(take_profit)*100}%")
    summary_lines.append(f"Completed Trades: {len(status_data.get('trades', []))}")
    
    # Market prices
    summary_lines.append("\nMarket Prices:")
    for symbol, price in prices.items():
        summary_lines.append(f"- {symbol}: ${price:,.2f}")

    # Check for strategy errors
    if strategy_errors:
        error_count = len(strategy_errors)
        alert_msg = f"STRATEGY ERRORS DETECTED: {error_count} errors in recent logs. Bot may not be functioning correctly."
        critical_alerts.append(alert_msg)
        critical_logger.warning(alert_msg)
        summary_lines.append(f"\n⚠️ Strategy Errors: {error_count} errors detected")

    # Check trades for potential issues
    trades = status_data.get('trades', [])
    if trades:
        # Check if any trades have unusual patterns
        buy_trades = [t for t in trades if t.get('side') == 'buy']
        sell_trades = [t for t in trades if t.get('side') == 'sell']
        
        if len(buy_trades) > 5 and len(sell_trades) == 0:
            alert_msg = f"WARNING: {len(buy_trades)} buy trades with no sell trades. Check trading strategy."
            critical_alerts.append(alert_msg)
            critical_logger.warning(alert_msg)
            summary_lines.append(f"\n⚠️ Trade Imbalance: {len(buy_trades)} buys, {len(sell_trades)} sells")

    if critical_alerts:
        summary_lines.append("\n🚨 CRITICAL ALERTS:")
        summary_lines.extend(critical_alerts)
    else:
        summary_lines.append("\n✅ No critical alerts detected.")

    summary_lines.append("\nRecent Logs:")
    if recent_logs:
        for log in recent_logs:
            summary_lines.append(f"- {log}")
    else:
        summary_lines.append("- No recent logs available.")

    return "\n".join(summary_lines)

if __name__ == "__main__":
    dashboard_data = fetch_data()
    result_summary = analyze_data(dashboard_data)
    print(result_summary)
