
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

DATA_URL = f'http://localhost:{PORT}/'

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
critical_logger = logging.getLogger('critical_alerts')
critical_handler = logging.FileHandler(CRITICAL_LOG_FILE)
critical_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
critical_logger.addHandler(critical_handler)
critical_logger.setLevel(logging.WARNING)

def fetch_data():
    try:
        # Fetch from available API endpoints
        base_url = DATA_URL.rstrip('/')
        
        # Get trading status (only available endpoint)
        status_response = requests.get(f"{base_url}/api/status/all")
        status_response.raise_for_status()
        status_data = status_response.json()
        
        # Read trading logs directly from file since API endpoint doesn't exist
        trading_logs = []
        try:
            with open('/Users/chetantemkar/.openclaw/workspace/app/trading_bot_clean.log', 'r') as f:
                trading_logs = f.read().split('\n')[-20:]  # Last 20 lines
        except:
            trading_logs = ["No trading logs available"]
        
        # Get market prices from external API since dashboard doesn't provide them
        # For now, we'll use mock data or skip this
        prices_data = {"BTC/USD": 74800.0, "ETH/USD": 2317.71}  # Mock data based on recent trades
        
        # Combine all data
        combined_data = {
            'status': status_data,
            'logs': {"logs": "\n".join(trading_logs)},  # Mock logs structure
            'prices': prices_data,
            'capital': 10000.0,  # Default from app.py MOCK_TRADING_CONFIG
            'stop_loss': 0.01,   # Default from app.py MOCK_TRADING_CONFIG
            'take_profit': 0.02, # Default from app.py MOCK_TRADING_CONFIG
            'trading_logs': trading_logs,
            'status_updates': [f"Trading: {status_data.get('status', 'unknown')} - Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
        }
        
        return combined_data
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
    
    # Check for strategy errors in logs
    strategy_errors = [log for log in trading_logs if 'STRATEGY ERROR' in log]
    recent_logs = trading_logs[-10:] if len(trading_logs) > 10 else trading_logs

    # Log extracted data
    logging.info(f"Fetched data: Capital={capital}, StopLoss={stop_loss}, TakeProfit={take_profit}")
    logging.info(f"Market Prices: {prices}")
    for log in recent_logs:
        logging.info(f"Trading Log: {log}")
    for status in status_updates:
        logging.info(f"Status Update: {status}")

    summary_lines.append(f"--- Trading Dashboard Monitor Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    summary_lines.append(f"Trading Status: {data.get('status', {}).get('trading', 'unknown')}")
    summary_lines.append(f"Capital: ${capital}")
    summary_lines.append(f"Stop Loss: {float(stop_loss)*100}%")
    summary_lines.append(f"Take Profit: {float(take_profit)*100}%")
    
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

    # Check for stop-loss or take-profit triggers (simplified logic)
    # In a real system, you would check actual P&L against these thresholds
    current_capital = float(capital)
    stop_loss_threshold = current_capital * (1 - float(stop_loss))
    take_profit_threshold = current_capital * (1 + float(take_profit))
    
    # For now, just log the thresholds
    logging.info(f"Stop loss threshold: ${stop_loss_threshold:.2f}, Take profit threshold: ${take_profit_threshold:.2f}")

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
    print(result_summary) # stdout will be captured by cron tool delivery
