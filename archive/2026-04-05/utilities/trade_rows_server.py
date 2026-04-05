
import http.server
import socketserver

PORT = 5012

class TradeRowsHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/trade_rows_dashboard.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

print(f"🚀 Starting Trade Rows Dashboard on port {PORT}")
print(f"📊 Open: http://localhost:{PORT}")
print("🔄 Auto-refresh every 30 seconds")

with socketserver.TCPServer(("", PORT), TradeRowsHandler) as httpd:
    httpd.serve_forever()
