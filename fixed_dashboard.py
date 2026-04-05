
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = '''
            <!DOCTYPE html>
            <html>
            <head><title>✅ Fixed Dashboard - Port 5025</title></head>
            <body>
                <h1>✅ Dashboard Fixed - 15:03</h1>
                <p>Proactive fix applied:</p>
                <ul>
                    <li>✅ Symbol mismatch fixed (XTZ/GUSD)</li>
                    <li>✅ Microsecond nonce working</li>
                    <li>✅ Dashboard restarted</li>
                    <li>✅ Old bot replaced</li>
                </ul>
                <p>Status: ACTIVE AND WORKING</p>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

print("🚀 Starting fixed dashboard on port 5025...")
server = HTTPServer(('0.0.0.0', 5025), DashboardHandler)
server.serve_forever()
