#!/usr/bin/env python3
"""
Update generator for $100 trading experiment
Sends updates every 4 hours and on significant events
"""

import json
import os
from datetime import datetime
import random

def generate_update():
    """Generate a trading update"""
    
    # Try to load actual data if available
    report_file = 'experiment_data/latest_report.json'
    
    if os.path.exists(report_file):
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        # Real data available
        update = {
            "type": "scheduled_update",
            "timestamp": datetime.now().isoformat(),
            "balance": report["current_balance"],
            "total_value": report["total_value"],
            "total_pnl": report["total_pnl"],
            "total_pnl_pct": report["total_pnl_pct"],
            "open_positions": report["open_positions"],
            "total_trades": report["total_trades"],
            "win_rate": report["win_rate"],
            "status": "active",
            "message": f"Trading progress: ${report['total_pnl']:+.2f} ({report['total_pnl_pct']:+.2f}%) from {report['total_trades']} trades"
        }
    else:
        # No data yet - simulate initial state
        update = {
            "type": "initial_update",
            "timestamp": datetime.now().isoformat(),
            "balance": 100.00,
            "total_value": 100.00,
            "total_pnl": 0.00,
            "total_pnl_pct": 0.00,
            "open_positions": 0,
            "total_trades": 0,
            "win_rate": 0,
            "status": "awaiting_payment",
            "message": "Awaiting $100 payment to begin trading. System ready."
        }
    
    return update

def generate_trade_alert(trade_data):
    """Generate alert for a new trade"""
    alert = {
        "type": "trade_alert",
        "timestamp": datetime.now().isoformat(),
        "trade": trade_data,
        "urgency": "high",
        "message": f"New trade executed: {trade_data['symbol']} @ ${trade_data['price']}"
    }
    return alert

def save_update(update):
    """Save update to file"""
    os.makedirs('experiment_updates', exist_ok=True)
    
    filename = f"experiment_updates/update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(update, f, indent=2)
    
    # Also update latest update
    with open('experiment_updates/latest.json', 'w') as f:
        json.dump(update, f, indent=2)
    
    return filename

def format_update_for_display(update):
    """Format update for human-readable display"""
    
    if update["type"] == "trade_alert":
        trade = update["trade"]
        return f"""🚨 TRADE ALERT 🚨
        
📊 {trade['symbol']}
💰 Price: ${trade['price']:,.2f}
📈 Signal: {trade.get('signal', 'BUY')}
💵 Size: ${trade.get('size_usd', 20):.2f}
⏰ Time: {datetime.fromisoformat(update['timestamp']).strftime('%H:%M:%S')}

{update['message']}"""
    
    else:  # scheduled_update or initial_update
        emoji = "📈" if update["total_pnl"] > 0 else "📉" if update["total_pnl"] < 0 else "📊"
        
        return f"""{emoji} TRADING UPDATE ({datetime.fromisoformat(update['timestamp']).strftime('%H:%M')})
        
💰 Balance: ${update['balance']:.2f}
📈 Total Value: ${update['total_value']:.2f}
🎯 P&L: ${update['total_pnl']:+.2f} ({update['total_pnl_pct']:+.2f}%)
📊 Open Positions: {update['open_positions']}
🎮 Total Trades: {update['total_trades']}
🏆 Win Rate: {update['win_rate']}%

💬 {update['message']}

📊 Dashboard: http://127.0.0.1:5080"""

if __name__ == "__main__":
    # Generate a sample update
    update = generate_update()
    
    # Save it
    filename = save_update(update)
    
    # Display it
    print(format_update_for_display(update))
    print(f"\n📁 Saved to: {filename}")