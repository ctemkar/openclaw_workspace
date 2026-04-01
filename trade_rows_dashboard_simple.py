import http.server
import socketserver
import json
import os
from datetime import datetime

PORT = 5013  # Using 5013 to avoid conflicts

class TradeRowsHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Read trade data
            trades = []
            try:
                with open('26_crypto_trade_history.json', 'r') as f:
                    trades = json.load(f)
            except Exception as e:
                trades = [{"error": str(e)}]
            
            # Create simple HTML with rows
            html = '''<!DOCTYPE html>
<html>
<head>
    <title>📊 TRADE ROWS - SIMPLE</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {
            font-family: monospace;
            margin: 20px;
            background: #000;
            color: #0f0;
        }
        h1 {
            color: #0f0;
            text-align: center;
        }
        .info {
            text-align: center;
            color: #666;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th {
            background: #111;
            color: #0f0;
            padding: 10px;
            text-align: left;
            border-bottom: 2px solid #0f0;
        }
        td {
            padding: 8px 10px;
            border-bottom: 1px solid #333;
        }
        tr:hover {
            background: #111;
        }
        .positive {
            color: #0f0;
        }
        .negative {
            color: #f00;
        }
        .gemini {
            color: #00d4ff;
        }
        .binance {
            color: #f0b90b;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <h1>📊 TRADE ROWS DASHBOARD</h1>
    <div class="info">Port ''' + str(PORT) + ''' • Simple view • Auto-refresh 30s</div>
    
    <table>
        <thead>
            <tr>
                <th>Symbol</th>
                <th>Exchange</th>
                <th>Side</th>
                <th>Entry</th>
                <th>Current</th>
                <th>Size</th>
                <th>P&L</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>'''
            
            # Add trade rows
            row_count = 0
            for trade in trades:
                if not isinstance(trade, dict):
                    continue
                    
                symbol = trade.get('symbol', 'N/A')
                exchange = trade.get('exchange', 'unknown').lower()
                side = trade.get('side', 'buy').lower()
                entry_price = float(trade.get('entry_price', 0))
                current_price = float(trade.get('current_price', entry_price))
                size = float(trade.get('position_size', trade.get('amount', 0)))
                pnl = float(trade.get('unrealized_pnl', 0))
                status = trade.get('status', 'open')
                
                # Determine classes
                exchange_class = 'gemini' if 'gemini' in exchange else 'binance'
                pnl_class = 'positive' if pnl >= 0 else 'negative'
                
                html += f'''
            <tr>
                <td><strong>{symbol}</strong></td>
                <td class="{exchange_class}">{exchange.upper()}</td>
                <td><strong>{side.upper()}</strong></td>
                <td>${entry_price:.4f}</td>
                <td>${current_price:.4f}</td>
                <td>${size:.2f}</td>
                <td class="{pnl_class}">${pnl:+.2f}</td>
                <td>{status}</td>
            </tr>'''
                
                row_count += 1
                if row_count >= 30:  # Limit to 30 rows
                    break
            
            if row_count == 0:
                html += '''
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px; color: #666;">
                    No trade data found.
                </td>
            </tr>'''
            
            html += f'''
        </tbody>
    </table>
    
    <div class="footer">
        <p>Showing {row_count} trades • Last update: {datetime.now().strftime("%H:%M:%S")}</p>
        <p>Port {PORT} • Trade Rows Dashboard</p>
    </div>
</body>
</html>'''
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            super().do_GET()

print(f"🚀 Starting Simple Trade Rows Dashboard on port {PORT}")
print(f"📊 Open: http://localhost:{PORT}")
print("🔄 Auto-refresh every 30 seconds")
print("📋 Showing trade rows in simple format")

with socketserver.TCPServer(("", PORT), TradeRowsHandler) as httpd:
    httpd.serve_forever()