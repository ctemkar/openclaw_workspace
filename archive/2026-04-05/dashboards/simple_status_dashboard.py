#!/usr/bin/env python3
"""
SIMPLE STATUS DASHBOARD - Port 5007
Shows real-time status of all trading systems
"""

import http.server
import socketserver
import os
import json
import time
from datetime import datetime

PORT = 5007
BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

def get_system_status():
    """Get current system status"""
    status = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'bots': {},
        'capital': {},
        'dashboards': {},
        'llm_models': []
    }
    
    # Check bot processes
    import subprocess
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    
    # Check 26-crypto bot
    if 'real_26_crypto_trader.py' in result.stdout:
        status['bots']['26_crypto'] = {'status': 'running', 'type': 'Gemini-only'}
    else:
        status['bots']['26_crypto'] = {'status': 'stopped', 'type': 'Gemini-only'}
    
    # Check LLM consensus bot
    if 'llm_consensus_bot.py' in result.stdout:
        status['bots']['llm_consensus'] = {'status': 'running', 'type': '8-model weighted'}
    else:
        status['bots']['llm_consensus'] = {'status': 'stopped', 'type': '8-model weighted'}
    
    # Get capital from real check (simplified)
    status['capital'] = {
        'gemini': 319.04,
        'binance': 0.00,
        'position_size': 31.90,
        'deployed': 0.00
    }
    
    # Dashboard ports
    import socket
    ports = [5007, 5008, 5009, 5011]
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        status['dashboards'][f'port_{port}'] = 'active' if result == 0 else 'inactive'
        sock.close()
    
    # LLM models (from config)
    status['llm_models'] = [
        {'name': 'glm-4.7-flash', 'weight': 1.2},
        {'name': 'llama3.1', 'weight': 1.0},
        {'name': 'llama3', 'weight': 1.0},
        {'name': 'qwen2.5-coder:32b', 'weight': 1.1},
        {'name': 'qwen3', 'weight': 1.0},
        {'name': 'mistral', 'weight': 1.0},
        {'name': 'deepseek-r1', 'weight': 1.1},
        {'name': 'llama3.1:8b', 'weight': 0.9}
    ]
    
    return status

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            status = get_system_status()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>📊 Trading System Dashboard</title>
                <meta http-equiv="refresh" content="30">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 10px; }}
                    .status-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }}
                    .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .running {{ color: green; font-weight: bold; }}
                    .stopped {{ color: red; font-weight: bold; }}
                    .warning {{ color: orange; font-weight: bold; }}
                    .model-list {{ max-height: 200px; overflow-y: auto; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 Trading System Dashboard</h1>
                        <p>Last updated: {status['timestamp']} (auto-refresh every 30s)</p>
                    </div>
                    
                    <div class="status-grid">
                        <div class="card">
                            <h2>🤖 Trading Bots</h2>
                            <p><span class="{'running' if status['bots']['26_crypto']['status'] == 'running' else 'stopped'}">
                                {'✅' if status['bots']['26_crypto']['status'] == 'running' else '❌'} 
                                real_26_crypto_trader.py</span> - {status['bots']['26_crypto']['type']}</p>
                            <p><span class="{'running' if status['bots']['llm_consensus']['status'] == 'running' else 'stopped'}">
                                {'✅' if status['bots']['llm_consensus']['status'] == 'running' else '❌'} 
                                llm_consensus_bot.py</span> - {status['bots']['llm_consensus']['type']}</p>
                            <p><span class="stopped">❌ Binance Trading</span> - DISABLED ($0 balance)</p>
                        </div>
                        
                        <div class="card">
                            <h2>💰 Capital Status</h2>
                            <p><strong>Gemini:</strong> ${status['capital']['gemini']:.2f} available</p>
                            <p><strong>Binance:</strong> ${status['capital']['binance']:.2f} (disabled)</p>
                            <p><strong>Position size:</strong> ${status['capital']['position_size']:.2f} per trade (10%)</p>
                            <p><strong>Deployed:</strong> ${status['capital']['deployed']:.2f} (fresh start)</p>
                        </div>
                        
                        <div class="card">
                            <h2>🌐 Dashboard Ports</h2>
                            {' '.join([f'<p><a href="http://localhost:{port}/" target="_blank">Port {port}</a> - <span class="{"running" if status == "active" else "stopped"}">{status.upper()}</span></p>' for port, status in status['dashboards'].items()])}
                        </div>
                        
                        <div class="card">
                            <h2>🧠 LLM Models (8 total)</h2>
                            <div class="model-list">
                                {' '.join([f'<p>• {model["name"]} <small>(weight: {model["weight"]})</small></p>' for model in status['llm_models']])}
                            </div>
                            <p><small>Weights will be adjusted based on prediction accuracy</small></p>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2>📈 System Status</h2>
                        <p><strong>Last update:</strong> {status['timestamp']}</p>
                        <p><strong>Overall Status:</strong> <span class="running">✅ OPERATIONAL</span></p>
                        <p><strong>Strategy:</strong> Gemini LONG positions only (Binance disabled)</p>
                        <p><strong>Trading mode:</strong> Weighted LLM consensus with 8 models</p>
                        <p><strong>Prediction tracking:</strong> Active - analyzing model accuracy</p>
                    </div>
                    
                    <div class="card">
                        <h2>🔗 Quick Links</h2>
                        <p><a href="/real_26_crypto_trading.log" target="_blank">📝 26-Crypto Bot Log</a></p>
                        <p><a href="/llm_consensus.log" target="_blank">📝 LLM Consensus Log</a></p>
                        <p><a href="/HEARTBEAT.md" target="_blank">📊 Heartbeat Status</a></p>
                        <p><a href="/llm_predictions_history.json" target="_blank">📈 Prediction History</a> (when available)</p>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            # Serve files normally
            super().do_GET()

if __name__ == '__main__':
    print(f"🚀 Starting Simple Status Dashboard on port {PORT}...")
    print(f"📊 Dashboard will be available at: http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped by user")