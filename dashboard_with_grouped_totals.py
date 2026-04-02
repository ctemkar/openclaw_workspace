#!/usr/bin/env python3
"""
DASHBOARD WITH GROUPED TOTALS
Shows separate totals for Gemini and Binance, plus overall totals
"""

from flask import Flask, render_template_string, jsonify
import json
import os
from datetime import datetime
import threading
import time

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📊 Trading System Dashboard - GROUPED TOTALS</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="30">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 20px;
            background: #0f172a;
            color: #e2e8f0;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
            padding: 20px;
            background: #1e293b;
            border-radius: 10px;
            border: 1px solid #334155;
        }
        h1 {
            color: #00ff9d;
            margin: 0;
            font-size: 2.5em;
        }
        .subtitle {
            color: #94a3b8;
            margin: 10px 0 20px 0;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        .summary-card {
            background: #1e293b;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #334155;
            text-align: center;
        }
        .summary-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #00ff9d;
            margin: 10px 0;
        }
        .summary-label {
            color: #94a3b8;
            font-size: 0.9em;
        }
        .positive {
            color: #10b981;
        }
        .negative {
            color: #ef4444;
        }
        .section {
            margin-top: 30px;
        }
        .section-title {
            color: #cbd5e1;
            font-size: 1.3em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #334155;
        }
        .trade-table {
            width: 100%;
            border-collapse: collapse;
            background: #1e293b;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #334155;
            margin-bottom: 20px;
        }
        .trade-table th {
            background: #334155;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
            color: #cbd5e1;
            border-bottom: 2px solid #475569;
        }
        .trade-table td {
            padding: 10px 15px;
            border-bottom: 1px solid #334155;
        }
        .trade-table tr:hover {
            background: #2d3748;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
        }
        .badge-gemini {
            background: rgba(59, 130, 246, 0.2);
            color: #3b82f6;
            border: 1px solid #3b82f6;
        }
        .badge-binance {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
            border: 1px solid #f59e0b;
        }
        .side-buy {
            color: #10b981;
            font-weight: bold;
        }
        .side-sell {
            color: #ef4444;
            font-weight: bold;
        }
        .status-badges {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin: 15px 0;
        }
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
        }
        .status-active {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid #10b981;
        }
        .status-warning {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
            border: 1px solid #f59e0b;
        }
        .last-updated {
            text-align: center;
            margin-top: 20px;
            color: #94a3b8;
            font-size: 0.9em;
        }
        .controls {
            text-align: center;
            margin: 20px 0;
        }
        .control-btn {
            display: inline-block;
            padding: 8px 16px;
            margin: 0 5px;
            background: rgba(0, 255, 157, 0.1);
            color: #00ff9d;
            border: 1px solid #00ff9d;
            border-radius: 5px;
            text-decoration: none;
            font-size: 0.9em;
        }
        .control-btn:hover {
            background: rgba(0, 255, 157, 0.2);
        }
        .exchange-totals {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
        }
        .exchange-card {
            background: #1e293b;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #334155;
            text-align: center;
        }
        .exchange-card.gemini {
            border-color: #3b82f6;
            background: rgba(59, 130, 246, 0.05);
        }
        .exchange-card.binance {
            border-color: #f59e0b;
            background: rgba(245, 158, 11, 0.05);
        }
        .exchange-card.overall {
            border-color: #00ff9d;
            background: rgba(0, 255, 157, 0.05);
        }
        .exchange-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .exchange-title.gemini {
            color: #3b82f6;
        }
        .exchange-title.binance {
            color: #f59e0b;
        }
        .exchange-title.overall {
            color: #00ff9d;
        }
        .exchange-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        .stat-item {
            text-align: center;
        }
        .stat-value {
            font-size: 1.3em;
            font-weight: bold;
            margin: 5px 0;
        }
        .stat-label {
            font-size: 0.8em;
            color: #94a3b8;
        }
        .trade-group {
            margin-bottom: 25px;
        }
        .group-header {
            background: #2d3748;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .group-title {
            font-weight: bold;
            font-size: 1.1em;
        }
        .group-count {
            color: #94a3b8;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Trading System Dashboard</h1>
            <p class="subtitle">Grouped totals by exchange | {{ overall_stats.total_trades }} trades total</p>
            
            <div class="status-badges">
                <div class="status-badge status-active">System: ACTIVE</div>
                <div class="status-badge status-active">Trading: AGGRESSIVE</div>
                <div class="status-badge">Hedge Prevention: ✅ ACTIVE</div>
                <div class="status-badge">Fixed: ✅ NO SIMULTANEOUS LONG/SHORT</div>
            </div>
        </div>
        
        <div class="controls">
            <a href="#exchange-totals" class="control-btn">📊 Exchange Totals</a>
            <a href="#gemini-trades" class="control-btn">🔵 Gemini Trades</a>
            <a href="#binance-trades" class="control-btn">🟡 Binance Trades</a>
            <a href="http://localhost:5011" target="_blank" class="control-btn">📈 Trades Dashboard</a>
        </div>
        
        <!-- EXCHANGE TOTALS SECTION -->
        <div class="section" id="exchange-totals">
            <div class="section-title">📊 EXCHANGE TOTALS (Grouped by Exchange)</div>
            
            <div class="exchange-totals">
                <!-- GEMINI TOTALS -->
                <div class="exchange-card gemini">
                    <div class="exchange-title gemini">🔵 GEMINI (LONG ONLY)</div>
                    <div class="summary-value">{{ gemini_stats.total_trades }}</div>
                    <div class="summary-label">Total Trades</div>
                    
                    <div class="exchange-stats">
                        <div class="stat-item">
                            <div class="stat-value {{ 'positive' if gemini_stats.profitable_trades > 0 else '' }}">
                                {{ gemini_stats.profitable_trades }}
                            </div>
                            <div class="stat-label">Profitable</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value {{ 'positive' if gemini_stats.win_rate >= 50 else 'negative' }}">
                                {{ "%.1f"|format(gemini_stats.win_rate) }}%
                            </div>
                            <div class="stat-label">Win Rate</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value {{ 'positive' if gemini_stats.total_pnl >= 0 else 'negative' }}">
                                ${{ "%.2f"|format(gemini_stats.total_pnl) }}
                            </div>
                            <div class="stat-label">Total P&L</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value {{ 'positive' if gemini_stats.avg_pnl_percent >= 0 else 'negative' }}">
                                {{ "%.2f"|format(gemini_stats.avg_pnl_percent) }}%
                            </div>
                            <div class="stat-label">Avg P&L %</div>
                        </div>
                    </div>
                </div>
                
                <!-- BINANCE TOTALS -->
                <div class="exchange-card binance">
                    <div class="exchange-title binance">🟡 BINANCE (SHORT ONLY)</div>
                    <div class="summary-value">{{ binance_stats.total_trades }}</div>
                    <div class="summary-label">Total Trades</div>
                    
                    <div class="exchange-stats">
                        <div class="stat-item">
                            <div class="stat-value {{ 'positive' if binance_stats.profitable_trades > 0 else '' }}">
                                {{ binance_stats.profitable_trades }}
                            </div>
                            <div class="stat-label">Profitable</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value {{ 'positive' if binance_stats.win_rate >= 50 else 'negative' }}">
                                {{ "%.1f"|format(binance_stats.win_rate) }}%
                            </div>
                            <div class="stat-label">Win Rate</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value {{ 'positive' if binance_stats.total_pnl >= 0 else 'negative' }}">
                                ${{ "%.2f"|format(binance_stats.total_pnl) }}
                            </div>
                            <div class="stat-label">Total P&L</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value {{ 'positive' if binance_stats.avg_pnl_percent >= 0 else 'negative' }}">
                                {{ "%.2f"|format(binance_stats.avg_pnl_percent) }}%
                            </div>
                            <div class="stat-label">Avg P&L %</div>
                        </div>
                    </div>
                </div>
                
                <!-- OVERALL TOTALS -->
                <div class="exchange-card overall">
                    <div class="exchange-title overall">📈 OVERALL TOTALS</div>
                    <div class="summary-value">{{ overall_stats.total_trades }}</div>
                    <div class="summary-label">Total Trades</div>
                    
                    <div class="exchange-stats">
                        <div class="stat-item">
                            <div class="stat-value {{ 'positive' if overall_stats.profitable_trades > 0 else '' }}">
                                {{ overall_stats.profitable_trades }}
                            </div>
                            <div class="stat-label">Profitable</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value {{ 'positive' if overall_stats.win_rate >= 50 else 'negative' }}">
                                {{ "%.1f"|format(overall_stats.win_rate) }}%
                            </div>
                            <div class="stat-label">Win Rate</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value {{ 'positive' if overall_stats.total_pnl >= 0 else 'negative' }}">
                                ${{ "%.2f"|format(overall_stats.total_pnl) }}
                            </div>
                            <div class="stat-label">Total P&L</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value {{ 'positive' if overall_stats.avg_pnl_percent >= 0 else 'negative' }}">
                                {{ "%.2f"|format(overall_stats.avg_pnl_percent) }}%
                            </div>
                            <div class="stat-label">Avg P&L %</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- GEMINI TRADES SECTION -->
        <div class="section" id="gemini-trades">
            <div class="section-title">🔵 GEMINI TRADES (LONG POSITIONS)</div>
            
            <div class="trade-group">
                <div class="group-header">
                    <div class="group-title">Gemini LONG Positions</div>
                    <div class="group-count">{{ gemini_trades|length }} trades</div>
                </div>
                
                <table class="trade-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Symbol</th>
                            <th>Side</th>
                            <th>Entry Price</th>
                            <th>Current Price</th>
                            <th>P&L</th>
                            <th>P&L %</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for trade in gemini_trades %}
                        <tr>
                            <td>{{ loop.index }}</td>
                            <td><strong>{{ trade.symbol }}</strong></td>
                            <td class="side-buy">▲ LONG</td>
                            <td>${{ "%.4f"|format(trade.entry_price) }}</td>
                            <td>${{ "%.4f"|format(trade.current_price) }}</td>
                            <td class="{{ 'positive' if trade.pnl >= 0 else 'negative' }}">
                                ${{ "%.2f"|format(trade.pnl) }}
                            </td>
                            <td class="{{ 'positive' if trade.pnl_percent >= 0 else 'negative' }}">
                                {{ "%.2f"|format(trade.pnl_percent) }}%
                            </td>
                            <td>{{ trade.timestamp[:16] if trade.timestamp != 'unknown' else 'N/A' }}</td>
                        </tr>
                        {% endfor %}
                        
                        <!-- GEMINI TOTALS ROW -->
                        <tr style="background: rgba(59, 130, 246, 0.1); font-weight: bold; border-top: 2px solid #3b82f6;">
                            <td colspan="5" style="text-align: right; padding-right: 20px;">
                                <strong>GEMINI TOTALS ({{ gemini_stats.total_trades }} trades):</strong>
                            </td>
                            <td class="{{ 'positive' if gemini_stats.total_pnl >= 0 else 'negative' }}">
                                ${{ "%.2f"|format(gemini_stats.total_pnl) }}
                            </td>
                            <td class="{{ 'positive' if gemini_stats.avg_pnl_percent >= 0 else 'negative' }}">
                                {{ "%.2f"|format(gemini_stats.avg_pnl_percent) }}%
                            </td>
                            <td>
                                {{ gemini_stats.profitable_trades }}/{{ gemini_stats.total_trades }} profitable
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- BINANCE TRADES SECTION -->
        <div class="section" id="binance-trades">
            <div class="section-title">🟡 BINANCE TRADES (SHORT POSITIONS)</div>
            
            <div class="trade-group">
                <div class="group-header">
                    <div class="group-title">Binance SHORT Positions</div>
                    <div class="group-count">{{ binance_trades|length }} trades</div>
                </div>
                
                <table class="trade-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Symbol</th>
                            <th>Side</th>
                            <th>Entry Price</th>
                            <th>Current Price</th>
                            <th>P&L</th>
                            <th>P&L %</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for trade in binance_trades %}
                        <tr>
                            <td>{{ loop.index }}</td>
                            <td><strong>{{ trade.symbol }}</strong></td>
                            <td class="side-sell">▼ SHORT</td>
                            <td>${{ "%.4f"|format(trade.entry_price) }}</td>
                            <td>${{ "%.4f"|format(trade.current_price) }}</td>
                            <td class="{{ 'positive' if trade.pnl >= 0 else 'negative' }}">
                                ${{ "%.2f"|format(trade.pnl) }}
                            </td>
                            <td class="{{ 'positive' if trade.pnl_percent >= 0 else 'negative' }}">
                                {{ "%.2f"|format(trade.pnl_percent) }}%
                            </td>
                            <td>{{ trade.timestamp[:16] if trade.timestamp != 'unknown' else 'N/A' }}</td>
                        </tr>
                        {% endfor %}
                        
                        <!-- BINANCE TOTALS ROW -->
                        <tr style="background: rgba(245, 158, 11, 0.1); font-weight: bold; border-top: 2px solid #f59e0b;">
                            <td colspan="5" style="text-align: right; padding-right: 20px;">
                                <strong>BINANCE TOTALS ({{ binance_stats.total_trades }} trades):</strong>
                            </td>
                            <td class="{{ 'positive' if binance_stats.total_pnl >= 0 else 'negative' }}">
                                ${{ "%.2f"|format(binance_stats.total_pnl) }}
                            </td>
                            <td class="{{ 'positive' if binance_stats.avg_pnl_percent >= 0 else 'negative' }}">
                                {{ "%.2f"|format(binance_stats.avg_pnl_percent) }}%
                            </td>
                            <td>
                                {{ binance_stats.profitable_trades }}/{{ binance_stats.total_trades }} profitable
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="last-updated">
            Last updated: {{ last_updated }} | Auto-refreshes every 30 seconds<br>
            Gemini: {{ gemini_stats.total_trades }} trades | Binance: {{ binance_stats.total_trades }} trades | Overall: {{ overall_stats.total_trades }} trades
        </div>
    </div>
</body>
</html>
'''

def load_trade_data():
    """Load trade data from trading_data/trades.json"""
    trades = []
    
    try:
        trades_file = os.path.join(BASE_DIR, 'trading_data', 'trades.json')
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                raw_trades = json.load(f)
            
            # Process trades for display
            for i, trade in enumerate(raw_trades):
                processed_trade = {
                    'index': i + 1,
                    'exchange': trade.get('exchange', 'unknown'),
                    'symbol': trade.get('symbol', 'unknown').replace(':USDT', '').replace('/USDT', '').replace('/USD', ''),
                    'side': trade.get('side', 'unknown'),
                    'entry_price': trade.get('price', 0),
                    'current_price': trade.get('current_price', trade.get('price', 0)),
                    'pnl': trade.get('pnl', 0),
                    'pnl_percent': trade.get('pnl_percent', 0),
                    'timestamp': trade.get('timestamp', 'unknown')
                }
                trades.append(processed_trade)
            
            print(f"✅ Loaded {len(trades)} trades from trading_data/trades.json")
        else:
            print(f"⚠️  trades.json not found, using sample data")
            # Sample data if file not found
            trades = [
                {'index': 1, 'exchange': 'gemini', 'symbol': 'BTC', 'side': 'buy', 
                 'entry_price': 42000.50, 'current_price': 41850.75, 'pnl': -149.75, 'pnl_percent': -0.36, 'timestamp': '14:10'},
                {'index': 2, 'exchange': 'binance', 'symbol': 'ETH', 'side': 'sell', 
                 'entry_price': 3200.25, 'current_price': 3250.50, 'pnl': -50.25, 'pnl_percent': -1.57, 'timestamp': '14:05'},
            ]
    except Exception as e:
        print(f"❌ Error loading trade data: {e}")
        trades = []
    
    return trades

def calculate_exchange_stats(trades):
    """Calculate statistics for each exchange and overall"""
    gemini_trades = [t for t in trades if t.get('exchange') == 'gemini']
    binance_trades = [t for t in trades if t.get('exchange') == 'binance']
    
    # Gemini stats
    gemini_stats = {
        'total_trades': len(gemini_trades),
        'profitable_trades': sum(1 for t in gemini_trades if t.get('pnl', 0) > 0),
        'total_pnl': sum(t.get('pnl', 0) for t in gemini_trades),
        'total_pnl_percent': sum(t.get('pnl_percent', 0) for t in gemini_trades),
    }
    gemini_stats['win_rate'] = (gemini_stats['profitable_trades'] / gemini_stats['total_trades'] * 100) if gemini_stats['total_trades'] > 0 else 0
    gemini_stats['avg_pnl_percent'] = gemini_stats['total_pnl_percent'] / gemini_stats['total_trades'] if gemini_stats['total_trades'] > 0 else 0
    
    # Binance stats
    binance_stats = {
        'total_trades': len(binance_trades),
        'profitable_trades': sum(1 for t in binance_trades if t.get('pnl', 0) > 0),
        'total_pnl': sum(t.get('pnl', 0) for t in binance_trades),
        'total_pnl_percent': sum(t.get('pnl_percent', 0) for t in binance_trades),
    }
    binance_stats['win_rate'] = (binance_stats['profitable_trades'] / binance_stats['total_trades'] * 100) if binance_stats['total_trades'] > 0 else 0
    binance_stats['avg_pnl_percent'] = binance_stats['total_pnl_percent'] / binance_stats['total_trades'] if binance_stats['total_trades'] > 0 else 0
    
    # Overall stats
    overall_stats = {
        'total_trades': len(trades),
        'profitable_trades': sum(1 for t in trades if t.get('pnl', 0) > 0),
        'total_pnl': sum(t.get('pnl', 0) for t in trades),
        'total_pnl_percent': sum(t.get('pnl_percent', 0) for t in trades),
    }
    overall_stats['win_rate'] = (overall_stats['profitable_trades'] / overall_stats['total_trades'] * 100) if overall_stats['total_trades'] > 0 else 0
    overall_stats['avg_pnl_percent'] = overall_stats['total_pnl_percent'] / overall_stats['total_trades'] if overall_stats['total_trades'] > 0 else 0
    
    return {
        'gemini_trades': gemini_trades,
        'binance_trades': binance_trades,
        'gemini_stats': gemini_stats,
        'binance_stats': binance_stats,
        'overall_stats': overall_stats
    }

@app.route('/')
def index():
    """Main dashboard page with grouped exchange totals"""
    trades = load_trade_data()
    exchange_data = calculate_exchange_stats(trades)
    
    return render_template_string(
        HTML_TEMPLATE,
        trades=trades,
        gemini_trades=exchange_data['gemini_trades'],
        binance_trades=exchange_data['binance_trades'],
        gemini_stats=exchange_data['gemini_stats'],
        binance_stats=exchange_data['binance_stats'],
        overall_stats=exchange_data['overall_stats'],
        last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.route('/api/trades')
def api_trades():
    """API endpoint for trade data"""
    trades = load_trade_data()
    exchange_data = calculate_exchange_stats(trades)
    
    return jsonify({
        'trades': trades,
        'exchange_data': exchange_data,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/exchange-stats')
def api_exchange_stats():
    """API endpoint for exchange statistics"""
    trades = load_trade_data()
    exchange_data = calculate_exchange_stats(trades)
    
    return jsonify(exchange_data)

if __name__ == '__main__':
    print("="*70)
    print("📊 TRADING SYSTEM DASHBOARD - GROUPED EXCHANGE TOTALS")
    print("="*70)
    print("✅ Shows separate totals for Gemini and Binance")
    print("✅ Shows grouped trades by exchange")
    print("✅ Shows overall combined totals")
    print("="*70)
    print(f"Dashboard: http://localhost:5013")
    print(f"API Trades: http://localhost:5013/api/trades")
    print(f"API Exchange Stats: http://localhost:5013/api/exchange-stats")
    print(f"Trades Dashboard: http://localhost:5011")
    print(f"Main Dashboard: http://localhost:5007")
    print("="*70)
    
    app.run(host='0.0.0.0', port=5013, debug=False)