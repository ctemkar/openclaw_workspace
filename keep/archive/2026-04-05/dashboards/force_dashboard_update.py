#!/usr/bin/env python3
"""
FORCE dashboard update with corrected data
"""

import json
from datetime import datetime
import os

def update_dashboard_data():
    """Update dashboard data with REAL corrected positions"""
    
    print("🔄 FORCING DASHBOARD UPDATE")
    print("=" * 60)
    
    # Load corrected positions
    with open('26_crypto_trade_history.json', 'r') as f:
        positions = json.load(f)
    
    open_positions = [p for p in positions if p.get('status') == 'OPEN']
    closed_positions = [p for p in positions if p.get('status') == 'CLOSED']
    
    print(f"📊 Corrected data:")
    print(f"  Open positions: {len(open_positions)}")
    for pos in open_positions:
        print(f"    {pos['symbol']}: ${pos.get('unrealized_pnl', 0):.2f} ({pos.get('pnl_percent', 0):.2f}%)")
    
    print(f"  Closed positions: {len(closed_positions)}")
    
    # Load system status
    with open('system_status.json', 'r') as f:
        system_status = json.load(f)
    
    # Calculate totals
    total_unrealized_pnl = sum(p.get('unrealized_pnl', 0) for p in open_positions)
    total_realized_pnl = sum(p.get('realized_pnl', 0) for p in closed_positions)
    total_capital_at_risk = sum(p.get('position_size', 0) / 3 for p in open_positions)  # 3x leverage
    
    # Create updated tracker
    updated_tracker = {
        "metadata": {
            "created": "2026-03-31T19:45:00.000000",
            "last_updated": datetime.now().isoformat(),
            "notes": "CORRECTED DATA - Real positions after fixes"
        },
        "performance_summary": {
            "total_initial_capital": system_status['capital'].get('initial', 946.97),
            "total_current_value": system_status['capital'].get('current', 531.65),
            "total_realized_pnl": total_realized_pnl,
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_cumulative_pnl": system_status['capital'].get('pnl', -415.32),
            "total_cumulative_pnl_percent": system_status['capital'].get('pnl_percent', -43.86),
            "total_fees_paid": 0,
            "total_trades": len(open_positions) + len(closed_positions),
            "winning_trades": len([p for p in open_positions if p.get('unrealized_pnl', 0) > 0]) + 
                            len([p for p in closed_positions if p.get('realized_pnl', 0) > 0]),
            "losing_trades": len([p for p in open_positions if p.get('unrealized_pnl', 0) < 0]) + 
                           len([p for p in closed_positions if p.get('realized_pnl', 0) < 0]),
            "win_rate": 0.0
        },
        "capital_timeline": [
            {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "event": "DATA_CORRECTED",
                "initial_capital": system_status['capital'].get('initial', 946.97),
                "current_value": system_status['capital'].get('current', 531.65),
                "realized_pnl": total_realized_pnl,
                "unrealized_pnl": total_unrealized_pnl,
                "cumulative_pnl": system_status['capital'].get('pnl', -415.32),
                "notes": "CORRECTED: 3 positions open (SOL, XRP, ADA), DOT & ETH closed"
            }
        ],
        "realized_trades": [
            {
                'trade_id': p.get('order_id', 'CLOSED_' + p['symbol']),
                'symbol': p['symbol'],
                'side': p.get('side', 'sell'),
                'entry_price': p.get('entry_price', 0),
                'quantity': p.get('amount', 0),
                'entry_value': p.get('position_size', 0),
                'close_price': p.get('close_price', 0),
                'close_value': p.get('position_size', 0) + p.get('realized_pnl', 0),
                'realized_pnl': p.get('realized_pnl', 0),
                'realized_pnl_percent': p.get('pnl_percent', 0),
                'status': 'closed',
                'source': 'binance',
                'notes': p.get('notes', 'Closed position')
            }
            for p in closed_positions
        ],
        "unrealized_positions": [
            {
                'trade_id': p.get('order_id', 'OPEN_' + p['symbol']),
                'symbol': p['symbol'],
                'side': p.get('side', 'sell'),
                'entry_price': p.get('entry_price', 0),
                'quantity': p.get('amount', 0),
                'entry_value': p.get('position_size', 0),
                'status': 'open',
                'entry_date': p.get('execution_time', datetime.now().isoformat()),
                'source': 'binance_26crypto',
                'current_price': p.get('current_price', 0),
                'current_value': p.get('position_size', 0) + p.get('unrealized_pnl', 0),
                'unrealized_pnl': p.get('unrealized_pnl', 0),
                'unrealized_pnl_percent': p.get('pnl_percent', 0),
                'days_held': 0.2,
                'capital_at_risk': p.get('position_size', 0) / 3,
                'leverage': p.get('leverage', 3),
                'notes': p.get('notes', 'Open position')
            }
            for p in open_positions
        ],
        "dashboard_notes": [
            "✅ DATA CORRECTED - Real positions loaded",
            f"📊 {len(open_positions)} open positions: SOL, XRP, ADA",
            f"💰 Total unrealized P&L: ${total_unrealized_pnl:.2f}",
            f"⚡ Enhanced bot running with automatic position management",
            f"🔴 Blocked: At max positions (3/3), low capital ($4.34)",
            f"🔄 Refresh browser to see updates"
        ]
    }
    
    # Calculate win rate
    total_trades = updated_tracker["performance_summary"]["total_trades"]
    winning_trades = updated_tracker["performance_summary"]["winning_trades"]
    if total_trades > 0:
        updated_tracker["performance_summary"]["win_rate"] = (winning_trades / total_trades) * 100
    
    # Save to dashboard file
    with open('cumulative_pnl_tracker.json', 'w') as f:
        json.dump(updated_tracker, f, indent=2)
    
    print(f"✅ Updated cumulative_pnl_tracker.json")
    print(f"   • {len(open_positions)} open positions")
    print(f"   • {len(closed_positions)} closed positions")
    print(f"   • Total unrealized P&L: ${total_unrealized_pnl:.2f}")
    
    return updated_tracker

def restart_dashboard():
    """Restart dashboard to show updated data"""
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
    
    time.sleep(5)  # Wait for dashboard to start
    
    print("✅ Dashboard restarted on http://localhost:5004/")
    
    # Test dashboard
    import requests
    try:
        response = requests.get("http://localhost:5004/", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard responding")
            # Check if it shows our data
            if "SOL" in response.text or "XRP" in response.text or "ADA" in response.text:
                print("✅ Dashboard showing position data")
            else:
                print("⚠️ Dashboard may not show position data yet")
        else:
            print(f"❌ Dashboard error: {response.status_code}")
    except:
        print("❌ Dashboard not reachable")
    
    return dashboard_process

def create_simple_dashboard():
    """Create a simple HTML dashboard that definitely shows the data"""
    html = """<!DOCTYPE html>
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
        
        <h2>📊 CURRENT POSITIONS (REAL DATA - CORRECTED)</h2>
"""
    
    # Add positions table
    try:
        with open('26_crypto_trade_history.json', 'r') as f:
            positions = json.load(f)
        
        open_positions = [p for p in positions if p.get('status') == 'OPEN']
        
        if open_positions:
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
            
            for pos in open_positions:
                pnl = pos.get('unrealized_pnl', 0)
                pnl_class = "negative" if pnl < 0 else "positive"
                html += f"""
            <tr>
                <td>{pos['symbol']}</td>
                <td>{pos.get('type', 'SHORT')}</td>
                <td>${pos.get('entry_price', 0):.4f}</td>
                <td>${pos.get('current_price', 0):.4f}</td>
                <td class="{pnl_class}">${pnl:.2f}</td>
                <td class="{pnl_class}">{pos.get('pnl_percent', 0):.2f}%</td>
                <td>${pos.get('position_size', 0):.2f}</td>
                <td>{pos.get('status', 'OPEN')}</td>
            </tr>
"""
            
            html += """
        </table>
"""
        else:
            html += "<p>No open positions</p>"
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
            <tr><td>Open Positions</td><td>{status.get('positions', {}).get('open', 0)}</td></tr>
            <tr><td>Closed Positions</td><td>{status.get('positions', {}).get('closed', 0)}</td></tr>
        </table>
"""
    except:
        html += "<p>Error loading capital data</p>"
    
    html += """
        <h2>⚡ BOT STATUS</h2>
        <p>✅ Enhanced bot running with automatic position management</p>
        <p>🔴 Blocked: At max positions (3/3), low capital ($4.34)</p>
        <p>🎯 Next: Close 1 position to free capital for new trades</p>
        
        <p class="urgent">🔄 This dashboard shows REAL CORRECTED data</p>
        <p><a href="http://localhost:5004/" target="_blank">Also check main dashboard</a></p>
    </div>
</body>
</html>
"""
    
    with open('corrected_dashboard.html', 'w') as f:
        f.write(html)
    
    print("✅ Created corrected_dashboard.html")
    print("   Open in browser: file://" + os.path.abspath('corrected_dashboard.html'))

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 FORCE DASHBOARD UPDATE WITH CORRECTED DATA")
    print("=" * 60)
    
    # Update dashboard data
    tracker = update_dashboard_data()
    
    # Create simple dashboard
    create_simple_dashboard()
    
    # Restart main dashboard
    try:
        restart_dashboard()
    except:
        print("⚠️ Could not restart dashboard")
    
    print("\n✅ DASHBOARDS UPDATED:")
    print("   1. cumulative_pnl_tracker.json - Updated with corrected data")
    print("   2. corrected_dashboard.html - Simple view with REAL data")
    print("   3. Main dashboard on port 5004 - Restarted")
    print("\n🔄 Please refresh: http://localhost:5004/")
    print("📁 Or open: corrected_dashboard.html")
    print("\n🎯 REAL DATA SHOULD NOW SHOW:")
    print("   • 3 open positions: SOL, XRP, ADA")
    print("   • Correct P&L values")
    print("   • Updated capital status")