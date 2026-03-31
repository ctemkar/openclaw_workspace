#!/usr/bin/env python3
"""
COMMON DASHBOARD - Uses common data layer
Single dashboard for all reporting
"""

from flask import Flask, jsonify
import trading_data
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Main dashboard using COMMON DATA LAYER"""
    
    # Get ALL data from common layer
    data = trading_data.TradingData.get_dashboard_data()
    
    # Auto-refresh JavaScript
    refresh_js = """
    <script>
        // Auto-refresh every 10 seconds
        setTimeout(() => location.reload(), 10000);
        
        // Update time every second
        function updateTime() {
            const now = new Date();
            document.getElementById('current-time').textContent = 
                now.toLocaleString('en-US', { 
                    timeZone: 'Asia/Bangkok',
                    year: 'numeric', 
                    month: '2-digit', 
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
        }
        setInterval(updateTime, 1000);
        updateTime();
        
        // Manual refresh
        function manualRefresh() {
            location.reload();
        }
    </script>
    """
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>🚀 COMMON DASHBOARD - Single Source of Truth</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: monospace;
            margin: 20px;
            background: #000;
            color: #0f0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            border: 1px solid #0f0;
            padding: 20px;
        }}
        .urgent {{
            color: #f00;
            animation: blink 1s infinite;
        }}
        @keyframes blink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #0f0;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background: #002200;
        }}
        .positive {{ color: #0f0; }}
        .negative {{ color: #f00; }}
        .timestamp {{ color: #888; font-size: 0.8em; }}
        .refresh-info {{ color: #0af; font-size: 0.9em; margin: 10px 0; }}
        button {{
            background: #3b82f6;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin: 5px;
        }}
        .data-source {{
            color: #aaa;
            font-size: 0.8em;
            margin-top: 20px;
            border-top: 1px solid #333;
            padding-top: 10px;
        }}
        .common-badge {{
            background: #10b981;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.7em;
            margin-left: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 COMMON DASHBOARD <span class="common-badge">SINGLE SOURCE</span></h1>
        <div class="refresh-info">
            ⏰ <span id="current-time">Loading...</span> (Bangkok) |
            🔄 Auto-refresh: 10s |
            <button onclick="manualRefresh()">🔄 REFRESH NOW</button>
        </div>
        <p class="urgent">✅ USING COMMON DATA LAYER - All components synchronized</p>
        
        <h2>📊 CURRENT POSITIONS <span class="common-badge">{len(data['positions'])} open</span></h2>
        <div class="positive">
            <p>✅ <strong>CURRENT STRATEGY:</strong> Trading only on ♊ GEMINI</p>
            <p>• Using Binance price data to detect 0.5%+ dips</p>
            <p>• Executing LONG buys on Gemini when dips detected</p>
        </div>
"""
    
    # Positions table
    if data['positions']:
        html += """
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
"""
        
        total_value = 0
        total_pnl = 0
        
        for pos in data['positions']:
            # Calculate P&L using common data layer
            pnl_data = trading_data.TradingData.calculate_position_pnl(pos)
            
            pnl = pnl_data.get('pnl', 0)
            pnl_percent = pnl_data.get('pnl_percent', 0)
            current_price = pnl_data.get('current_price', pos.get('price', 0))
            current_value = pnl_data.get('value', pos.get('value', 0))
            
            total_value += current_value
            total_pnl += pnl
            
            # Determine trade type
            side = pos.get('side', 'buy')
            trade_type = "LONG" if side == 'buy' else "SHORT"
            
            # Get exchange with emoji
            exchange = pos.get('exchange', 'unknown')
            exchange_emoji = "♊" if exchange == 'gemini' else "₿" if exchange == 'binance' else "❓"
            exchange_display = f"{exchange_emoji} {exchange.upper()}"
            
            entry_price = pos.get('price', 0)
            
            # Determine P&L class
            pnl_class = "positive" if pnl >= 0 else "negative"
            pnl_display = f"${pnl:+.2f}" if pnl != 0 else "$0.00"
            pnl_percent_display = f"{pnl_percent:+.2f}%" if pnl_percent != 0 else "0.00%"
            
            # Determine side class
            side_class = "positive" if side == 'buy' else "negative"
            side_display = "BUY" if side == 'buy' else "SELL"
            
            html += f"""
            <tr>
                <td><strong>{exchange_display}</strong></td>
                <td>{pos.get('symbol', 'N/A')}</td>
                <td><strong>{trade_type}</strong></td>
                <td class="{side_class}">{side_display}</td>
                <td>${entry_price:.4f}</td>
                <td>${current_price:.4f}</td>
                <td class="{pnl_class}">{pnl_display}</td>
                <td class="{pnl_class}">{pnl_percent_display}</td>
                <td>{pos.get('amount', 0):.6f}</td>
                <td>${current_value:.2f}</td>
                <td>{pos.get('timestamp', '')[:19].replace('T', ' ')}</td>
            </tr>
"""
        
        html += f"""
        </table>
        
        <h3>📈 EXCHANGE SUMMARY</h3>
        <table>
            <tr>
                <th>Exchange</th>
                <th>Positions</th>
                <th>Total Value</th>
                <th>Total P&L</th>
                <th>Avg P&L %</th>
                <th>Strategy</th>
            </tr>
"""
        
        # Calculate exchange summaries
        exchange_summary = {}
        for pos in data['positions']:
            exchange = pos.get('exchange', 'unknown')
            if exchange not in exchange_summary:
                exchange_summary[exchange] = {
                    'count': 0,
                    'total_value': 0,
                    'total_pnl': 0,
                    'total_pnl_percent': 0
                }
            
            pnl_data = trading_data.TradingData.calculate_position_pnl(pos)
            exchange_summary[exchange]['count'] += 1
            exchange_summary[exchange]['total_value'] += pnl_data.get('value', 0)
            exchange_summary[exchange]['total_pnl'] += pnl_data.get('pnl', 0)
            exchange_summary[exchange]['total_pnl_percent'] += pnl_data.get('pnl_percent', 0)
        
        for exchange, stats in exchange_summary.items():
            exchange_emoji = "♊" if exchange == 'gemini' else "₿" if exchange == 'binance' else "❓"
            exchange_display = f"{exchange_emoji} {exchange.upper()}"
            
            avg_pnl_percent = stats['total_pnl_percent'] / stats['count'] if stats['count'] > 0 else 0
            strategy = "ACTIVE: LONG (buy 0.5%+ dips)" if exchange == 'gemini' else "INACTIVE: Old migrated positions" if exchange == 'binance' else "Unknown"
            
            pnl_class = "positive" if stats['total_pnl'] >= 0 else "negative"
            
            html += f"""
            <tr>
                <td><strong>{exchange_display}</strong></td>
                <td>{stats['count']}</td>
                <td>${stats['total_value']:.2f}</td>
                <td class="{pnl_class}">${stats['total_pnl']:+.2f}</td>
                <td class="{pnl_class}">{avg_pnl_percent:+.2f}%</td>
                <td>{strategy}</td>
            </tr>
"""
        
        html += f"""
        </table>
        
        <p><strong>📊 TOTAL: {len(data['positions'])} positions | ${total_value:.2f} value | ${total_pnl:+.2f} P&L</strong></p>
        
        <div class="timestamp">
            <p>📝 <strong>Legend:</strong></p>
            <p>• ♊ <strong>GEMINI (ACTIVE)</strong>: Spot trading - Buys LONG on 0.5%+ dips detected via Binance price data</p>
            <p>• ₿ <strong>BINANCE (INACTIVE)</strong>: Futures trading - SHORT positions shown are OLD migrated positions</p>
            <p>• <strong>Current strategy:</strong> Only Gemini is active, using Binance for price signals</p>
            <p>• BUY = LONG (expect price to go up) | SELL = SHORT (expect price to go down)</p>
            <p>• P&L: Real-time calculation from current market prices</p>
            <p>• Prices update on every dashboard refresh (every 10 seconds)</p>
        </div>
"""
        
        html += f"""
        </table>
        <p><strong>Total positions value: ${total_value:.2f}</strong></p>
"""
    else:
        html += "<p>No open positions</p>"
    
    # Capital summary
    capital = data['capital']
    html += f"""
        <h2>💰 CAPITAL SUMMARY <span class="common-badge">auto-calculated</span></h2>
        <table>
            <tr><td>Total Capital</td><td>${capital.get('total_capital', 0):.2f}</td></tr>
            <tr><td>Gemini Capital</td><td>${capital.get('gemini_total', 0):.2f}</td></tr>
            <tr><td>Binance Capital</td><td>${capital.get('binance_total', 0):.2f}</td></tr>
            <tr><td>Deployed</td><td>${capital.get('deployed', 0):.2f}</td></tr>
            <tr><td>Available (Gemini)</td><td>${capital.get('available_gemini', 0):.2f}</td></tr>
            <tr><td>Open Positions</td><td>{capital.get('position_count', 0)}</td></tr>
            <tr><td>Avg Position Size</td><td>${capital.get('avg_position_value', 0):.2f}</td></tr>
            <tr><td>Last Updated</td><td>{capital.get('last_updated', '')[:19].replace('T', ' ')}</td></tr>
        </table>
"""
    
    # Bot status
    bot = data['bot_status']
    html += f"""
        <h2>⚡ BOT STATUS <span class="common-badge">live</span></h2>
        <table>
            <tr><td>Status</td><td>{bot.get('status', 'unknown').upper()}</td></tr>
            <tr><td>Strategy</td><td>{bot.get('strategy', 'Unknown')}</td></tr>
            <tr><td>Scan Interval</td><td>{bot.get('scan_interval', 0)} seconds</td></tr>
            <tr><td>Last Activity</td><td>{bot.get('last_activity', 'None')}</td></tr>
            <tr><td>Last Updated</td><td>{bot.get('last_updated', '')[:19].replace('T', ' ')}</td></tr>
        </table>
"""
    
    # Recent trades
    html += f"""
        <h2>📈 RECENT TRADES <span class="common-badge">{len(data['recent_trades'])} total</span></h2>
        <p>Last {len(data['recent_trades'])} trades from common data layer</p>
"""
    
    # Metadata
    meta = data['metadata']
    html += f"""
        <div class="data-source">
            <h3>🔧 SYSTEM ARCHITECTURE:</h3>
            <p>• <strong>Common Data Layer:</strong> Single source of truth for all data</p>
            <p>• <strong>Bot:</strong> Saves trades to common layer</p>
            <p>• <strong>Dashboard:</strong> Reads from common layer</p>
            <p>• <strong>Auto-sync:</strong> Capital calculated automatically from trades</p>
            <p>• <strong>Data Source:</strong> {meta.get('data_source', 'Unknown')}</p>
            <p>• <strong>Generated:</strong> {meta.get('generated_at', 'Unknown')}</p>
            <p>• <strong>Version:</strong> {meta.get('version', '1.0')}</p>
        </div>
        
        <p class="urgent">✅ ALL COMPONENTS USE COMMON DATA - NO STALE DATA</p>
        <button onclick="manualRefresh()">🔄 FORCE REFRESH</button>
    </div>
    {refresh_js}
</body>
</html>
"""
    
    return html

@app.route('/api/data')
def api_data():
    """JSON API endpoint using common data layer"""
    return jsonify(trading_data.TradingData.get_dashboard_data())

@app.route('/api/trades')
def api_trades():
    """Trades API"""
    return jsonify(trading_data.TradingData.get_trades())

@app.route('/api/capital')
def api_capital():
    """Capital API"""
    return jsonify(trading_data.TradingData.get_capital())

@app.route('/api/status')
def api_status():
    """Status API"""
    return jsonify(trading_data.TradingData.get_bot_status())

if __name__ == '__main__':
    print("🚀 STARTING COMMON DASHBOARD ON PORT 5007")
    print("✅ Uses common data layer - single source of truth")
    print("✅ All components synchronized")
    print("✅ Open: http://localhost:5007/")
    print("✅ API endpoints: /api/data, /api/trades, /api/capital, /api/status")
    app.run(host='0.0.0.0', port=5007, debug=False)