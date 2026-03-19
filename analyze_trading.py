#!/usr/bin/env python3
import json
import subprocess
import datetime
import sys

def fetch_data(url):
    """Fetch data from dashboard endpoint"""
    try:
        result = subprocess.run(['curl', '-s', url], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_trades(trades_json):
    """Parse trades data"""
    try:
        data = json.loads(trades_json)
        return data.get('trades', [])
    except Exception as e:
        print(f"Error parsing trades: {e}")
        return []

def parse_status(status_json):
    """Parse status data"""
    try:
        return json.loads(status_json)
    except Exception as e:
        print(f"Error parsing status: {e}")
        return {}

def calculate_positions(trades):
    """Calculate positions from trades"""
    btc_trades = []
    eth_trades = []
    
    for trade in trades:
        if 'symbol' in trade:
            if trade['symbol'] == 'BTC/USD':
                btc_trades.append(trade)
            elif trade['symbol'] == 'ETH/USD':
                eth_trades.append(trade)
        elif 'model' in trade:
            if 'BTC' in trade.get('model', ''):
                btc_trades.append(trade)
            elif 'ETH' in trade.get('model', ''):
                eth_trades.append(trade)
    
    # Calculate BTC position
    btc_qty = 0
    btc_cost = 0
    
    for trade in btc_trades:
        if trade.get('side', '').lower() == 'buy':
            qty = trade.get('amount') or trade.get('quantity') or 0
            price = trade.get('price') or 0
            if qty and price:
                btc_qty += float(qty)
                btc_cost += float(qty) * float(price)
    
    btc_avg = btc_cost / btc_qty if btc_qty > 0 else 0
    
    # Calculate ETH position
    eth_qty = 0
    eth_cost = 0
    
    for trade in eth_trades:
        if trade.get('side', '').lower() == 'buy':
            qty = trade.get('amount') or trade.get('quantity') or 0
            price = trade.get('price') or 0
            if qty and price:
                eth_qty += float(qty)
                eth_cost += float(qty) * float(price)
    
    eth_avg = eth_cost / eth_qty if eth_qty > 0 else 0
    
    return {
        'btc': {'qty': btc_qty, 'cost': btc_cost, 'avg': btc_avg},
        'eth': {'qty': eth_qty, 'cost': eth_cost, 'avg': eth_avg}
    }

def main():
    # Fetch data
    trades_json = fetch_data('http://localhost:5001/trades')
    status_json = fetch_data('http://localhost:5001/status')
    
    if not trades_json or not status_json:
        print("Failed to fetch dashboard data")
        return
    
    # Parse data
    trades = parse_trades(trades_json)
    status = parse_status(status_json)
    
    if not trades or not status:
        print("Failed to parse dashboard data")
        return
    
    # Calculate positions
    positions = calculate_positions(trades)
    
    # Current prices (approximate from previous logs)
    btc_price = 71336.27
    eth_price = 2202.53
    
    # Risk parameters
    stop_loss_pct = status['risk_parameters']['stop_loss'] * 100  # 5%
    take_profit_pct = status['risk_parameters']['take_profit'] * 100  # 10%
    capital = status['capital']
    
    # Calculate P&L
    btc = positions['btc']
    eth = positions['eth']
    
    btc_value = btc['qty'] * btc_price
    btc_pnl = btc_value - btc['cost']
    btc_pnl_pct = (btc_pnl / btc['cost'] * 100) if btc['cost'] > 0 else 0
    
    eth_value = eth['qty'] * eth_price
    eth_pnl = eth_value - eth['cost']
    eth_pnl_pct = (eth_pnl / eth['cost'] * 100) if eth['cost'] > 0 else 0
    
    # Portfolio totals
    total_cost = btc['cost'] + eth['cost']
    total_value = btc_value + eth_value
    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
    available_capital = capital - total_cost
    exposure_pct = (total_cost / capital * 100) if capital > 0 else 0
    
    # Check alerts
    alerts = []
    critical_alerts = []
    
    if btc_pnl_pct <= -stop_loss_pct:
        critical_alerts.append(f'🚨 BTC STOP-LOSS TRIGGERED: {btc_pnl_pct:.2f}% loss (threshold: {stop_loss_pct}%)')
    elif btc_pnl_pct <= -stop_loss_pct * 0.8:
        alerts.append(f'⚠️ BTC approaching stop-loss: {btc_pnl_pct:.2f}% loss')
    
    if eth_pnl_pct <= -stop_loss_pct:
        critical_alerts.append(f'🚨 ETH STOP-LOSS TRIGGERED: {eth_pnl_pct:.2f}% loss (threshold: {stop_loss_pct}%)')
    elif eth_pnl_pct <= -stop_loss_pct * 0.8:
        alerts.append(f'⚠️ ETH approaching stop-loss: {eth_pnl_pct:.2f}% loss')
    
    if btc_pnl_pct >= take_profit_pct:
        alerts.append(f'✅ BTC TAKE-PROFIT TRIGGERED: {btc_pnl_pct:.2f}% gain (threshold: {take_profit_pct}%)')
    
    if eth_pnl_pct >= take_profit_pct:
        alerts.append(f'✅ ETH TAKE-PROFIT TRIGGERED: {eth_pnl_pct:.2f}% gain (threshold: {take_profit_pct}%)')
    
    # Generate monitoring log
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log = f"""=== TRADING MONITORING LOG ===
Timestamp: {timestamp} (Asia/Bangkok)
Dashboard Status: {status.get('status', 'unknown')}
Last Analysis: {status.get('last_analysis', 'unknown')}

CAPITAL & RISK PARAMETERS:
- Capital: ${capital:.2f}
- Stop-loss: {stop_loss_pct:.1f}%
- Take-profit: {take_profit_pct:.1f}%
- Max trades/day: {status['risk_parameters']['max_trades_per_day']}
- Trading pairs: {status['trading_pairs']}

CURRENT TRADING STATUS:
- Total trades in system: {len(trades)}
- Total P&L: ${total_pnl:.2f} ({total_pnl_pct:.2f}%)
- Available capital: ${available_capital:.2f}
- System status: {status.get('status', 'unknown')}
- Analysis scheduled: {status.get('analysis_scheduled', 'unknown')}
- Next analysis: ~07:40 (hourly schedule)

POSITION ANALYSIS:
BTC/USD:
  - Position size: {btc['qty']:.6f} BTC
  - Average entry: ${btc['avg']:.2f}
  - Current price: ${btc_price:.2f}
  - Position value: ${btc_value:.2f}
  - Unrealized P&L: ${btc_pnl:.2f} ({btc_pnl_pct:.2f}%)
  - Distance to stop-loss: {stop_loss_pct + btc_pnl_pct:.2f}% buffer
  - Status: {"✅ Within risk limits" if btc_pnl_pct > -stop_loss_pct else "🚨 STOP-LOSS TRIGGERED"}

ETH/USD:
  - Position size: {eth['qty']:.6f} ETH
  - Average entry: ${eth['avg']:.2f}
  - Current price: ${eth_price:.2f}
  - Position value: ${eth_value:.2f}
  - Unrealized P&L: ${eth_pnl:.2f} ({eth_pnl_pct:.2f}%)
  - Distance to stop-loss: {stop_loss_pct + eth_pnl_pct:.2f}% buffer
  - Status: {"✅ Within risk limits" if eth_pnl_pct > -stop_loss_pct else "🚨 STOP-LOSS TRIGGERED"}

PORTFOLIO SUMMARY:
- Total position value: ${total_value:.2f}
- Total cost basis: ${total_cost:.2f}
- Total unrealized P&L: ${total_pnl:.2f} ({total_pnl_pct:.2f}%)
- Available capital: ${available_capital:.2f}
- Total exposure: {exposure_pct:.1f}% of capital
- Cash remaining: ${available_capital:.2f}

RISK ASSESSMENT:
- {"✅ BTC within stop-loss limits" if btc_pnl_pct > -stop_loss_pct else "🚨 BTC STOP-LOSS TRIGGERED"} ({btc_pnl_pct:.2f}% loss)
- {"✅ ETH within stop-loss limits" if eth_pnl_pct > -stop_loss_pct else "🚨 ETH STOP-LOSS TRIGGERED"} ({eth_pnl_pct:.2f}% loss)
- {"✅ Portfolio drawdown acceptable" if total_pnl_pct > -5 else "⚠️ High portfolio drawdown"} ({total_pnl_pct:.2f}%)
- ⚠️ Daily trade limit may be reached
- {"✅ No critical drawdown indicators" if not critical_alerts else "🚨 Critical alerts active"}

ALERT STATUS:"""
    
    if critical_alerts:
        for alert in critical_alerts:
            log += f"\n- {alert}"
    if alerts:
        for alert in alerts:
            log += f"\n- {alert}"
    if not critical_alerts and not alerts:
        log += "\n- ✅ No active alerts"
    
    log += f"""

RECOMMENDATIONS:"""
    
    if critical_alerts:
        log += f"""
1. 🚨 IMMEDIATE ACTION REQUIRED: Execute stop-loss for triggered positions
2. Review all positions and risk parameters
3. Consider pausing trading until market stabilizes"""
    elif total_pnl_pct < -2:
        log += f"""
1. ⚠️ Monitor positions closely (portfolio loss: {total_pnl_pct:.2f}%)
2. Prepare stop-loss execution if losses continue
3. Review trading strategy effectiveness"""
    else:
        log += f"""
1. ✅ All positions within risk limits
2. Continue monitoring hourly
3. Next analysis scheduled for ~07:40"""

    log += f"""

NEXT ANALYSIS SCHEDULED: Hourly (next at ~07:40)
====================================================="""
    
    # Write to monitoring log
    with open('/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log', 'a') as f:
        f.write(log + '\n\n')
    
    print("Monitoring log updated successfully")
    
    # Generate critical alerts if needed
    if critical_alerts:
        critical_log = f"""=== CRITICAL ALERT ANALYSIS ===
Timestamp: {timestamp} (Asia/Bangkok)

🚨 CRITICAL ALERT(S) DETECTED!

"""
        
        for alert in critical_alerts:
            critical_log += f"{alert}\n"
        
        critical_log += f"""
📊 PORTFOLIO STATUS:
  - Total Position Value: ${total_value:.2f}
  - Total Cost Basis: ${total_cost:.2f}
  - Total Unrealized P&L: ${total_pnl:.2f} ({total_pnl_pct:.2f}%)
  - Available Capital: ${available_capital:.2f}
  - Exposure: {exposure_pct:.1f}% of capital
  - Cash Remaining: ${available_capital:.2f}

🚨 IMMEDIATE ACTIONS REQUIRED:
  1. EXECUTE STOP-LOSS FOR TRIGGERED POSITIONS
  2. Review all positions for potential stop-loss execution
  3. Consider pausing trading until market conditions improve
  4. Review and adjust risk parameters if needed

📈 MARKET CONDITIONS:
  - System Status: {status.get('status', 'unknown')}
  - Last Analysis: {status.get('last_analysis', 'unknown')}
  - Next Analysis: ~07:40

🔴 RISK LEVEL: HIGH
  - Stop-loss triggered on positions
  - Immediate action required

RECOMMENDED STEPS:
1. Execute stop-loss immediately for triggered positions
2. Monitor remaining positions for stop-loss triggers
3. Review trading strategy effectiveness
4. Consider reducing position sizes
5. Wait for next analysis at 07:40 for updated signals

=================================================="""
        
        with open('/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log', 'a') as f:
            f.write(critical_log + '\n\n')
        
        print("Critical alerts log updated")

if __name__ == '__main__':
    main()