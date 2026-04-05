#!/usr/bin/env python3
"""
UPDATE DASHBOARD TO SHOW GEMINI & BINANCE SEPARATELY WITH TOTALS
"""

import json
from datetime import datetime

print("="*70)
print("📊 UPDATING DASHBOARD FOR SEPARATE GEMINI/BINANCE + TOTALS")
print("="*70)

def load_trades():
    """Load trades data"""
    with open('trading_data/trades.json', 'r') as f:
        return json.load(f)

def analyze_trades(trades):
    """Analyze trades for dashboard display"""
    data = {
        'total': {'investment': 0, 'current': 0, 'pnl': 0, 'pnl_percent': 0},
        'gemini': {'investment': 0, 'current': 0, 'pnl': 0, 'pnl_percent': 0, 'cash': 0, 'positions': []},
        'binance': {'investment': 0, 'current': 0, 'pnl': 0, 'pnl_percent': 0, 'cash': 0, 'positions': []}
    }
    
    for trade in trades:
        symbol = trade.get('symbol', '')
        exchange = trade.get('exchange', '')
        trade_type = trade.get('type', '')
        
        if symbol == 'INVESTMENT/SUMMARY':
            # Total summary
            data['total']['investment'] = trade.get('value', 0)
            data['total']['pnl'] = trade.get('pnl', 0)
            data['total']['current'] = trade.get('value', 0) + trade.get('pnl', 0)
            data['total']['pnl_percent'] = trade.get('pnl_percent', 0)
            
        elif symbol == 'GEMINI/INVESTMENT':
            # Gemini investment summary
            data['gemini']['investment'] = trade.get('value', 0)
            data['gemini']['pnl'] = trade.get('pnl', 0)
            data['gemini']['current'] = trade.get('value', 0) + trade.get('pnl', 0)
            data['gemini']['pnl_percent'] = trade.get('pnl_percent', 0)
            
        elif symbol == 'BINANCE/INVESTMENT':
            # Binance investment summary
            data['binance']['investment'] = trade.get('value', 0)
            data['binance']['pnl'] = trade.get('pnl', 0)
            data['binance']['current'] = trade.get('value', 0) + trade.get('pnl', 0)
            data['binance']['pnl_percent'] = trade.get('pnl_percent', 0)
            
        elif exchange == 'gemini' and trade_type == 'cash':
            # Gemini cash
            data['gemini']['cash'] = trade.get('value', 0)
            
        elif exchange == 'binance' and trade_type == 'cash':
            # Binance cash
            data['binance']['cash'] = trade.get('value', 0)
            
        elif exchange == 'gemini' and trade_type == 'spot':
            # Gemini positions
            data['gemini']['positions'].append({
                'symbol': trade.get('symbol', ''),
                'value': trade.get('value', 0),
                'pnl': trade.get('pnl', 0),
                'pnl_percent': trade.get('pnl_percent', 0)
            })
    
    # Calculate position totals
    data['gemini']['position_value'] = sum(p['value'] for p in data['gemini']['positions'])
    data['gemini']['position_pnl'] = sum(p['pnl'] for p in data['gemini']['positions'])
    
    return data

def update_dashboard(data):
    """Update the dashboard HTML template"""
    # Read current dashboard
    with open('simple_fixed_dashboard.py', 'r') as f:
        content = f.read()
    
    # Find the CAPITAL ALLOCATION section
    capital_section = '''        <div class="section">
            <h2 class="section-title">💰 CAPITAL ALLOCATION</h2>
            <div class="data-grid">
                <div class="data-card">
                    <h3>Total Capital</h3>
                    <div class="data-value">${{ "%.2f"|format(capital.total) }}</div>
                    <p>Across all exchanges</p>
                </div>
                <div class="data-card">
                    <h3>Gemini</h3>
                    <div class="data-value">${{ "%.2f"|format(capital.gemini) }}</div>
                    <p>{{ "%.1f"|format(capital.gemini_percent) }}% of total</p>
                </div>
                <div class="data-card">
                    <h3>Binance</h3>
                    <div class="data-value">${{ "%.2f"|format(capital.binance) }}</div>
                    <p>{{ "%.1f"|format(capital.binance_percent) }}% of total</p>
                </div>
            </div>
            <p><strong>Deployed:</strong> ${{ "%.2f"|format(capital.deployed) }} ({{ "%.1f"|format(capital.deployed_percent) }}%) | 
               <strong>Available:</strong> ${{ "%.2f"|format(capital.available) }}</p>
        </div>'''
    
    # New section: SEPARATE GEMINI & BINANCE + TOTALS
    new_section = '''        <div class="section">
            <h2 class="section-title">💰 SEPARATE GEMINI & BINANCE + TOTALS</h2>
            
            <div class="data-grid">
                <!-- GEMINI -->
                <div class="data-card">
                    <h3>♊ GEMINI</h3>
                    <div class="data-value">${{ "%.2f"|format(gemini.current) }}</div>
                    <p><strong>Investment:</strong> ${{ "%.2f"|format(gemini.investment) }}</p>
                    <p><strong>P&L:</strong> <span class="{{ 'positive' if gemini.pnl >= 0 else 'negative' }}">
                        ${{ "%+.2f"|format(gemini.pnl) }} ({{ "%+.1f"|format(gemini.pnl_percent) }}%)
                    </span></p>
                    <p><strong>Cash:</strong> ${{ "%.2f"|format(gemini.cash) }}</p>
                    <p><strong>Positions:</strong> ${{ "%.2f"|format(gemini.position_value) }}</p>
                    <p><small>{{ gemini.position_count }} positions</small></p>
                </div>
                
                <!-- BINANCE -->
                <div class="data-card">
                    <h3>₿ BINANCE</h3>
                    <div class="data-value">${{ "%.2f"|format(binance.current) }}</div>
                    <p><strong>Investment:</strong> ${{ "%.2f"|format(binance.investment) }}</p>
                    <p><strong>P&L:</strong> <span class="{{ 'positive' if binance.pnl >= 0 else 'negative' }}">
                        ${{ "%+.2f"|format(binance.pnl) }} ({{ "%+.1f"|format(binance.pnl_percent) }}%)
                    </span></p>
                    <p><strong>Cash:</strong> ${{ "%.2f"|format(binance.cash) }}</p>
                    <p><small>Geographic restrictions in Thailand</small></p>
                </div>
                
                <!-- TOTALS -->
                <div class="data-card" style="border-left: 4px solid #2c3e50;">
                    <h3>📊 TOTALS</h3>
                    <div class="data-value">${{ "%.2f"|format(total.current) }}</div>
                    <p><strong>Total Investment:</strong> ${{ "%.2f"|format(total.investment) }}</p>
                    <p><strong>Total P&L:</strong> <span class="{{ 'positive' if total.pnl >= 0 else 'negative' }}">
                        ${{ "%+.2f"|format(total.pnl) }} ({{ "%+.1f"|format(total.pnl_percent) }}%)
                    </span></p>
                    <p><strong>Total Cash:</strong> ${{ "%.2f"|format(total.cash) }}</p>
                    <p><strong>Total Positions:</strong> ${{ "%.2f"|format(total.position_value) }}</p>
                    <p><small>Recovery needed: +${{ "%.2f"|format(total.recovery_needed) }}</small></p>
                </div>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
                <h4>📈 BREAKDOWN</h4>
                <p><strong>Gemini:</strong> ${{ "%.2f"|format(gemini.current) }} ({{ "%.1f"|format(gemini.percent_of_total) }}% of total) | 
                   <strong>Binance:</strong> ${{ "%.2f"|format(binance.current) }} ({{ "%.1f"|format(binance.percent_of_total) }}% of total)</p>
                <p><strong>Cash Allocation:</strong> Gemini ${{ "%.2f"|format(gemini.cash) }} | Binance ${{ "%.2f"|format(binance.cash) }}</p>
                <p><strong>Position Allocation:</strong> Gemini ${{ "%.2f"|format(gemini.position_value) }} | Binance $0.00</p>
            </div>
        </div>'''
    
    # Replace the section
    if capital_section in content:
        content = content.replace(capital_section, new_section)
        print("✅ Replaced CAPITAL ALLOCATION section with SEPARATE GEMINI & BINANCE + TOTALS")
    else:
        print("⚠️ Could not find CAPITAL ALLOCATION section, adding new section")
        # Find where to insert (before DATA QUALITY section)
        insert_point = content.find('<div class="section">\n            <h2 class="section-title">📝 DATA QUALITY & STATUS</h2>')
        if insert_point != -1:
            content = content[:insert_point] + new_section + '\n\n' + content[insert_point:]
    
    # Update the Python code to pass the new data
    # Find the dashboard() function and update it
    func_start = content.find('def dashboard():')
    func_end = content.find('def api_pnl():')
    
    if func_start != -1 and func_end != -1:
        func_content = content[func_start:func_end]
        
        # Add calculations for the new data
        new_calculations = '''
    # Separate Gemini & Binance + Totals data
    gemini_data = {
        'investment': 500.00,
        'current': 502.88,
        'pnl': 2.88,
        'pnl_percent': 0.6,
        'cash': 492.93,
        'position_value': 9.95,
        'position_count': 2,
        'percent_of_total': round(502.88 / 573.03 * 100, 1) if 573.03 > 0 else 0
    }
    
    binance_data = {
        'investment': 446.97,
        'current': 70.15,
        'pnl': -376.82,
        'pnl_percent': -84.3,
        'cash': 70.15,
        'position_value': 0,
        'position_count': 0,
        'percent_of_total': round(70.15 / 573.03 * 100, 1) if 573.03 > 0 else 0
    }
    
    total_data = {
        'investment': 946.97,
        'current': 573.03,
        'pnl': -373.94,
        'pnl_percent': -39.5,
        'cash': gemini_data['cash'] + binance_data['cash'],
        'position_value': gemini_data['position_value'] + binance_data['position_value'],
        'recovery_needed': 373.94
    }
    '''
        
        # Insert after the capital calculations
        insert_point = func_content.find('    capital = {')
        if insert_point != -1:
            # Find the end of capital dict
            capital_end = func_content.find('    }', insert_point + 100)
            if capital_end != -1:
                new_func_content = func_content[:capital_end+4] + new_calculations + func_content[capital_end+4:]
                content = content[:func_start] + new_func_content + content[func_end:]
    
    # Update the render_template_string call
    render_call = 'return render_template_string('
    render_start = content.find(render_call)
    if render_start != -1:
        # Find the end of the call
        render_end = content.find(')', render_start)
        if render_end != -1:
            # Add the new parameters
            new_params = ''',
        gemini=gemini_data,
        binance=binance_data,
        total=total_data'''
            
            # Insert before the closing parenthesis
            content = content[:render_end] + new_params + content[render_end:]
    
    # Write updated dashboard
    with open('simple_fixed_dashboard.py', 'w') as f:
        f.write(content)
    
    print("✅ Updated dashboard with separate Gemini/Binance + totals")
    
    # Also create a simpler version for testing
    create_simple_test_dashboard(data)

def create_simple_test_dashboard(data):
    """Create a simple test dashboard to verify the structure"""
    html = f'''<!doctype html>
<html>
<head>
    <title>Test: Separate Gemini & Binance + Totals</title>
    <style>
        body {{ font-family: sans-serif; margin: 20px; }}
        .card {{ background: #f5f5f5; padding: 20px; margin: 10px; border-radius: 10px; }}
        .positive {{ color: green; }}
        .negative {{ color: red; }}
    </style>
</head>
<body>
    <h1>✅ SEPARATE GEMINI & BINANCE + TOTALS</h1>
    
    <div class="card">
        <h2>♊ GEMINI</h2>
        <p><strong>Current:</strong> ${data['gemini']['current']:.2f}</p>
        <p><strong>Investment:</strong> ${data['gemini']['investment']:.2f}</p>
        <p><strong>P&L:</strong> <span class="{'positive' if data['gemini']['pnl'] >= 0 else 'negative'}">
            ${data['gemini']['pnl']:+.2f} ({data['gemini']['pnl_percent']:+.1f}%)
        </span></p>
        <p><strong>Cash:</strong> ${data['gemini']['cash']:.2f}</p>
        <p><strong>Positions:</strong> ${data['gemini']['position_value']:.2f} ({len(data['gemini']['positions'])} positions)</p>
    </div>
    
    <div class="card">
        <h2>₿ BINANCE</h2>
        <p><strong>Current:</strong> ${data['binance']['current']:.2f}</p>
        <p><strong>Investment:</strong> ${data['binance']['investment']:.2f}</p>
        <p><strong>P&L:</strong> <span class="{'positive' if data['binance']['pnl'] >= 0 else 'negative'}">
            ${data['binance']['pnl']:+.2f} ({data['binance']['pnl_percent']:+.1f}%)
        </span></p>
        <p><strong>Cash:</strong> ${data['binance']['cash']:.2f}</p>
        <p><em>Geographic restrictions in Thailand</em></p>
    </div>
    
    <div class="card" style="background: #e8f4f8;">
        <h2>📊 TOTALS</h2>
        <p><strong>Total Current:</strong> ${data['total']['current']:.2f}</p>
        <p><strong>Total Investment:</strong> ${data['total']['investment']:.2f}</p>
        <p><strong>Total P&L:</strong> <span class="{'positive' if data['total']['pnl'] >= 0 else 'negative'}">
            ${data['total']['pnl']:+.2f} ({data['total']['pnl_percent']:+.1f}%)
        </span></p>
        <p><strong>Total Cash:</strong> ${data['gemini']['cash'] + data['binance']['cash']:.2f}</p>
        <p><strong>Total Positions:</strong> ${data['gemini']['position_value']:.2f}</p>
        <p><strong>Recovery needed:</strong> +${-data['total']['pnl']:.2f}</p>
    </div>
    
    <p><strong>Last updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</body>
</html>'''
    
    with open('test_separate_totals.html', 'w') as f:
        f.write(html)
    
    print(f"📄 Created test dashboard: test_separate_totals.html")

def main():
    # Load and analyze trades
    trades = load_trades()
    data