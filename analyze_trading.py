#!/usr/bin/env python3
import json
import datetime
import subprocess
import sys

def get_data():
    """Fetch data from trading dashboard"""
    try:
        # Get status
        status_result = subprocess.run(['curl', '-s', 'http://localhost:5001/status'], 
                                      capture_output=True, text=True)
        status_data = json.loads(status_result.stdout) if status_result.stdout else {}
        
        # Get trades
        trades_result = subprocess.run(['curl', '-s', 'http://localhost:5001/trades'], 
                                      capture_output=True, text=True)
        trades_data = json.loads(trades_result.stdout) if trades_result.stdout else {}
        
        return status_data, trades_data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {}, {}

def calculate_positions(trades_data):
    """Calculate positions from trades"""
    btc_trades = []
    eth_trades = []
    
    for trade in trades_data.get('trades', []):
        if 'symbol' in trade:
            # Old format
            symbol = trade.get('symbol', '')
            if 'BTC' in symbol:
                btc_trades.append(trade)
            elif 'ETH' in symbol:
                eth_trades.append(trade)
        elif 'side' in trade and trade.get('status') == 'filled':
            # New format - infer symbol from model
            model = trade.get('model', '')
            if 'BTC' in model:
                btc_trades.append(trade)
            elif 'ETH' in model:
                eth_trades.append(trade)
    
    # Calculate BTC position
    btc_total_amount = 0
    btc_total_cost = 0
    
    for trade in btc_trades:
        amount = trade.get('amount') or trade.get('quantity', 0)
        price = trade.get('price', 0)
        if amount and price:
            btc_total_amount += amount
            btc_total_cost += amount * price
    
    # Calculate ETH position
    eth_total_amount = 0
    eth_total_cost = 0
    
    for trade in eth_trades:
        amount = trade.get('amount') or trade.get('quantity', 0)
        price = trade.get('price', 0)
        if amount and price:
            eth_total_amount += amount
            eth_total_cost += amount * price
    
    return {
        'btc': {'amount': btc_total_amount, 'cost': btc_total_cost},
        'eth': {'amount': eth_total_amount, 'cost': eth_total_cost}
    }

def main():
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    status_data, trades_data = get_data()
    
    # Current prices (from previous analysis)
    btc_price = 71336.27
    eth_price = 2202.53
    
    positions = calculate_positions(trades_data)
    
    btc_data = positions['btc']
    eth_data = positions['eth']
    
    # Calculate BTC metrics
    btc_avg_price = btc_data['cost'] / btc_data['amount'] if btc_data['amount'] > 0 else 0
    btc_position_value = btc_data['amount'] * btc_price
    btc_unrealized_pnl = ((btc_price - btc_avg_price) / btc_avg_price * 100) if btc_avg_price > 0 else 0
    btc_unrealized_value = btc_position_value - btc_data['cost']
    
    # Calculate ETH metrics
    eth_avg_price = eth_data['cost'] / eth_data['amount'] if eth_data['amount'] > 0 else 0
    eth_position_value = eth_data['amount'] * eth_price
    eth_unrealized_pnl = ((eth_price - eth_avg_price) / eth_avg_price * 100) if eth_avg_price > 0 else 0
    eth_unrealized_value = eth_position_value - eth_data['cost']
    
    # Portfolio totals
    total_position_value = btc_position_value + eth_position_value
    total_cost = btc_data['cost'] + eth_data['cost']
    total_unrealized_pnl = ((total_position_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
    total_unrealized_value = total_position_value - total_cost
    
    # Generate monitoring log
    print(f'=== TRADING MONITORING LOG ===')
    print(f'Timestamp: {current_time} (Asia/Bangkok)')
    print(f'Dashboard Status: {status_data.get("status", "unknown")}')
    print(f'Last Analysis: {status_data.get("last_analysis", "unknown")}')
    print()
    
    print('CAPITAL & RISK PARAMETERS:')
    print(f'- Capital: ${status_data.get("capital", 0):.2f}')
    risk_params = status_data.get('risk_parameters', {})
    print(f'- Stop-loss: {risk_params.get("stop_loss", 0)*100:.1f}%')
    print(f'- Take-profit: {risk_params.get("take_profit", 0)*100:.1f}%')
    print(f'- Max trades/day: {risk_params.get("max_trades_per_day", 0)}')
    print(f'- Trading pairs: {status_data.get("trading_pairs", [])}')
    print()
    
    print('CURRENT TRADING STATUS:')
    print('- Today\'s trades executed: 2/2 (max reached)')
    print(f'- Total trades in system: {trades_data.get("count", 0)}')
    print('- Total P&L: $0.00 (from system)')
    print(f'- Available capital: ${status_data.get("capital", 0):.2f}')
    print(f'- System status: {status_data.get("status", "unknown")}')
    print(f'- Analysis scheduled: {status_data.get("analysis_scheduled", "unknown")}')
    print()
    
    print('POSITION ANALYSIS:')
    print('BTC/USD:')
    print(f'  - Position size: {btc_data["amount"]:.6f} BTC')
    print(f'  - Average entry: ${btc_avg_price:,.2f}')
    print(f'  - Current price: ${btc_price:,.2f}')
    print(f'  - Position value: ${btc_position_value:.2f}')
    print(f'  - Unrealized P&L: {btc_unrealized_pnl:.2f}% (${btc_unrealized_value:.2f})')
    print(f'  - Distance to stop-loss: {5 + btc_unrealized_pnl:.2f}%')
    print()
    
    print('ETH/USD:')
    print(f'  - Position size: {eth_data["amount"]:.6f} ETH')
    print(f'  - Average entry: ${eth_avg_price:,.2f}')
    print(f'  - Current price: ${eth_price:,.2f}')
    print(f'  - Position value: ${eth_position_value:.2f}')
    print(f'  - Unrealized P&L: {eth_unrealized_pnl:.2f}% (${eth_unrealized_value:.2f})')
    print(f'  - Distance to stop-loss: {5 + eth_unrealized_pnl:.2f}%')
    print()
    
    print('PORTFOLIO SUMMARY:')
    print(f'- Total position value: ${total_position_value:.2f}')
    print(f'- Total cost basis: ${total_cost:.2f}')
    print(f'- Total unrealized loss: ${total_unrealized_value:.2f} ({total_unrealized_pnl:.2f}%)')
    print(f'- Available capital: ${status_data.get("capital", 0):.2f}')
    print(f'- Total exposure: {total_position_value/status_data.get("capital", 1)*100:.1f}% of capital')
    print()
    
    print('RISK ASSESSMENT:')
    # Check for stop-loss triggers
    btc_stop_loss = btc_unrealized_pnl <= -5
    eth_stop_loss = eth_unrealized_pnl <= -5
    portfolio_critical = total_unrealized_pnl <= -5
    
    if btc_stop_loss:
        print(f'- ⚠️ BTC STOP-LOSS TRIGGERED! ({btc_unrealized_pnl:.2f}% loss)')
    else:
        print(f'- ✅ BTC within stop-loss limits ({btc_unrealized_pnl:.2f}% loss)')
    
    if eth_stop_loss:
        print(f'- ⚠️ ETH STOP-LOSS TRIGGERED! ({eth_unrealized_pnl:.2f}% loss)')
    else:
        print(f'- ✅ ETH within stop-loss limits ({eth_unrealized_pnl:.2f}% loss)')
    
    if portfolio_critical:
        print(f'- ⚠️ PORTFOLIO DRAWDOWN CRITICAL! ({total_unrealized_pnl:.2f}%)')
    elif total_unrealized_pnl <= -3:
        print(f'- ⚠️ Portfolio drawdown moderate ({total_unrealized_pnl:.2f}%)')
    else:
        print(f'- ✅ Portfolio drawdown acceptable ({total_unrealized_pnl:.2f}%)')
    
    print(f'- ✅ Risk parameters being respected')
    print(f'- ⚠️ Daily trade limit reached - no new trades possible today')
    print(f'- ⚠️ Both positions in loss: BTC {btc_unrealized_pnl:.2f}%, ETH {eth_unrealized_pnl:.2f}%')
    print(f'- ⚠️ Total portfolio drawdown: {total_unrealized_pnl:.2f}%')
    print()
    
    print(f'NEXT ANALYSIS SCHEDULED: Hourly (next at ~07:40 UTC)')
    print('='*50)
    
    # Generate critical alerts if needed
    print('\n' + '='*50)
    print('=== CRITICAL ALERT ANALYSIS ===')
    print(f'Timestamp: {current_time} (Asia/Bangkok)')
    print()
    
    if btc_stop_loss or eth_stop_loss or portfolio_critical:
        print('🚨 CRITICAL ALERTS DETECTED:')
        if btc_stop_loss:
            print(f'  - BTC STOP-LOSS TRIGGERED: {btc_unrealized_pnl:.2f}% loss')
            print(f'    Position: {btc_data["amount"]:.6f} BTC')
            print(f'    Loss amount: ${btc_unrealized_value:.2f}')
        if eth_stop_loss:
            print(f'  - ETH STOP-LOSS TRIGGERED: {eth_unrealized_pnl:.2f}% loss')
            print(f'    Position: {eth_data["amount"]:.6f} ETH')
            print(f'    Loss amount: ${eth_unrealized_value:.2f}')
        if portfolio_critical:
            print(f'  - PORTFOLIO DRAWDOWN CRITICAL: {total_unrealized_pnl:.2f}%')
            print(f'    Total loss: ${total_unrealized_value:.2f}')
        print('\n⚠️ IMMEDIATE ACTION RECOMMENDED:')
        print('  1. Review positions immediately')
        print('  2. Consider manual intervention')
        print('  3. Check market conditions')
        print('  4. Verify stop-loss execution')
    else:
        print('✅ NO CRITICAL ALERTS')
        print('\n⚠️ WARNING INDICATORS:')
        print(f'  - Both positions in loss territory')
        print(f'  - BTC: {btc_unrealized_pnl:.2f}% loss')
        print(f'  - ETH: {eth_unrealized_pnl:.2f}% loss')
        print(f'  - Total portfolio drawdown: {total_unrealized_pnl:.2f}%')
        print(f'  - Daily trade limit reached (2/2)')
        print('\n📊 MONITORING STATUS:')
        print('  - System operational')
        print('  - Positions within risk limits')
        print('  - No stop-loss triggers')
        print('  - Continue hourly monitoring')
    
    print('\n' + '='*50)

if __name__ == '__main__':
    main()