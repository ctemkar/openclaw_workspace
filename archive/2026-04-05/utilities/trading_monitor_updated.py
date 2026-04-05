import requests
import json
import logging
from datetime import datetime
import os

LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
CRITICAL_LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'

# Read the active port from .active_port file
try:
    with open('/Users/chetantemkar/.openclaw/workspace/app/.active_port', 'r') as f:
        PORT = f.read().strip()
except:
    PORT = '5001'  # fallback

DATA_URL = f'http://localhost:{PORT}/'
BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

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
        
        # Get trading status
        status_response = requests.get(f"{base_url}/api/status/all")
        status_response.raise_for_status()
        status_data = status_response.json()
        
        # Read trading config
        config_path = os.path.join(BASE_DIR, "trading_config.json")
        config_data = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config_data = json.load(f)
            except:
                pass
        
        # Read trading logs
        log_path = os.path.join(BASE_DIR, "trading.log")
        trading_logs = []
        if os.path.exists(log_path):
            try:
                with open(log_path, "r") as f:
                    trading_logs = f.readlines()[-50:]  # Last 50 lines
            except:
                pass
        
        # Read completed trades
        trades_path = os.path.join(BASE_DIR, "completed_trades.json")
        completed_trades = []
        if os.path.exists(trades_path):
            try:
                with open(trades_path, "r") as f:
                    completed_trades = json.load(f)
            except:
                pass
        
        # Combine all data
        combined_data = {
            'status': status_data,
            'config': config_data,
            'trading_logs': trading_logs,
            'completed_trades': completed_trades,
            'capital': config_data.get('capital', 1000.0),
            'stop_loss': config_data.get('stop_loss_pct', 0.01),
            'take_profit': config_data.get('take_profit_pct', 0.02),
            'trade_size': config_data.get('trade_size_usd', 100.0),
            'bot_status': status_data.get('status', 'unknown')
        }
        
        return combined_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data from dashboard: {e}")
        return None
    except Exception as e:
        logging.error(f"Error reading local files: {e}")
        return None

def analyze_data(data):
    if not data:
        return "No data received for analysis."

    summary_lines = []
    critical_alerts = []

    capital = data.get('capital', 'N/A')
    stop_loss = data.get('stop_loss', 'N/A')
    take_profit = data.get('take_profit', 'N/A')
    trade_size = data.get('trade_size', 'N/A')
    bot_status = data.get('bot_status', 'unknown')
    trading_logs = data.get('trading_logs', [])
    completed_trades = data.get('completed_trades', [])
    
    # Check for errors in logs
    error_logs = [log for log in trading_logs if 'ERROR' in log.upper() or 'FAILED' in log.upper()]
    recent_logs = trading_logs[-10:] if len(trading_logs) > 10 else trading_logs

    # Log extracted data
    logging.info(f"Fetched data: Capital=${capital}, StopLoss={float(stop_loss)*100}%, TakeProfit={float(take_profit)*100}%, TradeSize=${trade_size}")
    logging.info(f"Bot Status: {bot_status}")
    logging.info(f"Completed Trades: {len(completed_trades)}")
    
    for log in recent_logs:
        logging.info(f"Trading Log: {log.strip()}")

    summary_lines.append(f"--- Trading Dashboard Monitor Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    summary_lines.append(f"Bot Status: {bot_status}")
    summary_lines.append(f"Capital: ${float(capital):,.2f}")
    summary_lines.append(f"Trade Size: ${float(trade_size):,.2f}")
    summary_lines.append(f"Stop Loss: {float(stop_loss)*100}%")
    summary_lines.append(f"Take Profit: {float(take_profit)*100}%")
    summary_lines.append(f"Completed Trades: {len(completed_trades)}")
    
    # Show recent trades
    if completed_trades:
        summary_lines.append("\nRecent Trades:")
        for trade in completed_trades[-5:]:  # Last 5 trades
            side = trade.get('side', 'unknown')
            price = trade.get('price', 0)
            amount = trade.get('amount', 0)
            time = trade.get('time', 'unknown')
            summary_lines.append(f"- {time}: {side.upper()} {amount:.6f} BTC @ ${price:,.2f}")

    # Check for errors
    if error_logs:
        error_count = len(error_logs)
        alert_msg = f"ERRORS DETECTED: {error_count} errors in recent logs. Bot may not be functioning correctly."
        critical_alerts.append(alert_msg)
        critical_logger.warning(alert_msg)
        summary_lines.append(f"\n⚠️ Errors: {error_count} errors detected")

    # Check if bot is stopped
    if bot_status == 'stopped':
        alert_msg = "TRADING BOT IS STOPPED. No active trading processes detected."
        critical_alerts.append(alert_msg)
        critical_logger.warning(alert_msg)
        summary_lines.append(f"\n⚠️ Bot Status: STOPPED - No active trading")

    # Calculate risk metrics
    current_capital = float(capital)
    stop_loss_threshold = current_capital * (1 - float(stop_loss))
    take_profit_threshold = current_capital * (1 + float(take_profit))
    
    logging.info(f"Stop loss threshold: ${stop_loss_threshold:.2f}, Take profit threshold: ${take_profit_threshold:.2f}")

    # Check for drawdown (simplified - in real system, track P&L)
    if completed_trades:
        # Calculate total invested
        total_invested = sum(trade.get('price', 0) * trade.get('amount', 0) for trade in completed_trades if trade.get('side') == 'buy')
        # This is simplified - real drawdown would track current value vs invested
        if total_invested > current_capital * 0.5:  # If more than 50% of capital is invested
            summary_lines.append(f"\n⚠️ High Exposure: ${total_invested:,.2f} invested ({(total_invested/current_capital)*100:.1f}% of capital)")

    if critical_alerts:
        summary_lines.append("\n🚨 CRITICAL ALERTS:")
        summary_lines.extend(critical_alerts)
    else:
        summary_lines.append("\n✅ No critical alerts detected.")

    summary_lines.append("\nRecent Logs:")
    if recent_logs:
        for log in recent_logs[-5:]:  # Last 5 logs
            summary_lines.append(f"- {log.strip()}")
    else:
        summary_lines.append("- No recent logs available.")

    return "\n".join(summary_lines)

if __name__ == "__main__":
    dashboard_data = fetch_data()
    result_summary = analyze_data(dashboard_data)
    print(result_summary) # stdout will be captured by cron tool delivery