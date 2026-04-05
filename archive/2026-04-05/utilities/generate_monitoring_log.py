import json
import subprocess
import os
from datetime import datetime

# Read current port from .active_port file
try:
    with open(".active_port", "r") as f:
        PORT = f.read().strip()
except:
    PORT = "5001"  # Fallback

def get_api_data(endpoint):
    """Fetch data from API endpoint"""
    try:
        url = f'http://localhost:{PORT}{endpoint}'
        result = subprocess.run(['curl', '-s', url], 
                              capture_output=True, text=True, timeout=5)
        if result.stdout:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
    return {}

def main():
    # Get current time
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Get API data
    status_data = get_api_data('/api/trading/status')
    config_data = get_api_data('/api/trading/configure')
    prices_data = get_api_data('/api/market/prices')
    
    # Read completed trades
    try:
        with open('completed_trades.json', 'r') as f:
            trades = json.load(f)
    except Exception as e:
        print(f"Error reading trades: {e}")
        trades = []
    
    # Calculate P&L
    current_btc_price = prices_data.get('BTC/USDT', 40927.76)
    total_investment = 0
    total_current_value = 0
    critical_alerts = []
    
    for trade in trades:
        if trade.get('side') == 'buy':
            buy_price = trade.get('price', 0)
            amount = trade.get('amount', 0)
            investment = buy_price * amount
            current_value = current_btc_price * amount
            pnl = current_value - investment
            pnl_pct = (pnl / investment) * 100 if investment > 0 else 0
            
            total_investment += investment
            total_current_value += current_value
            
            # Check for stop-loss triggers
            stop_loss_pct = config_data.get('stop_loss_pct', 0.01) * 100
            if pnl_pct <= -stop_loss_pct:
                alert_msg = f'STOP-LOSS TRIGGERED: Trade at {trade.get("time", "unknown")} has P&L of {pnl_pct:.2f}% (threshold: -{stop_loss_pct:.1f}%)'
                critical_alerts.append(alert_msg)
            
            # Check for take-profit triggers
            take_profit_pct = config_data.get('take_profit_pct', 0.02) * 100
            if pnl_pct >= take_profit_pct:
                alert_msg = f'TAKE-PROFIT TRIGGERED: Trade at {trade.get("time", "unknown")} has P&L of {pnl_pct:.2f}% (threshold: {take_profit_pct:.1f}%)'
                critical_alerts.append(alert_msg)
    
    # Calculate total P&L
    total_pnl = total_current_value - total_investment
    total_pnl_pct = (total_pnl / total_investment) * 100 if total_investment > 0 else 0
    
    # Check for critical drawdown
    if total_pnl_pct <= -5.0:
        alert_msg = f'CRITICAL DRAWDOWN: Total portfolio loss of {total_pnl_pct:.2f}% exceeds 5% threshold'
        critical_alerts.append(alert_msg)
    elif total_pnl_pct <= -3.0:
        alert_msg = f'WARNING: Drawdown approaching critical levels at {total_pnl_pct:.2f}%'
        critical_alerts.append(alert_msg)
    
    # Prepare monitoring log entry
    log_entry = f'''=== TRADING MONITORING LOG ===
Timestamp: {current_time}
Dashboard Status: {status_data.get('trading', 'unknown')}
Last Update: {status_data.get('last_update', 'unknown')}

=== CONFIGURATION ===
Capital: ${config_data.get('capital', 0):.2f}
Stop Loss: {config_data.get('stop_loss_pct', 0)*100:.1f}%
Take Profit: {config_data.get('take_profit_pct', 0)*100:.1f}%
Trade Size: ${config_data.get('trade_size_usd', 0):.2f}

=== MARKET PRICES ===
BTC/USDT: ${prices_data.get('BTC/USDT', 0):.2f}
ETH/USDT: ${prices_data.get('ETH/USDT', 0):.2f}
SOL/USDT: ${prices_data.get('SOL/USDT', 0):.2f}

=== TRADE STATUS ===
Active Trades: {len(trades)}
Total Investment: ${total_investment:.2f}
Total Current Value: ${total_current_value:.2f}
Total P&L: ${total_pnl:.2f} ({total_pnl_pct:.2f}%)

=== ALERTS ===
{chr(10).join(critical_alerts) if critical_alerts else 'No critical alerts'}

=== END OF REPORT ===

'''
    
    return log_entry, critical_alerts

if __name__ == "__main__":
    log_entry, critical_alerts = main()
    print(log_entry)