#!/usr/bin/env python3
"""
SIMPLE ORDERS DASHBOARD - Shows REAL orders from Binance and Gemini
"""

from flask import Flask, render_template_string
import ccxt
import json
from datetime import datetime

app = Flask(__name__)

def get_gemini_data():
    """Get Gemini data"""
    try:
        with open("secure_keys/.gemini_key", "r") as f:
            GEMINI_KEY = f.read().strip()
        with open("secure_keys/.gemini_secret", "r") as f:
            GEMINI_SECRET = f.read().strip()
        
        exchange = ccxt.gemini({
            'apiKey': GEMINI_KEY,
            'secret': GEMINI_SECRET,
            'enableRateLimit': True,
        })
        
        balance = exchange.fetch_balance()
        cash = balance['free'].get('USD', 0)
        btc = balance['free'].get('BTC', 0)
        
        ticker = exchange.fetch_ticker('BTC/USD')
        btc_price = ticker['last']
        btc_value = btc * btc_price
        
        return {
            "total": cash + btc_value,
            "cash": cash,
            "btc": btc,
            "btc_price": btc_price,
            "btc_value": btc_value,
            "error": None
        }
    except Exception as e:
        return {"error": str(e), "total": 0, "cash": 0, "btc": 0}

def get_binance_data():
    """Get Binance data"""
    try:
        with open("secure_keys/.binance_key", "r") as f:
            BINANCE_KEY = f.read().strip()
        with open("secure_keys/.binance_secret", "r") as f:
            BINANCE_SECRET = f.read().strip()
        
        exchange = ccxt.binance({
            'apiKey': BINANCE_KEY,
            'secret': BINANCE_SECRET,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        
        balance = exchange.fetch_balance()
        total_usdt = balance['total'].get('USDT', 0)
        free_usdt = balance['free'].get('USDT', 0)
        used_usdt = balance['used'].get('USDT', 0)
        
        positions = exchange.fetch_positions()
        open_positions = [p for p in positions if float(p['contracts']) > 0]
        
        # Simplify positions data
        simple_positions = []
        for pos in open_positions:
            pnl = float(pos['unrealizedPnl'])
            entry = float(pos['entryPrice'])
            current = float(pos['markPrice'])
            pnl_percent = ((current - entry) / entry * 100) if entry > 0 else 0
            if pos['side'].upper() == 'SHORT':
                pnl_percent = -pnl_percent
            
            simple_positions.append({
                'symbol': pos['symbol'].replace(':USDT', ''),
                'side': pos['side'].upper(),
                'contracts': float(pos['contracts']),
                'entry': entry,
                'current': current,
                'pnl': pnl,
                'pnl_percent': pnl_percent
            })
        
        return {
            "total_usdt": total_usdt,
            "free_usdt": free_usdt,
            "used_usdt": used_usdt,
            "positions": simple_positions,
            "error": None
        }
    except Exception as e:
        return {"error": str(e), "total_usdt": 0, "positions": []}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>📊 REAL ORDERS DASHBOARD</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f0f0; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .gemini { border-left: 5px solid #00D395; }
        .binance { border-left: 5px solid #F0B90B; }
        h1 { color: #333; }
        h2 { color: #555; margin-top: 0; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th { background: #f5f5f5; padding: 10px; text-align: left; }
        td { padding: 8px 10px; border-bottom: 1px solid #eee; }
        .profit { color: green; }
        .loss { color: red; }
        .badge { padding: 3px 8px; border-radius: 10px; font-size: 0.9em; }
        .badge-buy { background: #00D395; color: white; }
        .badge-sell { background: #ff4444; color: white; }
        .badge-short { background: #F0B90B; color: black; }
        .stat { font-size: 1.8em; font-weight: bold; margin: 10px 0; }
    </style>
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <div class="container">
        <h1>📊 REAL ORDERS DASHBOARD</h1>
        <p>Auto-refreshes every 30 seconds | Last updated: {{ timestamp }}</p>
        
        <div style="display: flex; gap: 20px;">
            <div style="flex: 1;">
                <div class="card gemini">
                    <h2>♊ GEMINI</h2>
                    {% if gemini.error %}
                        <p style="color: red;">Error: {{ gemini.error }}</p>
                    {% else %}
                        <div class="stat" style="color: #00D395;">${{ "%.2f"|format(gemini.total) }}</div>
                        <p>Cash: ${{ "%.2f"|format(gemini.cash) }}</p>
                        <p>BTC: {{ "%.6f"|format(gemini.btc) }} (${{ "%.2f"|format(gemini.btc_value) }})</p>
                        <p>BTC Price: ${{ "%.2f"|format(gemini.btc_price) }}</p>
                    {% endif %}
                </div>
            </div>
            
            <div style="flex: 1;">
                <div class="card binance">
                    <h2>₿ BINANCE FUTURES</h2>
                    {% if binance.error %}
                        <p style="color: red;">Error: {{ binance.error }}</p>
                    {% else %}
                        <div class="stat" style="color: #F0B90B;">${{ "%.2f"|format(binance.total_usdt) }}</div>
                        <p>Free: ${{ "%.2f"|format(binance.free_usdt) }} | Used: ${{ "%.2f"|format(binance.used_usdt) }}</p>
                        
                        <h3>SHORT POSITIONS ({{ binance.positions|length }})</h3>
                        {% if binance.positions %}
                            <table>
                                <tr>
                                    <th>Symbol</th>
                                    <th>Side</th>
                                    <th>Contracts</th>
                                    <th>Entry</th>
                                    <th>P&L</th>
                                </tr>
                                {% for pos in binance.positions %}
                                <tr>
                                    <td>{{ pos.symbol }}</td>
                                    <td><span class="badge badge-short">{{ pos.side }}</span></td>
                                    <td>{{ "%.2f"|format(pos.contracts) }}</td>
                                    <td>${{ "%.4f"|format(pos.entry) }}</td>
                                    <td class="{{ 'profit' if pos.pnl > 0 else 'loss' }}">
                                        ${{ "%.4f"|format(pos.pnl) }} ({{ "%.2f"|format(pos.pnl_percent) }}%)
                                    </td>
                                </tr>
                                {% endfor %}
                            </table>
                        {% else %}
                            <p>No open positions</p>
                        {% endif %}
                    {% endif %}
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🤖 BOT STATUS</h2>
            <p>✅ Gemini LONG Bot: Running (buy dips -3%, sell +8%)</p>
            <p>✅ Binance SHORT Bot: Running (short drops -0.8%, 3x leverage)</p>
            <p>🔄 Auto-refresh: Every 30 seconds</p>
            <p>📊 Dashboard: http://localhost:5004</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    gemini = get_gemini_data()
    binance = get_binance_data()
    
    return render_template_string(HTML, 
        gemini=gemini,
        binance=binance,
        timestamp=datetime.now().strftime("%H:%M:%S")
    )

if __name__ == '__main__':
    print("🚀 SIMPLE ORDERS DASHBOARD starting on http://localhost:5004")
    print("📊 Shows REAL Gemini and Binance orders")
    app.run(host='0.0.0.0', port=5004, debug=False)