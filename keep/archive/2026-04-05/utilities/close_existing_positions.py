#!/usr/bin/env python3
"""
Close existing BTC positions from previous trading bot
"""

import json
import subprocess
import time
from datetime import datetime

def get_gemini_credentials():
    """Get Gemini API credentials"""
    try:
        key = subprocess.check_output(
            ["security", "find-generic-password", "-s", "GEMINI_API_KEY", "-w"],
            timeout=2
        ).decode().strip()
        secret = subprocess.check_output(
            ["security", "find-generic-password", "-s", "GEMINI_SECRET", "-w"],
            timeout=2
        ).decode().strip()
        return key, secret
    except:
        try:
            with open(".gemini_key", "r") as f:
                key = f.read().strip()
            with open(".gemini_secret", "r") as f:
                secret = f.read().strip()
            return key, secret
        except:
            return None, None

def get_current_btc_price():
    """Get current BTC price"""
    try:
        import requests
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"}
        )
        if response.status_code == 200:
            return response.json()["bitcoin"]["usd"]
    except:
        return None

def analyze_positions():
    """Analyze existing positions and provide closure recommendations"""
    print("=" * 60)
    print("EXISTING POSITION ANALYSIS & CLOSURE RECOMMENDATIONS")
    print("=" * 60)
    
    # Load existing trades
    try:
        with open("completed_trades.json", "r") as f:
            trades = json.load(f)
    except:
        print("ERROR: Could not load completed_trades.json")
        return
    
    # Filter for BTC buy positions
    btc_buys = [t for t in trades if t.get("side") == "buy"]
    
    if not btc_buys:
        print("\nNo existing BTC buy positions found.")
        return
    
    print(f"\nFound {len(btc_buys)} BTC buy positions:")
    print("-" * 40)
    
    total_btc = 0
    total_cost = 0
    
    for i, trade in enumerate(btc_buys, 1):
        amount = trade.get("amount", 0)
        price = trade.get("price", 0)
        cost = amount * price
        
        total_btc += amount
        total_cost += cost
        
        print(f"Position {i}:")
        print(f"  Amount: {amount:.8f} BTC")
        print(f"  Entry Price: ${price:,.2f}")
        print(f"  Cost: ${cost:,.2f}")
        print(f"  Time: {trade.get('time', 'N/A')}")
        print()
    
    # Get current price
    current_price = get_current_btc_price()
    if current_price:
        print(f"\nCurrent BTC Price: ${current_price:,.2f}")
        
        current_value = total_btc * current_price
        pnl = current_value - total_cost
        pnl_pct = (pnl / total_cost) * 100
        
        print(f"\nPOSITION SUMMARY:")
        print(f"  Total BTC: {total_btc:.8f}")
        print(f"  Total Cost: ${total_cost:,.4f}")
        print(f"  Current Value: ${current_value:,.4f}")
        print(f"  P&L: ${pnl:,.4f} ({pnl_pct:.2f}%)")
        
        # Check stop-loss
        stop_loss_price = total_cost / total_btc * 0.95  # 5% stop-loss
        print(f"\nSTOP-LOSS ANALYSIS:")
        print(f"  Average Entry: ${total_cost/total_btc:,.2f}")
        print(f"  5% Stop-Loss Level: ${stop_loss_price:,.2f}")
        
        if current_price < stop_loss_price:
            print(f"  ⚠️  STOP-LOSS TRIGGERED: Current price below stop-loss")
            print(f"  🔴 IMMEDIATE CLOSURE RECOMMENDED")
        else:
            distance_to_stop = ((current_price - stop_loss_price) / stop_loss_price) * 100
            print(f"  Distance to Stop-Loss: {distance_to_stop:.2f}%")
            
            if pnl_pct < -2:
                print(f"  🟡 WARNING: Position losing value ({pnl_pct:.2f}%)")
                print(f"  🟡 CONSIDER CLOSING to prevent further losses")
            else:
                print(f"  🟢 Position within acceptable risk range")
    
    print("\n" + "=" * 60)
    print("CLOSURE RECOMMENDATIONS:")
    print("=" * 60)
    
    print("\n1. MANUAL CLOSURE VIA GEMINI WEB INTERFACE:")
    print("   • Login to Gemini.com")
    print("   • Navigate to Trading → BTC/USD")
    print(f"   • Sell {total_btc:.8f} BTC at market price")
    print("   • Confirm trade execution")
    
    print("\n2. UPDATE TRADE RECORDS:")
    print("   • Add 'closed' field to trades in completed_trades.json")
    print("   • Record closure price and time")
    print("   • Calculate final P&L")
    
    print("\n3. PREVENT FUTURE ISSUES:")
    print("   • Review why previous bot's stop-loss failed")
    print("   • Implement health monitoring for trading scripts")
    print("   • Set up alerts for position management")
    
    print("\n" + "=" * 60)
    print("EXECUTION COMMANDS (if using API):")
    print("=" * 60)
    
    api_key, api_secret = get_gemini_credentials()
    if api_key and api_secret:
        print(f"\nAPI Key available: {api_key[:8]}...")
        print("\nTo close via API (Python):")
        print(f"""
import ccxt
exchange = ccxt.gemini({{
    'apiKey': '{api_key[:8]}...',
    'secret': '{api_secret[:8]}...',
    'enableRateLimit': True
}})

# Sell all BTC
amount = {total_btc:.8f}
order = exchange.create_market_sell_order('BTC/USD', amount)
print(f"Sold {{amount}} BTC")
        """)
    else:
        print("\n⚠️  Gemini API credentials not found")
        print("   Manual closure via web interface required")

if __name__ == "__main__":
    analyze_positions()