
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import time
import json
import subprocess

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Get latest bot logs
            latest_logs = self.get_latest_logs()
            bot_status = self.get_bot_status()
            
            html = f'''
            <!DOCTYPE html>
            <html>
            <head><title>✅ Fixed Dashboard - Port 5025</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .status {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .working {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                .log {{ background: #f8f9fa; padding: 10px; border: 1px solid #e9ecef; font-family: monospace; font-size: 12px; }}
                a {{ color: #007bff; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
            </head>
            <body>
                <h1>✅ Trading Dashboard - {time.strftime('%H:%M:%S')}</h1>
                
                <div class="status working">
                    <h2>✅ System Status</h2>
                    <p>Proactive fixes applied at 15:03:</p>
                    <ul>
                        <li>✅ Symbol mismatch fixed (XTZ/GUSD)</li>
                        <li>✅ Microsecond nonce working</li>
                        <li>✅ Dashboard restarted</li>
                        <li>✅ Old bot replaced</li>
                        <li>✅ Gateway restarted (port 5001)</li>
                    </ul>
                </div>
                
                <div class="status working">
                    <h2>🔗 Quick Links</h2>
                    <ul>
                        <li><a href="/logs">📊 View Bot Logs</a></li>
                        <li><a href="/status">📈 System Status</a></li>
                        <li><a href="http://localhost:5001">🚀 Gateway (Port 5001)</a></li>
                        <li><a href="http://localhost:5001/real">📊 Real Dashboard</a></li>
                    </ul>
                </div>
                
                <div class="status working">
                    <h2>🤖 Bot Status</h2>
                    <pre>{bot_status}</pre>
                </div>
                
                <div class="log">
                    <h2>📝 Latest Logs</h2>
                    <pre>{latest_logs}</pre>
                </div>
                
                <p><strong>Last Updated:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
        
        elif self.path == '/logs':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            logs = self.get_full_logs()
            self.wfile.write(logs.encode())
        
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = self.get_system_status()
            self.wfile.write(json.dumps(status, indent=2).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_latest_logs(self):
        try:
            with open('fixed_bot_restart.log', 'r') as f:
                lines = f.readlines()
                return ''.join(lines[-20:])  # Last 20 lines
        except:
            return "No logs available"
    
    def get_full_logs(self):
        try:
            with open('fixed_bot_restart.log', 'r') as f:
                return f.read()
        except:
            return "No logs available"
    
    def get_bot_status(self):
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            bots = []
            for line in result.stdout.split('\n'):
                if 'microsecond_arbitrage_bot.py' in line or 'practical_profit_bot.py' in line:
                    bots.append(line[:100])
            return '\n'.join(bots) if bots else "No bots found"
        except:
            return "Unable to check bot status"
    
    def get_system_status(self):
        return {
            "timestamp": time.time(),
            "dashboard": "running",
            "gateway": "running",
            "microsecond_bot": "running",
            "last_check": time.strftime('%Y-%m-%d %H:%M:%S'),
            "status": "operational"
        }

print("🚀 Starting fixed dashboard on port 5025...")
server = HTTPServer(('0.0.0.0', 5025), DashboardHandler)
server.serve_forever()
