from flask import Flask, jsonify
import socket, os, threading, time, psutil
from datetime import datetime

app = Flask(__name__)
TASK_STATUS = {"trading": "stopped", "last_update": None}

def update_task_statuses():
    while True:
        try:
            found = any("crypto_trading_llm_live.py" in " ".join(p.cmdline()) 
                        for p in psutil.process_iter(['cmdline']) if p.info['cmdline'])
            TASK_STATUS["trading"] = "running" if found else "stopped"
            TASK_STATUS["last_update"] = datetime.now().strftime("%H:%M:%S")
        except: pass
        time.sleep(5)

@app.route('/api/status/all')
def get_status():
    return jsonify(TASK_STATUS)

if __name__ == '__main__':
    monitor_thread = threading.Thread(target=update_task_statuses, daemon=True)
    monitor_thread.start()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]
    
    with open('/Users/chetantemkar/.openclaw/workspace/app/.active_port', 'w') as f:
        f.write(str(port))
        
    app.run(host='0.0.0.0', port=port)
