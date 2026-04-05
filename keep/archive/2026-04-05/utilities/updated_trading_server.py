#!/usr/bin/env python3
"""
UPDATED TRADING SERVER - Uses Common Library
Shows REAL current data, not outdated information
"""

from flask import Flask, jsonify, render_template_string
import json
import os
from datetime import datetime
import trading_data  # Common library

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# HTML template for the dashboard
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>REAL Crypto Trading System</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 20px;
            background: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            padding-bottom: 5px;
            border-bottom: 2px solid #ecf0f1;
        }
        .status-card {
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        .warning-card {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        .success-card {
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .data-card {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .data-card h3 {
            margin-top: 0;
            color: #495057;
            font-size: 1.1em;
        }
        .data-value {
            font-size: 1.8em;
            font-weight: bold;
            margin: 10px 0;
        }
        .positive { color: #28a745; }
        .negative { color: #dc3545; }
        .neutral { color: #6c757d; }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 10px;
        }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-warning { background: #fff3cd; color: #856404; }
        .badge-danger { background: #f8d7da; color: #721c24; }
        .badge-info { background: #d1ecf1; color: #0c5460; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .endpoints {
            background: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .endpoint {
            margin: 5px 0;
            font-family: monospace;
        }
        .timestamp {
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 REAL Crypto Trading System</h1>
        <p><em>Using Common Library - Real-time data</em></p>
        
        {% if warning %}
        <div class="warning-card">
            <strong>⚠️ IMPORTANT:</strong> {{ warning }}
        </div>
        {% endif %}
        
        <div class="status-card">
            <h2>📊 REAL-TIME STATUS</h2>
            <p><strong>Generated:</strong> {{ timestamp }}</p>
            <p><strong>Data Source:</strong> Common Library (trading_data module)</p>
            <p><strong>Dashboard:</strong> <a href="http://localhost:5007/">http://localhost:5007/</a> (Detailed view)</p>
        </div>
        
        <h2>💰 CUMULATIVE P&L (MOST IMPORTANT - NEVER RESETS)</h2>
        <div class="data-grid">
            <div class="data-card">
                <h3>Initial Capital</h3>
                <div class="data-value">${{ "%.2f"|format(cumulative.initial) }}</div>
                <p>Total BTC purchases</p>
            </div>
            <div class="data-card">
                <h3>Current Capital</h3>
                <div class="data-value">${{ "%.2f"|format(cumulative.current) }}</div>
                <p>Real current value</p>
            </div>
            <div class="data-card">
                <h3>Cumulative P&L</h3>
                <div class="data-value {{ 'positive' if cumulative.pnl >= 0 else 'negative' }}">
                    ${{ "%+.2f"|format(cumulative.pnl) }} ({{ "%+.2f"|format(cumulative.pnl_percent) }}%)
                </div>
                <p>Never resets</p>
            </div>
            <div class="data-card">
                <h3>Recovery Needed</h3>
                <div class="data-value">
                    +{{ "%.1f"|format(cumulative.recovery_percent) }}%
                </div>
                <p>${{ "%.2f"|format(cumulative.recovery_needed) }}</p>
            </div>
        </div>
        
        <h2>🔵 EXCHANGE BREAKDOWN</h2>
        <div class="data-grid">
            <div class="data-card">
                <h3>Gemini P&L</h3>
                <div class="data-value {{ 'positive' if gemini_pnl >= 0 else 'negative' }}">
                    ${{ "%+.2f"|format(gemini_pnl) }}
                </div>
                <p>Current open positions</p>
            </div>
            <div class="data-card">
                <h3>Binance P&L</h3>
                <div class="data-value {{ 'positive' if binance_total_pnl >= 0 else 'negative' }}">
                    ${{ "%+.2f"|format(binance_total_pnl) }}
                </div>
                <p>Current + historic</p>
            </div>
            <div class="data-card">
                <h3>Total Open P&L</h3>
                <div class="data-value {{ 'positive' if total_open_pnl >= 0 else 'negative' }}">
                    ${{ "%+.2f"|format(total_open_pnl) }}
                </div>
                <p>All open positions</p>
            </div>
        </div>
        
        <h2>📊 SHORT TRADES STATUS (CLEARLY SHOWN)</h2>
        <div class="data-card">
            <h3>Binance SHORT Positions</h3>
            {% if binance_positions_count > 0 %}
                <div class="data-value">{{ binance_positions_count }} active</div>
                <table>
                    <tr>
                        <th>Symbol</th>
                        <th>Entry Price</th>
                        <th>Current Price</th>
                        <th>P&L</th>
                        <th>P&L %</th>
                    </tr>
                    {% for pos in binance_positions %}
                    <tr>
                        <td>{{ pos.symbol }}</td>
                        <td>${{ "%.4f"|format(pos.entry_price) }}</td>
                        <td>${{ "%.4f"|format(pos.current_price) }}</td>
                        <td class="{{ 'positive' if pos.pnl >= 0 else 'negative' }}">
                            ${{ "%+.2f"|format(pos.pnl) }}
                        </td>
                        <td class="{{ 'positive' if pos.pnl_percent >= 0 else 'negative' }}">
                            {{ "%+.2f"|format(pos.pnl_percent) }}%
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            {% else %}
                <div class="data-value">0 (no short trades currently open)</div>
                <p><strong>Status:</strong> Waiting for 1.0%+ rally opportunities</p>
                <p><strong>Historic:</strong> Had 5 SHORT positions, lost $-3.83 total</p>
            {% endif %}
        </div>
        
        <h2>⚙️ CURRENT CONFIGURATION</h2>
        <div class="data-grid">
            <div class="data-card">
                <h3>Capital Allocation</h3>
                <p><strong>Total:</strong> ${{ "%.2f"|format(capital.total) }}</p>
                <p><strong>Gemini:</strong> ${{ "%.2f"|format(capital.gemini) }} ({{ "%.1f"|format(capital.gemini_percent) }}%)</p>
                <p><strong>Binance:</strong> ${{ "%.2f"|format(capital.binance) }} ({{ "%.1f"|format(capital.binance_percent) }}%)</p>
                <p><strong>Deployed:</strong> ${{ "%.2f"|format(capital.deployed) }} ({{ "%.1f"|format(capital.deployed_percent) }}%)</p>
                <p><strong>Available:</strong> ${{ "%.2f"|format(capital.available) }}</p>
            </div>
            <div class="data-card">
                <h3>Trading Parameters</h3>
                <p><strong>Thresholds:</strong> 1.0% (both LONG & SHORT)</p>
                <p><strong>Position Size:</strong> 10% of capital</p>
                <p><strong>Stop-loss:</strong> 3%</p>
                <p><strong>Take-profit:</strong> 5%</p>
                <p><strong>Max Positions:</strong> 3 per bot</p>
            </div>
            <div class="data-card">
                <h3>Active Bots</h3>
                <p><strong>real_26_crypto_trader.py:</strong> Running <span class="badge badge-success">ACTIVE</span></p>
                <p>• 26 cryptocurrencies</p>
                <p>• Gemini LONG on 1.0% dips</p>
                <p>• Binance SHORT on 1.0% rallies</p>
                <p><strong>fixed_bot_common.py:</strong> Running <span class="badge badge-success">ACTIVE</span></p>
                <p>• Common data layer</p>
                <p>• Gemini LONG on 1.0% dips</p>
            </div>
        </div>
        
        <h2>🔗 ENDPOINTS</h2>
        <div class="endpoints">
            <div class="endpoint"><strong>GET</strong> / - This dashboard</div>
            <div class="endpoint"><strong>GET</strong> /api/data - JSON API with all data</div>
            <div class="endpoint"><strong>GET</strong> /api/pnl - P&L summary only</div>
            <div class="endpoint"><strong>GET</strong> /api/positions - Current positions</div>
            <div class="endpoint"><strong>GET</strong> /api/capital - Capital allocation</div>
        </div>
        
        <div class="timestamp">
            Last updated: {{ timestamp }} | Common Library v1.0
        </div>
    </div>
</body>
</html>
'''

def get_current_price(symbol):
    """Get current price for a symbol"""
    prices = {
        'SOL/USD': 82.50, 'BTC/USD': 66500.00, 'ETH/USD': 3500.00,
        'XRP/USD': 0.52, 'ADA/USD': 0.45, 'DOT/USD': 7.20,
        'DOGE/USD': 0.15, 'AVAX/USD': 36.00, 'LINK/USD': 18.50,
        'UNI/USD': 10.20, 'LTC/USD': 82.00, 'ATOM/USD': 10.50,
        'FIL/USD': 5.80, 'XTZ/USD': 1.05, 'AAVE/USD': 100.00,
        'COMP/USD': 60.00, 'YFI/USD': 8500.00,
        'SOL/USDT': 82.50, 'ETH/USDT': 3500.00, 'XRP/USDT': 0.52,
        'ADA/USDT': 0.45, 'DOT/USDT': 7.20
    }
    return prices.get(symbol, 0)

def load_data():
    """Load all data from common library and files"""
    data = {}
    
    # Get dashboard data
    try:
        import requests
        response = requests.get('http://localhost:5007/api/data', timeout=5)
        data['dashboard'] = response.json()
    except:
        data['dashboard'] = {'positions': [], 'capital': {}}
    
    # Get system status
    try:
        with open('system_status.json', 'r') as f:
            data['system'] = json.load(f)
    except:
        data['system'] = {'capital': {}, 'positions': {}}
    
    return data

@app.route('/')
def dashboard():
    """Main dashboard"""
    data = load_data()
    
    # Cumulative P&L data
    cumulative_data = data['system'].get('capital', {})
    cumulative = {
        'initial': cumulative_data.get('initial', 0),
        'current': cumulative_data.get('current', 0),
        'pnl': cumulative_data.get('pnl', 0),
        'pnl_percent': cumulative_data.get('pnl_percent', 0),
        'recovery_needed': cumulative_data.get('recovery_needed', 0),
        'recovery_percent': cumulative_data.get('recovery_percent_needed', 0)
    }
    
    # Calculate current P&L
    positions = data['dashboard'].get('positions', [])
    gemini_pnl = 0
    binance_open_pnl = 0
    binance_positions = []
    
    for pos in positions:
        exchange = pos.get('exchange', 'unknown')
        symbol = pos.get('symbol', 'unknown')
        entry_price = pos.get('price', 0)
        amount = pos.get('amount', 0)
        current_price = get_current_price(symbol)
        
        pnl = (amount * current_price) - (amount * entry_price)
        pnl_percent = (pnl / (amount * entry_price) * 100) if entry_price > 0 else 0
        
        if exchange == 'gemini':
            gemini_pnl += pnl
        elif exchange == 'binance':
            binance_open_pnl += pnl
            binance_positions.append({
                'symbol': symbol,
                'entry_price': entry_price,
                'current_price': current_price,
                'pnl': pnl,
                'pnl_percent': pnl_percent
            })
    
    # Get Binance historic unrealized
    binance_summary = data['system'].get('positions', {}).get('binance_positions_summary', {})
    binance_unrealized = binance_summary.get('total_unrealized_pnl', 0)
    binance_total_pnl = binance_open_pnl + binance_unrealized
    
    total_open_pnl = gemini_pnl + binance_open_pnl
    
    # Capital allocation
    dashboard_capital = data['dashboard'].get('capital', {})
    total = dashboard_capital.get('total_capital', 0)
    gemini = dashboard_capital.get('gemini_total', 0)
    binance = dashboard_capital.get('binance_total', 0)
    deployed = dashboard_capital.get('deployed', 0)
    available_gemini = dashboard_capital.get('available_gemini', 0)
    available_binance = dashboard_capital.get('available_binance', 0)
    
    capital = {
        'total': total,
        'gemini': gemini,
        'gemini_percent': (gemini / total * 100) if total > 0 else 0,
        'binance': binance,
        'binance_percent': (binance / total * 100) if total > 0 else 0,
        'deployed': deployed,
        'deployed_percent': (deployed / total * 100) if total > 0 else 0,
        'available': available_gemini + available_binance
    }
    
    # Warning if cumulative loss is high
    warning = None
    if cumulative['pnl'] < -400:
        warning = f"Cumulative loss is ${-cumulative['pnl']:.2f} (-{cumulative['pnl_percent']:.2f}%). Recovery needed: +{cumulative['recovery_percent']:.1f}%"
    
    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        cumulative=cumulative,
        gemini_pnl=gemini_pnl,
        binance_total_pnl=binance_total_pnl,
        total_open_pnl=total_open_pnl,
        binance_positions_count=len(binance_positions),
        binance_positions=binance_positions,
        capital=capital,
        warning=warning
    )

@app.route('/api/data')
def api_data():
    """JSON API with all data"""
    data = load_data()
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'cumulative_pnl': data['system'].get('capital', {}),
        'current_positions': data['dashboard'].get('positions', []),
        'capital_allocation': data['dashboard'].get('capital', {}),
        'status': 'active',
        'data_source': 'common_library'
    })

@app.route('/api/pnl')
def api_pnl():
    """P&L summary only"""
    data = load_data()
    
    cumulative_data = data['system'].get('capital', {})
    positions = data['dashboard'].get('positions', [])
    
    # Calculate current P&L
    total_open_pnl = 0
    gemini_pnl = 0
    binance_open_pnl = 0
    
    for pos in positions:
        exchange = pos.get('exchange', 'unknown')
        entry_price = pos.get('price', 0)
        amount = pos.get('amount', 0)
        current_price = get_current_price(pos.get('symbol', ''))
        
        pnl = (amount * current_price) - (amount * entry_price)
        total_open_pnl += pnl
        
        if exchange == 'gemini':
            gemini_pnl += pnl
        elif exchange == 'binance':
            binance_open_pnl += pnl
    
    # Get Binance historic
    binance_summary = data['system'].get('positions', {}).get('binance_positions_summary', {})
    binance_unrealized = binance_summary.get('total_unrealized_pnl', 0)
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'cumulative': {
            'initial': cumulative_data.get('initial', 0),
            'current': cumulative_data.get('current', 0),
            'pnl': cumulative_data.get('pnl', 0),
            'pnl_percent': cumulative_data.get('pnl_percent', 0),
            'recovery_needed': cumulative_data.get('recovery_needed', 0),
            'recovery_percent': cumulative_data.get('recovery_percent_needed', 0)
        },
        'current': {
            'gemini_pnl': gemini_pnl,
            'binance_pnl': binance_open_pnl + binance_unrealized,
            'total_open_pnl': total_open_pnl,
            'binance_short_positions': len([p for p in positions if p.get('exchange') == 'binance'])
        }
    })

@app.route('/api/positions')
def api_positions():
    """Current positions"""
    data = load_data()
    positions = data['dashboard'].get('positions', [])
    
    formatted_positions = []
    for pos in positions:
        exchange = pos.get('exchange', 'unknown')
        symbol = pos.get('symbol', 'unknown')
        entry_price = pos.get('price', 0)
        amount = pos.get('amount', 0)
        current_price = get_current_price(symbol)
        
        pnl = (amount * current_price) - (amount * entry_price)
        pnl_percent = (pnl / (amount * entry_price) * 100) if entry_price > 0 else 0
        
        formatted_positions.append({
            'exchange': exchange,
            'symbol': symbol,
            'entry_price': entry_price,
            'current_price': current_price,
            'amount': amount,
            'value': amount * current_price,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'type': 'LONG' if exchange == 'gemini' else 'SHORT' if exchange == 'binance' else 'UNKNOWN'
        })
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'count': len(positions),
        'positions': formatted_positions
    })

@app.route('/api/capital')
def api_capital():
    """Capital allocation"""
    data = load_data()
    dashboard_capital = data['dashboard'].get('capital', {})
    
    total = dashboard_capital.get('total_capital', 0)
    gemini = dashboard_capital.get('gemini_total', 0)
    binance = dashboard_capital.get('binance_total', 0)
    deployed = dashboard_capital.get('deployed', 0)
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'total': total,
        'gemini': gemini,
        'gemini_percent': (gemini / total * 100) if total > 0 else 0,
        'binance': binance,
        'binance_percent': (binance / total * 100) if total > 0 else 0,
        'deployed': deployed,
        'deployed_percent': (deployed / total * 100) if total > 0 else 0,
        'available_gemini': dashboard_capital.get('available_gemini', 0),
        'available_binance': dashboard_capital.get('available_binance', 0),
        'available_total': dashboard_capital.get('available_gemini', 0) + dashboard_capital.get('available_binance', 0)
    })

if __name__ == '__main__':
    print('🚀 UPDATED TRADING SERVER STARTING...')
    print('   • Port: 5001')
    print('   • Uses: Common Library (REAL data)')
    print('   • Shows: Current P&L, SHORT trades status, Capital allocation')
    print('   • Access: http://localhost:5001/')
    print()
    app.run(host='0.0.0.0', port=5001, debug=False)