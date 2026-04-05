#!/usr/bin/env python3
"""
Dashboard showing trades with REAL-TIME current prices and P&L
Fetches live prices from exchanges
"""

from flask import Flask, render_template_string
import json
import os
import ccxt
from datetime import datetime
import time

app = Flask(__name__)

# Initialize exchanges
exchanges = {}

def init_exchanges():
    """Initialize exchange connections"""
    try:
        with open('secure_keys/binance_keys.json') as f:
            binance_keys = json.load(f)
        exchanges['binance'] = ccxt.binance({
            'apiKey': binance_keys['api_key'],
            'secret': binance_keys['api_secret']
        })
    except:
        exchanges['binance'] = None
    
    try:
        with open('secure_keys/gemini_keys.json') as f:
            gemini_keys = json.load(f)
        exchanges['gemini'] = ccxt.gemini({
            'apiKey': gemini_keys['api_key'],
            'secret': gemini_keys['api_secret']
        })
    except:
        exchanges['gemini'] = None

def fetch_current_price(exchange_name, symbol):
    """Fetch current price from exchange"""
    if exchange_name not in exchanges or exchanges[exchange_name] is None:
        return None
    
    exchange = exchanges[exchange_name]
    
    try:
        # Convert symbol format if needed
        # Binance uses /USDT, Gemini uses /USD
        if exchange_name == 'binance':
            if '/USD' in symbol and '/USDT' not in symbol:
                symbol = symbol.replace('/USD', '/USDT')
        elif exchange_name == 'gemini':
            if '/USDT' in symbol:
                symbol = symbol.replace('/USDT', '/USD')
        
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        print(f"❌ Error fetching {symbol} from {exchange_name}: {e}")
        return None

def update_trades_with_live_prices(trades):
    """Update trades with live prices and calculate P&L"""
    updated_trades = []
    
    for trade in trades:
        # Make a copy
        updated_trade = trade.copy()
        
        # Fetch current price
        current_price = fetch_current_price(trade['exchange'], trade['symbol'])
        
        if current_price is not None:
            updated_trade['current_price'] = current_price
            
            # Calculate P&L
            entry_price = trade['price']
            amount = trade['amount']
            
            if trade['side'] == 'buy':  # LONG position
                pnl = (current_price - entry_price) * amount
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                position_type = "LONG"
            else:  # SHORT position (sell)
                pnl = (entry_price - current_price) * amount
                pnl_percent = ((entry_price - current_price) / entry_price) * 100
                position_type = "SHORT"
            
            updated_trade['pnl'] = pnl
            updated_trade['pnl_percent'] = pnl_percent
            updated_trade['current_value'] = current_price * amount
            updated_trade['last_updated'] = datetime.now().isoformat()
            
            # Debug logging for shorts
            if trade['side'] == 'sell':
                print(f"✅ {trade['symbol']} SHORT: Entry ${entry_price:.4f}, Current ${current_price:.4f}, P&L ${pnl:+.4f}")
        else:
            # Keep old values if can't fetch price
            updated_trade['current_price'] = trade.get('current_price', trade['price'])
            updated_trade['pnl'] = trade.get('pnl', 0)
            updated_trade['pnl_percent'] = trade.get('pnl_percent', 0)
            updated_trade['current_value'] = trade.get('current_value', trade['value'])
            updated_trade['last_updated'] = trade.get('last_updated', datetime.now().isoformat())
            
            # Debug logging for failed fetches
            if trade['side'] == 'sell':
                print(f"⚠️ {trade['symbol']} SHORT: Failed to fetch price, using old value")
        
        updated_trades.append(updated_trade)
    
    return updated_trades

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Real-Time Trades Dashboard</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #0f0f23; color: #ccc; }
        .dashboard { max-width: 1400px; margin: 0 auto; }
        h1 { color: #00ff9d; }
        .summary { 
            background: #1a1a2e; 
            padding: 15px; 
            border-radius: 8px;
            margin: 20px 0;
            border: 1px solid #00ff9d;
        }
        table { 
            border-collapse: collapse; 
            width: 100%; 
            margin: 20px 0;
            font-size: 14px;
        }
        th, td { 
            border: 1px solid #2d2d4d; 
            padding: 8px; 
            text-align: right;
        }
        th { 
            background-color: #1a1a2e; 
            color: #00ff9d; 
            text-align: center;
            border-bottom: 2px solid #00ff9d;
        }
        tr:nth-child(even) { background-color: #1a1a2e; }
        tr:hover { background-color: #2d2d4d; }
        .positive { color: #00ff9d; font-weight: bold; }
        .negative { color: #ff0066; font-weight: bold; }
        .neutral { color: #666; }
        .exchange-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 5px;
        }
        .binance { background: #f0b90b; color: black; }
        .gemini { background: #00d2ff; color: black; }
        .last-updated {
            color: #666;
            font-size: 12px;
            margin-top: 20px;
            text-align: center;
        }
        .price-updating {
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>📈 Real-Time Trades Dashboard</h1>
        <p><strong>Live prices and P&L</strong> - Updated: {{ update_time }}</p>
        
        <div class="summary">
            <h2>📊 Trading Summary</h2>
            <p><strong>Total Trades:</strong> {{ total_trades }}</p>
            <p><strong>Total P&L:</strong> <span class="{{ 'positive' if total_pnl >= 0 else 'negative' }}">
                ${{ "%+.2f"|format(total_pnl) }}
            </span></p>
            <p><strong>Win Rate:</strong> {{ win_rate }}% ({{ winning_trades }}/{{ total_trades }} profitable)</p>
            <p><strong>Avg Trade Size:</strong> ${{ "%.2f"|format(avg_trade_size) }}</p>
            <p><strong>Exchange Status:</strong> 
                <span class="exchange-badge binance">BINANCE {{ '✅' if binance_ok else '❌' }}</span>
                <span class="exchange-badge gemini">GEMINI {{ '✅' if gemini_ok else '❌' }}</span>
            </p>
        </div>
        
        <h2>💱 Recent Trades <span class="price-updating">(Live Prices)</span></h2>
        <table>
            <tr>
                <th>Exchange</th>
                <th>Symbol</th>
                <th>Type</th>
                <th>Side</th>
                <th>Entry Price</th>
                <th>Current Price</th>
                <th>P&L</th>
                <th>P&L %</th>
                <th>Amount</th>
                <th>Value</th>
                <th>Time</th>
            </tr>
            
            {# Gemini LONG Positions #}
            {% if gemini_trades %}
            <tr style="background-color: rgba(0, 210, 255, 0.1);">
                <td colspan="11" style="text-align: center; font-weight: bold; color: #00d2ff;">
                    🔵 GEMINI LONG POSITIONS
                </td>
            </tr>
            {% for trade in gemini_trades %}
            <tr>
                <td>
                    <span class="exchange-badge gemini">
                        {{ trade.exchange|upper }}
                    </span>
                </td>
                <td><strong>{{ trade.symbol }}</strong></td>
                <td>{{ trade.type if trade.type else 'SPOT' }}</td>
                <td>{{ trade.side|upper }}</td>
                <td>${{ "%.4f"|format(trade.price) }}</td>
                <td class="price-updating">${{ "%.4f"|format(trade.current_price) }}</td>
                <td class="{{ 'positive' if trade.pnl > 0 else 'negative' if trade.pnl < 0 else 'neutral' }}">
                    ${{ "%+.4f"|format(trade.pnl) }}
                </td>
                <td class="{{ 'positive' if trade.pnl_percent > 0 else 'negative' if trade.pnl_percent < 0 else 'neutral' }}">
                    {{ "%+.2f"|format(trade.pnl_percent) }}%
                </td>
                <td>{{ "%.6f"|format(trade.amount) }}</td>
                <td>${{ "%.2f"|format(trade.value) }}</td>
                <td>{{ trade.timestamp[:19].replace('T', ' ') }}</td>
            </tr>
            {% endfor %}
            {# Gemini Total #}
            <tr style="background-color: rgba(0, 210, 255, 0.15); border-top: 2px solid #00d2ff;">
                <td colspan="6" style="text-align: right; font-weight: bold; color: #00d2ff;">
                    🔵 GEMINI TOTAL:
                </td>
                <td style="font-weight: bold;" class="{{ 'positive' if gemini_total_pnl >= 0 else 'negative' }}">
                    ${{ "%+.2f"|format(gemini_total_pnl) }}
                </td>
                <td style="font-weight: bold;" class="{{ 'positive' if gemini_total_pnl >= 0 else 'negative' }}">
                    {{ "%+.2f"|format(gemini_total_pnl_percent) }}%
                </td>
                <td style="font-weight: bold;">{{ gemini_trades|length }} trades</td>
                <td style="font-weight: bold; color: #00d2ff;">${{ "%.2f"|format(gemini_total_value) }}</td>
                <td></td>
            </tr>
            {% endif %}
            
            {# Binance SHORT Positions #}
            {% if binance_trades %}
            <tr style="background-color: rgba(240, 185, 11, 0.1);">
                <td colspan="11" style="text-align: center; font-weight: bold; color: #f0b90b;">
                    🟡 BINANCE SHORT POSITIONS
                </td>
            </tr>
            {% for trade in binance_trades %}
            <tr>
                <td>
                    <span class="exchange-badge binance">
                        {{ trade.exchange|upper }}
                    </span>
                </td>
                <td><strong>{{ trade.symbol }}</strong></td>
                <td>{{ trade.type if trade.type else 'SPOT' }}</td>
                <td>{{ trade.side|upper }}</td>
                <td>${{ "%.4f"|format(trade.price) }}</td>
                <td class="price-updating">${{ "%.4f"|format(trade.current_price) }}</td>
                <td class="{{ 'positive' if trade.pnl > 0 else 'negative' if trade.pnl < 0 else 'neutral' }}">
                    ${{ "%+.4f"|format(trade.pnl) }}
                </td>
                <td class="{{ 'positive' if trade.pnl_percent > 0 else 'negative' if trade.pnl_percent < 0 else 'neutral' }}">
                    {{ "%+.2f"|format(trade.pnl_percent) }}%
                </td>
                <td>{{ "%.6f"|format(trade.amount) }}</td>
                <td>${{ "%.2f"|format(trade.value) }}</td>
                <td>{{ trade.timestamp[:19].replace('T', ' ') }}</td>
            </tr>
            {% endfor %}
            {# Binance Total #}
            <tr style="background-color: rgba(240, 185, 11, 0.15); border-top: 2px solid #f0b90b;">
                <td colspan="6" style="text-align: right; font-weight: bold; color: #f0b90b;">
                    🟡 BINANCE TOTAL:
                </td>
                <td style="font-weight: bold;" class="{{ 'positive' if binance_total_pnl >= 0 else 'negative' }}">
                    ${{ "%+.2f"|format(binance_total_pnl) }}
                </td>
                <td style="font-weight: bold;" class="{{ 'positive' if binance_total_pnl >= 0 else 'negative' }}">
                    {{ "%+.2f"|format(binance_total_pnl_percent) }}%
                </td>
                <td style="font-weight: bold;">{{ binance_trades|length }} trades</td>
                <td style="font-weight: bold; color: #f0b90b;">${{ "%.2f"|format(binance_total_value) }}</td>
                <td></td>
            </tr>
            {% endif %}
        </table>
        
        <div class="last-updated">
            <p>🔁 Auto-refreshing every 30 seconds</p>
            <p>Last price update: {{ price_update_time }}</p>
            <p>Prices fetched directly from exchanges</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def trades_dashboard():
    try:
        # Initialize exchanges
        init_exchanges()
        
        # Load trades
        with open('trading_data/trades.json', 'r') as f:
            trades = json.load(f)
        
        # Update with live prices
        updated_trades = update_trades_with_live_prices(trades)
        
        # Calculate summary statistics
        total_trades = len(updated_trades)
        total_pnl = sum(t.get('pnl', 0) for t in updated_trades)
        winning_trades = sum(1 for t in updated_trades if t.get('pnl', 0) > 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        avg_trade_size = sum(t.get('value', 0) for t in updated_trades) / total_trades if total_trades > 0 else 0
        
        # Add trade type
        for trade in updated_trades:
            trade['type'] = 'SHORT' if trade['side'] == 'sell' else 'LONG'
        
        # Check exchange status
        binance_ok = exchanges.get('binance') is not None
        gemini_ok = exchanges.get('gemini') is not None
        
        # Calculate exchange-specific totals
        gemini_trades = [t for t in updated_trades if t.get('exchange') == 'gemini']
        binance_trades = [t for t in updated_trades if t.get('exchange') == 'binance']
        
        gemini_total_value = sum(t.get('value', 0) for t in gemini_trades)
        binance_total_value = sum(t.get('value', 0) for t in binance_trades)
        gemini_total_pnl = sum(t.get('pnl', 0) for t in gemini_trades)
        binance_total_pnl = sum(t.get('pnl', 0) for t in binance_trades)
        
        # Calculate P&L percentages
        gemini_total_pnl_percent = (gemini_total_pnl / gemini_total_value * 100) if gemini_total_value > 0 else 0
        binance_total_pnl_percent = (binance_total_pnl / binance_total_value * 100) if binance_total_value > 0 else 0
        
        # Prepare template data
        data = {
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'price_update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'trades': updated_trades,
            'total_trades': total_trades,
            'total_pnl': total_pnl,
            'winning_trades': winning_trades,
            'win_rate': round(win_rate, 1),
            'avg_trade_size': avg_trade_size,
            'binance_ok': binance_ok,
            'gemini_ok': gemini_ok,
            'gemini_trades': gemini_trades,
            'binance_trades': binance_trades,
            'gemini_total_value': gemini_total_value,
            'binance_total_value': binance_total_value,
            'gemini_total_pnl': gemini_total_pnl,
            'binance_total_pnl': binance_total_pnl,
            'gemini_total_pnl_percent': gemini_total_pnl_percent,
            'binance_total_pnl_percent': binance_total_pnl_percent
        }
        
        return render_template_string(HTML_TEMPLATE, **data)
        
    except Exception as e:
        return f"Error loading trades dashboard: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=False)