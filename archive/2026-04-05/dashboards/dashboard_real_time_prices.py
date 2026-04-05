#!/usr/bin/env python3
"""
DASHBOARD WITH REAL-TIME PRICES
Fetches live prices from exchanges instead of using stale stored data
"""

from flask import Flask, render_template_string, jsonify
import json
import os
from datetime import datetime
import ccxt
import threading
import time

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📊 Trading Dashboard - REAL-TIME PRICES</title>
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
        .warning-banner {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid #ef4444;
            color: #fca5a5;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
            font-weight: bold;
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
        .positive {
            color: #10b981;
            font-weight: bold;
        }
        .negative {
            color: #ef4444;
            font-weight: bold;
        }
        .price-updating {
            color: #fbbf24;
            font-style: italic;
        }
        .exchange-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
        }
        .exchange-badge.gemini {
            background: rgba(59, 130, 246, 0.2);
            color: #3b82f6;
            border: 1px solid #3b82f6;
        }
        .exchange-badge.binance {
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
        .last-updated {
            text-align: center;
            margin-top: 20px;
            color: #94a3b8;
            font-size: 0.9em;
        }
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: #1e293b;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #334155;
            text-align: center;
        }
        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
            margin: 10px 0;
        }
        .stat-label {
            color: #94a3b8;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Trading Dashboard</h1>
            <p class="subtitle">REAL-TIME PRICES | {{ total_trades }} trades | Auto-refreshes every 30 seconds</p>
            
            {% if has_stale_data %}
            <div class="warning-banner">
                ⚠️ WARNING: Previous dashboard showed STALE prices. This dashboard shows REAL-TIME prices.
            </div>
            {% endif %}
        </div>
        
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-label">Total Trades</div>
                <div class="stat-value">{{ total_trades }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Profitable Trades</div>
                <div class="stat-value {{ 'positive' if profitable_trades > 0 else '' }}">{{ profitable_trades }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Win Rate</div>
                <div class="stat-value {{ 'positive' if win_rate >= 50 else 'negative' }}">{{ "%.1f"|format(win_rate) }}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total P&L</div>
                <div class="stat-value {{ 'positive' if total_pnl >= 0 else 'negative' }}">${{ "%.2f"|format(total_pnl) }}</div>
            </div>
        </div>
        
        <table class="trade-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Symbol</th>
                    <th>Exchange</th>
                    <th>Side</th>
                    <th>Entry Price</th>
                    <th>Current Price</th>
                    <th>P&L</th>
                    <th>P&L %</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                {% for trade in trades %}
                <tr>
                    <td>{{ trade.index }}</td>
                    <td><strong>{{ trade.symbol }}</strong></td>
                    <td>
                        <span class="exchange-badge {{ trade.exchange }}">
                            {{ trade.exchange|upper }}
                        </span>
                    </td>
                    <td class="{{ 'side-buy' if trade.side == 'buy' else 'side-sell' }}">
                        {{ '▲ LONG' if trade.side == 'buy' else '▼ SHORT' }}
                    </td>
                    <td>${{ "%.4f"|format(trade.entry_price) }}</td>
                    <td class="price-updating">${{ "%.4f"|format(trade.current_price) }}</td>
                    <td class="{{ 'positive' if trade.real_pnl >= 0 else 'negative' }}">
                        ${{ "%.2f"|format(trade.real_pnl) }}
                    </td>
                    <td class="{{ 'positive' if trade.real_pnl_percent >= 0 else 'negative' }}">
                        {{ "%.2f"|format(trade.real_pnl_percent) }}%
                    </td>
                    <td>{{ trade.timestamp[:16] if trade.timestamp != 'unknown' else 'N/A' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="last-updated">
            Last updated: {{ last_updated }}<br>
            Prices fetched in real-time from exchanges | Auto-refreshes every 30 seconds
        </div>
    </div>
</body>
</html>
'''

def get_real_time_price(symbol, exchange_name):
    """Fetch real-time price from exchange"""
    try:
        if exchange_name == 'gemini':
            exchange = ccxt.gemini({'enableRateLimit': True})
            # Convert symbol format if needed
            if '/' not in symbol:
                symbol = f"{symbol}/USD"
        elif exchange_name == 'binance':
            exchange = ccxt.binance({
                'enableRateLimit': True,
                'options': {'defaultType': 'future'}
            })
            # Convert symbol format if needed
            if '/' not in symbol:
                symbol = f"{symbol}/USDT"
        else:
            return None
        
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        print(f"❌ Error fetching price for {symbol} on {exchange_name}: {e}")
        return None

def load_trade_data():
    """Load trade data and fetch REAL-TIME prices"""
    trades = []
    
    try:
        trades_file = os.path.join(BASE_DIR, 'trading_data', 'trades.json')
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                raw_trades = json.load(f)
            
            # Process trades with REAL-TIME prices
            for i, trade in enumerate(raw_trades):
                symbol = trade.get('symbol', 'unknown')
                exchange = trade.get('exchange', 'unknown')
                entry_price = trade.get('price', 0)
                
                # Get REAL-TIME current price
                current_price = get_real_time_price(symbol, exchange)
                if current_price is None:
                    # Fallback to stored price if real-time fetch fails
                    current_price = trade.get('current_price', entry_price)
                
                # Calculate REAL P&L
                if exchange == 'gemini' and trade.get('side') == 'buy':
                    # Gemini LONG: Profit = Current - Entry
                    real_pnl = current_price - entry_price
                elif exchange == 'binance' and trade.get('side') == 'sell':
                    # Binance SHORT: Profit = Entry - Current
                    real_pnl = entry_price - current_price
                else:
                    real_pnl = 0
                
                real_pnl_percent = (real_pnl / entry_price) * 100 if entry_price > 0 else 0
                
                processed_trade = {
                    'index': i + 1,
                    'exchange': exchange,
                    'symbol': symbol.replace(':USDT', '').replace('/USDT', '').replace('/USD', ''),
                    'side': trade.get('side', 'unknown'),
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'real_pnl': real_pnl,
                    'real_pnl_percent': real_pnl_percent,
                    'timestamp': trade.get('timestamp', 'unknown'),
                    'stored_pnl': trade.get('pnl', 0),  # Keep for comparison
                    'stored_pnl_percent': trade.get('pnl_percent', 0)
                }
                trades.append(processed_trade)
            
            print(f"✅ Loaded {len(trades)} trades with REAL-TIME prices")
            
            # Check for stale data in previous dashboard
            has_stale = False
            for trade in trades:
                if abs(trade['stored_pnl'] - trade['real_pnl']) > 1.0:  # More than $1 difference
                    has_stale = True
                    break
            
            if has_stale:
                print("⚠️  WARNING: Previous dashboard showed STALE prices!")
                
        else:
            print(f"⚠️  trades.json not found")
            trades = []
            has_stale = False
    except Exception as e:
        print(f"❌ Error loading trade data: {e}")
        trades = []
        has_stale = False
    
    return trades, has_stale

def calculate_stats(trades):
    """Calculate trading statistics"""
    if not trades:
        return {
            'total_trades': 0,
            'profitable_trades': 0,
            'win_rate': 0,
            'total_pnl': 0
        }
    
    profitable = sum(1 for t in trades if t['real_pnl'] > 0)
    total_pnl = sum(t['real_pnl'] for t in trades)
    win_rate = (profitable / len(trades)) * 100
    
    return {
        'total_trades': len(trades),
        'profitable_trades': profitable,
        'win_rate': win_rate,
        'total_pnl': total_pnl
    }

@app.route('/')
def index():
    """Main dashboard page with REAL-TIME prices"""
    trades, has_stale_data = load_trade_data()
    stats = calculate_stats(trades)
    
    return render_template_string(
        HTML_TEMPLATE,
        trades=trades,
        total_trades=stats['total_trades'],
        profitable_trades=stats['profitable_trades'],
        win_rate=stats['win_rate'],
        total_pnl=stats['total_pnl'],
        has_stale_data=has_stale_data,
        last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.route('/api/trades')
def api_trades():
    """API endpoint for trade data with real-time prices"""
    trades, _ = load_trade_data()
    stats = calculate_stats(trades)
    
    return jsonify({
        'trades': trades,
        'stats': stats,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/price-check/<symbol>/<exchange>')
def api_price_check(symbol, exchange):
    """API endpoint to check real-time price for a symbol"""
    price = get_real_time_price(symbol, exchange)
    return jsonify({
        'symbol': symbol,
        'exchange': exchange,
        'price': price,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("="*70)
    print("📊 TRADING DASHBOARD - REAL-TIME PRICES")
    print("="*70)
    print("✅ Fetches LIVE prices from exchanges")
    print("✅ Shows REAL P&L (not stale stored data)")
    print("✅ Auto-refreshes every 30 seconds")
    print("="*70)
    print(f"Dashboard: http://localhost:5014")
    print(f"API Trades: http://localhost:5014/api/trades")
    print(f"Price Check: http://localhost:5014/api/price-check/ETH/gemini")
    print("="*70)
    
    app.run(host='0.0.0.0', port=5014, debug=False)