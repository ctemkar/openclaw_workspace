#!/usr/bin/env python3
"""
TRUTH DASHBOARD - Shows REAL orders from Binance and Gemini
"""

from flask import Flask, render_template_string
import requests
import json
import os
import ccxt
from datetime import datetime

app = Flask(__name__)

# Initialize exchanges (will load keys when needed)
gemini_exchange = None
binance_exchange = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🚀 REAL-TIME TRADING DASHBOARD 🚀</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; }
        .card { background: white; border-radius: 10px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .gemini { border-left: 10px solid #00D395; background: #f5fffb; }
        .binance { border-left: 10px solid #F0B90B; background: #fffbf0; }
        .status { border-left: 10px solid #4444ff; background: #f5f5ff; }
        h1 { color: #333; }
        h2 { color: #555; margin-top: 0; }
        h3 { color: #666; margin: 15px 0 10px 0; }
        .stat { font-size: 1.8em; font-weight: bold; margin: 10px 0; }
        .green { color: #00D395; }
        .red { color: #ff4444; }
        .yellow { color: #ffaa44; }
        .row { display: flex; flex-wrap: wrap; gap: 20px; }
        .col { flex: 1; min-width: 300px; }
        .order-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        .order-table th { background: #f0f0f0; padding: 10px; text-align: left; }
        .order-table td { padding: 8px 10px; border-bottom: 1px solid #eee; }
        .order-table tr:hover { background: #f9f9f9; }
        .badge { display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }
        .badge-buy { background: #00D395; color: white; }
        .badge-sell { background: #ff4444; color: white; }
        .badge-short { background: #F0B90B; color: black; }
        .badge-long { background: #00D395; color: white; }
        .badge-profit { background: #00D395; color: white; }
        .badge-loss { background: #ff4444; color: white; }
        .badge-neutral { background: #888; color: white; }
        .exchange-header { display: flex; align-items: center; gap: 10px; }
        .exchange-logo { font-size: 1.5em; }
        .refresh-btn { background: #4444ff; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; }
        .refresh-btn:hover { background: #3333ee; }
    </style>
    <script>
        function refreshDashboard() {
            document.getElementById('refresh-btn').innerHTML = '🔄 Refreshing...';
            location.reload();
        }
        
        // Auto-refresh every 30 seconds
        setTimeout(function() {
            location.reload();
        }, 30000);
    </script>
</head>
<body>
    <div class="container">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h1>🚀 REAL-TIME TRADING DASHBOARD</h1>
            <button id="refresh-btn" class="refresh-btn" onclick="refreshDashboard()">🔄 Refresh Now</button>
        </div>
        <p><em>Showing REAL orders from Gemini and Binance - Auto-refreshes every 30 seconds</em></p>
        
        <div class="row">
            <div class="col">
                <div class="card gemini">
                    <div class="exchange-header">
                        <div class="exchange-logo">♊</div>
                        <h2>GEMINI - LONG POSITIONS</h2>
                    </div>
                    
                    {% if gemini_data.error %}
                        <p style="color: red;">❌ {{ gemini_data.error }}</p>
                    {% else %}
                        <div class="stat green">${{ "%.2f"|format(gemini_data.balance.total) }}</div>
                        <p>Cash: ${{ "%.2f"|format(gemini_data.balance.cash) }} | BTC: {{ "%.6f"|format(gemini_data.balance.btc) }} (${{
                         "%.2f"|format(gemini_data.balance.btc_value) }})</p>
                        <p>BTC Price: ${{ "%.2f"|format(gemini_data.balance.btc_price) }}</p>
                        
                        <h3>📋 Open Orders ({{ gemini_data.open_orders|length }})</h3>
                        {% if gemini_data.open_orders %}
                            <table class="order-table">
                                <tr>
                                    <th>Symbol</th>
                                    <th>Side</th>
                                    <th>Amount</th>
                                    <th>Price</th>
                                    <th>Status</th>
                                </tr>
                                {% for order in gemini_data.open_orders %}
                                <tr>
                                    <td>{{ order.symbol }}</td>
                                    <td><span class="badge badge-{{ order.side|lower }}">{{ order.side }}</span></td>
                                    <td>{{ "%.6f"|format(order.amount) }}</td>
                                    <td>${{ "%.2f"|format(order.price) }}</td>
                                    <td>{{ order.status }}</td>
                                </tr>
                                {% endfor %}
                            </table>
                        {% else %}
                            <p>No open orders</p>
                        {% endif %}
                        
                        <h3>📜 Recent Trades ({{ gemini_data.recent_trades|length }})</h3>
                        {% if gemini_data.recent_trades %}
                            <table class="order-table">
                                <tr>
                                    <th>Time</th>
                                    <th>Side</th>
                                    <th>Amount</th>
                                    <th>Price</th>
                                    <th>Cost</th>
                                </tr>
                                {% for trade in gemini_data.recent_trades %}
                                <tr>
                                    <td>{{ trade.timestamp[11:19] if trade.timestamp else 'N/A' }}</td>
                                    <td><span class="badge badge-{{ trade.side|lower }}">{{ trade.side }}</span></td>
                                    <td>{{ "%.6f"|format(trade.amount) }}</td>
                                    <td>${{ "%.2f"|format(trade.price) }}</td>
                                    <td>${{ "%.2f"|format(trade.cost) }}</td>
                                </tr>
                                {% endfor %}
                            </table>
                        {% else %}
                            <p>No recent trades</p>
                        {% endif %}
                    {% endif %}
                </div>
            </div>
            
            <div class="col">
                <div class="card binance">
                    <div class="exchange-header">
                        <div class="exchange-logo">₿</div>
                        <h2>BINANCE - SHORT POSITIONS</h2>
                    </div>
                    
                    {% if binance_data.error %}
                        <p style="color: red;">❌ {{ binance_data.error }}</p>
                    {% else %}
                        <div class="stat yellow">${{ "%.2f"|format(binance_data.balance.total_usdt) }}</div>
                        <p>Free: ${{ "%.2f"|format(binance_data.balance.free_usdt) }} | Used: ${{ "%.2f"|format(binance_data.balance.used_usdt) }}</p>
                        
                        <h3>📊 Open Positions ({{ binance_data.open_positions|length }})</h3>
                        {% if binance_data.open_positions %}
                            <table class="order-table">
                                <tr>
                                    <th>Symbol</th>
                                    <th>Side</th>
                                    <th>Contracts</th>
                                    <th>Entry</th>
                                    <th>Current</th>
                                    <th>P&L</th>
                                </tr>
                                {% for pos in binance_data.open_positions %}
                                {% set pnl = pos.unrealizedPnl|float %}
                                {% set entry = pos.entryPrice|float %}
                                {% set current = pos.markPrice|float %}
                                {% set pnl_percent = ((current - entry) / entry * 100) if entry > 0 else 0 %}
                                {% if pos.side|upper == 'SHORT' %}
                                    {% set pnl_percent = -pnl_percent %}
                                {% endif %}
                                <tr>
                                    <td>{{ pos.symbol.replace(':USDT', '') }}</td>
                                    <td><span class="badge badge-short">{{ pos.side|upper }}</span></td>
                                    <td>{{ "%.2f"|format(pos.contracts|float) }}</td>
                                    <td>${{ "%.4f"|format(entry) }}</td>
                                    <td>${{ "%.4f"|format(current) }}</td>
                                    <td>
                                        <span class="badge badge-{% if pnl > 0 %}profit{% elif pnl < 0 %}loss{% else %}neutral{% endif %}">
                                            ${{ "%.4f"|format(pnl) }} ({{ "%.2f"|format(pnl_percent) }}%)
                                        </span>
                                    </td>
                                </tr>
                                {% endfor %}
                            </table>
                        {% else %}
                            <p>No open positions</p>
                        {% endif %}
                        
                        <h3>📋 Open Orders ({{ binance_data.open_orders|length }})</h3>
                        {% if binance_data.open_orders %}
                            <table class="order-table">
                                <tr>
                                    <th>Symbol</th>
                                    <th>Side</th>
                                    <th>Amount</th>
                                    <th>Price</th>
                                    <th>Status</th>
                                </tr>
                                {% for order in binance_data.open_orders %}
                                <tr>
                                    <td>{{ order.symbol }}</td>
                                    <td><span class="badge badge-{{ order.side|lower }}">{{ order.side }}</span></td>
                                    <td>{{ "%.2f"|format(order.amount) }}</td>
                                    <td>${{ "%.4f"|format(order.price) }}</td>
                                    <td>{{ order.status }}</td>
                                </tr>
                                {% endfor %}
                            </table>
                        {% else %}
                            <p>No open orders</p>
                        {% endif %}
                        
                        <h3>📜 Recent Trades ({{ binance_data.recent_trades|length }})</h3>
                        {% if binance_data.recent_trades %}
                            <table class="order-table">
                                <tr>
                                    <th>Time</th>
                                    <th>Symbol</th>
                                    <th>Side</th>
                                    <th>Amount</th>
                                    <th>Price</th>
                                </tr>
                                {% for trade in binance_data.recent_trades %}
                                <tr>
                                    <td>{{ trade.timestamp[11:19] if trade.timestamp else 'N/A' }}</td>
                                    <td>{{ trade.symbol }}</td>
                                    <td><span class="badge badge-{{ trade.side|lower }}">{{ trade.side }}</span></td>
                                    <td>{{ "%.2f"|format(trade.amount) }}</td>
                                    <td>${{ "%.4f"|format(trade.price) }}</td>
                                </tr>
                                {% endfor %}
                            </table>
                        {% else %}
                            <p>No recent trades</p>
                        {% endif %}
                    {% endif %}
                </div>
            </div>
        </div>
        
        <div class="card status">
            <h2>🤖 BOT STATUS</h2>
            <div class="row">
                {% for bot in active_bots %}
                <div style="flex: 1; min-width: 200px;">
                    <h3>{{ bot.name }}</h3>
                    <p>Status: <strong>{{ bot.status }}</strong></p>
                    <p>PID: {{ bot.pid }}</p>
                </div>
                {% endfor %}
            </div>
            <p><strong>Total:</strong> {{ active_bots|length }} bots running</p>
        </div>
        
        <div class="card">
            <h2>📈 TRADING STRATEGY</h2>
            <div class="row">
                <div style="flex: 1;">
                    <h3>♊ Gemini (LONG)</h3>
                    <ul>
                        <li>Buy: Price drops 3%+ (buy dip)</li>
                        <li>Sell: Price rises 8%+ (take profit)</li>
                        <li>Capital: $100 trading capital</li>
                        <li>Risk: 2% per trade ($2)</li>
                    </ul>
                </div>
                <div style="flex: 1;">
                    <h3>₿ Binance (SHORT)</h3>
                    <ul>
                        <li>Short: Price drops 0.8%+</li>
                        <li>Cover: Price drops 8% (profit) or rises 5% (stop-loss)</li>
                        <li>Capital: $25 futures capital</li>
                        <li>Leverage: 3x</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="card">
            <p><strong>Last updated:</strong> {{ timestamp }}</p>
            <p><strong>Dashboard URL:</strong> http://localhost:5003</p>
            <p><strong>Auto-refresh:</strong> Every 30 seconds</p>
            <p><em>This dashboard shows REAL orders from Gemini and Binance APIs</em></p>
        </div>
    </div>
</body>
</html>
"""

def init_gemini():
    """Initialize Gemini exchange"""
    global gemini_exchange
    if gemini_exchange is None:
        try:
            with open("secure_keys/.gemini_key", "r") as f:
                GEMINI_KEY = f.read().strip()
            with open("secure_keys/.gemini_secret", "r") as f:
                GEMINI_SECRET = f.read().strip()
            
            gemini_exchange = ccxt.gemini({
                'apiKey': GEMINI_KEY,
                'secret': GEMINI_SECRET,
                'enableRateLimit': True,
            })
            return True
        except Exception as e:
            print(f"Gemini init error: {e}")
            return False
    return True

def init_binance():
    """Initialize Binance exchange"""
    global binance_exchange
    if binance_exchange is None:
        try:
            with open("secure_keys/.binance_key", "r") as f:
                BINANCE_KEY = f.read().strip()
            with open("secure_keys/.binance_secret", "r") as f:
                BINANCE_SECRET = f.read().strip()
            
            binance_exchange = ccxt.binance({
                'apiKey': BINANCE_KEY,
                'secret': BINANCE_SECRET,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',
                    'warnOnFetchOpenOrdersWithoutSymbol': False
                }
            })
            return True
        except Exception as e:
            print(f"Binance init error: {e}")
            return False
    return True

def get_gemini_orders():
    """Get REAL Gemini orders and positions"""
    if not init_gemini():
        return {"error": "Gemini API not available", "orders": [], "positions": []}
    
    try:
        # Get balance
        balance = gemini_exchange.fetch_balance()
        cash = balance['free'].get('USD', 0)
        btc = balance['free'].get('BTC', 0)
        
        # Get current BTC price
        ticker = gemini_exchange.fetch_ticker('BTC/USD')
        btc_price = ticker['last']
        btc_value = btc * btc_price
        
        # Get open orders
        open_orders = gemini_exchange.fetch_open_orders('BTC/USD')
        
        # Get recent trades
        trades = gemini_exchange.fetch_my_trades('BTC/USD', limit=10)
        
        return {
            "balance": {
                "cash": cash,
                "btc": btc,
                "btc_price": btc_price,
                "btc_value": btc_value,
                "total": cash + btc_value
            },
            "open_orders": open_orders,
            "recent_trades": trades[-5:] if len(trades) > 5 else trades,  # Last 5 trades
            "error": None
        }
    except Exception as e:
        return {"error": str(e), "orders": [], "positions": []}

def get_binance_orders():
    """Get REAL Binance orders and positions"""
    if not init_binance():
        return {"error": "Binance API not available", "orders": [], "positions": []}
    
    try:
        # Get futures balance
        balance = binance_exchange.fetch_balance()
        total_usdt = balance['total'].get('USDT', 0)
        free_usdt = balance['free'].get('USDT', 0)
        used_usdt = balance['used'].get('USDT', 0)
        
        # Get open positions
        positions = binance_exchange.fetch_positions()
        open_positions = [p for p in positions if float(p['contracts']) > 0]
        
        # Get open orders for common symbols
        symbols_to_check = ['DOGE/USDT', 'ADA/USDT', 'DOT/USDT', 'SOL/USDT', 'ETH/USDT', 'XRP/USDT']
        all_orders = []
        for symbol in symbols_to_check:
            try:
                orders = binance_exchange.fetch_open_orders(symbol=symbol)
                all_orders.extend(orders)
            except:
                pass
        
        # Get recent trades
        recent_trades = []
        for symbol in symbols_to_check[:3]:  # Check first 3 symbols
            try:
                trades = binance_exchange.fetch_my_trades(symbol=symbol, limit=3)
                recent_trades.extend(trades)
            except:
                pass
        
        return {
            "balance": {
                "total_usdt": total_usdt,
                "free_usdt": free_usdt,
                "used_usdt": used_usdt
            },
            "open_positions": open_positions,
            "open_orders": all_orders,
            "recent_trades": recent_trades[:10],  # Last 10 trades max
            "error": None
        }
    except Exception as e:
        return {"error": str(e), "orders": [], "positions": []}

def get_active_bots():
    """Check which bots are actually running"""
    bots = []
    
    bot_checks = [
        {"name": "Gemini LONG Bot", "cmd": "fixed_trading_bot_with_safety"},
        {"name": "Binance SHORT Bot", "cmd": "binance_futures_with_safety"},
        {"name": "Trading Server", "cmd": "trading_server"},
        {"name": "Truth Dashboard", "cmd": "truth_dashboard"}
    ]
    
    import psutil
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            for bot in bot_checks:
                if bot["cmd"] in cmdline:
                    bots.append({
                        "name": bot["name"],
                        "pid": proc.info['pid'],
                        "status": "✅ RUNNING"
                    })
        except:
            continue
    
    return bots

@app.route('/')
def index():
    """Main dashboard page with REAL orders"""
    # Get REAL data from exchanges
    gemini_data = get_gemini_orders()
    binance_data = get_binance_orders()
    active_bots = get_active_bots()
    
    context = {
        "gemini_data": gemini_data,
        "binance_data": binance_data,
        "active_bots": active_bots,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return render_template_string(HTML_TEMPLATE, **context)

if __name__ == '__main__':
    print("🚀 TRUTH DASHBOARD starting on http://localhost:5003")
    print("🎯 This shows what's ACTUALLY happening (not simulated data)")
    app.run(host='0.0.0.0', port=5003, debug=False)