#!/usr/bin/env python3
"""
BULLETPROOF DASHBOARD - Simple, reliable, never fails
"""

from flask import Flask, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_simple_data():
    """Get simple, reliable data"""
    try:
        # Try to load tracker
        tracker_path = os.path.join(BASE_DIR, 'cumulative_pnl_tracker.json')
        if os.path.exists(tracker_path):
            with open(tracker_path, 'r') as f:
                tracker = json.load(f)
                summary = tracker['performance_summary']
                
                return {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'cumulative': {
                        'initial': summary['total_initial_capital'],
                        'current': summary['total_current_value'],
                        'pnl': summary['total_cumulative_pnl'],
                        'pnl_percent': summary['total_cumulative_pnl_percent']
                    },
                    'trades': {
                        'total': summary['total_trades'],
                        'winning': summary['winning_trades'],
                        'losing': summary['losing_trades'],
                        'win_rate': summary['win_rate']
                    },
                    'status': 'tracker_loaded'
                }
    except Exception as e:
        pass
    
    # Fallback data
    return {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'cumulative': {
            'initial': 946.97,
            'current': 531.65,
            'pnl': -415.32,
            'pnl_percent': -43.86
        },
        'trades': {
            'total': 7,
            'winning': 5,
            'losing': 2,
            'win_rate': 71.4
        },
        'status': 'fallback_data'
    }

@app.route('/')
def dashboard():
    """Simple text dashboard - never fails"""
    data = get_simple_data()
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>BULLETPROOF Trading Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: monospace;
            margin: 20px;
            background: #000;
            color: #0f0;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            border: 1px solid #0f0;
            padding: 20px;
        }}
        h1 {{ color: #0f0; }}
        .positive {{ color: #0f0; }}
        .negative {{ color: #f00; }}
        .warning {{ color: #ff0; }}
        .data {{ margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 BULLETPROOF TRADING DASHBOARD</h1>
        <p>Time: {data['timestamp']}</p>
        <p>Status: {data['status']}</p>
        
        <div class="warning">
            <h2>⚠️ CUMULATIVE P&L NEVER RESETS</h2>
            <p>Historical losses: -43.86% (permanent)</p>
        </div>
        
        <div class="data">
            <h2>💰 PERFORMANCE</h2>
            <p>Initial: ${data['cumulative']['initial']:.2f}</p>
            <p>Current: ${data['cumulative']['current']:.2f}</p>
            <p>P&L: <span class="{'positive' if data['cumulative']['pnl'] >= 0 else 'negative'}">${data['cumulative']['pnl']:+.2f} ({data['cumulative']['pnl_percent']:+.2f}%)</span></p>
        </div>
        
        <div class="data">
            <h2>📊 TRADING STATS</h2>
            <p>Total Trades: {data['trades']['total']}</p>
            <p>Winning: {data['trades']['winning']}</p>
            <p>Losing: {data['trades']['losing']}</p>
            <p>Win Rate: {data['trades']['win_rate']:.1f}%</p>
        </div>
        
        <div class="data">
            <h2>🔄 AUTO-REFRESH</h2>
            <p>Page refreshes every 30 seconds</p>
            <button onclick="location.reload()">Refresh Now</button>
        </div>
        
        <div class="warning">
            <h2>🚨 CRITICAL ISSUE</h2>
            <p>Binance Free Balance: $3.47 (TRADING BLOCKED)</p>
            <p>Need to use entire $76 balance</p>
            <p>Options: 1) Close positions 2) Add capital</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>
"""
    return html

@app.route('/api')
def api():
    """Simple API endpoint"""
    data = get_simple_data()
    return jsonify(data)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'bulletproof_dashboard'
    })

if __name__ == '__main__':
    print("="*70)
    print("🚀 BULLETPROOF DASHBOARD")
    print("="*70)
    print("📊 Simple, reliable, never fails")
    print("💰 Cumulative P&L: -43.86% (never resets)")
    print("🚨 Binance: $3.47 free (TRADING BLOCKED)")
    print("🌐 URL: http://localhost:5004")
    print("="*70)
    
    # Run on port 5004
    app.run(host='0.0.0.0', port=5004, debug=False)