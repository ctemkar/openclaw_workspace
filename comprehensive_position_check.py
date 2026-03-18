#!/usr/bin/env python3
"""
Comprehensive position monitor for BTC and ETH trades.
Checks current prices against actual entry prices from completed_trades.json
and calculates if 5% stop-loss is triggered.
"""

import requests
import json
from datetime import datetime
import sys

# Load actual trades from completed_trades.json
def load_trades():
    try:
        with open('completed_trades.json', 'r') as f:
            trades = json.load(f)
        return trades
    except Exception as e:
        print(f"Error loading trades: {e}")
        return []

def get_current_prices():
    """Get current BTC and ETH prices from CoinGecko"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum", "vs_currencies": "usd"},
            timeout=10
        )
        data = response.json()
        return {
            "btc": data["bitcoin"]["usd"],
            "eth": data["ethereum"]["usd"]
        }
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return None

def analyze_positions(trades, prices):
    """Analyze positions and calculate stop-loss status"""
    btc_trades = []
    eth_trades = []
    
    for trade in trades:
        symbol = str(trade.get('symbol', '')).upper()
        price = trade.get('price')
        
        if price and price > 0:
            if 'BTC' in symbol or 'BTC' in str(trade.get('model', '')):
                btc_trades.append(price)
            elif 'ETH' in symbol or 'ETH' in str(trade.get('model', '')):
                eth_trades.append(price)
    
    results = {}
    
    # Analyze BTC
    if btc_trades:
        avg_btc = sum(btc_trades) / len(btc_trades)
        current_btc = prices["btc"]
        btc_pnl_pct = (current_btc - avg_btc) / avg_btc * 100
        stop_loss_btc = avg_btc * 0.95  # 5% stop-loss
        
        results["btc"] = {
            "entry_price": avg_btc,
            "current_price": current_btc,
            "pnl_pct": btc_pnl_pct,
            "stop_loss_price": stop_loss_btc,
            "stop_loss_triggered": current_btc <= stop_loss_btc,
            "num_trades": len(btc_trades),
            "total_investment": sum(btc_trades)
        }
    
    # Analyze ETH
    if eth_trades:
        avg_eth = sum(eth_trades) / len(eth_trades)
        current_eth = prices["eth"]
        eth_pnl_pct = (current_eth - avg_eth) / avg_eth * 100
        stop_loss_eth = avg_eth * 0.95  # 5% stop-loss
        
        results["eth"] = {
            "entry_price": avg_eth,
            "current_price": current_eth,
            "pnl_pct": eth_pnl_pct,
            "stop_loss_price": stop_loss_eth,
            "stop_loss_triggered": current_eth <= stop_loss_eth,
            "num_trades": len(eth_trades),
            "total_investment": sum(eth_trades)
        }
    
    return results

def log_to_file(filename, message):
    """Append message to log file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def main():
    print("=== COMPREHENSIVE POSITION MONITOR ===")
    print("Checking positions against 5% stop-loss threshold")
    print()
    
    # Load trades
    trades = load_trades()
    if not trades:
        print("No trades found. Exiting.")
        return 1
    
    print(f"Loaded {len(trades)} trades from completed_trades.json")
    
    # Get current prices
    prices = get_current_prices()
    if not prices:
        print("Failed to get current prices. Exiting.")
        return 1
    
    print(f"Current BTC Price: ${prices['btc']:,.2f}")
    print(f"Current ETH Price: ${prices['eth']:,.2f}")
    print()
    
    # Analyze positions
    results = analyze_positions(trades, prices)
    
    critical_alerts = []
    
    # Display BTC results
    if "btc" in results:
        btc = results["btc"]
        print("=== BTC POSITION ===")
        print(f"Number of trades: {btc['num_trades']}")
        print(f"Average entry price: ${btc['entry_price']:,.2f}")
        print(f"Current price: ${btc['current_price']:,.2f}")
        print(f"P&L: {btc['pnl_pct']:.2f}%")
        print(f"5% Stop-loss level: ${btc['stop_loss_price']:,.2f}")
        
        if btc['stop_loss_triggered']:
            print(f"🚨 BTC STOP-LOSS TRIGGERED! Current price is ${btc['current_price'] - btc['stop_loss_price']:,.2f} below stop-loss")
            critical_alerts.append(f"BTC STOP-LOSS TRIGGERED: Price ${btc['current_price']:,.2f} below stop-loss ${btc['stop_loss_price']:,.2f}")
        else:
            print(f"✅ BTC position within limits ({btc['current_price'] - btc['stop_loss_price']:,.2f} above stop-loss)")
        print()
    
    # Display ETH results
    if "eth" in results:
        eth = results["eth"]
        print("=== ETH POSITION ===")
        print(f"Number of trades: {eth['num_trades']}")
        print(f"Average entry price: ${eth['entry_price']:,.2f}")
        print(f"Current price: ${eth['current_price']:,.2f}")
        print(f"P&L: {eth['pnl_pct']:.2f}%")
        print(f"5% Stop-loss level: ${eth['stop_loss_price']:,.2f}")
        
        if eth['stop_loss_triggered']:
            print(f"🚨 ETH STOP-LOSS TRIGGERED! Current price is ${eth['current_price'] - eth['stop_loss_price']:,.2f} below stop-loss")
            critical_alerts.append(f"ETH STOP-LOSS TRIGGERED: Price ${eth['current_price']:,.2f} below stop-loss ${eth['stop_loss_price']:,.2f}")
        else:
            print(f"✅ ETH position within limits ({eth['current_price'] - eth['stop_loss_price']:,.2f} above stop-loss)")
        print()
    
    # Log results
    log_message = f"Comprehensive Check - BTC: ${prices['btc']:,.2f}, ETH: ${prices['eth']:,.2f}"
    if "btc" in results:
        log_message += f", BTC P&L: {results['btc']['pnl_pct']:.2f}%"
    if "eth" in results:
        log_message += f", ETH P&L: {results['eth']['pnl_pct']:.2f}%"
    
    log_to_file("trading_monitoring.log", log_message)
    
    # Log critical alerts
    if critical_alerts:
        print("=== CRITICAL ALERTS ===")
        for alert in critical_alerts:
            print(f"⚠️  {alert}")
            log_to_file("critical_alerts.log", alert)
        
        # Add detailed summary
        summary = f"STOP-LOSS FAILURE SUMMARY - System shows positions below stop-loss but no exit orders executed"
        log_to_file("critical_alerts.log", summary)
        
        return 2  # Exit with error code for stop-loss triggers
    
    print("✅ All positions within stop-loss limits.")
    return 0

if __name__ == "__main__":
    sys.exit(main())