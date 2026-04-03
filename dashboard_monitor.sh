#!/bin/bash
echo "🔍 Dashboard Monitor - Checking every 30 seconds"
echo "Press Ctrl+C to stop"
echo ""

while true; do
    echo "=== $(date '+%H:%M:%S') ==="
    
    # Check if dashboard is running
    if ps aux | grep -q "arbitration_trading_dashboard.py" | grep -v grep; then
        echo "✅ Dashboard: RUNNING"
        
        # Check if port is responding
        if curl -s --head http://localhost:5020 >/dev/null; then
            echo "🌐 Port 5020: RESPONDING"
            echo "📊 Open: http://localhost:5020"
        else
            echo "❌ Port 5020: NOT RESPONDING"
            echo "   Dashboard may have crashed"
        fi
    else
        echo "❌ Dashboard: NOT RUNNING"
        echo "   Attempting to restart..."
        python3 arbitration_trading_dashboard.py &
        sleep 3
    fi
    
    echo "⏰ Next check in 30 seconds..."
    echo "----------------------------------------"
    sleep 30
done
