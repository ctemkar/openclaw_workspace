#!/bin/bash
# Process trading data - fetch, analyze, and generate reports

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="trading_data_processing_${TIMESTAMP}.log"
REPORT_FILE="trading_report_${TIMESTAMP}.txt"
SUMMARY_FILE="trading_summary_latest.txt"

echo "=== Trading Data Processing Started at $(date) ===" | tee "$LOG_FILE"

# Check if trading server is running
echo "Checking trading server status..." | tee -a "$LOG_FILE"
if ! curl -s http://localhost:5001/status > /dev/null 2>&1; then
    echo "ERROR: Trading server is not responding on port 5001" | tee -a "$LOG_FILE"
    echo "Attempting to restart trading server..." | tee -a "$LOG_FILE"
    
    # Kill any existing process on port 5001
    lsof -ti:5001 | xargs kill -9 2>/dev/null || true
    
    # Start trading server
    python3 trading_server.py > trading_server.log 2>&1 &
    SERVER_PID=$!
    echo "Started trading server with PID: $SERVER_PID" | tee -a "$LOG_FILE"
    
    # Wait for server to start
    sleep 5
    
    # Check again
    if ! curl -s http://localhost:5001/status > /dev/null 2>&1; then
        echo "ERROR: Failed to start trading server" | tee -a "$LOG_FILE"
        exit 1
    fi
fi

# Fetch and process trading data
echo "Fetching and processing trading data..." | tee -a "$LOG_FILE"
python3 fetch_trading_data.py 2>&1 | tee -a "$LOG_FILE"

# Run trading analysis
echo "Running trading analysis..." | tee -a "$LOG_FILE"
ANALYSIS_RESULT=$(curl -s -X POST http://localhost:5001/analysis)
echo "Analysis result: $ANALYSIS_RESULT" | tee -a "$LOG_FILE"

# Generate final summary
echo "Generating final summary..." | tee -a "$LOG_FILE"

# Create a Python script for summary generation
cat > /tmp/generate_summary.py << 'EOF'
import json
import sys
from datetime import datetime

def get_server_status():
    import urllib.request
    try:
        with urllib.request.urlopen('http://localhost:5001/status') as response:
            return json.load(response)
    except:
        return {}

def get_trades():
    import urllib.request
    try:
        with urllib.request.urlopen('http://localhost:5001/trades') as response:
            return json.load(response)
    except:
        return {'trades': []}

status = get_server_status()
trades_data = get_trades()
trades = trades_data.get('trades', [])

print("=== TRADING DATA PROCESSING COMPLETE ===")
print(f"Timestamp: {datetime.now()}")
print("========================================")
print()
print("Server Status:")
print(f"  Status: {status.get('status', 'unknown')}")
print(f"  Capital: ${status.get('capital', 0):.2f}")
print(f"  Last Analysis: {status.get('last_analysis', 'unknown')}")
print()
print("Recent Trades Summary:")
print(f"  Total Trades: {len(trades)}")
if trades:
    buys = sum(1 for t in trades if t.get('side', '').lower() == 'buy')
    sells = sum(1 for t in trades if t.get('side', '').lower() == 'sell')
    filled = sum(1 for t in trades if t.get('status', '').lower() == 'filled')
    print(f"  Buy Trades: {buys}")
    print(f"  Sell Trades: {sells}")
    print(f"  Filled Trades: {filled}")
    print(f"  Pending Trades: {len(trades) - filled}")
EOF

python3 /tmp/generate_summary.py > "$REPORT_FILE"

# Update latest summary
cp "$REPORT_FILE" "$SUMMARY_FILE"

echo "" | tee -a "$LOG_FILE"
echo "=== Processing Complete ===" | tee -a "$LOG_FILE"
echo "Report saved to: $REPORT_FILE" | tee -a "$LOG_FILE"
echo "Latest summary: $SUMMARY_FILE" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"

# Display quick summary
echo ""
echo "=== QUICK SUMMARY ==="
cat "$SUMMARY_FILE" | tail -20