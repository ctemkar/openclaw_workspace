import json
import datetime
import sys

def analyze_trading_data():
    # Parse the status data (from curl output)
    status_data = {
        'analysis_scheduled': 'hourly',
        'capital': 135.5,
        'last_analysis': '2026-03-31T17:39:36.973070',
        'pnl': {
            'binance': {
                'open_positions': 4,
                'realized': 0.0,
                'total': 0.8489641113192214,
                'trades': 4,
                'unrealized': 0.8489641113192214
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
                'total': 0.8489641113192214,
                'unrealized': 0.8489641113192214
            }
        },
        'port': 5001,
        'risk_parameters': {
            'max_trades_per_day': 999,
            'stop_loss': 0.05,
            'take_profit': 0.1
        },
        'status': 'running',
        'timestamp': '2026-03-31T17:53:17.081483',
        'trading_pairs': ['BTC/USD', 'ETH/USD', 'SOL/USD', 'ADA/USD', 'XRP/USD', 'DOT/USD', 'DOGE/USD', 'AVAX/USD', 'MATIC/USD', 'LINK/USD']
    }
    
    # Parse trades data
    trades_data = {
        'count': 5,
        'timestamp': '2026-03-31T17:53:26.316810',
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
    analysis_output.append(f'Dashboard Status: {status_data["status"]}')
    analysis_output.append(f'Capital: ${status_data["capital"]:.2f}')
    analysis_output.append(f'Last Analysis: {status_data["last_analysis"]}')
    analysis_output.append('')
    
    analysis_output.append('=== PnL ANALYSIS ===')
    pnl = status_data['pnl']['total']
    analysis_output.append(f'Total PnL: ${pnl["total"]:.4f}')
    analysis_output.append(f'Unrealized PnL: ${pnl["unrealized"]:.4f}')
    analysis_output.append(f'Realized PnL: ${pnl["realized"]:.4f}')
    analysis_output.append(f'Open Positions: {pnl["open_positions"]}')
    analysis_output.append('')
    
    analysis_output.append('=== RISK PARAMETERS ===')
    risk = status_data['risk_parameters']
    analysis_output.append(f'Stop Loss: {risk["stop_loss"]*100}%')
    analysis_output.append(f'Take Profit: {risk["take_profit"]*100}%')
    analysis_output.append(f'Max Trades/Day: {risk["max_trades_per_day"]}')
    analysis_output.append('')
    
    analysis_output.append('=== TRADES SUMMARY ===')
    analysis_output.append(f'Total Trades: {trades_data["count"]}')
    for i, trade in enumerate(trades_data['trades'], 1):
        analysis_output.append(f'{i}. {trade["symbol"]} - {trade["side"]} @ ${trade["price"]:.2f} ({trade["quantity"]}) - {trade["time"]}')
    analysis_output.append('')
    
    # Check for critical conditions
    critical_alerts = []
    capital = status_data['capital']
    initial_capital = 250.0  # From dashboard config
    drawdown = ((initial_capital - capital) / initial_capital) * 100
    
    analysis_output.append('=== RISK ASSESSMENT ===')
    analysis_output.append(f'Initial Capital: ${initial_capital:.2f}')
    analysis_output.append(f'Current Capital: ${capital:.2f}')
    analysis_output.append(f'Drawdown: {drawdown:.2f}%')
    
    if drawdown > 10:
        critical_alerts.append(f'CRITICAL: High drawdown detected: {drawdown:.2f}% (above 10% threshold)')
        analysis_output.append(f'⚠️  ALERT: High drawdown: {drawdown:.2f}%')
    
    if pnl['total'] < -20:
        critical_alerts.append(f'CRITICAL: Significant losses: ${pnl["total"]:.2f}')
        analysis_output.append(f'⚠️  ALERT: Significant losses: ${pnl["total"]:.2f}')
    
    if pnl['open_positions'] > 5:
        critical_alerts.append(f'WARNING: High number of open positions: {pnl["open_positions"]}')
        analysis_output.append(f'⚠️  WARNING: High open positions: {pnl["open_positions"]}')
    
    analysis_output.append('')
    
    if critical_alerts:
        analysis_output.append('=== CRITICAL ALERTS DETECTED ===')
        for alert in critical_alerts:
            analysis_output.append(f'🔴 {alert}')
    else:
        analysis_output.append('✅ No critical alerts detected. System operating within normal parameters.')
    
    return '\n'.join(analysis_output), critical_alerts

if __name__ == '__main__':
    analysis, critical_alerts = analyze_trading_data()
    print(analysis)
    
    # Write to monitoring log
    with open('/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log', 'a') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Monitoring Check: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n")
        f.write(analysis)
        f.write("\n")
    
    # Write critical alerts if any
    if critical_alerts:
        with open('/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log', 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"CRITICAL ALERT: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
            for alert in critical_alerts:
                f.write(f"{alert}\n")
            f.write("\n")