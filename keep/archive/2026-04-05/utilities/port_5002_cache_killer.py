#!/usr/bin/env python3
"""
PORT 5002 CACHE KILLER
Starts a simple server on port 5002 that FORCES browser to load new content
"""

from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def cache_killer():
    """Simple page that forces cache clear"""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>🚨 CACHE CLEARED - USE PORT 5003 or 5004</title>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: #ff0000;
            color: white;
        }}
        .warning {{
            font-size: 2em;
            font-weight: bold;
            margin: 20px;
        }}
        .links {{
            margin: 30px;
        }}
        a {{
            display: block;
            margin: 10px;
            padding: 15px;
            background: white;
            color: red;
            text-decoration: none;
            font-weight: bold;
            border-radius: 10px;
        }}
    </style>
</head>
<body>
    <div class="warning">🚨 OLD DASHBOARD KILLED - CACHE CLEARED</div>
    <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>The old dashboard on port 5002 was killed. Your browser was showing cached data.</p>
    
    <div class="links">
        <h2>✅ USE THESE WORKING DASHBOARDS:</h2>
        <a href="http://localhost:5003" target="_blank">📊 PORT 5003: Simple Dashboard</a>
        <a href="http://localhost:5004" target="_blank">🛡️ PORT 5004: Bulletproof Dashboard</a>
    </div>
    
    <script>
        // Force cache clear
        if ('caches' in window) {{
            caches.keys().then(function(names) {{
                for (let name of names) caches.delete(name);
            }});
        }}
        
        // Auto-redirect after 5 seconds
        setTimeout(() => {{
            window.location.href = 'http://localhost:5004';
        }}, 5000);
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    print("="*70)
    print("🚨 PORT 5002 CACHE KILLER")
    print("="*70)
    print("Forces browser to clear cache and shows new content")
    print("Redirects to working dashboards on ports 5003/5004")
    print("="*70)
    
    app.run(host='0.0.0.0', port=5002, debug=False)