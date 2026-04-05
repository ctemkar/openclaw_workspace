#!/bin/bash

# PAPER TRADING WATCHDOG
# Monitors paper trading bots only - NO REAL TRADING

echo "📝 PAPER TRADING WATCHDOG STARTING..."
echo "=========================================="
echo "🚫 REAL TRADING DISABLED - PAPER MODE ONLY"
echo "🔒 ALL API KEYS DELETED - 100% SIMULATION"
echo "=========================================="

# Configuration
CHECK_INTERVAL=300  # 5 minutes - paper trading doesn't need frequent checks
LOG_FILE="paper_watchdog.log"
CRASH_LOG="paper_crash_history.log"

# PAPER TRADING BOTS ONLY - NO REAL TRADING
declare -A BOTS=(
    ["paper_trader"]="final_paper_trading_system.py"
    ["binance_demo"]="binance_demo_paper_trader.py"
)

# Required paper bots
REQUIRED_BOTS=("paper_trader")

# Track restart counts
declare -A RESTART_COUNTS
declare -A LAST_RESTART_TIME

# Initialize
for bot in "${!BOTS[@]}"; do
    RESTART_COUNTS[$bot]=0
    LAST_RESTART_TIME[$bot]=0
done

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_crash() {
    local bot=$1
    local reason=$2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] PAPER_CRASH: $bot - $reason" >> "$CRASH_LOG"
}

check_bot_running() {
    local bot=$1
    local script=${BOTS[$bot]}
    
    # Check if process is running
    if pgrep -f "$script" > /dev/null; then
        # Get PID and uptime
        local pid=$(pgrep -f "$script" | head -1)
        local uptime=$(ps -p "$pid" -o etime= 2>/dev/null | xargs)
        echo "RUNNING:$pid:$uptime"
        return 0
    else
        echo "STOPPED"
        return 1
    fi
}

start_bot() {
    local bot=$1
    local script=${BOTS[$bot]}
    
    # Safety check - ensure we're in paper mode
    if [ ! -f "trading_mode.txt" ]; then
        log_message "🚨 SAFETY ERROR: trading_mode.txt not found - CANNOT START BOT"
        log_crash "$bot" "Safety check failed - trading_mode.txt missing"
        return 1
    fi
    
    if ! grep -q "PAPER_TRADING_ONLY=1" "trading_mode.txt"; then
        log_message "🚨 SAFETY ERROR: Not in paper trading mode - CANNOT START BOT"
        log_crash "$bot" "Safety check failed - not in paper mode"
        return 1
    fi
    
    log_message "📝 Starting PAPER bot: $bot ($script)..."
    
    # Start the bot in background
    if [ -f "$script" ]; then
        python3 "$script" >> "paper_${bot}.log" 2>&1 &
        local pid=$!
        
        # Wait a bit to see if it starts
        sleep 5
        
        if ps -p "$pid" > /dev/null 2>&1; then
            log_message "✅ Paper bot $bot started (PID: $pid)"
            LAST_RESTART_TIME[$bot]=$(date +%s)
            RESTART_COUNTS[$bot]=$((RESTART_COUNTS[$bot] + 1))
            return 0
        else
            log_message "❌ Paper bot $bot failed to start"
            log_crash "$bot" "Failed to start - process died"
            return 1
        fi
    else
        log_message "❌ Script not found: $script"
        log_crash "$bot" "Script not found: $script"
        return 1
    fi
}

stop_bot() {
    local bot=$1
    local result=$(check_bot_running "$bot")
    
    if echo "$result" | grep -q "RUNNING"; then
        local pid=$(echo "$result" | cut -d: -f2)
        log_message "🛑 Stopping paper bot $bot (PID: $pid)..."
        kill "$pid" 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if pgrep -f "${BOTS[$bot]}" > /dev/null; then
            kill -9 "$pid" 2>/dev/null
            log_message "⚠️ Force killed paper bot $bot"
        fi
        
        log_message "✅ Paper bot $bot stopped"
    else
        log_message "ℹ️ Paper bot $bot is not running"
    fi
}

print_status() {
    echo ""
    echo "📊 PAPER BOT STATUS - $(date '+%H:%M:%S')"
    echo "=========================================="
    echo "🔒 MODE: PAPER TRADING ONLY - NO REAL MONEY"
    echo "💰 VIRTUAL BALANCE: $10,000.00"
    echo "=========================================="
    
    for bot in "${!BOTS[@]}"; do
        local result=$(check_bot_running "$bot")
        local status="❓ UNKNOWN"
        local extra=""
        
        if echo "$result" | grep -q "RUNNING"; then
            local pid=$(echo "$result" | cut -d: -f2)
            local uptime=$(echo "$result" | cut -d: -f3)
            status="✅ RUNNING"
            extra="(PID: $pid, Uptime: $uptime)"
        else
            status="❌ STOPPED"
        fi
        
        # Check if required
        local required=""
        for req in "${REQUIRED_BOTS[@]}"; do
            if [ "$req" = "$bot" ]; then
                required="[REQUIRED]"
                break
            fi
        done
        
        echo "  $bot $required: $status $extra"
    done
    
    echo "=========================================="
}

# Main execution
echo ""
echo "🔍 Checking paper trading mode..."
if [ ! -f "trading_mode.txt" ]; then
    echo "🚨 CRITICAL ERROR: trading_mode.txt not found!"
    echo "   Creating emergency paper mode file..."
    echo "PAPER_TRADING_ONLY=1" > trading_mode.txt
    echo "REAL_TRADING_DISABLED=1" >> trading_mode.txt
    echo "EMERGENCY_CREATED=$(date '+%Y-%m-%d %H:%M:%S %z')" >> trading_mode.txt
    echo "✅ Emergency paper mode created"
fi

if grep -q "PAPER_TRADING_ONLY=1" "trading_mode.txt"; then
    echo "✅ System is in PAPER TRADING MODE"
else
    echo "🚨 WARNING: Not in paper trading mode!"
    echo "   Forcing paper mode for safety..."
    echo "PAPER_TRADING_ONLY=1" > trading_mode.txt
    echo "REAL_TRADING_DISABLED=1" >> trading_mode.txt
    echo "FORCED_AT=$(date '+%Y-%m-%d %H:%M:%S %z')" >> trading_mode.txt
    echo "✅ Paper mode forced for safety"
fi

echo ""
echo "🛑 Stopping any existing paper bots..."
for bot in "${!BOTS[@]}"; do
    stop_bot "$bot"
done

echo ""
echo "🚀 Starting required paper bots..."
for bot in "${REQUIRED_BOTS[@]}"; do
    start_bot "$bot"
done

echo ""
print_status

# Main monitoring loop
cycle=0
while true; do
    cycle=$((cycle + 1))
    
    # Print status every 10 cycles (50 minutes)
    if [ $((cycle % 10)) -eq 0 ]; then
        print_status
    fi
    
    # Check each required bot
    for bot in "${REQUIRED_BOTS[@]}"; do
        # Check if running
        if ! check_bot_running "$bot" | grep -q "RUNNING"; then
            log_message "⚠️ Paper bot $bot is not running, restarting..."
            start_bot "$bot"
        fi
    done
    
    # Wait for next check
    sleep "$CHECK_INTERVAL"
done