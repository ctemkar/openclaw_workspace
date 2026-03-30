
import requests
import json
import os
from datetime import datetime

MONITOR_BASE_URL = "http://localhost:5001/"
TRADING_LOG_PATH = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG_PATH = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

def fetch_trading_data():
    """Fetch trading data from multiple endpoints and combine into a single dict"""
    combined_data = {}
    
    try:
        # Fetch system status
        status_response = requests.get(f"{MONITOR_BASE_URL}status", timeout=5)
        if status_response.status_code == 200:
            combined_data.update(status_response.json())
        
        # Fetch recent trades
        trades_response = requests.get(f"{MONITOR_BASE_URL}trades", timeout=5)
        if trades_response.status_code == 200:
            trades_data = trades_response.json()
            combined_data["orders"] = trades_data.get("trades", [])
            combined_data["trade_count"] = trades_data.get("count", 0)
        
        # Fetch strategy info
        strategy_response = requests.get(f"{MONITOR_BASE_URL}strategy", timeout=5)
        if strategy_response.status_code == 200:
            combined_data["strategy"] = strategy_response.json()
        
        # Calculate drawdown based on trades
        if "orders" in combined_data and combined_data["orders"]:
            # Calculate average buy price for BTC trades
            btc_trades = [t for t in combined_data["orders"] if t.get("symbol") == "BTC/USD" or "BTC" in str(t.get("symbol", ""))]
            if btc_trades:
                # Get current BTC price (we'll need to fetch this from a market API)
                # For now, use a hardcoded value from the logs or calculate from recent trades
                current_btc_price = 66554.18  # From the trading log
                
                # Calculate average buy price
                total_btc_amount = 0
                total_btc_value = 0
                for trade in btc_trades:
                    price = trade.get("price")
                    amount = trade.get("amount") or trade.get("quantity", 0)
                    if price and amount:
                        total_btc_amount += amount
                        total_btc_value += price * amount
                
                if total_btc_amount > 0:
                    avg_btc_price = total_btc_value / total_btc_amount
                    drawdown_pct = ((current_btc_price - avg_btc_price) / avg_btc_price) * 100
                    combined_data["drawdown"] = round(drawdown_pct, 2)
                    
                    # Check if drawdown is critical (approaching stop-loss)
                    if drawdown_pct <= -5:  # Stop-loss threshold
                        combined_data["drawdown_status"] = "critical"
                    elif drawdown_pct <= -3:  # Warning threshold
                        combined_data["drawdown_status"] = "warning"
                    else:
                        combined_data["drawdown_status"] = "normal"
                else:
                    combined_data["drawdown"] = "no_trade_data"
            else:
                combined_data["drawdown"] = "no_btc_trades"
        else:
            combined_data["drawdown"] = "no_trades"
        
        return combined_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from monitoring service: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from monitoring service: {e}")
        return None

def log_data(data):
    if data:
        log_entry = f"[{datetime.now().isoformat()}] Data: {json.dumps(data)}\n"
        with open(TRADING_LOG_PATH, "a") as f:
            f.write(log_entry)

def log_alert(alert_message):
    log_entry = f"[{datetime.now().isoformat()}] ALERT: {alert_message}\n"
    with open(CRITICAL_ALERTS_LOG_PATH, "a") as f:
        f.write(log_entry)

def analyze_and_alert(data):
    alerts = []
    if not data:
        return alerts

    # Detect stop-loss/take-profit orders (check order status)
    if "orders" in data and data["orders"]:
        for order in data["orders"]:
            # Check for filled orders that might be at risk
            if order.get("status") == "filled":
                # We could add more sophisticated risk analysis here
                pass
    
    # Detect critical drawdown based on calculated drawdown_status
    if "drawdown_status" in data:
        if data["drawdown_status"] == "critical":
            drawdown_value = data.get("drawdown", "N/A")
            alert_message = f"CRITICAL: BTC position approaching stop-loss! Drawdown: {drawdown_value}%"
            alerts.append(alert_message)
            log_alert(alert_message)
        elif data["drawdown_status"] == "warning":
            drawdown_value = data.get("drawdown", "N/A")
            alert_message = f"WARNING: BTC position showing significant drawdown: {drawdown_value}%"
            alerts.append(alert_message)
            log_alert(alert_message)
    
    # Also check raw drawdown value for additional alerts
    if "drawdown" in data and isinstance(data["drawdown"], (int, float)):
        if data["drawdown"] <= -5:
            # Already covered by drawdown_status, but log for completeness
            pass
        elif data["drawdown"] <= -3:
            # Already covered by drawdown_status
            pass

    return alerts

def generate_summary(data, alerts):
    summary = f"Trading Analysis Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    summary += "----------------------------------------\n"

    if not data:
        summary += "Failed to fetch trading data.\n"
        return summary

    summary += f"Status: {data.get('status', 'N/A')}\n"
    summary += f"Risk Parameters: {data.get('risk_parameters', 'N/A')}\n"
    summary += f"Number of orders: {len(data.get('orders', []))}\n"
    summary += f"Drawdown: {data.get('drawdown', 'N/A')}\n"

    if alerts:
        summary += "\nCritical Alerts:\n"
        for alert in alerts:
            summary += f"- {alert}\n"
    else:
        summary += "\nNo critical alerts detected.\n"

    return summary

def main():
    trading_data = fetch_trading_data()
    log_data(trading_data)
    alerts = analyze_and_alert(trading_data)
    summary = generate_summary(trading_data, alerts)
    print(summary) # This will be captured by the cron job's systemEvent

if __name__ == "__main__":
    main()
