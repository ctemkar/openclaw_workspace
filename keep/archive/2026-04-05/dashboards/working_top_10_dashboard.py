#!/usr/bin/env python3
"""
WORKING TOP 10 DASHBOARD - Simple, reliable, shows actual data
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import re
from datetime import datetime
import time

PORT = 5027  # New port that definitely works
LOG_FILE = "real_26_crypto_arbitrage.log"

def get_latest_spreads():
    """Get latest top 10 spreads - SIMPLE VERSION"""
    try:
        if not os.path.exists(LOG_FILE):
            return "No arbitrage log file found"
        
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
        
        # Find the most recent TOP 10 section
        for i in range(len(lines)-1, -1, -1):
            if "TOP 10 CRYPTO SPREADS" in lines[i]:
                # Collect next 15 lines
                result = []
                for j in range(i, min(i+20, len(lines))):
                    result.append(lines[j])
                return ''.join(result)
        
        return "No TOP 10 data found in log"
    except Exception as e:
        return f"Error reading log: {e}"

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            spreads = get_latest_spreads()
            
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>✅ WORKING Top 10 Spreads Dashboard</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="30">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #0f172a; color: white; }}
        .header {{ background: #1e40af; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        h1 {{ margin: 0; }}
        .subtitle {{ color: #cbd5e1; margin: 10px 0; }}
        .content {{ background: #1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155; }}
        pre {{ 
            background: #0f172a; 
            padding: 20px; 
            border-radius: 5px; 
            border: 1px solid #334155;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
        }}
        .positive {{ color: #10b981; }}
        .negative {{ color: #ef4444; }}
        .tradable {{ color: #fbbf24; font-weight: bold; }}
        .footer {{ text-align: center; margin-top: 20px; color: #64748b; font-size: 0.9em; }}
        .status {{ 
            display: inline-block; 
            padding: 5px 10px; 
            border-radius: 5px; 
            margin-bottom: 10px;
            background: #10b981;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>✅ WORKING Top 10 Spreads Dashboard</h1>
        <div class="subtitle">Actual data from arbitrage bot - Auto-refreshes every 30 seconds</div>
        <div class="status">🟢 ONLINE - Port 5027</div>
    </div>
    
    <div class="content">
        <h2>📊 Latest Top 10 Crypto Spreads (Binance ↔ Gemini)</h2>
        <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <pre>{spreads}</pre>
        
        <h3>💡 How to read:</h3>
        <ul>
            <li><span class="negative">Negative spread</span> = Binance price < Gemini price (Buy Binance, Sell Gemini)</li>
            <li><span class="positive">Positive spread</span> = Binance price > Gemini price (Buy Gemini, Sell Binance)</li>
            <li><span class="tradable">Spread ≥ 0.5%</span> = Tradable opportunity</li>
            <li>Profit/$100 = Profit per $100 traded</li>
        </ul>
    </div>
    
    <div class="footer">
        <p>Dashboard running on port 5027 | Data source: {LOG_FILE}</p>
        <p>Next auto-refresh in 30 seconds | Last scan: {datetime.now().strftime('%H:%M:%S')}</p>
    </div>
</body>
</html>"""
            
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 - Not Found')

def run_server():
    print(f"🚀 Starting WORKING Top 10 Dashboard on port {PORT}...")
    print(f"   URL: http://localhost:{PORT}")
    print(f"   Data source: {LOG_FILE}")
    print(f"   Auto-refresh: Every 30 seconds")
    print("\nPress Ctrl+C to stop")
    
    server = HTTPServer(('0.0.0.0', PORT), SimpleHandler)
    server.serve_forever()

if __name__ == '__main__':
    run_server()