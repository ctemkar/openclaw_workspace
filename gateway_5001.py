#!/usr/bin/env python3
"""
Gateway Service on port 5001
Simple redirect service for dashboard access
"""

from flask import Flask, redirect, jsonify
import os
import socket
from datetime import datetime

app = Flask(__name__)
BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

@app.route("/")
def index():
    """Redirect to active dashboard"""
    try:
        # Check for active port file
        port_file = os.path.join(BASE_DIR, ".active_port")
        if os.path.exists(port_file):
            with open(port_file, "r") as f:
                port = f.read().strip()
            return redirect(f"http://127.0.0.1:{port}")
        
        # Check common dashboard ports
        common_ports = [8080, 8081, 8501, 5000, 5005]
        for port in common_ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                result = s.connect_ex(('127.0.0.1', port))
                s.close()
                if result == 0:
                    return redirect(f"http://127.0.0.1:{port}")
            except:
                continue
        
        return "No active dashboard found. Available services:<br>" + \
               "<a href='http://127.0.0.1:8080'>Port 8080</a><br>" + \
               "<a href='http://127.0.0.1:8081'>Port 8081</a><br>" + \
               "<a href='http://127.0.0.1:8501'>Port 8501</a>"
                
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/status")
def status():
    """Gateway status endpoint"""
    return jsonify({
        "service": "gateway",
        "port": 5001,
        "status": "running",
        "time": datetime.now().isoformat(),
        "endpoints": {
            "/": "Redirect to active dashboard",
            "/status": "Gateway status",
            "/ports": "List available ports"
        }
    })

@app.route("/ports")
def ports():
    """Check available dashboard ports"""
    common_ports = [8080, 8081, 8501, 5000, 5005]
    available = []
    
    for port in common_ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            s.close()
            if result == 0:
                available.append({
                    "port": port,
                    "status": "active",
                    "url": f"http://127.0.0.1:{port}"
                })
            else:
                available.append({
                    "port": port,
                    "status": "inactive",
                    "url": None
                })
        except Exception as e:
            available.append({
                "port": port,
                "status": f"error: {str(e)}",
                "url": None
            })
    
    return jsonify({
        "available_ports": available,
        "gateway_port": 5001,
        "checked_at": datetime.now().isoformat()
    })

if __name__ == "__main__":
    print(f"🚀 Starting Gateway Service on port 5001")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"🔗 Access: http://localhost:5001")
    print(f"📊 Status: http://localhost:5001/status")
    print(f"🔍 Ports: http://localhost:5001/ports")
    app.run(host="0.0.0.0", port=5001, debug=False)