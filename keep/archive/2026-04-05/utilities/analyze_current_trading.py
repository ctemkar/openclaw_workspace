#!/usr/bin/env python3
"""
Analyze current trading data for monitoring
"""

import json
import os
from datetime import datetime
import requests

def get_current_sol_price():
    """Get current SOL price from Binance"""
    try:
        response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT', timeout=5)
        return float(response.json()['price'])
    except:
        # Fallback price
        return 82.69

def analyze_trading_data():
    """Analyze trading data for monitoring"""
    
    # Load data
    with open('trading_data/trades.json', 'r') as f:
        trades = json.load(f)
    
    with open('trading_data/capital.json', 'r') as f:
        capital = json.load(f)
    
    with open('trading_data/bot_status.json', 'r') as f:
        bot_status = json.load(f)
    
    # Get current SOL price
    current_price = get_current_sol_price()
    
    # Analyze trades
    total_unrealized_pl = 0
    total_value = 0
    total_entry_value = 0
    position_count = len(trades)
    
    for trade in trades:
        entry_price = trade['price']
        amount = trade['amount']
        entry_value = trade['value']
        
        current_value = amount * current_price
        unrealized_pl = current_value - entry_value
        
        total_unrealized_pl += unrealized_pl
        total_value += current_value
        total_entry_value += entry_value
    
    # Calculate metrics
    if total_entry_value > 0:
        unrealized_pl_percent = (total_unrealized_pl / total_entry_value) * 100
    else:
        unrealized_pl_percent = 0
    
    # Risk parameters
    stop_loss_percent = 3  # 3% stop-loss
    take_profit_percent = 5  # 5% take-profit
    
    avg_entry_price = total_entry_value / sum(t['amount'] for t in trades) if trades else 0
    stop_loss_price = avg_entry_price * (1 - stop_loss_percent/100)
    take_profit_price = avg_entry_price * (1 + take_profit_percent/100)
    
    # Check triggers
    stop_loss_triggered = current_price <= stop_loss_price
    take_profit_triggered = current_price >= take_profit_price
    
    # Drawdown analysis
    total_capital = capital.get('total_capital', 0)
    deployed_capital = capital.get('deployed', 0)
    available_capital = total_capital - deployed_capital
    
    if total_capital > 0:
        drawdown_percent = (1 - (total_value + available_capital) / total_capital) * 100
    else:
        drawdown_percent = 0
    
    # Critical conditions
    critical_drawdown = drawdown_percent > 20  # 20% drawdown threshold
    critical_capital = available_capital < 10  # Less than $10 available
    bots_stopped = bot_status.get('status') == 'waiting'
    
    # Prepare analysis
    analysis = {
        'timestamp': datetime.now().isoformat(),
        'current_price': current_price,
        'avg_entry_price': avg_entry_price,
        'position_count': position_count,
        'total_value': total_value,
        'total_entry_value': total_entry_value,
        'total_unrealized_pl': total_unrealized_pl,
        'unrealized_pl_percent': unrealized_pl_percent,
        'stop_loss_price': stop_loss_price,
        'take_profit_price': take_profit_price,
        'stop_loss_triggered': stop_loss_triggered,
        'take_profit_triggered': take_profit_triggered,
        'total_capital': total_capital,
        'deployed_capital': deployed_capital,
        'available_capital': available_capital,
        'drawdown_percent': drawdown_percent,
        'critical_drawdown': critical_drawdown,
        'critical_capital': critical_capital,
        'bots_stopped': bots_stopped,
        'bot_status': bot_status.get('status'),
        'bot_last_activity': bot_status.get('last_activity'),
        'risk_level': 'NORMAL'
    }
    
    # Determine risk level
    if stop_loss_triggered or take_profit_triggered:
        analysis['risk_level'] = 'HIGH'
    if critical_drawdown or critical_capital:
        analysis['risk_level'] = 'CRITICAL'
    
    return analysis

def log_monitoring_data(analysis):
    """Log monitoring data to file"""
    
    log_entry = f"""
=== TRADING MONITORING REPORT ===
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Risk Level: {analysis['risk_level']}

=== POSITION ANALYSIS ===
• Current SOL Price: ${analysis['current_price']:.2f}
• Average Entry Price: ${analysis['avg_entry_price']:.2f}
• Price Difference: ${analysis['current_price'] - analysis['avg_entry_price']:.2f} ({((analysis['current_price'] - analysis['avg_entry_price']) / analysis['avg_entry_price'] * 100):.2f}%)
• Total Position Value: ${analysis['total_value']:.2f} ({analysis['position_count']} positions)
• Unrealized P&L: ${analysis['total_unrealized_pl']:.2f} ({analysis['unrealized_pl_percent']:.2f}%)
• Stop-Loss Trigger: ${analysis['stop_loss_price']:.2f} (3% below entry)
• Take-Profit Trigger: ${analysis['take_profit_price']:.2f} (5% above entry)
• Current vs Stop-Loss: {'🔴 TRIGGERED' if analysis['stop_loss_triggered'] else '✅ SAFE'} (${analysis['current_price'] - analysis['stop_loss_price']:.2f})
• Current vs Take-Profit: {'✅ TRIGGERED' if analysis['take_profit_triggered'] else '❌ NOT TRIGGERED'} (${analysis['current_price'] - analysis['take_profit_price']:.2f})

=== CAPITAL ANALYSIS ===
• Total Capital: ${analysis['total_capital']:.2f}
• Deployed Capital: ${analysis['deployed_capital']:.2f}
• Available Capital: ${analysis['available_capital']:.2f}
• Drawdown: {analysis['drawdown_percent']:.2f}% {'🔴 CRITICAL' if analysis['critical_drawdown'] else '✅ NORMAL'}

=== BOT STATUS ===
• Bot Status: {analysis['bot_status']}
• Last Activity: {analysis['bot_last_activity']}
• Bots Stopped: {'🔴 YES' if analysis['bots_stopped'] else '✅ NO'}

=== RISK ASSESSMENT ===
• Stop-Loss Status: {'🔴 TRIGGERED' if analysis['stop_loss_triggered'] else '✅ SAFE'}
• Take-Profit Status: {'✅ TRIGGERED' if analysis['take_profit_triggered'] else '❌ NOT TRIGGERED'}
• Drawdown Status: {'🔴 CRITICAL' if analysis['critical_drawdown'] else '✅ NORMAL'}
• Available Capital Status: {'🔴 CRITICAL' if analysis['critical_capital'] else '✅ NORMAL'}
• Bot Status: {'🔴 STOPPED' if analysis['bots_stopped'] else '✅ ACTIVE'}

=== ALERTS ===
"""
    
    alerts = []
    if analysis['stop_loss_triggered']:
        alerts.append("🔴 STOP-LOSS TRIGGERED: Current price has hit stop-loss level")
    if analysis['take_profit_triggered']:
        alerts.append("✅ TAKE-PROFIT TRIGGERED: Current price has hit take-profit level")
    if analysis['critical_drawdown']:
        alerts.append("🔴 CRITICAL DRAWDOWN: Drawdown exceeds 20% threshold")
    if analysis['critical_capital']:
        alerts.append("🔴 CRITICAL CAPITAL: Available capital below $10")
    if analysis['bots_stopped']:
        alerts.append("🔴 BOTS STOPPED: Trading bots are not active")
    
    if alerts:
        log_entry += "\n".join(alerts)
    else:
        log_entry += "✅ No critical alerts at this time"
    
    log_entry += "\n\n=== END OF REPORT ===\n"
    
    return log_entry

if __name__ == "__main__":
    # Analyze data
    analysis = analyze_trading_data()
    
    # Generate log entry
    log_entry = log_monitoring_data(analysis)
    
    # Print to console
    print(log_entry)
    
    # Save to monitoring log
    with open('trading_monitoring.log', 'a') as f:
        f.write(log_entry)
    
    # Check for critical alerts
    if (analysis['stop_loss_triggered'] or analysis['take_profit_triggered'] or 
        analysis['critical_drawdown'] or analysis['critical_capital']):
        
        alert_entry = f"""
=== CRITICAL TRADING ALERT ===
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Alert Level: {analysis['risk_level']}

=== ALERT DETAILS ===
"""
        
        if analysis['stop_loss_triggered']:
            alert_entry += f"• 🔴 STOP-LOSS TRIGGERED: SOL at ${analysis['current_price']:.2f} <= ${analysis['stop_loss_price']:.2f}\n"
        if analysis['take_profit_triggered']:
            alert_entry += f"• ✅ TAKE-PROFIT TRIGGERED: SOL at ${analysis['current_price']:.2f} >= ${analysis['take_profit_price']:.2f}\n"
        if analysis['critical_drawdown']:
            alert_entry += f"• 🔴 CRITICAL DRAWDOWN: {analysis['drawdown_percent']:.2f}% (threshold: 20%)\n"
        if analysis['critical_capital']:
            alert_entry += f"• 🔴 CRITICAL CAPITAL: ${analysis['available_capital']:.2f} available (threshold: $10)\n"
        if analysis['bots_stopped']:
            alert_entry += f"• 🔴 BOTS STOPPED: Trading bots inactive\n"
        
        alert_entry += f"""
=== POSITION SUMMARY ===
• Current SOL Price: ${analysis['current_price']:.2f}
• Total P&L: ${analysis['total_unrealized_pl']:.2f} ({analysis['unrealized_pl_percent']:.2f}%)
• Total Capital: ${analysis['total_capital']:.2f}
• Available Capital: ${analysis['available_capital']:.2f}

=== ACTION REQUIRED ===
"""
        
        if analysis['stop_loss_triggered']:
            alert_entry += "1. 🔴 EXECUTE STOP-LOSS ORDERS: Close positions to limit losses\n"
        if analysis['take_profit_triggered']:
            alert_entry += "1. ✅ EXECUTE TAKE-PROFIT ORDERS: Close positions to realize profits\n"
        if analysis['critical_drawdown']:
            alert_entry += "2. 🔴 REVIEW TRADING STRATEGY: Drawdown exceeds acceptable limits\n"
        if analysis['critical_capital']:
            alert_entry += "3. 🔴 DEPOSIT ADDITIONAL CAPITAL: Insufficient funds for trading\n"
        if analysis['bots_stopped']:
            alert_entry += "4. 🔴 RESTART TRADING BOTS: Bots are not active\n"
        
        alert_entry += "\n=== ALERT END ===\n"
        
        # Save to critical alerts log
        with open('critical_alerts.log', 'a') as f:
            f.write(alert_entry)
        
        print("\n" + "="*50)
        print("CRITICAL ALERT GENERATED AND SAVED TO critical_alerts.log")
        print("="*50)