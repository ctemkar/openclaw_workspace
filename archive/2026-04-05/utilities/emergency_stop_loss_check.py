#!/usr/bin/env python3
"""
Emergency stop-loss checker.
This script should be run frequently (e.g., every 5 minutes) to monitor positions.
It will alert if positions are below stop-loss levels.
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
STOP_LOSS_PERCENT = 0.05  # 5%
CHECK_INTERVAL = 300  # 5 minutes in seconds
MAX_CHECKS = 12  # Check for 1 hour

def load_trades():
    """Load completed trades from JSON file"""
    try:
        with open('completed_trades.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading trades: {e}")
        return []

def get_current_prices():
    """Get current BTC and ETH prices"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum", "vs_currencies": "usd"},
            timeout=10
        )
        data = response.json()
        return {
            "BTC": data["bitcoin"]["usd"],
            "ETH": data["ethereum"]["usd"]
        }
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return None

def analyze_position(trades, symbol, current_price):
    """Analyze position for a specific symbol"""
    symbol_trades = []
    
    for trade in trades:
        trade_symbol = str(trade.get('symbol', '')).upper()
        trade_model = str(trade.get('model', '')).upper()
        price = trade.get('price')
        
        if price and price > 0:
            if symbol in trade_symbol or symbol in trade_model:
                symbol_trades.append(price)
    
    if not symbol_trades:
        return None
    
    avg_price = sum(symbol_trades) / len(symbol_trades)
    pnl_pct = (current_price - avg_price) / avg_price * 100
    stop_loss_price = avg_price * (1 - STOP_LOSS_PERCENT)
    stop_loss_triggered = current_price <= stop_loss_price
    
    return {
        "symbol": symbol,
        "entry_price": avg_price,
        "current_price": current_price,
        "pnl_pct": pnl_pct,
        "stop_loss_price": stop_loss_price,
        "stop_loss_triggered": stop_loss_triggered,
        "num_trades": len(symbol_trades),
        "distance_to_stop_loss": current_price - stop_loss_price
    }

def log_alert(message, critical=False):
    """Log alert to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = "🚨 CRITICAL: " if critical else "⚠️  ALERT: "
    
    log_file = "critical_alerts.log"
    
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {prefix}{message}\n")
    
    print(f"{prefix}{message}")

def main():
    print("=== EMERGENCY STOP-LOSS MONITOR ===")
    print(f"Checking positions every {CHECK_INTERVAL//60} minutes")
    print(f"Stop-loss threshold: {STOP_LOSS_PERCENT*100}%")
    print()
    
    check_count = 0
    
    while check_count < MAX_CHECKS:
        check_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n--- Check #{check_count} at {timestamp} ---")
        
        # Load trades
        trades = load_trades()
        if not trades:
            print("No trades found. Waiting...")
            time.sleep(CHECK_INTERVAL)
            continue
        
        # Get current prices
        prices = get_current_prices()
        if not prices:
            print("Failed to get prices. Waiting...")
            time.sleep(CHECK_INTERVAL)
            continue
        
        # Analyze BTC position
        btc_analysis = analyze_position(trades, "BTC", prices["BTC"])
        if btc_analysis:
            print(f"BTC: ${btc_analysis['current_price']:,.2f} (Entry: ${btc_analysis['entry_price']:,.2f}, P&L: {btc_analysis['pnl_pct']:.2f}%)")
            print(f"  Stop-loss: ${btc_analysis['stop_loss_price']:,.2f} (Distance: ${btc_analysis['distance_to_stop_loss']:,.2f})")
            
            if btc_analysis['stop_loss_triggered']:
                alert_msg = f"BTC STOP-LOSS TRIGGERED! Price ${btc_analysis['current_price']:,.2f} below stop-loss ${btc_analysis['stop_loss_price']:,.2f}"
                log_alert(alert_msg, critical=True)
        
        # Analyze ETH position
        eth_analysis = analyze_position(trades, "ETH", prices["ETH"])
        if eth_analysis:
            print(f"ETH: ${eth_analysis['current_price']:,.2f} (Entry: ${eth_analysis['entry_price']:,.2f}, P&L: {eth_analysis['pnl_pct']:.2f}%)")
            print(f"  Stop-loss: ${eth_analysis['stop_loss_price']:,.2f} (Distance: ${eth_analysis['distance_to_stop_loss']:,.2f})")
            
            if eth_analysis['stop_loss_triggered']:
                alert_msg = f"ETH STOP-LOSS TRIGGERED! Price ${eth_analysis['current_price']:,.2f} below stop-loss ${eth_analysis['stop_loss_price']:,.2f}"
                log_alert(alert_msg, critical=True)
        
        # Wait for next check
        if check_count < MAX_CHECKS:
            print(f"\nWaiting {CHECK_INTERVAL//60} minutes for next check...")
            time.sleep(CHECK_INTERVAL)
    
    print(f"\n=== Monitoring completed after {MAX_CHECKS} checks ===")
    print("Check critical_alerts.log for any alerts.")
    
    # Final summary
    print("\n=== FINAL POSITION SUMMARY ===")
    if btc_analysis:
        status = "🚨 STOP-LOSS" if btc_analysis['stop_loss_triggered'] else "✅ OK"
        print(f"BTC: {status} (P&L: {btc_analysis['pnl_pct']:.2f}%)")
    
    if eth_analysis:
        status = "🚨 STOP-LOSS" if eth_analysis['stop_loss_triggered'] else "✅ OK"
        print(f"ETH: {status} (P&L: {eth_analysis['pnl_pct']:.2f}%)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
        sys.exit(0)