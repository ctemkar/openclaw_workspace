#!/usr/bin/env python3
import json
import datetime
import sys

# Current market prices (from CoinGecko API)
current_prices = {
    "BTC/USD": 67842.0,
    "ETH/USD": 2068.6
}

# Risk parameters from dashboard
risk_params = {
    "stop_loss": 0.05,  # 5%
    "take_profit": 0.10  # 10%
}

# Trades data from /trades endpoint
trades_data = {
    "count": 5,
    "timestamp": "2026-03-31T10:20:11.393607",
    "trades": [
        {"price": 2325.28, "quantity": 0.086, "reason": "Near support level: $2308.08 (current: $2325.28)", "side": "BUY", "symbol": "ETH/USD", "time": "13:39:49"},
        {"price": 2193.6, "quantity": 0.0912, "reason": "Near support level: $2167.99 (current: $2193.60)", "side": "BUY", "symbol": "ETH/USD", "time": "00:33:02"},
        {"price": 67247.51, "quantity": 0.002974, "reason": "Near support level: $67110.20 (current: $67247.51)", "side": "BUY", "symbol": "BTC/USD", "time": "21:29:41"},
        {"price": 2052.38, "quantity": 0.0974, "reason": "Near support level: $2033.94 (current: $2052.38)", "side": "BUY", "symbol": "ETH/USD", "time": "21:29:42"},
        {"price": 2021.51, "quantity": 0.2474, "reason": "Conservative entry: ETH showing +0.68% 24h momentum. Risk/Reward 1:2 with 5% stop-loss ($1,920.43) and 10% take-profit ($2,223.66)", "side": "BUY", "symbol": "ETH/USD", "time": "07:24:00"}
    ]
}

def analyze_trades():
    alerts = []
    critical_alerts = []
    
    print("=== TRADING POSITION ANALYSIS ===")
    print(f"Analysis Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Current Prices: BTC=${current_prices['BTC/USD']:,.2f}, ETH=${current_prices['ETH/USD']:,.2f}")
    print(f"Risk Parameters: Stop-loss={risk_params['stop_loss']*100}%, Take-profit={risk_params['take_profit']*100}%")
    print()
    
    total_investment = 0
    total_current_value = 0
    
    for i, trade in enumerate(trades_data['trades']):
        symbol = trade['symbol']
        entry_price = trade['price']
        quantity = trade['quantity']
        side = trade['side']
        time = trade['time']
        
        current_price = current_prices.get(symbol)
        if not current_price:
            print(f"Warning: No current price for {symbol}")
            continue
        
        # Calculate P&L
        investment = entry_price * quantity
        current_value = current_price * quantity
        pnl = current_value - investment
        pnl_percent = (pnl / investment) * 100
        
        total_investment += investment
        total_current_value += current_value
        
        # Check stop-loss and take-profit
        stop_loss_price = entry_price * (1 - risk_params['stop_loss'])
        take_profit_price = entry_price * (1 + risk_params['take_profit'])
        
        print(f"Trade {i+1}: {symbol} {side} @ ${entry_price:,.2f}")
        print(f"  Quantity: {quantity}, Investment: ${investment:,.2f}")
        print(f"  Current Price: ${current_price:,.2f}, Current Value: ${current_value:,.2f}")
        print(f"  P&L: ${pnl:,.2f} ({pnl_percent:+.2f}%)")
        print(f"  Stop-loss: ${stop_loss_price:,.2f} ({risk_params['stop_loss']*100}% below entry)")
        print(f"  Take-profit: ${take_profit_price:,.2f} ({risk_params['take_profit']*100}% above entry)")
        
        # Check for alerts
        if current_price <= stop_loss_price:
            alert_msg = f"🚨 STOP-LOSS TRIGGERED: {symbol} at ${current_price:,.2f} (entry: ${entry_price:,.2f}, stop-loss: ${stop_loss_price:,.2f})"
            critical_alerts.append(alert_msg)
            print(f"  ⚠️  {alert_msg}")
        elif current_price >= take_profit_price:
            alert_msg = f"🎯 TAKE-PROFIT TRIGGERED: {symbol} at ${current_price:,.2f} (entry: ${entry_price:,.2f}, take-profit: ${take_profit_price:,.2f})"
            alerts.append(alert_msg)
            print(f"  ✅ {alert_msg}")
        elif pnl_percent < -3:
            alert_msg = f"⚠️  Drawdown Warning: {symbol} down {abs(pnl_percent):.2f}% (entry: ${entry_price:,.2f}, current: ${current_price:,.2f})"
            alerts.append(alert_msg)
            print(f"  ⚠️  {alert_msg}")
        elif pnl_percent > 5:
            alert_msg = f"📈 Profit Alert: {symbol} up {pnl_percent:.2f}% (entry: ${entry_price:,.2f}, current: ${current_price:,.2f})"
            alerts.append(alert_msg)
            print(f"  📈 {alert_msg}")
        
        print()
    
    # Overall portfolio analysis
    total_pnl = total_current_value - total_investment
    total_pnl_percent = (total_pnl / total_investment * 100) if total_investment > 0 else 0
    
    print("=== PORTFOLIO SUMMARY ===")
    print(f"Total Investment: ${total_investment:,.2f}")
    print(f"Total Current Value: ${total_current_value:,.2f}")
    print(f"Total P&L: ${total_pnl:,.2f} ({total_pnl_percent:+.2f}%)")
    
    # Check for critical drawdown
    if total_pnl_percent < -7:
        critical_msg = f"🚨 CRITICAL DRAWDOWN: Portfolio down {abs(total_pnl_percent):.2f}% (${abs(total_pnl):,.2f})"
        critical_alerts.append(critical_msg)
        print(f"⚠️  {critical_msg}")
    elif total_pnl_percent < -3:
        alert_msg = f"⚠️  Portfolio Drawdown: Down {abs(total_pnl_percent):.2f}% (${abs(total_pnl):,.2f})"
        alerts.append(alert_msg)
        print(f"⚠️  {alert_msg}")
    
    return alerts, critical_alerts, total_investment, total_current_value, total_pnl_percent

if __name__ == "__main__":
    alerts, critical_alerts, total_inv, total_val, total_pnl_pct = analyze_trades()
    
    # Log to monitoring file
    with open("/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log", "a") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Monitoring Check: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Portfolio Value: ${total_val:,.2f} (P&L: {total_pnl_pct:+.2f}%)\n")
        f.write(f"Alerts: {len(alerts)}, Critical: {len(critical_alerts)}\n")
        for alert in alerts:
            f.write(f"  - {alert}\n")
        for critical in critical_alerts:
            f.write(f"  ⚠️ {critical}\n")
    
    # Log critical alerts to separate file
    if critical_alerts:
        with open("/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log", "a") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Critical Alert: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            for critical in critical_alerts:
                f.write(f"{critical}\n")