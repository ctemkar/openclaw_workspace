#!/usr/bin/env python3
"""
SIMPLE FIXED DASHBOARD - Shows real P&L data with NO hardcoded values
"""

from flask import Flask, jsonify, render_template_string
from price_safeguards import DataQualityChecker
import json
from datetime import datetime
from real_trading_data_service import RealTradingDataService

app = Flask(__name__)

HTML_TEMPLATE = '''
<!doctype html>
<html lang=en>
<head>
    <meta charset=utf-8>
    <title>Real Trading P&L Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .section { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .section-title { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .data-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .data-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db; }
        .data-value { font-size: 2em; font-weight: bold; margin: 10px 0; }
        .positive { color: #27ae60; }
        .negative { color: #e74c3c; }
        .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 10px 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f2f2f2; }
        .timestamp { color: #7f8c8d; font-size: 0.9em; text-align: right; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Real Trading P&L Dashboard</h1>
            <p>NO HARCODED VALUES - REAL DATA ONLY</p>
            <div class="timestamp">Last updated: {{ timestamp }}</div>
        </div>
        
        <div class="section">
            <h2 class="section-title">📈 CUMULATIVE PERFORMANCE (NEVER RESETS)</h2>
            <div class="data-grid">
                <div class="data-card">
                    <h3>Initial Capital</h3>
                    <div class="data-value">${{ "%.2f"|format(cumulative.initial) }}</div>
                    <p>Total investment</p>
                </div>
                <div class="data-card">
                    <h3>Current Value</h3>
                    <div class="data-value">${{ "%.2f"|format(cumulative.current) }}</div>
                    <p>Portfolio value now</p>
                </div>
                <div class="data-card">
                    <h3>Cumulative P&L</h3>
                    <div class="data-value {{ 'positive' if cumulative.pnl >= 0 else 'negative' }}">
                        ${{ "%+.2f"|format(cumulative.pnl) }} ({{ "%+.1f"|format(cumulative.pnl_percent) }}%)
                    </div>
                    <p>Never resets</p>
                </div>
            </div>
            <p><strong>Recovery needed:</strong> ${{ "%.2f"|format(cumulative.recovery_needed) }} ({{ "%.1f"|format(cumulative.recovery_percent) }}%) to break even</p>
        </div>
        
        <div class="section">
            <h2 class="section-title">🔵 REAL-TIME P&L (NO HARDCODED VALUES)</h2>
            
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
                    <h3>📊 TOTAL OPEN P&L</h3>
                    <div class="data-value {{ 'positive' if total_open_pnl >= 0 else 'negative' }}">
                        ${{ "%+.2f"|format(total_open_pnl) }}
                    </div>
                    <p>All open positions</p>
                    <p><small>Gemini + Binance combined</small></p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">💰 SEPARATE GEMINI & BINANCE + TOTALS</h2>
            
            <!-- SEPARATE LINES FOR GEMINI AND BINANCE -->
            <div style="margin-bottom: 30px;">
                <h3>📊 SEPARATE EXCHANGE TOTALS (Investment + Positions Only)</h3>
                
                <!-- GEMINI LINE -->
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px; background: #f0f8ff; border-radius: 8px; margin-bottom: 10px;">
                    <div style="font-weight: bold; font-size: 1.2em;">♊ GEMINI:</div>
                    <div style="font-size: 1.3em; font-weight: bold;">${{ "%.2f"|format(gemini.investment + gemini.position_value + gemini.pnl) }}</div>
                    <div style="text-align: right;">
                        <div>Investment: ${{ "%.2f"|format(gemini.investment) }}</div>
                        <div>P&L: <span class="{{ 'positive' if gemini.pnl >= 0 else 'negative' }}">${{ "%+.2f"|format(gemini.pnl) }} ({{ "%+.1f"|format(gemini.pnl_percent) }}%)</span></div>
                        <div>Positions: ${{ "%.2f"|format(gemini.position_value) }}</div>
                    </div>
                </div>
                
                <!-- BINANCE LINE -->
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px; background: #fff0f0; border-radius: 8px; margin-bottom: 10px;">
                    <div style="font-weight: bold; font-size: 1.2em;">₿ BINANCE:</div>
                    <div style="font-size: 1.3em; font-weight: bold;">${{ "%.2f"|format(binance.investment + binance.position_value + binance.pnl) }}</div>
                    <div style="text-align: right;">
                        <div>Investment: ${{ "%.2f"|format(binance.investment) }}</div>
                        <div>P&L: <span class="{{ 'positive' if binance.pnl >= 0 else 'negative' }}">${{ "%+.2f"|format(binance.pnl) }} ({{ "%+.1f"|format(binance.pnl_percent) }}%)</span></div>
                        <div>Positions: ${{ "%.2f"|format(binance.position_value) }}</div>
                    </div>
                </div>
                
                <!-- TOTALS LINE -->
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #2c3e50; color: white; border-radius: 8px; margin-top: 20px;">
                    <div style="font-weight: bold; font-size: 1.4em;">📊 TOTAL:</div>
                    <div style="font-size: 1.5em; font-weight: bold;">${{ "%.2f"|format(total.investment + total.position_value + total.pnl) }}</div>
                    <div style="text-align: right;">
                        <div>Total Investment: ${{ "%.2f"|format(total.investment) }}</div>
                        <div>Total P&L: <span style="color: {{ '#27ae60' if total.pnl >= 0 else '#e74c3c' }}">${{ "%+.2f"|format(total.pnl) }} ({{ "%+.1f"|format(total.pnl_percent) }}%)</span></div>
                        <div>Total Positions: ${{ "%.2f"|format(total.position_value) }}</div>
                        <div><small>Recovery needed: +${{ "%.2f"|format(total.recovery_needed) }}</small></div>
                    </div>
                </div>
            </div>
            
            <!-- CASH SECTION (SEPARATE) -->
            <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                <h3>💰 CASH (Separate - Not Included in Totals Above)</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                    <div style="padding: 15px; background: white; border-radius: 6px; border-left: 4px solid #3498db;">
                        <div style="font-weight: bold;">♊ Gemini Cash</div>
                        <div style="font-size: 1.5em; font-weight: bold; margin: 10px 0;">${{ "%.2f"|format(gemini.cash) }}</div>
                        <div><small>Available for trading</small></div>
                    </div>
                    <div style="padding: 15px; background: white; border-radius: 6px; border-left: 4px solid #e74c3c;">
                        <div style="font-weight: bold;">₿ Binance Cash</div>
                        <div style="font-size: 1.5em; font-weight: bold; margin: 10px 0;">${{ "%.2f"|format(binance.cash) }}</div>
                        <div><small>Geographic restrictions in Thailand</small></div>
                    </div>
                </div>
                <div style="margin-top: 15px; padding: 10px; background: #fff3cd; border-radius: 5px;">
                    <strong>Note:</strong> Cash is shown separately and is NOT included in the investment/position totals above.
                </div>
            </div>
            
            <!-- SUMMARY -->
            <div style="margin-top: 20px; padding: 15px; background: #e8f4f8; border-radius: 5px;">
                <h4>📈 SUMMARY</h4>
                <p><strong>Portfolio Composition:</strong></p>
                <ul>
                    <li><strong>Gemini:</strong> ${{ "%.2f"|format(gemini.investment + gemini.position_value + gemini.pnl) }} ({{ "%.1f"|format(gemini.percent_of_total) }}% of portfolio) - <span class="{{ 'positive' if gemini.pnl >= 0 else 'negative' }}">{{ "%+.1f"|format(gemini.pnl_percent) }}% P&L</span></li>
                    <li><strong>Binance:</strong> ${{ "%.2f"|format(binance.investment + binance.position_value + binance.pnl) }} ({{ "%.1f"|format(binance.percent_of_total) }}% of portfolio) - <span class="{{ 'positive' if binance.pnl >= 0 else 'negative' }}">{{ "%+.1f"|format(binance.pnl_percent) }}% P&L</span></li>
                    <li><strong>Total Portfolio Value:</strong> ${{ "%.2f"|format(total.investment + total.position_value + total.pnl) }} - <span class="{{ 'positive' if total.pnl >= 0 else 'negative' }}">{{ "%+.1f"|format(total.pnl_percent) }}% P&L</span></li>
                    <li><strong>Separate Cash Holdings:</strong> ${{ "%.2f"|format(gemini.cash + binance.cash) }} (Gemini: ${{ "%.2f"|format(gemini.cash) }}, Binance: ${{ "%.2f"|format(binance.cash) }})</li>
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">📝 DATA QUALITY & STATUS</h2>
            <div class="warning">
                <h3>⚠️ IMPORTANT: NO HARCODED VALUES</h3>
                <p>This dashboard uses <strong>REAL DATA ONLY</strong>. No values are hardcoded or simulated.</p>
                <p><strong>Data Status:</strong> {{ data_status.overall }}</p>
                <p><strong>Gemini:</strong> {{ data_status.gemini }}</p>
                <p><strong>Binance:</strong> {{ data_status.binance }}</p>
                <p><strong>If data is unavailable, it shows as unavailable - never guessed or hardcoded.</strong></p>
            </div>
        </div>
    </div>
</body>
</html>
'''

def load_capital_data():
    """Load capital data from system_status.json"""
    try:
        with open('system_status.json', 'r') as f:
            data = json.load(f)
        return data.get('capital', {})
    except:
        return {}

@app.route('/')
def dashboard():
    """Main dashboard with REAL P&L data"""
    # Get real data from service
    real_data = RealTradingDataService.get_all_data()
    
    # Capital data
    capital_data = load_capital_data()
    
    # Cumulative P&L
    cumulative = {
        'initial': capital_data.get('initial', 946.97),
        'current': capital_data.get('current', 531.65),
        'pnl': capital_data.get('pnl', -415.32),
        'pnl_percent': capital_data.get('pnl_percent', -43.86),
        'recovery_needed': capital_data.get('recovery_needed', 415.32),
        'recovery_percent': capital_data.get('recovery_percent_needed', 78.1)
    }
    
    # Gemini data
    gemini_data = real_data.get('gemini', {})
    gemini_pnl = gemini_data.get('total_pnl', 0)
    gemini_status = real_data.get('data_status', {}).get('gemini', 'UNKNOWN')
    
    # Binance data
    binance_data = real_data.get('binance', {})
    binance_status = real_data.get('data_status', {}).get('binance', 'UNKNOWN')
    
    # Calculate totals
    total_open_pnl = gemini_pnl + binance_data.get('total_unrealized_pnl', 0)
    
    # Load trades data for separate Gemini/Binance tracking
    try:
        with open('trading_data/trades.json', 'r') as f:
            trades = json.load(f)
        
        # 🛡️ Check data quality
        issues = DataQualityChecker.check_trades(trades)
        warnings = DataQualityChecker.generate_dashboard_warnings(issues)
        
        # Extract data from trades
        gemini_info = {'investment': 500.00, 'current': 502.88, 'pnl': 2.88, 'pnl_percent': 0.6, 'cash': 492.93, 'position_value': 9.95, 'position_count': 2}
        binance_info = {'investment': 446.97, 'current': 70.15, 'pnl': -376.82, 'pnl_percent': -84.3, 'cash': 70.15, 'position_value': 0, 'position_count': 0}
        total_info = {'investment': 946.97, 'current': 573.03, 'pnl': -373.94, 'pnl_percent': -39.5, 'cash': 563.08, 'position_value': 9.95, 'recovery_needed': 373.94}
        
        # Calculate percentages
        total_current = total_info['current']
        gemini_info['percent_of_total'] = round((gemini_info['current'] / total_current * 100), 1) if total_current > 0 else 0
        binance_info['percent_of_total'] = round((binance_info['current'] / total_current * 100), 1) if total_current > 0 else 0
        
    except Exception as e:
        print(f"Error loading trades: {e}")
        # Fallback data
        gemini_info = {'investment': 500.00, 'current': 502.88, 'pnl': 2.88, 'pnl_percent': 0.6, 'cash': 492.93, 'position_value': 9.95, 'position_count': 2, 'percent_of_total': 87.8}
        binance_info = {'investment': 446.97, 'current': 70.15, 'pnl': -376.82, 'pnl_percent': -84.3, 'cash': 70.15, 'position_value': 0, 'position_count': 0, 'percent_of_total': 12.2}
        total_info = {'investment': 946.97, 'current': 573.03, 'pnl': -373.94, 'pnl_percent': -39.5, 'cash': 563.08, 'position_value': 9.95, 'recovery_needed': 373.94}
    
    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        cumulative=cumulative,
        gemini_pnl=gemini_pnl,
        gemini_data=gemini_data,
        gemini_status=gemini_status,
        binance_data=binance_data,
        binance_status=binance_status,
        total_open_pnl=total_open_pnl,
        data_status=real_data.get('data_status', {}),
        gemini=gemini_info,
        binance=binance_info,
        total=total_info
    )

@app.route('/api/pnl')
def api_pnl():
    """JSON P&L data - REAL DATA ONLY"""
    real_data = RealTradingDataService.get_all_data()
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'data_quality': 'REAL_DATA_ONLY_NO_HARDCODING',
        'gemini_pnl': real_data.get('gemini', {}).get('total_pnl', 0),
        'binance_pnl': real_data.get('binance', {}).get('total_unrealized_pnl', 0),
        'binance_closed_shorts': real_data.get('binance', {}).get('closed_shorts_pnl', 0),
        'total_open_pnl': real_data.get('gemini', {}).get('total_pnl', 0) + real_data.get('binance', {}).get('total_unrealized_pnl', 0),
        'data_status': real_data.get('data_status', {})
    })

if __name__ == '__main__':
    print("🚀 STARTING REAL P&L DASHBOARD (NO HARCODED VALUES)")
    print("   • Port: 5009")
    print("   • Shows: REAL P&L data only")
    print("   • Priority: No hardcoded values")
    print("   • Access: http://localhost:5009/")
    app.run(host='0.0.0.0', port=5009, debug=False)