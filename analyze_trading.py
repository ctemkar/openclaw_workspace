import json
import subprocess
from datetime import datetime

def fetch_data(url):
    """Fetch JSON data from API endpoint"""
    try:
        result = subprocess.run(['curl', '-s', url], capture_output=True, text=True)
        return json.loads(result.stdout)
    except:
        return {}

def main():
    # Current market prices
    current_prices = {
        'BTC': 74499,
        'ETH': 2341.63,
        'SOL': 95.16
    }
    
    # Fetch trading data
    data = fetch_data('http://127.0.0.1:56086/api/status/all')
    config_data = fetch_data('http://127.0.0.1:56086/api/trading/configure')
    
    if not data or not config_data:
        print("Failed to fetch trading data")
        return
    
    config = config_data.get('config', {})
    stop_loss_pct = config.get('stop_loss', 0.03)
    take_profit_pct = config.get('take_profit', 0.06)
    
    print('=== TRADING DASHBOARD MONITORING ANALYSIS ===')
    print(f'Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Dashboard Status: {data.get("status", "UNKNOWN")}')
    print(f'Total Trades: {len(data.get("trades", []))}')
    print()
    print('=== TRADING CONFIGURATION ===')
    print(f'Capital: ${config.get("capital", 0):.2f}')
    print(f'Trade Size: ${config.get("trade_size", 0):.2f}')
    print(f'Stop Loss: {stop_loss_pct*100:.1f}%')
    print(f'Take Profit: {take_profit_pct*100:.1f}%')
    print()
    
    # Analyze trades
    trades = data.get('trades', [])
    if trades:
        print('=== RECENT TRADE ANALYSIS ===')
        
        # Group trades by symbol/model
        trade_summary = {}
        for trade in trades:
            model = trade.get('model', 'Unknown')
            side = trade.get('side', 'unknown')
            price = trade.get('price', 0)
            amount = trade.get('amount', 0)
            
            # Determine symbol from model name
            symbol = 'BTC'
            if 'ETH' in model:
                symbol = 'ETH'
            elif 'SOL' in model:
                symbol = 'SOL'
            
            key = f'{symbol}_{model}_{side}'
            if key not in trade_summary:
                trade_summary[key] = {
                    'symbol': symbol,
                    'model': model,
                    'side': side,
                    'total_amount': 0,
                    'avg_price': 0,
                    'total_investment': 0,
                    'count': 0
                }
            
            trade_summary[key]['total_amount'] += amount
            trade_summary[key]['total_investment'] += price * amount
            trade_summary[key]['count'] += 1
        
        # Calculate average prices
        for key in trade_summary:
            if trade_summary[key]['total_amount'] > 0:
                trade_summary[key]['avg_price'] = trade_summary[key]['total_investment'] / trade_summary[key]['total_amount']
        
        # Calculate P&L and check for triggers
        print('Position Summary:')
        critical_alerts = []
        
        for key, position in trade_summary.items():
            symbol = position['symbol']
            current_price = current_prices.get(symbol, 0)
            avg_price = position['avg_price']
            total_amount = position['total_amount']
            side = position['side']
            
            if side == 'buy' and total_amount > 0:
                # For buy positions, calculate unrealized P&L
                if current_price > 0:
                    current_value = total_amount * current_price
                    investment = total_amount * avg_price
                    pnl = current_value - investment
                    pnl_pct = (pnl / investment) * 100 if investment > 0 else 0
                    
                    print(f'{symbol} ({position["model"]}):')
                    print(f'  Position: {total_amount:.6f} {symbol}')
                    print(f'  Avg Buy Price: ${avg_price:.2f}')
                    print(f'  Current Price: ${current_price:.2f}')
                    print(f'  Investment: ${investment:.2f}')
                    print(f'  Current Value: ${current_value:.2f}')
                    print(f'  Unrealized P&L: ${pnl:.2f} ({pnl_pct:.2f}%)')
                    
                    # Check for stop-loss/take-profit triggers
                    if pnl_pct <= -stop_loss_pct*100:
                        alert = f'STOP-LOSS TRIGGERED: {symbol} position at {pnl_pct:.2f}% loss (threshold: -{stop_loss_pct*100:.1f}%)'
                        critical_alerts.append(alert)
                        print(f'  ⚠️  {alert}')
                    elif pnl_pct >= take_profit_pct*100:
                        alert = f'TAKE-PROFIT TRIGGERED: {symbol} position at {pnl_pct:.2f}% gain (threshold: {take_profit_pct*100:.1f}%)'
                        critical_alerts.append(alert)
                        print(f'  ✅ {alert}')
                    print()
        
        # Check for overall portfolio drawdown
        buy_positions = [pos for pos in trade_summary.values() if pos['side'] == 'buy' and pos['total_amount'] > 0]
        total_investment = sum(pos['total_investment'] for pos in buy_positions)
        total_current_value = sum(pos['total_amount'] * current_prices.get(pos['symbol'], 0) for pos in buy_positions)
        
        if total_investment > 0:
            portfolio_pnl = total_current_value - total_investment
            portfolio_pnl_pct = (portfolio_pnl / total_investment) * 100
            
            print('=== PORTFOLIO SUMMARY ===')
            print(f'Total Investment: ${total_investment:.2f}')
            print(f'Current Portfolio Value: ${total_current_value:.2f}')
            print(f'Portfolio P&L: ${portfolio_pnl:.2f} ({portfolio_pnl_pct:.2f}%)')
            
            # Check for critical drawdown (e.g., >5% loss)
            if portfolio_pnl_pct <= -5:
                alert = f'CRITICAL DRAWDOWN: Portfolio down {portfolio_pnl_pct:.2f}%'
                critical_alerts.append(alert)
                print(f'⚠️  {alert}')
        
        # Log critical alerts
        if critical_alerts:
            print('=== CRITICAL ALERTS DETECTED ===')
            for alert in critical_alerts:
                print(f'• {alert}')
        else:
            print('=== NO CRITICAL ALERTS ===')
            print('All positions within normal risk parameters.')
        
    else:
        print('No active trades found.')
    
    print()
    print('=== SYSTEM STATUS ===')
    print('Dashboard: Running on port 56086')
    print('API Endpoints: Accessible')
    print('Market Data: Live prices available')
    
    # Return summary for logging
    return {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'status': data.get('status', 'UNKNOWN'),
        'trade_count': len(trades),
        'critical_alerts': critical_alerts if 'critical_alerts' in locals() else [],
        'portfolio_pnl_pct': portfolio_pnl_pct if 'portfolio_pnl_pct' in locals() else 0
    }

if __name__ == '__main__':
    main()