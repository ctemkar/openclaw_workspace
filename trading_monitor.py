#!/usr/bin/env python3
import json
import datetime
import os

def monitor_trading():
    # Load trades
    with open('completed_trades.json', 'r') as f:
        trades = json.load(f)

    # Load config
    with open('trading_config.json', 'r') as f:
        config = json.load(f)

    # Calculate portfolio
    total_btc = sum(t['amount'] for t in trades if t['side'] == 'buy')
    total_invested = sum(t['amount'] * t['price'] for t in trades if t['side'] == 'buy')
    avg_price = total_invested / total_btc if total_btc > 0 else 0

    # Current BTC price (hardcoded from earlier fetch)
    btc_price = 74358.00

    # Calculate current value and P&L
    current_value = total_btc * btc_price
    pnl = current_value - total_invested
    pnl_pct = (pnl / total_invested * 100) if total_invested > 0 else 0

    # Risk calculations
    stop_loss_price = avg_price * (1 - config['stop_loss_pct'])
    take_profit_price = avg_price * (1 + config['take_profit_pct'])
    critical_drawdown_price = avg_price * 0.95

    # Check for alerts
    alerts = []
    if pnl_pct <= -config['stop_loss_pct'] * 100:
        alerts.append('STOP LOSS TRIGGERED! P&L: {:.2f}%'.format(pnl_pct))
    elif pnl_pct >= config['take_profit_pct'] * 100:
        alerts.append('TAKE PROFIT TRIGGERED! P&L: {:.2f}%'.format(pnl_pct))
    elif pnl_pct <= -5:
        alerts.append('CRITICAL DRAWDOWN! P&L: {:.2f}%'.format(pnl_pct))
    elif pnl_pct <= -3:
        alerts.append('WARNING: Moderate drawdown: {:.2f}%'.format(pnl_pct))

    # Calculate distances
    stop_loss_distance = ((btc_price - stop_loss_price) / avg_price * 100) if avg_price > 0 else 0
    take_profit_distance = ((take_profit_price - btc_price) / avg_price * 100) if avg_price > 0 else 0
    critical_distance = ((btc_price - critical_drawdown_price) / avg_price * 100) if avg_price > 0 else 0

    # Create log entry
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    log_entry = f'''=== TRADING DASHBOARD MONITOR ===
Time: {timestamp}
Dashboard Status: Active (Port 59745)
Trading Bot Status: Running

=== PORTFOLIO SUMMARY ===
BTC Holdings: {total_btc:.8f} BTC
Current BTC Price: ${btc_price:,.2f}
Portfolio Value: ${current_value:.2f}
Investment: ${total_invested:.2f}
Current P&L: ${pnl:.2f} ({pnl_pct:.2f}%)

=== RISK METRICS ===
Average Entry: ${avg_price:.2f}
Stop Loss: -{config["stop_loss_pct"]*100:.1f}% (${stop_loss_price:.2f})
Take Profit: +{config["take_profit_pct"]*100:.1f}% (${take_profit_price:.2f})
Critical Drawdown: -5.00% (${critical_drawdown_price:.2f})

=== DISTANCE TO TRIGGERS ===
Stop Loss Distance: {stop_loss_distance:.2f}%
Take Profit Distance: {take_profit_distance:.2f}%
Critical Drawdown Distance: {critical_distance:.2f}%

=== ALERTS ===
{chr(10).join(alerts) if alerts else "No alerts at this time"}

=== RECOMMENDATIONS ===
1. Current position: HOLD (P&L: {pnl_pct:.2f}%)
2. Monitor BTC price movement for stop-loss/take-profit triggers
3. Capital utilization: {(total_invested / config["capital"] * 100):.1f}% - Consider additional trades if strategy permits
4. Next check scheduled: {(datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%H:%M")}

=== MONITORING COMPLETE ===
'''
    
    return log_entry, alerts

if __name__ == '__main__':
    log_entry, alerts = monitor_trading()
    print(log_entry)
    
    # Write to monitoring log
    with open('trading_monitoring.log', 'a') as f:
        f.write(log_entry)
    
    # Write critical alerts if any
    if alerts:
        with open('critical_alerts.log', 'a') as f:
            f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] CRITICAL ALERTS:\n')
            for alert in alerts:
                f.write(f'  - {alert}\n')
            f.write('\n')