#!/usr/bin/env python3
import json
import sys
from datetime import datetime

def analyze_trades(trades_data):
    """Analyze trades for performance and risk metrics"""
    
    trades = trades_data.get('trades', [])
    total_trades = len(trades)
    
    print(f"=== TRADE ANALYSIS ===\n")
    print(f"Total Trades: {total_trades}")
    print(f"Timestamp: {trades_data.get('timestamp', 'N/A')}")
    
    # Categorize trades by model
    models = {}
    for trade in trades:
        model = trade.get('model', 'unknown')
        if model not in models:
            models[model] = []
        models[model].append(trade)
    
    print(f"\n=== TRADES BY MODEL ===")
    for model, model_trades in models.items():
        print(f"{model}: {len(model_trades)} trades")
    
    # Analyze BTC trades
    btc_trades = [t for t in trades if 'BTC' in str(t.get('symbol', '')) or 'BTC' in str(t.get('model', ''))]
    eth_trades = [t for t in trades if 'ETH' in str(t.get('symbol', '')) or 'ETH' in str(t.get('model', ''))]
    sol_trades = [t for t in trades if 'SOL' in str(t.get('symbol', '')) or 'SOL' in str(t.get('model', ''))]
    
    print(f"\n=== TRADES BY ASSET ===")
    print(f"BTC Trades: {len(btc_trades)}")
    print(f"ETH Trades: {len(eth_trades)}")
    print(f"SOL Trades: {len(sol_trades)}")
    
    # Calculate average prices
    if btc_trades:
        btc_prices = [t.get('price', 0) for t in btc_trades if t.get('price')]
        avg_btc_price = sum(btc_prices) / len(btc_prices) if btc_prices else 0
        print(f"\nBTC Average Price: ${avg_btc_price:,.2f}")
        print(f"BTC Price Range: ${min(btc_prices):,.2f} - ${max(btc_prices):,.2f}")
    
    if eth_trades:
        eth_prices = [t.get('price', 0) for t in eth_trades if t.get('price')]
        avg_eth_price = sum(eth_prices) / len(eth_prices) if eth_prices else 0
        print(f"ETH Average Price: ${avg_eth_price:,.2f}")
        print(f"ETH Price Range: ${min(eth_prices):,.2f} - ${max(eth_prices):,.2f}")
    
    # Check for stop-loss/take-profit triggers
    print(f"\n=== RISK ASSESSMENT ===")
    
    # Get current BTC price (approximate from last trade)
    current_btc_price = btc_prices[-1] if btc_prices else 0
    current_eth_price = eth_prices[-1] if eth_prices else 0
    
    # Dashboard parameters
    dashboard_stop_loss = 5.0  # 5%
    dashboard_take_profit = 10.0  # 10%
    
    # Trading API parameters  
    api_stop_loss = 1.0  # 1%
    api_take_profit = 2.0  # 2%
    
    print(f"Dashboard Parameters:")
    print(f"  - Stop Loss: {dashboard_stop_loss}%")
    print(f"  - Take Profit: {dashboard_take_profit}%")
    
    print(f"\nTrading API Parameters:")
    print(f"  - Stop Loss: {api_stop_loss}%")
    print(f"  - Take Profit: {api_take_profit}%")
    
    # Check for critical conditions
    print(f"\n=== CRITICAL CONDITIONS CHECK ===")
    
    # Check if any trades would hit stop loss
    if btc_trades:
        entry_price = btc_prices[0]  # First BTC trade
        stop_loss_price = entry_price * (1 - dashboard_stop_loss/100)
        take_profit_price = entry_price * (1 + dashboard_take_profit/100)
        
        print(f"BTC Entry Price: ${entry_price:,.2f}")
        print(f"Dashboard Stop Loss: ${stop_loss_price:,.2f} ({dashboard_stop_loss}% below entry)")
        print(f"Dashboard Take Profit: ${take_profit_price:,.2f} ({dashboard_take_profit}% above entry)")
        print(f"Current BTC Price: ${current_btc_price:,.2f}")
        
        # Calculate drawdown
        if current_btc_price < entry_price:
            drawdown = ((entry_price - current_btc_price) / entry_price) * 100
            print(f"Current Drawdown: {drawdown:.2f}%")
            
            if drawdown >= dashboard_stop_loss:
                print(f"⚠️ CRITICAL: BTC drawdown ({drawdown:.2f}%) exceeds stop loss ({dashboard_stop_loss}%)")
            elif drawdown >= dashboard_stop_loss * 0.8:
                print(f"⚠️ WARNING: BTC drawdown ({drawdown:.2f}%) approaching stop loss ({dashboard_stop_loss}%)")
        else:
            profit = ((current_btc_price - entry_price) / entry_price) * 100
            print(f"Current Profit: {profit:.2f}%")
            
            if profit >= dashboard_take_profit:
                print(f"✅ TAKE PROFIT: BTC profit ({profit:.2f}%) exceeds target ({dashboard_take_profit}%)")
            elif profit >= dashboard_take_profit * 0.8:
                print(f"⚠️ WARNING: BTC profit ({profit:.2f}%) approaching take profit ({dashboard_take_profit}%)")
    
    return {
        'total_trades': total_trades,
        'models': models,
        'btc_trades': len(btc_trades),
        'eth_trades': len(eth_trades),
        'sol_trades': len(sol_trades),
        'current_btc_price': current_btc_price,
        'current_eth_price': current_eth_price
    }

if __name__ == "__main__":
    # Read trades data from stdin or file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    
    analyze_trades(data)