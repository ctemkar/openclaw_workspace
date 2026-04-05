#!/usr/bin/env python3
"""
Dashboard Server for Next-Gen Trading System
Serves the main dashboard on port 8080
"""

import http.server
import socketserver
import os
import json
from datetime import datetime

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for dashboard"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        # Serve index.html for root
        if self.path == '/':
            self.path = '/index.html'
        
        # Serve next_gen_dashboard.html directly
        if self.path == '/dashboard':
            self.path = '/next_gen_dashboard.html'
        
        # Serve JSON data
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "trading_status": "PAUSED",
                "balance": 28.47,
                "min_required": 28.50,
                "total_profit": -0.12,
                "total_trades": 10,
                "win_rate": 0.0,
                "active_bots": 0,
                "dashboards": {
                    "gateway": {"port": 5001, "status": "online"},
                    "dashboard_5024": {"port": 5024, "status": "online"},
                    "dashboard_5025": {"port": 5025, "status": "online"},
                    "dashboard_5026": {"port": 5026, "status": "online"}
                },
                "next_gen_analysis": {
                    "XTZ": {
                        "spread": 3.90,
                        "quantitative": "AVOID",
                        "qualitative": "TRADE",
                        "cio_ai": "WAIT",
                        "net_profit": -3.83
                    },
                    "YFI": {
                        "spread": 1.48,
                        "quantitative": "AVOID",
                        "qualitative": "AVOID",
                        "cio_ai": "SKIP",
                        "net_profit": -7.56
                    }
                }
            }
            
            self.wfile.write(json.dumps(status_data, indent=2).encode())
            return
        
        return super().do_GET()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def main():
    """Start the dashboard server"""
    print(f"\n{'='*60}")
    print("🚀 NEXT-GEN TRADING SYSTEM DASHBOARD")
    print("="*60)
    print(f"📊 Serving dashboard on: http://localhost:{PORT}")
    print(f"📁 Directory: {DIRECTORY}")
    print("="*60)
    print("\n📋 Available Pages:")
    print("  • http://localhost:8080/          - Main Dashboard Hub")
    print("  • http://localhost:8080/dashboard - Next-Gen Dashboard")
    print("  • http://localhost:8080/api/status - JSON Status API")
    print("\n🔗 Other Dashboards:")
    print("  • http://localhost:5001 - Gateway Dashboard")
    print("  • http://localhost:5024 - Trading Dashboard")
    print("  • http://localhost:5025 - Market Dashboard")
    print("  • http://localhost:5026 - AI Dashboard")
    print("\n📄 Reports:")
    print("  • http://localhost:8080/next_gen_analysis.json")
    print("  • http://localhost:8080/next_gen_trading_results.json")
    print("  • http://localhost:8080/HEARTBEAT.md")
    print("="*60)
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard server stopped")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"\n❌ Port {PORT} is already in use!")
            print("Try: kill -9 $(lsof -ti:8080)")
        else:
            raise

if __name__ == "__main__":
    main()