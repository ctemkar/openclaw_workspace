#!/usr/bin/env python3
import json
import sys
import math
from datetime import datetime

def analyze_trading_data():
    # Fetch data from status endpoint
    import subprocess
    result = subprocess.run(['curl', '-s', 'http://localhost:5001/status'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Failed to fetch trading data")
        return
    
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Invalid JSON response")
        return
    
    print('=== TRADING DASHBOARD ANALYSIS ===')
    print(f'Timestamp: {data.get("timestamp", "N/A")}')
    print(f'Capital: ${data.get("capital", 0):.2f}')
    print(f'Status: {data.get("status", "unknown")}')
    print(f'Last Analysis: {data.get("last_analysis", "N/A")}')
    
    print('\n=== P&L SUMMARY ===')
    pnl = data.get('pnl', {})
    total_pnl = pnl.get('total', {})
    print(f'Total P&L: ${total_pnl.get("total", 0):.2f}')
    print(f'  Unrealized: ${total_pnl.get("unrealized", 0):.2f}')
    print(f'  Realized: ${total_pnl.get("realized", 0):.2f}')
    print(f'  Open Positions: {total_pnl.get("open_positions", 0)}')
    
    print('\n=== EXCHANGE BREAKDOWN ===')
    gemini = pnl.get('gemini', {})
    binance = pnl.get('binance', {})
    
    print(f'Gemini (LONG):')
    print(f'  P&L: ${gemini.get("total", 0):.2f}')
    print(f'  Trades: {gemini.get("trades", 0)}')
    print(f'  Open Positions: {gemini.get("open_positions", 0)}')
    
    print(f'Binance (SHORT):')
    print(f'  P&L: ${binance.get("total", 0):.2f}')
    print(f'  Trades: {binance.get("trades", 0)}')
    print(f'  Open Positions: {binance.get("open_positions", 0)}')
    
    print('\n=== RISK PARAMETERS ===')
    risk = data.get('risk_parameters', {})
    print(f'Stop Loss: {risk.get("stop_loss", 0)*100:.1f}%')
    print(f'Take Profit: {risk.get("take_profit", 0)*100:.1f}%')
    print(f'Max Trades/Day: {risk.get("max_trades_per_day", 0)}')
    
    # Check for critical conditions
    print('\n=== ALERT ANALYSIS ===')
    critical_alerts = []
    
    # Get current values
    total_pnl_value = total_pnl.get('total', 0)
    capital = data.get('capital', 250.0)
    initial_capital = 250.0
    drawdown = (initial_capital - capital) / initial_capital * 100 if initial_capital > 0 else 0
    
    # Alert conditions
    if total_pnl_value < -10:  # More than $10 loss
        critical_alerts.append(f'⚠️ SIGNIFICANT LOSS: Total P&L is -${abs(total_pnl_value):.2f}')
    
    if drawdown > 5:  # More than 5% drawdown from initial capital
        critical_alerts.append(f'⚠️ HIGH DRAWDOWN: {drawdown:.1f}% from initial $250 capital')
    
    if binance.get('total', 0) < -5:  # Binance losses
        critical_alerts.append(f'⚠️ BINANCE LOSSES: ${abs(binance.get("total", 0)):.2f}')
    
    # Check if we have too many open positions
    if total_pnl.get('open_positions', 0) > 3:
        critical_alerts.append(f'⚠️ HIGH POSITION COUNT: {total_pnl.get("open_positions", 0)} open positions')
    
    # Check if stop-loss or take-profit would be triggered
    # Based on current P&L vs risk parameters
    stop_loss_pct = risk.get('stop_loss', 0.05) * 100
    take_profit_pct = risk.get('take_profit', 0.10) * 100
    
    # For each position, we'd need position-specific data
    # For now, check overall portfolio
    portfolio_return = (capital - initial_capital) / initial_capital * 100
    
    if portfolio_return <= -stop_loss_pct:
        critical_alerts.append(f'🚨 STOP-LOSS TRIGGERED: Portfolio at {portfolio_return:.1f}% (below -{stop_loss_pct:.1f}%)')
    
    if portfolio_return >= take_profit_pct:
        critical_alerts.append(f'🎯 TAKE-PROFIT TRIGGERED: Portfolio at {portfolio_return:.1f}% (above {take_profit_pct:.1f}%)')
    
    if critical_alerts:
        print('CRITICAL ALERTS FOUND:')
        for alert in critical_alerts:
            print(f'  {alert}')
    else:
        print('✅ No critical alerts detected')
    
    print('\n=== RECOMMENDATIONS ===')
    if total_pnl_value < 0:
        print('🔸 Consider reducing position sizes or tightening stop-losses')
    if binance.get('open_positions', 0) > 0 and binance.get('total', 0) < 0:
        print('🔸 Review Binance short positions - consider partial exits')
    if capital < 200:
        print('🔸 Capital below $200 - consider risk reduction')
    if total_pnl.get('open_positions', 0) >= 4:
        print('🔸 High number of open positions - consider consolidating')
    
    # Log to monitoring file
    log_entry = f"""
[{datetime.now().isoformat()}] Trading Dashboard Analysis
Capital: ${capital:.2f}
Total P&L: ${total_pnl_value:.2f}
Open Positions: {total_pnl.get('open_positions', 0)}
Alerts: {len(critical_alerts)}
Status: {'CRITICAL' if critical_alerts else 'NORMAL'}
"""
    
    with open('/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log', 'a') as f:
        f.write(log_entry)
    
    # Log critical alerts separately
    if critical_alerts:
        alert_entry = f"""
[{datetime.now().isoformat()}] CRITICAL ALERTS
{chr(10).join(critical_alerts)}
Capital: ${capital:.2f}
Total P&L: ${total_pnl_value:.2f}
"""
        with open('/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log', 'a') as f:
            f.write(alert_entry)
    
    return critical_alerts, capital, total_pnl_value

if __name__ == '__main__':
    analyze_trading_data()