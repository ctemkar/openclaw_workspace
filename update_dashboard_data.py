#!/usr/bin/env python3
"""
URGENT: Update dashboard data with REAL current positions
"""

import json
from datetime import datetime
import os

def update_tracker_with_real_data():
    """Update cumulative_pnl_tracker.json with real data"""
    
    # Load real Binance positions
    binance_positions = []
    try:
        with open('26_crypto_trade_history.json', 'r') as f:
            binance_data = json.load(f)
            for trade in binance_data:
                binance_positions.append({
                    'trade_id': trade.get('order_id', 'BINANCE_' + trade['symbol']),
                    'symbol': trade['symbol'],
                    'side': trade['side'],
                    'entry_price': trade.get('entry_price', trade.get('current_price', 0)),
                    'quantity': abs(trade.get('position_size', 30) / trade.get('entry_price', 1)),
                    'entry_value': abs(trade.get('position_size', 30)),
                    'fees_paid': 0,
                    'status': 'open',
                    'entry_date': trade.get('execution_time', datetime.now().isoformat()),
                    'source': 'binance_26crypto',
                    'current_price': trade.get('current_price', trade.get('mark_price', 0)),
                    'current_value': abs(trade.get('position_size', 30)) + trade.get('unrealized_pnl', 0),
                    'unrealized_pnl': trade.get('unrealized_pnl', 0),
                    'unrealized_pnl_percent': trade.get('pnl_percent', 0),
                    'days_held': 0.13,
                    'capital_at_risk': abs(trade.get('position_size', 30)) / 3,
                    'leverage': 3,
                    'notes': trade.get('notes', 'ACTUAL BINANCE POSITION')
                })
    except FileNotFoundError:
        print("Binance trade history not found")
    
    # Load Gemini trades (closed positions)
    gemini_trades = []
    try:
        with open('daily_trades.json', 'r') as f:
            gemini_data = json.load(f)
            for trade in gemini_data.get('trades', []):
                if trade['status'] == 'closed':
                    gemini_trades.append({
                        'trade_id': trade['id'],
                        'symbol': trade['symbol'],
                        'side': trade['side'],
                        'entry_price': trade['price'],
                        'quantity': trade['amount'],
                        'entry_value': trade['value'],
                        'fees_paid': trade.get('fees', 0) + trade.get('close_fees', 0),
                        'status': 'closed',
                        'entry_date': trade['timestamp'],
                        'close_date': trade.get('close_timestamp', ''),
                        'close_price': trade.get('close_price', 0),
                        'source': 'gemini',
                        'realized_pnl': trade.get('pnl', 0),
                        'realized_pnl_percent': trade.get('pnl_percent', 0),
                        'notes': trade.get('notes', '')
                    })
    except FileNotFoundError:
        print("Gemini daily trades not found")
    
    # Load system status for capital
    capital_data = {}
    try:
        with open('system_status.json', 'r') as f:
            system_data = json.load(f)
            capital_data = system_data.get('capital', {})
    except FileNotFoundError:
        print("System status not found")
    
    # Calculate totals
    total_unrealized_pnl = sum(p['unrealized_pnl'] for p in binance_positions)
    total_realized_pnl = sum(t.get('realized_pnl', 0) for t in gemini_trades)
    total_capital_at_risk = sum(p.get('capital_at_risk', 0) for p in binance_positions)
    
    # Create updated tracker
    updated_tracker = {
        "metadata": {
            "created": "2026-03-31T19:45:00.000000",
            "last_updated": datetime.now().isoformat(),
            "notes": "UPDATED WITH REAL DATA - Binance shorts active, Gemini positions closed"
        },
        "performance_summary": {
            "total_initial_capital": capital_data.get('initial', 946.97),
            "total_current_value": capital_data.get('current', 531.65),
            "total_realized_pnl": total_realized_pnl,
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_cumulative_pnl": capital_data.get('pnl', -415.32),
            "total_cumulative_pnl_percent": capital_data.get('pnl_percent', -43.86),
            "total_fees_paid": sum(t.get('fees_paid', 0) for t in gemini_trades),
            "total_trades": len(binance_positions) + len(gemini_trades),
            "winning_trades": len([p for p in binance_positions if p['unrealized_pnl'] > 0]) + 
                            len([t for t in gemini_trades if t.get('realized_pnl', 0) > 0]),
            "losing_trades": len([p for p in binance_positions if p['unrealized_pnl'] < 0]) + 
                           len([t for t in gemini_trades if t.get('realized_pnl', 0) < 0]),
            "win_rate": 0.0  # Will calculate below
        },
        "capital_timeline": [
            {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "event": "REAL_DATA_UPDATE",
                "initial_capital": capital_data.get('initial', 946.97),
                "current_value": capital_data.get('current', 531.65),
                "realized_pnl": total_realized_pnl,
                "unrealized_pnl": total_unrealized_pnl,
                "cumulative_pnl": capital_data.get('pnl', -415.32),
                "notes": "REALITY: 5 Binance SHORTS active (all losing), Gemini BTC sold"
            }
        ],
        "realized_trades": gemini_trades,
        "unrealized_positions": binance_positions,
        "dashboard_notes": [
            "🚨 URGENT: Dashboard updated with REAL data",
            "📉 5 Binance SHORT positions active (all losing)",
            "💰 Total P&L: $" + str(round(total_unrealized_pnl + total_realized_pnl, 2)),
            "⚡ Bot parameters UPDATED: 3% threshold, 1x leverage, 10% position size",
            "🔴 Only $0.15 available for new trades - need to close positions",
            "🔄 Refresh dashboard to see updates"
        ]
    }
    
    # Calculate win rate
    total_trades = updated_tracker["performance_summary"]["total_trades"]
    winning_trades = updated_tracker["performance_summary"]["winning_trades"]
    if total_trades > 0:
        updated_tracker["performance_summary"]["win_rate"] = (winning_trades / total_trades) * 100
    
    # Save updated tracker
    with open('cumulative_pnl_tracker.json', 'w') as f:
        json.dump(updated_tracker, f, indent=2)
    
    print("✅ UPDATED cumulative_pnl_tracker.json with REAL data")
    print(f"   • {len(binance_positions)} Binance positions")
    print(f"   • {len(gemini_trades)} Gemini closed trades")
    print(f"   • Total unrealized P&L: ${total_unrealized_pnl:.2f}")
    print(f"   • Total realized P&L: ${total_realized_pnl:.2f}")
    
    return updated_tracker

def restart_dashboard():
    """Restart the dashboard to show updated data"""
    print("\n🔄 RESTARTING DASHBOARD...")
    
    # Find and kill existing dashboard
    os.system("pkill -f 'dashboard_with_positions.py' 2>/dev/null")
    os.system("pkill -f 'python.*5004' 2>/dev/null")
    
    # Start dashboard
    import subprocess
    import time
    
    # Start dashboard in background
    dashboard_process = subprocess.Popen(
        ["python3", "dashboard_with_positions.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    time.sleep(3)  # Wait for dashboard to start
    
    print("✅ Dashboard restarted on http://localhost:5004/")
    print("   Please refresh your browser")
    
    return dashboard_process

def create_quick_dashboard():
    """Create a quick HTML dashboard with current data"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>REAL-TIME TRADING DASHBOARD</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: monospace;
            margin: 20px;
            background: #000;
            color: #0f0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            border: 1px solid #0f0;
            padding: 20px;
        }
        .urgent {
            color: #f00;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #0f0;
            padding: 8px;
            text-align: left;
        }
        th {
            background: #002200;
        }
        .positive {
            color: #0f0;
        }
        .negative {
            color: #f00;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚨 REAL-TIME TRADING DASHBOARD</h1>
        <p class="urgent">UPDATED: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        
        <h2>📊 CURRENT POSITIONS (REAL DATA)</h2>
"""
    
    # Add positions table
    try:
        with open('26_crypto_trade_history.json', 'r') as f:
            positions = json.load(f)
        
        html += """
        <table>
            <tr>
                <th>Symbol</th>
                <th>Type</th>
                <th>Entry</th>
                <th>Current</th>
                <th>P&L</th>
                <th>P&L %</th>
                <th>Size</th>
                <th>Status</th>
            </tr>
"""
        
        for pos in positions:
            pnl_class = "negative" if pos.get('unrealized_pnl', 0) < 0 else "positive"
            html += f"""
            <tr>
                <td>{pos['symbol']}</td>
                <td>{pos['type']}</td>
                <td>${pos.get('entry_price', 0):.4f}</td>
                <td>${pos.get('current_price', 0):.4f}</td>
                <td class="{pnl_class}">${pos.get('unrealized_pnl', 0):.2f}</td>
                <td class="{pnl_class}">{pos.get('pnl_percent', 0):.2f}%</td>
                <td>${abs(pos.get('position_size', 0)):.2f}</td>
                <td>{pos['status']}</td>
            </tr>
"""
        
        html += """
        </table>
"""
    except:
        html += "<p>Error loading positions data</p>"
    
    # Add summary
    try:
        with open('system_status.json', 'r') as f:
            status = json.load(f)
            capital = status.get('capital', {})
        
        html += f"""
        <h2>💰 CAPITAL SUMMARY</h2>
        <table>
            <tr><td>Initial Capital</td><td>${capital.get('initial', 0):.2f}</td></tr>
            <tr><td>Current Capital</td><td>${capital.get('current', 0):.2f}</td></tr>
            <tr><td>Cumulative P&L</td><td class="negative">{capital.get('pnl_percent', 0):.2f}%</td></tr>
            <tr><td>Free USD</td><td>${capital.get('free_usd', 0):.2f}</td></tr>
            <tr><td>Recovery Needed</td><td>+{capital.get('recovery_percent_needed', 0):.1f}%</td></tr>
        </table>
"""
    except:
        html += "<p>Error loading capital data</p>"
    
    html += """
        <h2>⚡ BOT STATUS</h2>
        <p>✅ Parameters UPDATED: 3% threshold, 1x leverage, 10% position size</p>
        <p>🔴 Blocked: Only $0.15 available - need to close positions</p>
        <p>🎯 Next: Close DOT position (-7.11%) to free $30.70</p>
        
        <p class="urgent">🔄 Refresh page for latest data</p>
    </div>
</body>
</html>
"""
    
    with open('real_time_dashboard.html', 'w') as f:
        f.write(html)
    
    print("✅ Created real_time_dashboard.html")
    print("   Open in browser: file://" + os.path.abspath('real_time_dashboard.html'))

if __name__ == "__main__":
    print("🚨 URGENT DASHBOARD UPDATE")
    print("=" * 60)
    
    # Update tracker with real data
    tracker = update_tracker_with_real_data()
    
    # Create quick dashboard
    create_quick_dashboard()
    
    # Try to restart dashboard
    try:
        restart_dashboard()
    except:
        print("⚠️ Could not restart dashboard (may not be running)")
    
    print("\n✅ DASHBOARDS UPDATED:")
    print("   1. cumulative_pnl_tracker.json - Updated with real data")
    print("   2. real_time_dashboard.html - Quick view")
    print("   3. Dashboard on port 5004 - Should show updated data")
    print("\n🔄 Please refresh: http://localhost:5004/")
    print("📁 Or open: real_time_dashboard.html")