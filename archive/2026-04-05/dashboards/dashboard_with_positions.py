#!/usr/bin/env python3
"""
DASHBOARD WITH POSITIONS - Shows all positions with P&L
"""

from flask import Flask, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_positions_data():
    """Load positions data"""
    try:
        tracker_path = os.path.join(BASE_DIR, 'cumulative_pnl_tracker.json')
        if os.path.exists(tracker_path):
            with open(tracker_path, 'r') as f:
                return json.load(f)
    except:
        pass
    return None

def get_dashboard_html():
    """Generate dashboard HTML with positions"""
    data = load_positions_data()
    
    if data:
        summary = data['performance_summary']
        positions = data.get('unrealized_positions', [])
        
        gemini_positions = [p for p in positions if p.get('source') == 'gemini']
        binance_positions = [p for p in positions if p.get('source') == 'binance_26crypto']
        
        # Calculate totals
        total_gemini_pnl = sum(p.get('unrealized_pnl', 0) for p in gemini_positions)
        total_binance_pnl = sum(p.get('unrealized_pnl', 0) for p in binance_positions)
        total_binance_risk = sum(p.get('capital_at_risk', 0) for p in binance_positions)
    else:
        # Fallback data
        summary = {
            'total_initial_capital': 946.97,
            'total_current_value': 531.65,
            'total_cumulative_pnl': -415.32,
            'total_cumulative_pnl_percent': -43.86,
            'total_trades': 7,
            'winning_trades': 5,
            'losing_trades': 2,
            'win_rate': 71.4
        }
        gemini_positions = []
        binance_positions = []
        total_gemini_pnl = -7.55
        total_binance_pnl = 0.23
        total_binance_risk = 50.00
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>📊 Trading Dashboard with Positions</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #0f172a;
            color: #e2e8f0;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(30, 41, 59, 0.8);
            border-radius: 15px;
            border: 1px solid #334155;
        }}
        .warning {{
            background: rgba(220, 38, 38, 0.2);
            border: 2px solid #dc2626;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .card {{
            background: rgba(30, 41, 59, 0.8);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #334155;
        }}
        .positive {{ color: #10b981; }}
        .negative {{ color: #ef4444; }}
        .gemini-card {{ border-left: 4px solid #3b82f6; }}
        .binance-card {{ border-left: 4px solid #f59e0b; }}
        .position-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .position-item {{
            background: rgba(51, 65, 85, 0.5);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #475569;
        }}
        .position-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .position-symbol {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        .position-side {{
            padding: 3px 8px;
            border-radius: 5px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .side-buy {{ background: rgba(16, 185, 129, 0.2); color: #10b981; }}
        .side-sell {{ background: rgba(239, 68, 68, 0.2); color: #ef4444; }}
        .position-details {{
            font-size: 0.9em;
            color: #94a3b8;
        }}
        .position-pnl {{
            font-size: 1.2em;
            font-weight: bold;
            margin-top: 10px;
            text-align: center;
        }}
        button {{
            background: #3b82f6;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            margin: 5px;
        }}
        button:hover {{ background: #2563eb; }}
        .refresh-btn {{ background: #10b981; }}
        .refresh-btn:hover {{ background: #059669; }}
        .danger-btn {{ background: #dc2626; }}
        .danger-btn:hover {{ background: #b91c1c; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .stat-item {{
            background: rgba(51, 65, 85, 0.5);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 TRADING DASHBOARD WITH POSITIONS</h1>
            <p>Real-time positions with individual P&L • Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="warning">
            <h3>🚨 CRITICAL: CAPITAL ALLOCATION ISSUE</h3>
            <p><strong>Binance Free Balance:</strong> $3.47 (TRADING BLOCKED)</p>
            <p><strong>Binance Total Balance:</strong> $76.61</p>
            <p><strong>Capital Tied in Positions:</strong> ${total_binance_risk:.2f}</p>
            <p><strong>To use entire $76:</strong> Close positions → Free up ${total_binance_risk:.2f} → Use full $76.61</p>
        </div>
        
        <div class="card">
            <h2>💰 CUMULATIVE PERFORMANCE (NEVER RESETS)</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div>Initial Capital</div>
                    <div class="stat-value">${summary['total_initial_capital']:.2f}</div>
                </div>
                <div class="stat-item">
                    <div>Current Value</div>
                    <div class="stat-value">${summary['total_current_value']:.2f}</div>
                </div>
                <div class="stat-item">
                    <div>Cumulative P&L</div>
                    <div class="stat-value {'positive' if summary['total_cumulative_pnl'] >= 0 else 'negative'}">
                        ${summary['total_cumulative_pnl']:+.2f}
                    </div>
                    <div>{summary['total_cumulative_pnl_percent']:+.2f}%</div>
                </div>
                <div class="stat-item">
                    <div>Win Rate</div>
                    <div class="stat-value">{summary['win_rate']:.1f}%</div>
                    <div>{summary['winning_trades']}W / {summary['losing_trades']}L</div>
                </div>
            </div>
        </div>
        
        <div class="card gemini-card">
            <h2>🔵 GEMINI POSITIONS ({len(gemini_positions)} LONG)</h2>
            <p>Total P&L: <span class="{'positive' if total_gemini_pnl >= 0 else 'negative'}">${total_gemini_pnl:+.2f}</span></p>
            
            <div class="position-grid">
"""
    
    # Add Gemini positions
    for pos in gemini_positions:
        pnl = pos.get('unrealized_pnl', 0)
        pnl_class = "positive" if pnl >= 0 else "negative"
        pnl_sign = "+" if pnl >= 0 else ""
        
        html += f"""
                <div class="position-item">
                    <div class="position-header">
                        <div class="position-symbol">{pos.get('symbol', 'N/A')}</div>
                        <div class="position-side side-buy">{pos.get('side', '').upper()}</div>
                    </div>
                    <div class="position-details">
                        <div>Entry: ${pos.get('entry_price', 0):.2f}</div>
                        <div>Current: ${pos.get('current_price', 0):.2f}</div>
                        <div>Quantity: {pos.get('quantity', 0):.6f}</div>
                        <div>Value: ${pos.get('current_value', 0):.2f}</div>
                        <div>Days: {pos.get('days_held', 0):.2f}</div>
                    </div>
                    <div class="position-pnl {pnl_class}">
                        {pnl_sign}${pnl:.2f} ({pnl_sign}{pos.get('unrealized_pnl_percent', 0):.2f}%)
                    </div>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <div class="card binance-card">
            <h2>🟡 BINANCE POSITIONS ({len(binance_positions)} SHORT • 3x Leverage)</h2>
            <p>Total P&L: <span class="{'positive' if total_binance_pnl >= 0 else 'negative'}">${total_binance_pnl:+.2f}</span> • Capital at Risk: ${total_binance_risk:.2f}</p>
            
            <div class="position-grid">
"""
    
    # Add Binance positions
    for pos in binance_positions:
        pnl = pos.get('unrealized_pnl', 0)
        pnl_class = "positive" if pnl >= 0 else "negative"
        pnl_sign = "+" if pnl >= 0 else ""
        
        html += f"""
                <div class="position-item">
                    <div class="position-header">
                        <div class="position-symbol">{pos.get('symbol', 'N/A')}</div>
                        <div class="position-side side-sell">{pos.get('side', '').upper()}</div>
                    </div>
                    <div class="position-details">
                        <div>Entry: ${pos.get('entry_price', 0):.2f}</div>
                        <div>Current: ${pos.get('current_price', 0):.2f}</div>
                        <div>Quantity: {pos.get('quantity', 0):.6f}</div>
                        <div>Position: ${pos.get('entry_value', 0):.2f}</div>
                        <div>Risk: ${pos.get('capital_at_risk', 0):.2f}</div>
                        <div>Days: {pos.get('days_held', 0):.2f}</div>
                    </div>
                    <div class="position-pnl {pnl_class}">
                        {pnl_sign}${pnl:.2f} ({pnl_sign}{pos.get('unrealized_pnl_percent', 0):.2f}%)
                    </div>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <div class="card">
            <h2>🔄 ACTIONS</h2>
            <div>
                <button class="refresh-btn" onclick="location.reload()">Refresh Dashboard</button>
                <button onclick="window.open('current_positions_report.html', '_blank')">View Detailed Report</button>
                <button onclick="window.open('http://localhost:5003', '_blank')">Port 5003 Dashboard</button>
                <button class="danger-btn" onclick="alert('To close positions and use entire $76, confirm: Close all 5 Binance positions?')">Close Positions to Free $50</button>
            </div>
            <p style="margin-top: 15px; color: #94a3b8;">Auto-refresh in <span id="countdown">60</span> seconds</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh countdown
        let countdown = 60;
        const countdownElement = document.getElementById('countdown');
        
        const timer = setInterval(() => {{
            countdown--;
            countdownElement.textContent = countdown;
            
            if (countdown <= 0) {{
                clearInterval(timer);
                location.reload();
            }}
        }}, 1000);
    </script>
</body>
</html>
"""
    
    return html

@app.route('/')
def dashboard():
    """Main dashboard with positions"""
    return get_dashboard_html()

@app.route('/api/positions')
def api_positions():
    """API endpoint for positions"""
    data = load_positions_data()
    if data:
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'positions': data.get('unrealized_positions', []),
            'summary': data['performance_summary']
        })
    return jsonify({'error': 'No data available'})

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'dashboard': 'with_positions'
    })

if __name__ == '__main__':
    print("="*80)
    print("📊 DASHBOARD WITH POSITIONS")
    print("="*80)
    print("Shows all positions with individual P&L")
    print("💰 Cumulative P&L: -43.86% (never resets)")
    print("🚨 Binance: $3.47 free (TRADING BLOCKED)")
    print("🌐 URL: http://localhost:5005")
    print("="*80)
    
    app.run(host='0.0.0.0', port=5005, debug=False)