#!/usr/bin/env python3
import json
import requests
from datetime import datetime

def fetch_dashboard_data():
    """Fetch all dashboard data"""
    data = {}
    
    try:
        # Get status
        response = requests.get('http://localhost:5001/status', timeout=10)
        if response.status_code == 200:
            data['status'] = response.json()
        
        # Get trades
        response = requests.get('http://localhost:5001/trades', timeout=10)
        if response.status_code == 200:
            data['trades'] = response.json()
        
        # Get summary for market data
        response = requests.get('http://localhost:5001/summary', timeout=10)
        if response.status_code == 200:
            data['summary_text'] = response.text
            
            # Parse key metrics from summary
            lines = response.text.split('\n')
            market_data = {}
            for line in lines:
                if 'BTC/USD:' in line and '$' in line:
                    parts = line.split('$')
                    if len(parts) > 1:
                        market_data['btc_price'] = float(parts[1].replace(',', '').strip())
                elif 'ETH/USD:' in line and '$' in line:
                    parts = line.split('$')
                    if len(parts) > 1:
                        market_data['eth_price'] = float(parts[1].replace(',', '').strip())
                elif 'Market Sentiment:' in line:
                    market_data['sentiment'] = line.split(':')[-1].strip()
                elif 'TRADING DECISION:' in line:
                    market_data['decision'] = line.split(':')[-1].strip()
            
            data['market'] = market_data
            
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
    
    return data

def analyze_trades_for_alerts(trades_data, market_prices):
    """Analyze trades for alerts"""
    alerts = []
    
    if 'trades' not in trades_data or 'trades' not in trades_data['trades']:
        return alerts
    
    trades = trades_data['trades']['trades']
    
    for trade in trades:
        symbol = trade.get('symbol', '')
        entry_price = trade.get('price', 0)
        quantity = trade.get('quantity', 0)
        side = trade.get('side', 'BUY')
        
        # Get current price
        if symbol == 'BTC/USD':
            current_price = market_prices.get('btc_price', 0)
        elif symbol == 'ETH/USD':
            current_price = market_prices.get('eth_price', 0)
        else:
            continue
        
        if not current_price or not entry_price:
            continue
        
        # Calculate P&L
        if side == 'BUY':
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
        else:
            pnl_pct = ((entry_price - current_price) / entry_price) * 100
        
        # Check triggers
        if pnl_pct <= -5.0:  # Stop-loss triggered
            alerts.append({
                'type': 'STOP_LOSS_TRIGGERED',
                'symbol': symbol,
                'entry_price': entry_price,
                'current_price': current_price,
                'pnl_pct': pnl_pct,
                'quantity': quantity,
                'side': side,
                'time': trade.get('time', ''),
                'reason': trade.get('reason', ''),
                'position_value': entry_price * quantity,
                'current_value': current_price * quantity,
                'loss_amount': (current_price - entry_price) * quantity if side == 'BUY' else (entry_price - current_price) * quantity
            })
        elif pnl_pct >= 10.0:  # Take-profit triggered
            alerts.append({
                'type': 'TAKE_PROFIT_TRIGGERED',
                'symbol': symbol,
                'entry_price': entry_price,
                'current_price': current_price,
                'pnl_pct': pnl_pct,
                'quantity': quantity,
                'side': side,
                'time': trade.get('time', ''),
                'reason': trade.get('reason', ''),
                'position_value': entry_price * quantity,
                'current_value': current_price * quantity,
                'profit_amount': (current_price - entry_price) * quantity if side == 'BUY' else (entry_price - current_price) * quantity
            })
        elif pnl_pct <= -3.0:  # Approaching stop-loss
            alerts.append({
                'type': 'APPROACHING_STOP_LOSS',
                'symbol': symbol,
                'entry_price': entry_price,
                'current_price': current_price,
                'pnl_pct': pnl_pct,
                'quantity': quantity,
                'side': side,
                'time': trade.get('time', ''),
                'reason': trade.get('reason', ''),
                'warning': f'Only {abs(pnl_pct + 5.0):.1f}% from stop-loss',
                'position_value': entry_price * quantity
            })
    
    return alerts

def main():
    """Main function to create logs"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Fetch data
    print(f"Fetching dashboard data at {timestamp}...")
    data = fetch_dashboard_data()
    
    if not data:
        print("Failed to fetch dashboard data")
        return
    
    # Analyze for alerts
    market_prices = data.get('market', {})
    alerts = analyze_trades_for_alerts(data, market_prices)
    
    # Prepare monitoring log entry
    monitoring_log = {
        'timestamp': timestamp,
        'system_status': data.get('status', {}).get('status', 'unknown'),
        'capital': data.get('status', {}).get('capital', 0),
        'last_analysis': data.get('status', {}).get('last_analysis', ''),
        'market_data': market_prices,
        'total_trades': len(data.get('trades', {}).get('trades', [])) if 'trades' in data else 0,
        'alerts_count': len(alerts),
        'alerts': alerts,
        'critical_alerts': [a for a in alerts if 'TRIGGERED' in a['type']]
    }
    
    # Write to monitoring log
    monitoring_log_path = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
    try:
        with open(monitoring_log_path, 'a') as f:
            f.write(json.dumps(monitoring_log, indent=2) + '\n\n')
        print(f"Monitoring log updated: {monitoring_log_path}")
    except Exception as e:
        print(f"Error writing monitoring log: {e}")
    
    # Write critical alerts to separate log
    critical_alerts = [a for a in alerts if 'TRIGGERED' in a['type']]
    if critical_alerts:
        critical_log_path = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'
        critical_entry = {
            'timestamp': timestamp,
            'critical_alert_count': len(critical_alerts),
            'alerts': critical_alerts,
            'total_exposure': sum(a.get('position_value', 0) for a in critical_alerts),
            'total_loss': sum(a.get('loss_amount', 0) for a in critical_alerts if 'loss_amount' in a),
            'total_profit': sum(a.get('profit_amount', 0) for a in critical_alerts if 'profit_amount' in a)
        }
        
        try:
            with open(critical_log_path, 'a') as f:
                f.write(json.dumps(critical_entry, indent=2) + '\n\n')
            print(f"CRITICAL ALERTS LOGGED: {critical_log_path}")
            
            # Print critical alert summary
            print("\n=== CRITICAL ALERT SUMMARY ===")
            for alert in critical_alerts:
                print(f"  {alert['type']} - {alert['symbol']}")
                print(f"    Entry: ${alert['entry_price']:.2f}, Current: ${alert['current_price']:.2f}")
                print(f"    P&L: {alert['pnl_pct']:.2f}%, Position: ${alert['position_value']:.2f}")
                if 'loss_amount' in alert:
                    print(f"    Loss: ${alert['loss_amount']:.2f}")
                if 'profit_amount' in alert:
                    print(f"    Profit: ${alert['profit_amount']:.2f}")
                print()
                
        except Exception as e:
            print(f"Error writing critical alerts log: {e}")
    
    # Print summary
    print(f"\n=== MONITORING SUMMARY ===")
    print(f"Time: {timestamp}")
    print(f"System Status: {monitoring_log['system_status']}")
    print(f"Capital: ${monitoring_log['capital']:.2f}")
    print(f"Total Trades: {monitoring_log['total_trades']}")
    print(f"Alerts: {monitoring_log['alerts_count']} ({len(critical_alerts)} critical)")
    
    if market_prices:
        print(f"\nMarket Prices:")
        if 'btc_price' in market_prices:
            print(f"  BTC/USD: ${market_prices['btc_price']:.2f}")
        if 'eth_price' in market_prices:
            print(f"  ETH/USD: ${market_prices['eth_price']:.2f}")
        if 'sentiment' in market_prices:
            print(f"  Sentiment: {market_prices['sentiment']}")
        if 'decision' in market_prices:
            print(f"  Trading Decision: {market_prices['decision']}")

if __name__ == '__main__':
    main()