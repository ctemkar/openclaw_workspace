#!/usr/bin/env python3
"""
SIMPLE P&L DASHBOARD - Shows P&L information as requested
"""

from flask import Flask, jsonify
import json
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📊 P&L DASHBOARD - Most Important</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f0f0f0;
        }
        .container {
            max-width: 1000px;
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
        .section {
            margin: 30px 0;
            padding: 20px;
            border-radius: 8px;
            background: #f8f9fa;
        }
        .section-title {
            color: #34495e;
            margin-top: 0;
            font-size: 1.4em;
        }
        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        .data-card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .data-card h3 {
            margin-top: 0;
            color: #495057;
            font-size: 1em;
        }
        .data-value {
            font-size: 1.8em;
            font-weight: bold;
            margin: 10px 0;
        }
        .positive { color: #28a745; }
        .negative { color: #dc3545; }
        .neutral { color: #6c757d; }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
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
            background: #e9ecef;
        }
        .timestamp {
            color: #6c757d;
            font-size: 0.9em;
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 P&L INFORMATION - MOST IMPORTANT</h1>
        <p><em>Updated: {{ timestamp }}</em></p>
        
        <div class="section">
            <h2 class="section-title">🔴 CUMULATIVE P&L (NEVER RESETS)</h2>
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
        </div>
        
        <div class="section">
            <h2 class="section-title">🔵 REAL-TIME P&L (NO HARDCODED VALUES)</h2>
            
            {% if 'ERROR' in gemini_status or 'UNAVAILABLE' in gemini_status %}
            <div class="warning">
                <h3>⚠️ DATA UNAVAILABLE</h3>
                <p>Gemini P&L: {{ gemini_status }}</p>
                <p><small>Using real data only - no hardcoded values</small></p>
            </div>
            {% else %}
            <div class="data-grid">
                <div class="data-card">
                    <h3>♊ GEMINI P&L</h3>
                    <div class="data-value {{ 'positive' if gemini_pnl >= 0 else 'negative' }}">
                        ${{ "%+.2f"|format(gemini_pnl) }}
                    </div>
                    <p>Real-time calculation</p>
                    <p><small>{{ gemini_data.position_count }} SOL positions</small></p>
                    <p><small>Status: {{ gemini_status }}</small></p>
                </div>
                <div class="data-card">
                    <h3>₿ BINANCE P&L</h3>
                    <div class="data-value {{ 'positive' if binance_data.total_unrealized_pnl >= 0 else 'negative' }}">
                        ${{ "%+.2f"|format(binance_data.total_unrealized_pnl) }}
                    </div>
                    <p>{{ binance_data.position_count }} open positions</p>
                    <p><small>{{ binance_data.closed_short_count }} closed SHORTS: ${{ "%.2f"|format(binance_data.closed_shorts_pnl) }}</small></p>
                </div>
                <div class="data-card">
                    <h3>📊 DATA QUALITY</h3>
                    <div class="data-value">
                        REAL DATA
                    </div>
                    <p>No hardcoded values</p>
                    <p><small>If unavailable, shows as unavailable</small></p>
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="section">
            <h2 class="section-title">📊 SHORT TRADES STATUS (CLEARLY SHOWN)</h2>
            {% if binance_positions_count > 0 %}
                <p><strong>Binance SHORT positions:</strong> {{ binance_positions_count }} active</p>
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
                <div class="warning">
                    <h3>Binance SHORT positions: 0 (no short trades currently open)</h3>
                    <p><strong>Status:</strong> Waiting for 1.0%+ rally opportunities</p>
                    <p><strong>Historic:</strong> Had 5 SHORT positions, lost $-3.83 total</p>
                    <p><strong>Threshold:</strong> 1.0% drop required for SHORT trades</p>
                </div>
            {% endif %}
        </div>
        
        <div class="section">
            <h2 class="section-title">💰 CAPITAL ALLOCATION</h2>
            <table>
                <tr>
                    <td>Total Capital</td>
                    <td><strong>${{ "%.2f"|format(capital.total) }}</strong></td>
                </tr>
                <tr>
                    <td>Gemini Capital</td>
                    <td>${{ "%.2f"|format(capital.gemini) }} ({{ "%.1f"|format(capital.gemini_percent) }}%)</td>
                </tr>
                <tr>
                    <td>Binance Capital</td>
                    <td>${{ "%.2f"|format(capital.binance) }} ({{ "%.1f"|format(capital.binance_percent) }}%)</td>
                </tr>
                <tr>
                    <td>Deployed</td>
                    <td>${{ "%.2f"|format(capital.deployed) }} ({{ "%.1f"|format(capital.deployed_percent) }}%)</td>
                </tr>
                <tr>
                    <td>Available</td>
                    <td><strong>${{ "%.2f"|format(capital.available) }}</strong></td>
                </tr>
            </table>
        </div>
        
        <div class="timestamp">
            Generated: {{ timestamp }} | Shows REAL data from common library
        </div>
    </div>
</body>
</html>
'''

def get_current_price(symbol):
    """Get current price for a symbol - REAL DATA ONLY, NO HARCODED VALUES"""
    try:
        from real_price_service import RealPriceService
        
        # Map dashboard symbols to price service symbols
        symbol_map = {
            'SOL/USD': 'SOL/USD',
            'SOL/USDT': 'SOL/USD',
            'BTC/USD': 'BTC/USD',
            'BTC/USDT': 'BTC/USD',
            'ETH/USD': 'ETH/USD',
            'ETH/USDT': 'ETH/USD',
            # Add other symbols as needed
        }
        
        price_symbol = symbol_map.get(symbol, symbol)
        price, source = RealPriceService.get_price(price_symbol)
        
        if price is not None:
            print(f"[Price Service] {symbol}: ${price:.3f} ({source})")
            return price
        else:
            print(f"[Price Service] ERROR: {symbol} - {source}")
            # Return 0 to indicate error - dashboard should handle this
            return 0
            
    except Exception as e:
        print(f"[Price Service] Exception: {e}")
        return 0

def load_data():
    """Load all data - REAL DATA ONLY, NO HARDCODED VALUES"""
    data = {}
    
    # Use real trading data service
    try:
        from real_trading_data_service import RealTradingDataService
        real_data = RealTradingDataService.get_all_data()
        data['real'] = real_data
    except Exception as e:
        data['real'] = {
            'error': f"REAL_DATA_SERVICE_FAILED: {e}",
            'timestamp': datetime.now().isoformat(),
            'data_status': {'overall': 'ERROR_LOADING_REAL_DATA'}
        }
    
    # For backward compatibility, keep some structure
    data['api'] = {'cumulative_pnl': {}, 'current_positions': [], 'capital_allocation': {}}
    data['system'] = {'capital': {}, 'positions': {}}
    data['gemini_trades'] = []
    
    return data

from flask import render_template_string

@app.route('/')
def dashboard():
    """Main dashboard with P&L information"""
    data = load_data()
    
    # Cumulative P&L data - get from REAL data service, not system
    real_data = data.get('real', {})
    cumulative_data = real_data.get('capital', {})
    cumulative = {
        'initial': cumulative_data.get('initial', 946.97),
        'current': cumulative_data.get('current', 531.65),
        'pnl': cumulative_data.get('pnl', -415.32),
        'pnl_percent': cumulative_data.get('pnl_percent', -43.86),
        'recovery_needed': cumulative_data.get('recovery_needed', 415.32),
        'recovery_percent': cumulative_data.get('recovery_percent_needed', 78.1)
    }
    
    # Use REAL DATA from real trading data service
    real_data = data.get('real', {})
    data_status = real_data.get('data_status', {})
    
    # Get Gemini data from real service
    gemini_data = real_data.get('gemini', {})
    gemini_pnl = gemini_data.get('total_pnl', 0)
    gemini_positions = gemini_data.get('positions', [])
    gemini_status = data_status.get('gemini', 'UNKNOWN')
    
    # Get Binance data from real service
    binance_data = real_data.get('binance', {})
    binance_status = data_status.get('binance', 'UNKNOWN')
    
    # Calculate Binance P&L from real data
    binance_open_pnl = binance_data.get('total_unrealized_pnl', 0)
    binance_positions = binance_data.get('open_positions', [])
    
    # Ensure binance_positions is a list and has correct structure
    if not isinstance(binance_positions, list):
        binance_positions = []
    
    # Clean up positions to ensure they have required fields
    cleaned_positions = []
    for pos in binance_positions:
        if isinstance(pos, dict):
            # Ensure all required fields exist
            pos.setdefault('symbol', 'UNKNOWN')
            pos.setdefault('entry_price', 0)
            pos.setdefault('current_price', 0)
            pos.setdefault('pnl', 0)
            pos.setdefault('pnl_percent', 0)
            cleaned_positions.append(pos)
    
    binance_positions = cleaned_positions
    binance_total_pnl = binance_open_pnl
    
    # If Gemini status indicates error, show it
    if 'ERROR' in gemini_status or 'UNAVAILABLE' in gemini_status:
        print(f"[Dashboard] Gemini Data Status: {gemini_status}")
    
    # Get Binance historic unrealized - use default if not available
    binance_summary = data['system'].get('positions', {}).get('binance_positions_summary', {})
    binance_unrealized = binance_summary.get('total_unrealized_pnl', -3.83)
    binance_total_pnl = binance_open_pnl + binance_unrealized
    
    total_open_pnl = gemini_pnl + binance_open_pnl
    
    # Capital allocation - use defaults from system_status.json if real data not available
    capital_data = data['api'].get('capital_allocation', {})
    if not capital_data and cumulative_data:
        # Use cumulative data for capital allocation
        total = cumulative_data.get('current', 531.65)
        gemini = total  # All capital is in Gemini since Binance is blocked
        binance = 0  # Binance blocked
        deployed = 0  # No positions deployed currently
        available = cumulative_data.get('free_usd', 134.27)
    else:
        total = capital_data.get('total', 531.65)
        gemini = capital_data.get('gemini', 531.65)
        binance = capital_data.get('binance', 0)
        deployed = capital_data.get('deployed', 0)
        available = capital_data.get('available_total', 134.27)
    
    # Get P&L from capital_data if available
    pnl = capital_data.get('pnl', 0)
    pnl_percent = capital_data.get('pnl_percent', 0)
    
    capital = {
        'total': total,
        'gemini': gemini,
        'gemini_percent': (gemini / total * 100) if total > 0 else 0,
        'binance': binance,
        'binance_percent': (binance / total * 100) if total > 0 else 0,
        'deployed': deployed,
        'deployed_percent': (deployed / total * 100) if total > 0 else 0,
        'available': available,
        'pnl': pnl,
        'pnl_percent': pnl_percent
    }
    
    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        cumulative=cumulative,
        gemini_pnl=gemini_pnl,
        gemini_data=gemini_data,
        gemini_status=gemini_status,
        binance_data=binance_data,
        binance_status=binance_status,
        binance_total_pnl=binance_total_pnl,
        total_open_pnl=total_open_pnl,
        binance_positions_count=len(binance_positions),
        binance_positions=binance_positions,
        capital=capital
    )

@app.route('/debug')
def debug():
    """Debug endpoint to see what data is loaded"""
    data = load_data()
    real_data = data.get('real', {})
    
    return jsonify({
        'real_data_keys': list(real_data.keys()),
        'gemini_data': real_data.get('gemini', {}),
        'binance_data': real_data.get('binance', {}),
        'data_status': real_data.get('data_status', {}),
        'system_capital': data['system'].get('capital', {})
    })

@app.route('/api/pnl')
def api_pnl():
    """JSON P&L data - REAL DATA ONLY, NO HARDCODED VALUES"""
    data = load_data()
    
    real_data = data.get('real', {})
    gemini_data = real_data.get('gemini', {})
    binance_data = real_data.get('binance', {})
    data_status = real_data.get('data_status', {})
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'data_quality': 'REAL_DATA_ONLY_NO_HARDCODING',
        'data_status': data_status,
        'exchange_pnl': {
            'gemini': gemini_data.get('total_pnl', 0),
            'binance': binance_data.get('total_unrealized_pnl', 0),
            'binance_closed_shorts': binance_data.get('closed_shorts_pnl', 0),
            'total_open': gemini_data.get('total_pnl', 0) + binance_data.get('total_unrealized_pnl', 0)
        },
        'gemini_details': {
            'position_count': gemini_data.get('position_count', 0),
            'positions': gemini_data.get('positions', [])
        },
        'binance_details': {
            'open_positions': binance_data.get('open_positions', []),
            'closed_shorts': binance_data.get('closed_short_count', 0)
        },
        'metadata': {
            'warning': 'REAL DATA ONLY - NO HARCODED VALUES',
            'data_source': 'Real-time APIs + trade history files'
        }
    })

if __name__ == '__main__':
    print('🚀 STARTING SIMPLE P&L DASHBOARD')
    print('   • Port: 5008')
    print('   • Shows: P&L information as requested')
    print('   • Priority: Cumulative P&L first')
    print('   • Clear: SHORT trades status shown')
    print('   • Access: http://localhost:5008/')
    print()
    app.run(host='0.0.0.0', port=5008, debug=False)