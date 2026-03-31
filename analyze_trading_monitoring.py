#!/usr/bin/env python3
"""
Analyze trading data for monitoring
"""

import json
from datetime import datetime

def analyze_trades():
    """Analyze current trades for SL/TP triggers"""
    
    # Current price from dashboard API (as of 03:59)
    current_price = 83.12
    
    # Load trades
    with open('trading_data/trades.json') as f:
        trades = json.load(f)
    
    # SL/TP settings from trader code
    STOP_LOSS = 0.03  # 3%
    TAKE_PROFIT = 0.05  # 5%
    
    print('=== TRADE ANALYSIS ===')
    print(f'Current SOL Price: ${current_price:.3f}')
    print(f'Stop Loss: {STOP_LOSS*100:.0f}%')
    print(f'Take Profit: {TAKE_PROFIT*100:.0f}%')
    print()
    
    critical_alerts = []
    
    for trade in trades:
        entry_price = trade['price']
        stop_loss_price = entry_price * (1 - STOP_LOSS)  # For LONG positions, stop loss if price drops
        take_profit_price = entry_price * (1 + TAKE_PROFIT)  # For LONG positions, profit if price rises
        
        print(f'Trade {trade["id"]}:')
        print(f'  Entry: ${entry_price:.3f}')
        print(f'  Current: ${current_price:.3f}')
        print(f'  P&L: ${trade["unrealized_pl"]:.3f} ({trade["unrealized_pl_percent"]:.2f}%)')
        print(f'  Stop Loss: ${stop_loss_price:.3f} ({((stop_loss_price-entry_price)/entry_price*100):.1f}%)')
        print(f'  Take Profit: ${take_profit_price:.3f} ({((take_profit_price-entry_price)/entry_price*100):.1f}%)')
        
        # Check triggers
        if current_price <= stop_loss_price:
            alert_msg = f'⚠️  STOP LOSS TRIGGERED! Trade {trade["id"]}: Current price ${current_price:.3f} <= Stop Loss ${stop_loss_price:.3f}'
            print(f'  {alert_msg}')
            critical_alerts.append({
                'trade_id': trade['id'],
                'type': 'STOP_LOSS',
                'message': alert_msg,
                'entry_price': entry_price,
                'current_price': current_price,
                'stop_loss_price': stop_loss_price,
                'pnl': trade['unrealized_pl'],
                'pnl_percent': trade['unrealized_pl_percent']
            })
        elif current_price >= take_profit_price:
            alert_msg = f'✅ TAKE PROFIT TRIGGERED! Trade {trade["id"]}: Current price ${current_price:.3f} >= Take Profit ${take_profit_price:.3f}'
            print(f'  {alert_msg}')
            critical_alerts.append({
                'trade_id': trade['id'],
                'type': 'TAKE_PROFIT',
                'message': alert_msg,
                'entry_price': entry_price,
                'current_price': current_price,
                'take_profit_price': take_profit_price,
                'pnl': trade['unrealized_pl'],
                'pnl_percent': trade['unrealized_pl_percent']
            })
        else:
            print(f'  ✓ Within SL/TP range')
        print()
    
    return critical_alerts

def analyze_capital_drawdown():
    """Analyze capital drawdown indicators"""
    
    # Load capital data
    with open('trading_data/capital.json') as f:
        capital = json.load(f)
    
    # Load cumulative P&L from system (approximate from dashboard)
    # Initial capital: $946.97, Current: $531.65 (from dashboard code)
    initial_capital = 946.97
    current_capital = 531.65
    total_drawdown = initial_capital - current_capital
    drawdown_percent = (total_drawdown / initial_capital) * 100
    
    print('=== CAPITAL DRAWDOWN ANALYSIS ===')
    print(f'Initial Capital: ${initial_capital:.2f}')
    print(f'Current Capital: ${current_capital:.2f}')
    print(f'Total Drawdown: ${total_drawdown:.2f} ({drawdown_percent:.1f}%)')
    print(f'Recovery Needed: +{(total_drawdown/current_capital*100):.1f}% to break even')
    print()
    
    critical_alerts = []
    
    # Check for critical drawdown levels
    if drawdown_percent >= 40:
        alert_msg = f'🚨 CRITICAL DRAWDOWN: {drawdown_percent:.1f}% from initial capital'
        print(f'  {alert_msg}')
        critical_alerts.append({
            'type': 'CRITICAL_DRAWDOWN',
            'message': alert_msg,
            'drawdown_percent': drawdown_percent,
            'initial_capital': initial_capital,
            'current_capital': current_capital,
            'recovery_needed_percent': (total_drawdown/current_capital*100)
        })
    elif drawdown_percent >= 30:
        alert_msg = f'⚠️  HIGH DRAWDOWN: {drawdown_percent:.1f}% from initial capital'
        print(f'  {alert_msg}')
        critical_alerts.append({
            'type': 'HIGH_DRAWDOWN',
            'message': alert_msg,
            'drawdown_percent': drawdown_percent,
            'initial_capital': initial_capital,
            'current_capital': current_capital,
            'recovery_needed_percent': (total_drawdown/current_capital*100)
        })
    
    return critical_alerts

def main():
    """Main analysis function"""
    
    print(f'Trading Dashboard Monitoring - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)
    print()
    
    # Analyze trades for SL/TP triggers
    trade_alerts = analyze_trades()
    
    # Analyze capital drawdown
    capital_alerts = analyze_capital_drawdown()
    
    # Combine all alerts
    all_alerts = trade_alerts + capital_alerts
    
    # Save monitoring log
    with open('trading_monitoring.log', 'w') as f:
        f.write(f'Trading Dashboard Monitoring Report\n')
        f.write(f'Generated: {datetime.now().isoformat()}\n')
        f.write('=' * 60 + '\n\n')
        
        # Write trade analysis
        f.write('TRADE ANALYSIS:\n')
        f.write(f'Current SOL Price: $83.12\n')
        f.write(f'Stop Loss: 3%\n')
        f.write(f'Take Profit: 5%\n\n')
        
        with open('trading_data/trades.json') as tf:
            trades = json.load(tf)
            for trade in trades:
                f.write(f'Trade {trade["id"]}:\n')
                f.write(f'  Entry: ${trade["price"]:.3f}\n')
                f.write(f'  Current: $83.12\n')
                f.write(f'  P&L: ${trade["unrealized_pl"]:.3f} ({trade["unrealized_pl_percent"]:.2f}%)\n')
                f.write(f'  Status: {"STOP_LOSS_TRIGGERED" if 83.12 <= trade["price"] * 0.97 else "TAKE_PROFIT_TRIGGERED" if 83.12 >= trade["price"] * 1.05 else "WITHIN_SL_TP_RANGE"}\n\n')
        
        # Write capital analysis
        f.write('CAPITAL ANALYSIS:\n')
        f.write(f'Initial Capital: $946.97\n')
        f.write(f'Current Capital: $531.65\n')
        f.write(f'Drawdown: $415.32 (43.9%)\n')
        f.write(f'Recovery Needed: +78.1% to break even\n\n')
        
        # Write alerts summary
        f.write('ALERTS SUMMARY:\n')
        if all_alerts:
            for alert in all_alerts:
                f.write(f'  {alert["message"]}\n')
        else:
            f.write('  No critical alerts at this time.\n')
    
    print('=' * 60)
    print('Monitoring report saved to: trading_monitoring.log')
    
    # Save critical alerts if any
    if all_alerts:
        with open('critical_alerts.log', 'w') as f:
            f.write(f'CRITICAL TRADING ALERTS\n')
            f.write(f'Generated: {datetime.now().isoformat()}\n')
            f.write('=' * 60 + '\n\n')
            
            for alert in all_alerts:
                f.write(f'ALERT TYPE: {alert["type"]}\n')
                f.write(f'MESSAGE: {alert["message"]}\n')
                if 'trade_id' in alert:
                    f.write(f'TRADE ID: {alert["trade_id"]}\n')
                if 'drawdown_percent' in alert:
                    f.write(f'DRAWDOWN: {alert["drawdown_percent"]:.1f}%\n')
                f.write('-' * 40 + '\n')
            
            f.write(f'\nTotal Critical Alerts: {len(all_alerts)}\n')
        
        print(f'Critical alerts saved to: critical_alerts.log')
        print(f'Total critical alerts: {len(all_alerts)}')
    else:
        print('No critical alerts detected.')
    
    return all_alerts

if __name__ == '__main__':
    main()