#!/usr/bin/env python3
"""
EXCHANGE SIMPLE DASHBOARD
Shows EXACTLY what's on each exchange - no filtering, no heuristics
"""

from flask import Flask, render_template_string, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_TEMPLATE = '''
<!doctype html>
<html lang=en>
<head>
    <meta charset=utf-8>
    <title>💰 EXCHANGE SIMPLE DASHBOARD - Exact Holdings</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 20px; background: #0f172a; color: white; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; padding: 20px; background: #1e293b; border-radius: 10px; }
        h1 { color: #00ff9d; margin: 0; }
        .subtitle { color: #94a3b8; margin: 10px 0 20px 0; }
        .exchange-section { background: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 30px; border: 1px solid #334155; }
        .exchange-title { color: #cbd5e1; font-size: 1.3em; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #334155; }
        .gemini-title { border-bottom-color: #00d4aa; }
        .binance-title { border-bottom-color: #f0b90b; }
        .holdings-table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; margin-bottom: 20px; }
        .holdings-table th { background: #334155; padding: 12px 15px; text-align: left; font-weight: 600; color: #cbd5e1; border-bottom: 2px solid #475569; }
        .holdings-table td { padding: 10px 15px; border-bottom: 1px solid #334155; }
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
        .investment-card { background: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 15px; }
        .investment-value { font-size: 1.8em; font-weight: bold; color: #00ff9d; margin: 10px 0; }
        .gemini-value { color: #00d4aa; }
        .binance-value { color: #f0b90b; }
        .timestamp { color: #7f8c8d; font-size: 0.9em; text-align: right; }
        .no-holdings { text-align: center; padding: 40px; color: #94a3b8; }
        .exchange-total { background: #2d3748; padding: 15px; border-radius: 8px; margin-top: 20px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 EXCHANGE SIMPLE DASHBOARD</h1>
            <p class="subtitle">EXACT holdings on each exchange - No filtering, No heuristics</p>
            <div class="timestamp">Last updated: {{ timestamp }}</div>
        </div>
        
        <!-- GEMINI EXCHANGE -->
        <div class="exchange-section">
            <h2 class="exchange-title gemini-title">🟢 GEMINI EXCHANGE</h2>
            <p style="color: #94a3b8; margin-bottom: 15px;">Exact holdings on Gemini - Matches exchange data</p>
            
            {% if gemini_holdings %}
            <table class="holdings-table">
                <thead>
                    <tr>
                        <th>Coin</th>
                        <th>Amount</th>
                        <th>Entry Price</th>
                        <th>Current Price</th>
                        <th>Investment</th>
                        <th>Current Value</th>
                        <th>P&L</th>
                        <th>P&L %</th>
                    </tr>
                </thead>
                <tbody>
                    {% for holding in gemini_holdings %}
                    <tr>
                        <td><strong>{{ holding.symbol }}</strong></td>
                        <td>{{ "%.8f"|format(holding.amount) }}</td>
                        <td>${{ "%.2f"|format(holding.entry_price) }}</td>
                        <td>${{ "%.2f"|format(holding.current_price) }}</td>
                        <td>${{ "%.2f"|format(holding.investment) }}</td>
                        <td>${{ "%.2f"|format(holding.current_value) }}</td>
                        <td class="{{ 'positive' if holding.pnl >= 0 else 'negative' }}">
                            ${{ "%.2f"|format(holding.pnl) }}
                        </td>
                        <td class="{{ 'positive' if holding.pnl_percent >= 0 else 'negative' }}">
                            {{ "%.1f"|format(holding.pnl_percent) }}%
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <div class="exchange-total">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <h3>Gemini Investment</h3>
                        <div class="investment-value gemini-value">${{ "%.2f"|format(gemini_investment) }}</div>
                    </div>
                    <div>
                        <h3>Gemini Current Value</h3>
                        <div class="investment-value gemini-value {{ 'positive' if gemini_pnl >= 0 else 'negative' }}">
                            ${{ "%.2f"|format(gemini_current_value) }}
                        </div>
                    </div>
                </div>
                <div style="margin-top: 15px; text-align: center;">
                    <h3>Gemini Net P&L</h3>
                    <div class="investment-value {{ 'positive' if gemini_pnl >= 0 else 'negative' }}">
                        ${{ "%+.2f"|format(gemini_pnl) }} ({{ "%+.1f"|format(gemini_pnl_percent) }}%)
                    </div>
                </div>
            </div>
            {% else %}
            <div class="no-holdings">
                <h3>No holdings on Gemini</h3>
                <p>No cryptocurrency holdings found on Gemini exchange</p>
            </div>
            {% endif %}
        </div>
        
        <!-- BINANCE EXCHANGE -->
        <div class="exchange-section">
            <h2 class="exchange-title binance-title">🟡 BINANCE EXCHANGE</h2>
            <p style="color: #94a3b8; margin-bottom: 15px;">Exact holdings on Binance - Matches exchange data</p>
            
            {% if binance_holdings %}
            <table class="holdings-table">
                <thead>
                    <tr>
                        <th>Coin</th>
                        <th>Amount</th>
                        <th>Entry Price</th>
                        <th>Current Price</th>
                        <th>Investment</th>
                        <th>Current Value</th>
                        <th>P&L</th>
                        <th>P&L %</th>
                    </tr>
                </thead>
                <tbody>
                    {% for holding in binance_holdings %}
                    <tr>
                        <td><strong>{{ holding.symbol }}</strong></td>
                        <td>{{ "%.8f"|format(holding.amount) }}</td>
                        <td>${{ "%.2f"|format(holding.entry_price) }}</td>
                        <td>${{ "%.2f"|format(holding.current_price) }}</td>
                        <td>${{ "%.2f"|format(holding.investment) }}</td>
                        <td>${{ "%.2f"|format(holding.current_value) }}</td>
                        <td class="{{ 'positive' if holding.pnl >= 0 else 'negative' }}">
                            ${{ "%.2f"|format(holding.pnl) }}
                        </td>
                        <td class="{{ 'positive' if holding.pnl_percent >= 0 else 'negative' }}">
                            {{ "%.1f"|format(holding.pnl_percent) }}%
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <div class="exchange-total">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <h3>Binance Investment</h3>
                        <div class="investment-value binance-value">${{ "%.2f"|format(binance_investment) }}</div>
                    </div>
                    <div>
                        <h3>Binance Current Value</h3>
                        <div class="investment-value binance-value {{ 'positive' if binance_pnl >= 0 else 'negative' }}">
                            ${{ "%.2f"|format(binance_current_value) }}
                        </div>
                    </div>
                </div>
                <div style="margin-top: 15px; text-align: center;">
                    <h3>Binance Net P&L</h3>
                    <div class="investment-value {{ 'positive' if binance_pnl >= 0 else 'negative' }}">
                        ${{ "%+.2f"|format(binance_pnl) }} ({{ "%+.1f"|format(binance_pnl_percent) }}%)
                    </div>
                </div>
            </div>
            {% else %}
            <div class="no-holdings">
                <h3>No holdings on Binance</h3>
                <p>No cryptocurrency holdings found on Binance exchange</p>
            </div>
            {% endif %}
        </div>
        
        <!-- OVERALL TOTALS -->
        <div class="exchange-section" style="background: #2d3748;">
            <h2 class="exchange-title" style="border-bottom-color: #00ff9d;">📊 OVERALL TOTALS</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; text-align: center;">
                <div>
                    <h3>Total Investment</h3>
                    <div class="investment-value">${{ "%.2f"|format(total_investment) }}</div>
                    <p>Gemini: ${{ "%.2f"|format(gemini_investment) }} | Binance: ${{ "%.2f"|format(binance_investment) }}</p>
                </div>
                <div>
                    <h3>Total Current Value</h3>
                    <div class="investment-value {{ 'positive' if total_pnl >= 0 else 'negative' }}">
                        ${{ "%.2f"|format(total_current_value) }}
                    </div>
                    <p>Gemini: ${{ "%.2f"|format(gemini_current_value) }} | Binance: ${{ "%.2f"|format(binance_current_value) }}</p>
                </div>
                <div>
                    <h3>Total Net P&L</h3>
                    <div class="investment-value {{ 'positive' if total_pnl >= 0 else 'negative' }}">
                        ${{ "%+.2f"|format(total_pnl) }} ({{ "%+.1f"|format(total_pnl_percent) }}%)
                    </div>
                    <p>Gemini: {{ "%+.1f"|format(gemini_pnl_percent) }}% | Binance: {{ "%+.1f"|format(binance_pnl_percent) }}%</p>
                </div>
            </div>
        </div>
        
        <div class="timestamp" style="margin-top: 30px;">
            Simple rule: Always matches exchange holdings exactly | Auto-refreshes every 30 seconds
        </div>
    </div>
</body>
</html>
'''

def load_exchange_holdings(exchange_name):
    """Load holdings for a specific exchange - NO FILTERING, exact matches"""
    holdings = []
    
    try:
        with open('trading_data/trades.json', 'r') as f:
            trades = json.load(f)
        
        # Get ALL spot trades for this exchange
        exchange_trades = []
        for trade in trades:
            if trade.get('type') != 'spot':
                continue  # Skip non-spot trades
            
            trade_exchange = trade.get('exchange', '').lower()
            if trade_exchange == exchange_name.lower():
                exchange_trades.append(trade)
        
        print(f"📊 {exchange_name.upper()}: Found {len(exchange_trades)} spot trades")
        
        # Group by symbol
        holdings_by_symbol = {}
        for trade in exchange_trades:
            symbol = trade.get('symbol', '').replace('/USD', '').replace('/USDT', '')
            
            if symbol not in holdings_by_symbol:
                holdings_by_symbol[symbol] = {
                    'symbol': symbol,
                    'amount': 0,
                    'entry_price': 0,
                    'investment': 0,
                    'current_price': trade.get('current_price', trade.get('price', 0)),
                    'current_value': 0,
                    'pnl': 0,
                    'pnl_percent': 0
                }
            
            # Add to existing holding
            amount = trade.get('amount', 0)
            price = trade.get('price', 0)
            investment = amount * price
            
            holdings_by_symbol[symbol]['amount'] += amount
            holdings_by_symbol[symbol]['investment'] += investment
        
        # Calculate values
        for symbol, holding in holdings_by_symbol.items():
            if holding['amount'] > 0:
                holding['entry_price'] = holding['investment'] / holding['amount'] if holding['amount'] > 0 else 0
                holding['current_value'] = holding['amount'] * holding['current_price']
                holding['pnl'] = holding['current_value'] - holding['investment']
                holding['pnl_percent'] = (holding['pnl'] / holding['investment'] * 100) if holding['investment'] > 0 else 0
                
                holdings.append(holding)
        
        # Sort by investment amount (largest first)
        holdings.sort(key=lambda x: x['investment'], reverse=True)
        
        print(f"✅ {exchange_name.upper()}: {len(holdings)} holdings")
        for holding in holdings:
            print(f"   • {holding['symbol']}: ${holding['investment']:.2f} ({holding['amount']:.8f} coins)")
        
    except Exception as e:
        print(f"❌ Error loading {exchange_name} holdings: {e}")
    
    return holdings

@app.route('/')
def index():
    """Main dashboard - Separate tables for each exchange"""
    # Load holdings for each exchange
    gemini_holdings = load_exchange_holdings('gemini')
    binance_holdings = load_exchange_holdings('binance')
    
    # Calculate Gemini totals
    gemini_investment = sum(h['investment'] for h in gemini_holdings)
    gemini_current_value = sum(h['current_value'] for h in gemini_holdings)
    gemini_pnl = gemini_current_value - gemini_investment
    gemini_pnl_percent = (gemini_pnl / gemini_investment * 100) if gemini_investment > 0 else 0
    
    # Calculate Binance totals
    binance_investment = sum(h['investment'] for h in binance_holdings)
    binance_current_value = sum(h['current_value'] for h in binance_holdings)
    binance_pnl = binance_current_value - binance_investment
    binance_pnl_percent = (binance_pnl / binance_investment * 100) if binance_investment > 0 else 0
    
    # Calculate overall totals
    total_investment = gemini_investment + binance_investment
    total_current_value = gemini_current_value + binance_current_value
    total_pnl = total_current_value - total_investment
    total_pnl_percent = (total_pnl / total_investment * 100) if total_investment > 0 else 0
    
    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        gemini_holdings=gemini_holdings,
        binance_holdings=binance_holdings,
        gemini_investment=gemini_investment,
        gemini_current_value=gemini_current_value,
        gemini_pnl=gemini_pnl,
        gemini_pnl_percent=gemini_pnl_percent,
        binance_investment=binance_investment,
        binance_current_value=binance_current_value,
        binance_pnl=binance_pnl,
        binance_pnl_percent=binance_pnl_percent,
        total_investment=total_investment,
        total_current_value=total_current_value,
        total_pnl=total_pnl,
        total_pnl_percent=total_pnl_percent
    )

@app.route('/api/gemini')
def api_gemini():
    """API endpoint for Gemini holdings"""
    holdings = load_exchange_holdings('gemini')
    
    # Calculate totals
    investment = sum(h['investment'] for h in holdings)
    current_value = sum(h['current_value'] for h in holdings)
    pnl = current_value - investment
    pnl_percent = (pnl / investment * 100) if investment > 0 else 0
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'exchange': 'gemini',
        'holdings': holdings,
        'summary': {
            'total_holdings': len(holdings),
            'total_investment': investment,
            'total_current_value': current_value,
            'total_pnl': pnl,
            'total_pnl_percent': pnl_percent
        }
    })

@app.route('/api/binance')
def api_binance():
    """API endpoint for Binance holdings"""
    holdings = load_exchange_holdings('binance')
    
    # Calculate totals
    investment = sum(h['investment'] for h in holdings)
    current_value = sum(h['current_value'] for h in holdings)
    pnl = current_value - investment
    pnl_percent = (pnl / investment * 100) if investment > 0 else 0
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'exchange': 'binance',
        'holdings': holdings,
        'summary': {
            'total_holdings': len(holdings),
            'total_investment': investment,
            'total_current_value': current_value,
            'total_pnl': pnl,
            'total_pnl_percent': pnl_percent
        }
    })

@app.route('/api/all')
def api_all():
    """API endpoint for all holdings"""
    gemini_holdings = load_exchange_holdings('gemini')
    binance_holdings = load_exchange_holdings('binance')
    
    # Calculate totals
    gemini_investment = sum(h['investment'] for h in gemini_holdings)
    gemini_current_value = sum(h['current_value'] for h in gemini_holdings)
    gemini_pnl = gemini_current_value - gemini_investment
    
    binance_investment = sum(h['investment'] for h in binance_holdings)
    binance_current_value = sum(h['current_value'] for h in binance_holdings)
    binance_pnl = binance_current_value - binance_investment
    
    total_investment = gemini_investment + binance_investment
    total_current_value = gemini_current_value + binance_current_value
    total_pnl = total_current_value - total_investment
    total_pnl_percent = (total_pnl / total_investment * 100) if total_investment > 0 else 0
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'exchanges': {
            'gemini': {
                'holdings': gemini_holdings,
                'investment': gemini_investment,
                'current_value': gemini_current_value,
                'pnl': gemini_pnl
            },
            'binance': {
                'holdings': binance_holdings,
                'investment': binance_investment,
                'current_value': binance_current_value,
                'pnl': binance_pnl
            }
        },
        'summary': {
            'total_investment': total_investment,
            'total_current_value': total_current_value,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent
        }
    })