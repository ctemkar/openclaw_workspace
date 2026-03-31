#!/usr/bin/env python3
import json
import requests
from datetime import datetime
import sys

def fetch_current_prices():
    """Fetch current market prices from the dashboard"""
    try:
        # Get summary data to extract current prices
        response = requests.get('http://localhost:5001/summary', timeout=10)
        if response.status_code == 200:
            content = response.text
            # Extract BTC and ETH prices from summary
            btc_price = None
            eth_price = None
            
            for line in content.split('\n'):
                if 'BTC/USD:' in line and '$' in line:
                    parts = line.split('$')
                    if len(parts) > 1:
                        btc_price = float(parts[1].replace(',', '').strip())
                elif 'ETH/USD:' in line and '$' in line:
                    parts = line.split('$')
                    if len(parts) > 1:
                        eth_price = float(parts[1].replace(',', '').strip())
            
            return {'BTC/USD': btc_price, 'ETH/USD': eth_price}
    except Exception as e:
        print(f"Error fetching prices: {e}")
    
    return {'BTC/USD': 67667.37, 'ETH/USD': 2064.36}  # Fallback to last known prices

def analyze_trades():
    """Analyze existing trades for stop-loss/take-profit triggers"""
    try:
        # Fetch current trades
        response = requests.get('http://localhost:5001/trades', timeout=10)
        if response.status_code != 200:
            print("Failed to fetch trades")
            return []
        
        trades_data = response.json()
        trades = trades_data.get('trades', [])
        
        # Fetch current prices
        current_prices = fetch_current_prices()
        
        alerts = []
        
        for trade in trades:
            symbol = trade.get('symbol', '')
            entry_price = trade.get('price', 0)
            quantity = trade.get('quantity', 0)
            side = trade.get('side', 'BUY')
            reason = trade.get('reason', '')
            time = trade.get('time', '')
            
            current_price = current_prices.get(symbol, 0)
            
            if not current_price or not entry_price:
                continue
            
            # Calculate P&L percentage
            if side == 'BUY':
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
            else:  # SHORT
                pnl_pct = ((entry_price - current_price) / entry_price) * 100
            
            # Check for stop-loss (5%) or take-profit (10%) triggers
            stop_loss_pct = -5.0  # 5% stop-loss
            take_profit_pct = 10.0  # 10% take-profit
            
            alert = None
            if pnl_pct <= stop_loss_pct:
                alert = {
                    'type': 'STOP_LOSS_TRIGGERED',
                    'symbol': symbol,
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'pnl_pct': pnl_pct,
                    'quantity': quantity,
                    'side': side,
                    'time': time,
                    'reason': reason,
                    'threshold': f'{stop_loss_pct}%',
                    'position_value': entry_price * quantity
                }
            elif pnl_pct >= take_profit_pct:
                alert = {
                    'type': 'TAKE_PROFIT_TRIGGERED',
                    'symbol': symbol,
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'pnl_pct': pnl_pct,
                    'quantity': quantity,
                    'side': side,
                    'time': time,
                    'reason': reason,
                    'threshold': f'{take_profit_pct}%',
                    'position_value': entry_price * quantity
                }
            elif pnl_pct <= -3.0:  # Warning for approaching stop-loss
                alert = {
                    'type': 'APPROACHING_STOP_LOSS',
                    'symbol': symbol,
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'pnl_pct': pnl_pct,
                    'quantity': quantity,
                    'side': side,
                    'time': time,
                    'reason': reason,
                    'warning': f'Only {abs(pnl_pct - stop_loss_pct):.1f}% from stop-loss',
                    'position_value': entry_price * quantity
                }
            
            if alert:
                alerts.append(alert)
        
        return alerts
    
    except Exception as e:
        print(f"Error analyzing trades: {e}")
        return []

def check_system_health():
    """Check system health and risk parameters"""
    try:
        response = requests.get('http://localhost:5001/status', timeout=10)
        if response.status_code != 200:
            return {'status': 'ERROR', 'message': 'Dashboard not responding'}
        
        status_data = response.json()
        
        # Check if system is running
        if status_data.get('status') != 'running':
            return {'status': 'WARNING', 'message': f"System status: {status_data.get('status')}"}
        
        # Check last analysis time
        last_analysis = status_data.get('last_analysis', '')
        if last_analysis:
            try:
                last_time = datetime.fromisoformat(last_analysis.replace('Z', '+00:00'))
                current_time = datetime.now(last_time.tzinfo) if last_time.tzinfo else datetime.now()
                hours_since = (current_time - last_time).total_seconds() / 3600
                
                if hours_since > 2:
                    return {
                        'status': 'WARNING',
                        'message': f'Last analysis was {hours_since:.1f} hours ago',
                        'last_analysis': last_analysis
                    }
            except:
                pass
        
        return {'status': 'HEALTHY', 'data': status_data}
    
    except Exception as e:
        return {'status': 'ERROR', 'message': f'Health check failed: {e}'}

def main():
    """Main analysis function"""
    print("=== TRADING DASHBOARD MONITORING ANALYSIS ===")
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check system health
    print("1. SYSTEM HEALTH CHECK")
    health = check_system_health()
    print(f"   Status: {health.get('status')}")
    if health.get('message'):
        print(f"   Message: {health.get('message')}")
    print()
    
    # Analyze trades
    print("2. TRADE ANALYSIS")
    alerts = analyze_trades()
    
    if not alerts:
        print("   No stop-loss or take-profit triggers detected")
        print("   All positions within safe parameters")
    else:
        print(f"   ⚠️  Found {len(alerts)} alert(s):")
        for i, alert in enumerate(alerts, 1):
            print(f"   {i}. {alert['type']}")
            print(f"      Symbol: {alert['symbol']}")
            print(f"      Side: {alert['side']}")
            print(f"      Entry: ${alert['entry_price']:.2f}")
            print(f"      Current: ${alert['current_price']:.2f}")
            print(f"      P&L: {alert['pnl_pct']:.2f}%")
            print(f"      Position Value: ${alert['position_value']:.2f}")
            if alert.get('warning'):
                print(f"      Warning: {alert['warning']}")
            print()
    
    # Get current market summary
    print("3. MARKET SUMMARY")
    try:
        response = requests.get('http://localhost:5001/summary', timeout=10)
        if response.status_code == 200:
            content = response.text
            lines = content.split('\n')
            
            # Extract key information
            for line in lines[:50]:  # First 50 lines should contain summary
                if 'BTC/USD:' in line or 'ETH/USD:' in line or 'Market Sentiment:' in line:
                    print(f"   {line.strip()}")
                if 'TRADING DECISION:' in line:
                    print(f"   {line.strip()}")
                    break
    except:
        print("   Could not fetch market summary")
    
    print()
    print("=== ANALYSIS COMPLETE ===")
    
    # Return alerts for logging
    return alerts, health

if __name__ == '__main__':
    alerts, health = main()
    
    # Prepare data for logging
    result = {
        'timestamp': datetime.now().isoformat(),
        'health_status': health.get('status'),
        'health_message': health.get('message'),
        'alerts_count': len(alerts),
        'alerts': alerts,
        'critical': len([a for a in alerts if 'TRIGGERED' in a['type']]) > 0
    }
    
    print(json.dumps(result, indent=2))