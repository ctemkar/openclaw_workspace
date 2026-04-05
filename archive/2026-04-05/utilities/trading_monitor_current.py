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

BASE_URL = f'http://localhost:{PORT}'
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
        # Fetch from dashboard endpoints
        status_response = requests.get(f"{BASE_URL}/status")
        status_response.raise_for_status()
        status_data = status_response.json()
        
        trades_response = requests.get(f"{BASE_URL}/trades")
        trades_response.raise_for_status()
        trades_data = trades_response.json()
        
        # Read completed trades
        trades_path = os.path.join(BASE_DIR, "completed_trades.json")
        completed_trades = []
        if os.path.exists(trades_path):
            try:
                with open(trades_path, "r") as f:
                    completed_trades = json.load(f)
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
        
        # Extract risk parameters from status
        risk_params = status_data.get('risk_parameters', {})
        
        # Combine all data
        combined_data = {
            'status': status_data,
            'trades': trades_data,
            'completed_trades': completed_trades,
            'trading_logs': trading_logs,
            'capital': status_data.get('capital', 250.0),
            'stop_loss': risk_params.get('stop_loss', 0.05),
            'take_profit': risk_params.get('take_profit', 0.1),
            'bot_status': status_data.get('status', 'unknown'),
            'last_analysis': status_data.get('last_analysis', 'unknown'),
            'analysis_scheduled': status_data.get('analysis_scheduled', 'unknown'),
            'trading_pairs': status_data.get('trading_pairs', []),
            'max_trades_per_day': risk_params.get('max_trades_per_day', 2)
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

    capital = data.get('capital', 250.0)
    stop_loss = data.get('stop_loss', 0.05)
    take_profit = data.get('take_profit', 0.1)
    bot_status = data.get('bot_status', 'unknown')
    last_analysis = data.get('last_analysis', 'unknown')
    analysis_scheduled = data.get('analysis_scheduled', 'unknown')
    trading_pairs = data.get('trading_pairs', [])
    max_trades_per_day = data.get('max_trades_per_day', 2)
    
    trades_data = data.get('trades', {})
    trades_list = trades_data.get('trades', [])
    trade_count = trades_data.get('count', 0)
    
    completed_trades = data.get('completed_trades', [])
    trading_logs = data.get('trading_logs', [])
    
    # Check for errors in logs
    error_logs = [log for log in trading_logs if 'ERROR' in log.upper() or 'FAILED' in log.upper()]
    recent_logs = trading_logs[-10:] if len(trading_logs) > 10 else trading_logs

    # Log extracted data
    logging.info(f"Fetched data: Capital=${capital}, StopLoss={float(stop_loss)*100}%, TakeProfit={float(take_profit)*100}%")
    logging.info(f"Bot Status: {bot_status}, Last Analysis: {last_analysis}")
    logging.info(f"Active Trades: {trade_count}, Completed Trades: {len(completed_trades)}")
    logging.info(f"Trading Pairs: {', '.join(trading_pairs)}")
    
    for log in recent_logs:
        logging.info(f"Trading Log: {log.strip()}")

    summary_lines.append(f"--- Trading Dashboard Monitor Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    summary_lines.append(f"Bot Status: {bot_status}")
    summary_lines.append(f"Capital: ${float(capital):,.2f}")
    summary_lines.append(f"Stop Loss: {float(stop_loss)*100}%")
    summary_lines.append(f"Take Profit: {float(take_profit)*100}%")
    summary_lines.append(f"Max Trades/Day: {max_trades_per_day}")
    summary_lines.append(f"Analysis Schedule: {analysis_scheduled}")
    summary_lines.append(f"Last Analysis: {last_analysis}")
    summary_lines.append(f"Trading Pairs: {', '.join(trading_pairs)}")
    summary_lines.append(f"Active Trades: {trade_count}")
    summary_lines.append(f"Completed Trades: {len(completed_trades)}")
    
    # Show recent active trades
    if trades_list:
        summary_lines.append("\nRecent Active Trades:")
        for trade in trades_list[:5]:  # First 5 trades
            side = trade.get('side', 'unknown')
            price = trade.get('price', 0)
            quantity = trade.get('quantity', 0)
            symbol = trade.get('symbol', 'unknown')
            time = trade.get('time', 'unknown')
            value = price * quantity
            summary_lines.append(f"- {time}: {side} {quantity:.4f} {symbol} @ ${price:,.2f} (${value:,.2f})")

    # Show recent completed trades
    if completed_trades:
        summary_lines.append("\nRecent Completed Trades:")
        for trade in completed_trades[-5:]:  # Last 5 trades
            side = trade.get('side', 'unknown')
            price = trade.get('price', 0)
            quantity = trade.get('quantity', 0)
            symbol = trade.get('symbol', 'unknown')
            time = trade.get('time', 'unknown')
            value = price * quantity
            summary_lines.append(f"- {time}: {side} {quantity:.4f} {symbol} @ ${price:,.2f} (${value:,.2f})")

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

    # Check trade limits
    if trade_count >= max_trades_per_day:
        alert_msg = f"TRADE LIMIT REACHED: {trade_count}/{max_trades_per_day} trades today. No more trades will be executed."
        critical_alerts.append(alert_msg)
        critical_logger.warning(alert_msg)
        summary_lines.append(f"\n⚠️ Trade Limit: {trade_count}/{max_trades_per_day} trades - LIMIT REACHED")

    # Calculate risk metrics
    current_capital = float(capital)
    stop_loss_threshold = current_capital * (1 - float(stop_loss))
    take_profit_threshold = current_capital * (1 + float(take_profit))
    
    logging.info(f"Stop loss threshold: ${stop_loss_threshold:.2f}, Take profit threshold: ${take_profit_threshold:.2f}")

    # Calculate total exposure from active trades
    total_exposure = 0
    for trade in trades_list:
        price = trade.get('price', 0)
        quantity = trade.get('quantity', 0)
        total_exposure += price * quantity
    
    if total_exposure > 0:
        exposure_pct = (total_exposure / current_capital) * 100
        summary_lines.append(f"\n📊 Current Exposure: ${total_exposure:,.2f} ({exposure_pct:.1f}% of capital)")
        
        # Check if exposure is high
        if exposure_pct > 50:
            alert_msg = f"HIGH EXPOSURE DETECTED: ${total_exposure:,.2f} ({exposure_pct:.1f}% of capital) invested. Consider reducing position sizes."
            critical_alerts.append(alert_msg)
            critical_logger.warning(alert_msg)
            summary_lines.append(f"⚠️ High Exposure: {exposure_pct:.1f}% of capital invested")

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