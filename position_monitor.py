#!/usr/bin/env python3
"""
Simple position monitor for BTC trades.
Checks current BTC price and calculates if stop loss is triggered.
"""

import requests
import json
from datetime import datetime
import time
import sys

# BTC positions from the trading data
BTC_POSITIONS = [
    74770.04,  # Trade 1
    74800.00,  # Trade 2
    74700.83,  # Trade 3
    74700.83,  # Trade 4
]

STOP_LOSS_THRESHOLD = -1.0  # 1% stop loss

def get_btc_price():
    """Get current BTC price from CoinGecko"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"},
            timeout=10
        )
        data = response.json()
        return data["bitcoin"]["usd"]
    except Exception as e:
        print(f"Error fetching BTC price: {e}")
        return None

def calculate_position_status(btc_price):
    """Calculate current position status"""
    total_investment = sum(BTC_POSITIONS)
    current_value = btc_price * len(BTC_POSITIONS)
    total_loss = current_value - total_investment
    loss_percent = (total_loss / total_investment) * 100
    
    return {
        "btc_price": btc_price,
        "total_investment": total_investment,
        "current_value": current_value,
        "total_loss": total_loss,
        "loss_percent": loss_percent,
        "stop_loss_triggered": loss_percent <= STOP_LOSS_THRESHOLD
    }

def log_to_file(filename, message):
    """Append message to log file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def main():
    print("=== BTC Position Monitor ===")
    print(f"Monitoring {len(BTC_POSITIONS)} BTC positions")
    print(f"Stop Loss Threshold: {STOP_LOSS_THRESHOLD}%")
    print(f"Total Investment: ${sum(BTC_POSITIONS):,.2f}")
    print()
    
    btc_price = get_btc_price()
    if btc_price is None:
        print("Failed to get BTC price. Exiting.")
        return 1
    
    status = calculate_position_status(btc_price)
    
    print(f"Current BTC Price: ${btc_price:,.2f}")
    print(f"Current Portfolio Value: ${status['current_value']:,.2f}")
    print(f"Total Loss: ${status['total_loss']:,.2f}")
    print(f"Loss Percentage: {status['loss_percent']:.2f}%")
    
    # Log to monitoring log
    log_message = f"Position Check - BTC: ${btc_price:,.2f}, Loss: {status['loss_percent']:.2f}%, Stop Loss: {'TRIGGERED' if status['stop_loss_triggered'] else 'Not triggered'}"
    log_to_file("trading_monitoring.log", log_message)
    
    # Check for stop loss trigger
    if status['stop_loss_triggered']:
        alert_message = f"🚨 STOP LOSS TRIGGERED! Loss: {status['loss_percent']:.2f}% exceeds {STOP_LOSS_THRESHOLD}% threshold"
        print(f"\n⚠️  {alert_message}")
        log_to_file("critical_alerts.log", alert_message)
        
        # Add detailed position info
        details = f"STOP LOSS DETAILS - BTC Price: ${btc_price:,.2f}, Total Loss: ${status['total_loss']:,.2f}, Loss %: {status['loss_percent']:.2f}%"
        log_to_file("critical_alerts.log", details)
        
        return 2  # Exit with error code for stop loss
    
    print(f"\n✅ Positions within limits. Stop loss not triggered.")
    return 0

if __name__ == "__main__":
    sys.exit(main())