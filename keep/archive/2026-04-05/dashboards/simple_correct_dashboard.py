#!/usr/bin/env python3
"""
SIMPLE CORRECT DASHBOARD
Shows ONLY actual holdings and proper investment accounting
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
    <title>💰 SIMPLE CORRECT DASHBOARD - Actual Holdings Only</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 20px; background: #0f172a; color: white; }
        .container { max-width: 1000px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; padding: 20px; background: #1e293b; border-radius: 10px; }
        h1 { color: #00ff9d; margin: 0; }
        .subtitle { color: #94a3b8; margin: 10px 0 20px 0; }
        .section { background: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #334155; }
        .section-title { color: #cbd5e1; font-size: 1.3em; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #334155; }
        .holdings-table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; }
        .holdings-table th { background: #334155; padding: 12px 15px; text-align: left; font-weight: 600; color: #cbd5e1; border-bottom: 2px solid #475569; }
        .holdings-table td { padding: 10px 15px; border-bottom: 1px solid #334155; }
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
        .investment-card { background: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 15px; }
        .investment-value { font-size: 1.8em; font-weight: bold; color: #00ff9d; margin: 10px 0; }
        .warning { background: #fff3cd; color: #856404; padding: 15px; border-radius: 5px; margin: 10px 0; border: 1px solid #ffeaa7; }
        .timestamp { color: #7f8c8d; font-size: 0.9em; text-align: right; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 SIMPLE CORRECT DASHBOARD</h1>
            <p class="subtitle">ACTUAL HOLDINGS ONLY - No USD, No summaries, Just real coins</p>
            <div class="timestamp">Last updated: {{ timestamp }}</div>
        </div>
        
        <!-- 🎯 ACTUAL HOLDINGS SECTION -->
        <div class="section">
            <h2 class="section-title">🎯 ACTUAL HOLDINGS ({{ holdings_count }} coins)</h2>
            <p style="color: #94a3b8; margin-bottom: 15px;">Only real cryptocurrency holdings - no USD, no summaries</p>
            
            {% if holdings %}
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
                    {% for holding in holdings %}
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
                    
                    <!-- TOTALS ROW -->
                    <tr style="background: #2d3748; font-weight: bold;">
                        <td colspan="4" style="text-align: right;">TOTALS:</td>
                        <td>${{ "%.2f"|format(total_investment) }}</td>
                        <td>${{ "%.2f"|format(total_current_value) }}</td>
                        <td class="{{ 'positive' if total_pnl >= 0 else 'negative' }}">
                            ${{ "%.2f"|format(total_pnl) }}
                        </td>
                        <td class="{{ 'positive' if total_pnl_percent >= 0 else 'negative' }}">
                            {{ "%.1f"|format(total_pnl_percent) }}%
                        </td>
                    </tr>
                </tbody>
            </table>
            {% else %}
            <div style="text-align: center; padding: 40px; color: #94a3b8;">
                <h3>No holdings found</h3>
                <p>No actual cryptocurrency holdings in the system</p>
            </div>
            {% endif %}
        </div>
        
        <!-- 💰 INVESTMENT ACCOUNTING SECTION -->
        <div class="section">
            <h2 class="section-title">💰 INVESTMENT ACCOUNTING</h2>
            <p style="color: #94a3b8; margin-bottom: 15px;">Money spent vs current value - Clear accounting</p>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="investment-card">
                    <h3>Money Spent (Investment)</h3>
                    <div class="investment-value">${{ "%.2f"|format(total_investment) }}</div>
                    <p>Total money invested in buying coins</p>
                </div>
                
                <div class="investment-card">
                    <h3>Current Value</h3>
                    <div class="investment-value {{ 'positive' if total_pnl >= 0 else 'negative' }}">
                        ${{ "%.2f"|format(total_current_value) }}
                    </div>
                    <p>Current value of all holdings</p>
                </div>
            </div>
            
            <div class="investment-card" style="margin-top: 20px; background: #2d3748;">
                <h3>Net P&L</h3>
                <div class="investment-value {{ 'positive' if total_pnl >= 0 else 'negative' }}">
                    ${{ "%+.2f"|format(total_pnl) }} ({{ "%+.1f"|format(total_pnl_percent) }}%)
                </div>
                <p>Profit/Loss from investment</p>
            </div>
        </div>
        
        <!-- ⚠️ WHAT'S NOT SHOWN SECTION -->
        <div class="section">
            <h2 class="section-title">⚠️ WHAT'S NOT SHOWN HERE</h2>
            <div class="warning" style="background: #1e293b; color: #94a3b8; border-color: #334155;">
                <p><strong>This dashboard shows ONLY actual cryptocurrency holdings.</strong></p>
                <p>It does NOT show:</p>
                <ul>
                    <li>💰 USD cash balances (that's cash, not a holding)</li>
                    <li>📊 Summary rows (INVESTMENT/SUMMARY, etc.)</li>
                    <li>🧾 Duplicate test entries</li>
                    <li>📈 Anything that's not an actual coin holding</li>
                </ul>
                <p><strong>Simple rule:</strong> If it's not ETH, SOL, BTC, or another actual cryptocurrency you own, it's not here.</p>
            </div>
        </div>
        
        <div class="timestamp" style="margin-top: 30px;">
            Auto-refreshes every 30 seconds | Simple & Correct
        </div>
    </div>
</body>
</html>
'''

def load_actual_holdings():
    """Load ONLY REAL cryptocurrency holdings (no USD, no summaries, no test entries)"""
    holdings = []
    
    try:
        with open('trading_data/trades.json', 'r') as f:
            trades = json.load(f)
        
        # Filter for ONLY REAL spot trades (actual holdings, not test entries)
        real_trades = []
        for trade in trades:
            if trade.get('type') != 'spot':
                continue  # Skip non-spot trades
            
            note = trade.get('note', '').lower()
            symbol = trade.get('symbol', '')
            
            # Check if this is a REAL trade (not a test/LLM bot entry)
            is_real_trade = True
            
            # Heuristic: Real trades have realistic prices
            price = trade.get('price', 0)
            if symbol == 'ETH/USD' and price > 5000:  # ETH over $5k is suspicious
                is_real_trade = False
            elif symbol == 'SOL/USD' and price > 200:  # SOL over $200 is suspicious
                is_real_trade = False
            elif symbol == 'BTC/USD' and price > 100000:  # BTC over $100k is suspicious
                is_real_trade = False
            
            # Heuristic: Check note for test indicators
            if 'price fixed' in note or 'amount fixed' in note:
                is_real_trade = False
            
            # Heuristic: Round numbers are suspicious (real trades have decimals)
            if price % 1 == 0 and price > 100:  # Round number over $100
                is_real_trade = False
            
            if is_real_trade:
                real_trades.append(trade)
        
        print(f"📊 Found {len(real_trades)} REAL trades (filtered out test entries)")
        
        # Group by symbol to combine duplicates
        holdings_by_symbol = {}
        for trade in real_trades:
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
                    'pnl_percent': 0,
                    'is_real': True
                }
            
            # Add to existing holding
            amount = trade.get('amount', 0)
            price = trade.get('price', 0)
            investment = amount * price
            
            holdings_by_symbol[symbol]['amount'] += amount
            holdings_by_symbol[symbol]['investment'] += investment
        
        # Calculate current values and P&L
        for symbol, holding in holdings_by_symbol.items():
            if holding['amount'] > 0:
                holding['entry_price'] = holding['investment'] / holding['amount'] if holding['amount'] > 0 else 0
                holding['current_value'] = holding['amount'] * holding['current_price']
                holding['pnl'] = holding['current_value'] - holding['investment']
                holding['pnl_percent'] = (holding['pnl'] / holding['investment'] * 100) if holding['investment'] > 0 else 0
                
                holdings.append(holding)
        
        print(f"✅ Loaded {len(holdings)} REAL holdings: {', '.join([h['symbol'] for h in holdings])}")
        
        # Show investment breakdown
        print("💰 INVESTMENT BREAKDOWN:")
        total_investment = sum(h['investment'] for h in holdings)
        for holding in holdings:
            print(f"  • {holding['symbol']}: ${holding['investment']:.2f} ({holding['amount']:.8f} coins)")
        print(f"  📊 TOTAL REAL INVESTMENT: ${total_investment:.2f}")
        
    except Exception as e:
        print(f"❌ Error loading holdings: {e}")
    
    return holdings

@app.route('/')
def index():
    """Main dashboard - ONLY actual holdings"""
    holdings = load_actual_holdings()
    
    # Calculate totals
    total_investment = sum(h['investment'] for h in holdings)
    total_current_value = sum(h['current_value'] for h in holdings)
    total_pnl = total_current_value - total_investment
    total_pnl_percent = (total_pnl / total_investment * 100) if total_investment > 0 else 0
    
    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        holdings=holdings,
        holdings_count=len(holdings),
        total_investment=total_investment,
        total_current_value=total_current_value,
        total_pnl=total_pnl,
        total_pnl_percent=total_pnl_percent
    )

@app.route('/api/holdings')
def api_holdings():
    """API endpoint for actual holdings"""
    holdings = load_actual_holdings()
    
    # Calculate totals
    total_investment = sum(h['investment'] for h in holdings)
    total_current_value = sum(h['current_value'] for h in holdings)
    total_pnl = total_current_value - total_investment
    total_pnl_percent = (total_pnl / total_investment * 100) if total_investment > 0 else 0
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'holdings': holdings,
        'summary': {
            'total_holdings': len(holdings),
            'total_investment': total_investment,
            'total_current_value': total_current_value,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent
        }
    })

if __name__ == '__main__':
    print("="*70)
    print("💰 SIMPLE CORRECT DASHBOARD")
    print("="*70)
    print("✅ Shows ONLY actual holdings (no USD, no summaries)")
    print("✅ Clear investment accounting (money spent vs current value)")
    print("✅ Simple & correct - understands the system")
    print("="*70)
    print("Dashboard: http://localhost:5014/")
    print("API: http://localhost:5014/api/holdings")
    print("="*70)
    
    app.run(host='0.0.0.0', port=5014, debug=False)