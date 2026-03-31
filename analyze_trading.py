#!/usr/bin/env python3
import json
import datetime
import sys

def analyze_trading_data():
    # Current data from status endpoint
    status_data = {
        'analysis_scheduled': 'hourly',
        'capital': 175.53,
        'last_analysis': '2026-03-31T13:37:42.037501',
        'pnl': {
            'binance': {
                'open_positions': 4,
                'realized': 0.0,
                'total': -1.6225342731146148,
                'trades': 4,
                'unrealized': -1.6225342731146148
            },
            'gemini': {
                'open_positions': 0,
                'realized': 0.0,
                'total': 0.0,
                'trades': 0,
                'unrealized': 0.0
            },
            'total': {
                'open_positions': 4,
                'realized': 0.0,
                'total': -1.6225342731146148,
                'trades': 4,
                'unrealized': -1.6225342731146148
            }
        },
        'port': 5001,
        'risk_parameters': {
            'max_trades_per_day': 999,
            'stop_loss': 0.05,
            'take_profit': 0.1
        },
        'status': 'running',
        'timestamp': '2026-03-31T13:58:08.767444',
        'trading_pairs': ['BTC/USD', 'ETH/USD', 'SOL/USD', 'ADA/USD', 'XRP/USD', 'DOT/USD', 'DOGE/USD', 'AVAX/USD', 'MATIC/USD', 'LINK/USD']
    }

    # Trades data
    trades_data = {
        'count': 5,
        'timestamp': '2026-03-31T13:58:18.496322',
        'trades': [
            {
                'price': 2325.28,
                'quantity': 0.086,
                'reason': 'Near support level: $2308.08 (current: $2325.28)',
                'side': 'BUY',
                'symbol': 'ETH/USD',
                'time': '13:39:49'
            },
            {
                'price': 2193.6,
                'quantity': 0.0912,
                'reason': 'Near support level: $2167.99 (current: $2193.60)',
                'side': 'BUY',
                'symbol': 'ETH/USD',
                'time': '00:33:02'
            },
            {
                'price': 67247.51,
                'quantity': 0.002974,
                'reason': 'Near support level: $67110.20 (current: $67247.51)',
                'side': 'BUY',
                'symbol': 'BTC/USD',
                'time': '21:29:41'
            },
            {
                'price': 2052.38,
                'quantity': 0.0974,
                'reason': 'Near support level: $2033.94 (current: $2052.38)',
                'side': 'BUY',
                'symbol': 'ETH/USD',
                'time': '21:29:42'
            },
            {
                'price': 2021.51,
                'quantity': 0.2474,
                'reason': 'Conservative entry: ETH showing +0.68% 24h momentum. Risk/Reward 1:2 with 5% stop-loss ($1,920.43) and 10% take-profit ($2,223.66)',
                'side': 'BUY',
                'symbol': 'ETH/USD',
                'time': '07:24:00'
            }
        ]
    }

    analysis_output = []
    
    analysis_output.append('=== TRADING DASHBOARD ANALYSIS ===')
    analysis_output.append(f'Timestamp: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    analysis_output.append(f'System Status: {status_data["status"]}')
    analysis_output.append(f'Capital: ${status_data["capital"]:.2f}')
    analysis_output.append(f'Last Analysis: {status_data["last_analysis"]}')
    
    # P&L Analysis
    analysis_output.append('\n=== P&L ANALYSIS ===')
    total_pnl = status_data['pnl']['total']['total']
    unrealized_pnl = status_data['pnl']['total']['unrealized']
    open_positions = status_data['pnl']['total']['open_positions']
    
    analysis_output.append(f'Total P&L: ${total_pnl:.4f}')
    analysis_output.append(f'Unrealized P&L: ${unrealized_pnl:.4f}')
    analysis_output.append(f'Open Positions: {open_positions}')
    
    # Binance specific
    binance_pnl = status_data['pnl']['binance']['total']
    binance_trades = status_data['pnl']['binance']['trades']
    analysis_output.append(f'Binance P&L: ${binance_pnl:.4f} ({binance_trades} trades)')
    
    # Risk Parameters
    analysis_output.append('\n=== RISK PARAMETERS ===')
    analysis_output.append(f'Stop Loss: {status_data["risk_parameters"]["stop_loss"]*100}%')
    analysis_output.append(f'Take Profit: {status_data["risk_parameters"]["take_profit"]*100}%')
    analysis_output.append(f'Max Trades/Day: {status_data["risk_parameters"]["max_trades_per_day"]}')
    
    # Trades Analysis
    analysis_output.append('\n=== RECENT TRADES ===')
    analysis_output.append(f'Total Trades: {trades_data["count"]}')
    for i, trade in enumerate(trades_data['trades'][:3], 1):
        analysis_output.append(f'{i}. {trade["symbol"]} - {trade["side"]} @ ${trade["price"]:.2f} ({trade["time"]})')
    
    # Critical Alerts
    analysis_output.append('\n=== ALERT ANALYSIS ===')
    alerts = []
    critical_alerts = []
    
    # Check capital drawdown
    initial_capital = 250.00
    current_capital = status_data['capital']
    drawdown = ((initial_capital - current_capital) / initial_capital) * 100
    
    if drawdown > 10:
        alert_msg = f'⚠️ CRITICAL: Capital drawdown {drawdown:.1f}% (${initial_capital:.2f} → ${current_capital:.2f})'
        alerts.append(alert_msg)
        critical_alerts.append(alert_msg)
    elif drawdown > 5:
        alert_msg = f'⚠️ WARNING: Capital drawdown {drawdown:.1f}% (${initial_capital:.2f} → ${current_capital:.2f})'
        alerts.append(alert_msg)
    
    # Check P&L
    if total_pnl < -20:
        alert_msg = f'⚠️ CRITICAL: Total P&L loss exceeds $20 (${total_pnl:.2f})'
        alerts.append(alert_msg)
        critical_alerts.append(alert_msg)
    elif total_pnl < -10:
        alert_msg = f'⚠️ WARNING: Total P&L loss exceeds $10 (${total_pnl:.2f})'
        alerts.append(alert_msg)
    
    # Check open positions
    if open_positions > 5:
        alert_msg = f'⚠️ WARNING: High number of open positions ({open_positions})'
        alerts.append(alert_msg)
    
    # Check if any trades might be near stop-loss
    if unrealized_pnl < -5:
        alert_msg = f'⚠️ WARNING: Significant unrealized losses (${unrealized_pnl:.2f})'
        alerts.append(alert_msg)
    
    if alerts:
        for alert in alerts:
            analysis_output.append(alert)
    else:
        analysis_output.append('✅ No critical alerts detected')
    
    analysis_output.append('\n=== RECOMMENDATIONS ===')
    if drawdown > 5:
        analysis_output.append('1. Consider reducing position sizes or taking a break from trading')
    if open_positions > 3:
        analysis_output.append('2. Consider closing some positions to manage risk')
    if total_pnl < 0:
        analysis_output.append('3. Review trading strategy and consider adjusting stop-loss/take-profit levels')
    
    # Log to monitoring file
    monitoring_log = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
    with open(monitoring_log, 'a') as f:
        f.write('\n' + '='*60 + '\n')
        f.write(f'Trading Dashboard Monitor - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write('='*60 + '\n')
        for line in analysis_output:
            f.write(line + '\n')
    
    # Log critical alerts to separate file
    if critical_alerts:
        critical_log = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'
        with open(critical_log, 'a') as f:
            f.write('\n' + '='*60 + '\n')
            f.write(f'CRITICAL ALERTS - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write('='*60 + '\n')
            for alert in critical_alerts:
                f.write(alert + '\n')
    
    return '\n'.join(analysis_output), critical_alerts

if __name__ == '__main__':
    analysis, critical = analyze_trading_data()
    print(analysis)
    
    if critical:
        print('\n⚠️ CRITICAL ALERTS LOGGED TO FILE')
        for alert in critical:
            print(f'  - {alert}')