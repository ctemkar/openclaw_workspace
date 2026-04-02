#!/bin/bash
# Start Resilient Trading System

echo "=================================================="
echo "🚀 STARTING RESILIENT TRADING SYSTEM"
echo "=================================================="

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

# Kill any existing processes
echo "🛑 Stopping any existing processes..."
pkill -f "real_26_crypto_trader.py" 2>/dev/null
pkill -f "llm_consensus_bot" 2>/dev/null
pkill -f "simple_dashboard.py" 2>/dev/null
pkill -f "trading_system_supervisor.py" 2>/dev/null
sleep 2

# Check Ollama
echo "🔍 Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags >/dev/null; then
    echo "⚠️ Ollama not running. Starting Ollama..."
    open -a Ollama 2>/dev/null &
    sleep 10
fi

# Check if Ollama is ready
if curl -s http://localhost:11434/api/tags >/dev/null; then
    echo "✅ Ollama is running"
else
    echo "❌ Ollama failed to start. LLM features will be limited."
fi

# Start the supervisor
echo "🚀 Starting system supervisor..."
python3 trading_system_supervisor.py &
SUPERVISOR_PID=$!
sleep 5

# Check if supervisor started
if ps -p $SUPERVISOR_PID > /dev/null; then
    echo "✅ Supervisor started (PID: $SUPERVISOR_PID)"
    
    # Wait for components to start
    echo "⏳ Waiting for components to start..."
    sleep 10
    
    # Check system status
    if [ -f "system_status_supervised.json" ]; then
        echo "📊 System status:"
        python3 -c "
import json
with open('system_status_supervised.json') as f:
    data = json.load(f)
print(f'  Timestamp: {data[\"timestamp\"]}')
print(f'  Components: {data[\"summary\"][\"healthy\"]}/{data[\"summary\"][\"total\"]} healthy')
for name, comp in data['components'].items():
    status = '✅' if comp['health'] == 'healthy' else '⚠️' if comp['health'] == 'unhealthy' else '❌'
    print(f'  {status} {name}: {comp[\"health\"]}')
        "
    fi
    
    echo ""
    echo "=================================================="
    echo "🎯 SYSTEM STARTED SUCCESSFULLY"
    echo "=================================================="
    echo ""
    echo "📊 Dashboard: http://localhost:5007"
    echo "📈 Supervisor PID: $SUPERVISOR_PID"
    echo ""
    echo "🛑 To stop the system:"
    echo "   pkill -f 'trading_system_supervisor.py'"
    echo "   or"
    echo "   kill $SUPERVISOR_PID"
    echo ""
    echo "🔍 To monitor logs:"
    echo "   tail -f supervisor.log"
    echo "   tail -f trader_supervised.log"
    echo "   tail -f llm_supervised.log"
    echo "   tail -f dashboard_supervised.log"
    echo ""
    echo "=================================================="
    
    # Keep script running to show logs
    echo "📋 Showing supervisor log (Ctrl+C to exit):"
    echo "------------------------------------------"
    tail -f supervisor.log
    
else
    echo "❌ Failed to start supervisor"
    exit 1
fi