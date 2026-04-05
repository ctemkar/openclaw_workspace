#!/usr/bin/env python3
import json
import requests
from datetime import datetime
import sys

# Current market prices (from CoinGecko)
current_prices = {
    "BTC/USD": 67577,
    "ETH/USD": 2082.31
}

# Trades data from the dashboard
trades_data = {
    "count": 5,
    "trades": [
        {
            "price": 2325.28,
            "quantity": 0.086,
            "reason": "Near support level: $2308.08 (current: $2325.28)",
            "side": "BUY",
            "symbol": "ETH/USD",
            "time": "13:39:49"
        },
        {
            "price": 2193.6,
            "quantity": 0.0912,
            "reason": "Near support level: $2167.99 (current: $2193.60)",
            "side": "BUY",
            "symbol": "ETH/USD",
            "time": "00:33:02"
        },
        {
            "price": 67247.51,
            "quantity": 0.002974,
            "reason": "Near support level: $67110.20 (current: $67247.51)",
            "side": "BUY",
            "symbol": "BTC/USD",
            "time": "21:29:41"
        },
        {
            "price": 2052.38,
            "quantity": 0.0974,
            "reason": "Near support level: $2033.94 (current: $2052.38)",
            "side": "BUY",
            "symbol": "ETH/USD",
            "time": "21:29:42"
        },
        {
            "price": 2021.51,
            "quantity": 0.2474,
            "reason": "Conservative entry: ETH showing +0.68% 24h momentum. Risk/Reward 1:2 with 5% stop-loss ($1,920.43) and 10% take-profit ($2,223.66)",
            "side": "BUY",
            "symbol": "ETH/USD",
            "time": "07:24:00"
        }
    ]
}

# Risk parameters
STOP_LOSS = 0.05  # 5%
TAKE_PROFIT = 0.10  # 10%
CRITICAL_DRAWDOWN = 0.20  # 20%

def analyze_positions():
    print("=== POSITION ANALYSIS ===\n")
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Current Prices: BTC=${current_prices['BTC/USD']:,}, ETH=${current_prices['ETH/USD']:,.2f}\n")
    
    total_pnl = 0
    total_investment = 0
    alerts = []
    
    for i, trade in enumerate(trades_data["trades"], 1):
        symbol = trade["symbol"]
        entry_price = trade["price"]
        quantity = trade["quantity"]
        current_price = current_prices.get(symbol)
        
        if not current_price:
            print(f"Warning: No current price for {symbol}")
            continue
        
        # Calculate P&L
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        pnl_dollar = (current_price - entry_price) * quantity
        investment = entry_price * quantity
        
        total_pnl += pnl_dollar
        total_investment += investment
        
        # Check for alerts
        position_status = "NORMAL"
        
        # Stop-loss check (5% down)
        if pnl_percent <= -5:
            position_status = "STOP-LOSS TRIGGERED"
            alerts.append(f"🚨 STOP-LOSS TRIGGERED: {symbol} at {entry_price:.2f}, current {current_price:.2f} ({pnl_percent:.2f}%)")
        elif pnl_percent <= -4:  # Within 1% of stop-loss
            position_status = "NEAR STOP-LOSS"
            alerts.append(f"⚠️ NEAR STOP-LOSS: {symbol} at {entry_price:.2f}, current {current_price:.2f} ({pnl_percent:.2f}%)")
        
        # Take-profit check (10% up)
        elif pnl_percent >= 10:
            position_status = "TAKE-PROFIT TRIGGERED"
            alerts.append(f"🎯 TAKE-PROFIT TRIGGERED: {symbol} at {entry_price:.2f}, current {current_price:.2f} ({pnl_percent:.2f}%)")
        elif pnl_percent >= 9:  # Within 1% of take-profit
            position_status = "NEAR TAKE-PROFIT"
            alerts.append(f"📈 NEAR TAKE-PROFIT: {symbol} at {entry_price:.2f}, current {current_price:.2f} ({pnl_percent:.2f}%)")
        
        print(f"Position {i}: {symbol}")
        print(f"  Entry: ${entry_price:.2f} | Current: ${current_price:.2f}")
        print(f"  Quantity: {quantity}")
        print(f"  Investment: ${investment:.2f}")
        print(f"  P&L: ${pnl_dollar:.2f} ({pnl_percent:.2f}%)")
        print(f"  Status: {position_status}")
        print(f"  Stop-loss: ${entry_price * (1 - STOP_LOSS):.2f} (-5%)")
        print(f"  Take-profit: ${entry_price * (1 + TAKE_PROFIT):.2f} (+10%)")
        print()
    
    # Calculate overall metrics
    if total_investment > 0:
        total_pnl_percent = (total_pnl / total_investment) * 100
    else:
        total_pnl_percent = 0
    
    print("=== OVERALL SUMMARY ===")
    print(f"Total Investment: ${total_investment:.2f}")
    print(f"Total P&L: ${total_pnl:.2f} ({total_pnl_percent:.2f}%)")
    print(f"Number of Positions: {len(trades_data['trades'])}")
    
    # Check for critical drawdown
    if total_pnl_percent <= -CRITICAL_DRAWDOWN * 100:
        alerts.append(f"🚨 CRITICAL DRAWDOWN: Overall P&L at {total_pnl_percent:.2f}% (exceeds 20% threshold)")
    
    print("\n=== ALERTS ===")
    if alerts:
        for alert in alerts:
            print(alert)
    else:
        print("No critical alerts at this time.")
    
    return alerts, total_pnl, total_pnl_percent

if __name__ == "__main__":
    alerts, total_pnl, total_pnl_percent = analyze_positions()
    
    # Exit with code based on alerts
    if any("TRIGGERED" in alert for alert in alerts):
        sys.exit(2)  # Critical alert
    elif alerts:
        sys.exit(1)  # Warning alert
    else:
        sys.exit(0)  # Normal