from flask import Flask, jsonify, render_template, send_from_directory
import socket, os, threading, time, psutil
from datetime import datetime

app = Flask(__name__)
TASK_STATUS = {"trading": "stopped", "last_update": "never"}

def update_task_statuses():
    while True:
        try:
            # Look for the trading bot process
            found = any("crypto_trading_llm_live.py" in " ".join(p.cmdline()) 
                        for p in psutil.process_iter(['cmdline']) if p.info['cmdline'])
            TASK_STATUS["trading"] = "running" if found else "stopped"
            TASK_STATUS["last_update"] = datetime.now().strftime("%H:%M:%S")
        except Exception as e: 
            print(f"Error in update_task_statuses: {e}") # Added error logging
            pass # Continue to next iteration even if there's an error
        time.sleep(5)

@app.route('/')
def home():
    # Serve the index.html file from the templates directory
    return render_template('index.html')

# Route to serve static files (like CSS, JS)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/api/status/all')
def get_status():
    # This route might be redundant if index.html and script.js handle status updates directly
    # but keeping it for now as it was part of the previous code.
    return jsonify(TASK_STATUS)

if __name__ == '__main__':
    # Start the background thread for monitoring task statuses
    monitor_thread = threading.Thread(target=update_task_statuses, daemon=True)
    monitor_thread.start()
    
    # Find and write the active port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]
    
    with open('/Users/chetantemkar/.openclaw/workspace/app/.active_port', 'w') as f:
        f.write(str(port))
        
    # Run the Flask app
    # Use host='0.0.0.0' to make it accessible externally if needed, 
    # but for localhost development, host='127.0.0.1' is often preferred.
    # Changed to 0.0.0.0 for broader accessibility within the network if needed by the user.
    app.run(host='0.0.0.0', port=port, debug=False) 
