#!/usr/bin/env python3
import json
import datetime
import subprocess
import sys

def get_current_data():
    """Fetch current status, trades, and summary data"""
    try:
        # Get status
        status_result = subprocess.run(['curl', '-s', 'http://localhost:5001/status'], 
                                     capture_output=True, text=True)
        status = json.loads(status_result.stdout)
        
        # Get trades
        trades_result = subprocess.run(['curl', '-s', 'http://localhost:5001/trades'], 
                                     capture_output=True, text=True)
        trades_data = json.loads(trades_result.stdout)
        
        # Get summary (text format)
        summary_result = subprocess.run(['curl', '-s', 'http://localhost:5001/summary'], 
                                      capture_output=True, text=True)
        summary_text = summary_result.stdout
        
        return status, trades_data, summary_text
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None, None

def extract_prices_from_summary(summary_text):
    """Extract current prices from summary text"""
    prices = {}
    lines = summary_text.split('\n')
    for line in lines:
        if 'Price:' in line and '$' in line:
            parts = line.split(':')
            if len(parts) > 1:
                price_str = parts[1].strip()
                # Extract numeric price
                price_str = price_str.replace('$', '').replace(',', '').strip()
                try:
                    if 'BTC/USD' in line:
                        prices['BTC/USD'] = float(price_str)
                    elif 'ETH/USD' in line:
                        prices['ETH/USD'] = float(price_str)
                except:
                    pass
    return prices

def analyze_positions(trades_data, current_prices):
    """Analyze all positions and calculate drawdowns"""
    positions = []
    
    for trade in trades_data.get('trades', []):
        if trade.get('side', '').lower() in ['buy', 'BUY']:
            symbol = trade.get('symbol', '')
            if not symbol:
                # Try to infer from model or other fields
                if 'BTC' in str(trade.get('model', '')):
                    symbol = 'BTC/USD'
                elif 'ETH' in str(trade.get('model', '')):
                    symbol = 'ETH/USD'
                else:
                    continue
            
            entry_price = trade.get('price', 0)
            if entry_price == 0:
                continue
                
            current_price = current_prices.get(symbol, 0)
            if current_price == 0:
                continue
                
            # Calculate drawdown
            drawdown = ((current_price - entry_price) / entry_price) * 100
            
            positions.append({
                'symbol': symbol,
                'entry_price': entry_price,
                'current_price': current_price,
                'drawdown': drawdown,
                'time': trade.get('time', ''),
                'status': trade.get('status', ''),
                'amount': trade.get('amount', trade.get('quantity', 0))
            })
    
    return positions

def calculate_risk_metrics(positions):
    """Calculate risk metrics from positions"""
    metrics = {
        'total_positions': len(positions),
        'stop_loss_triggered': 0,
        'take_profit_triggered': 0,
        'active_positions': 0,
        'total_exposure': 0,
        'total_unrealized_loss': 0,
        'excess_loss_beyond_stop_loss': 0,
        'by_symbol': {}
    }
    
    for pos in positions:
        symbol = pos['symbol']
        if symbol not in metrics['by_symbol']:
            metrics['by_symbol'][symbol] = {
                'count': 0,
                'stop_loss_triggered': 0,
                'total_exposure': 0,
                'total_loss': 0
            }
        
        metrics['by_symbol'][symbol]['count'] += 1
        exposure = pos['entry_price'] * pos.get('amount', 0.001)
        metrics['by_symbol'][symbol]['total_exposure'] += exposure
        metrics['total_exposure'] += exposure
        
        loss = (pos['current_price'] - pos['entry_price']) * pos.get('amount', 0.001)
        metrics['by_symbol'][symbol]['total_loss'] += loss
        metrics['total_unrealized_loss'] += loss
        
        # Check stop-loss (5%) and take-profit (10%)
        if pos['drawdown'] <= -5:
            metrics['stop_loss_triggered'] += 1
            metrics['by_symbol'][symbol]['stop_loss_triggered'] += 1
            excess_loss = abs(pos['drawdown']) - 5
            if excess_loss > 0:
                excess_amount = (excess_loss / 100) * exposure
                metrics['excess_loss_beyond_stop_loss'] += excess_amount
        elif pos['drawdown'] >= 10:
            metrics['take_profit_triggered'] += 1
        else:
            metrics['active_positions'] += 1
    
    return metrics

def main():
    print("=== TRADING POSITION ANALYSIS ===\n")
    
    status, trades_data, summary_text = get_current_data()
    if not all([status, trades_data, summary_text]):
        print("Failed to fetch data from dashboard")
        return
    
    current_prices = extract_prices_from_summary(summary_text)
    print(f"Current Prices: BTC/USD=${current_prices.get('BTC/USD', 0):,.2f}, ETH/USD=${current_prices.get('ETH/USD', 0):,.2f}")
    
    positions = analyze_positions(trades_data, current_prices)
    print(f"\nTotal Positions Found: {len(positions)}")
    
    metrics = calculate_risk_metrics(positions)
    
    print(f"\n=== RISK METRICS ===")
    print(f"Total Exposure: ${metrics['total_exposure']:,.2f}")
    print(f"Total Unrealized Loss: ${metrics['total_unrealized_loss']:,.2f}")
    print(f"Excess Loss Beyond Stop-Loss: ${metrics['excess_loss_beyond_stop_loss']:,.2f}")
    print(f"Stop-Loss Triggers: {metrics['stop_loss_triggered']}")
    print(f"Take-Profit Triggers: {metrics['take_profit_triggered']}")
    print(f"Active Positions: {metrics['active_positions']}")
    
    print(f"\n=== POSITION DETAILS ===")
    for i, pos in enumerate(positions, 1):
        status_indicator = "🚨 STOP-LOSS" if pos['drawdown'] <= -5 else "✅ ACTIVE" if pos['drawdown'] > -5 and pos['drawdown'] < 10 else "🎯 TAKE-PROFIT"
        print(f"{i}. {pos['symbol']} @ ${pos['entry_price']:,.2f} → ${pos['current_price']:,.2f} ({pos['drawdown']:.2f}%) {status_indicator}")
    
    print(f"\n=== BY SYMBOL ===")
    for symbol, data in metrics['by_symbol'].items():
        print(f"{symbol}: {data['count']} positions, ${data['total_exposure']:,.2f} exposure, ${data['total_loss']:,.2f} loss, {data['stop_loss_triggered']} stop-loss triggers")
    
    # Check system constraints
    print(f"\n=== SYSTEM CONSTRAINTS ===")
    max_trades = status.get('risk_parameters', {}).get('max_trades_per_day', 2)
    today_trades = 2  # From summary
    print(f"Daily Trade Limit: {today_trades}/{max_trades}")
    if today_trades >= max_trades:
        print("⚠️ DAILY TRADE LIMIT REACHED - No automatic trading possible")
    
    # Time analysis
    last_analysis = status.get('last_analysis', '')
    if last_analysis:
        last_dt = datetime.datetime.fromisoformat(last_analysis)
        current_dt = datetime.datetime.now()
        minutes_since = (current_dt - last_dt).total_seconds() / 60
        print(f"\nTime since last analysis: {minutes_since:.1f} minutes")
        print(f"Next analysis in: {60 - minutes_since:.1f} minutes")
    
    # Critical alerts
    if metrics['stop_loss_triggered'] > 0:
        print(f"\n🚨 CRITICAL ALERT: {metrics['stop_loss_triggered']} STOP-LOSS TRIGGERS NOT EXECUTED")
        if today_trades >= max_trades:
            print("🚨 SYSTEM CONSTRAINT: Daily trade limit preventing stop-loss execution")
            print("🚨 URGENT: Manual intervention required on external platform")

if __name__ == "__main__":
    main()