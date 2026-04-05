#!/bin/bash

# TRADING BOT WATCHDOG
# Simple script to monitor and restart crashed bots

echo "🐕 TRADING BOT WATCHDOG STARTING..."
echo "=========================================="

# Configuration
CHECK_INTERVAL=60  # seconds
MAX_RESTARTS_PER_HOUR=5
LOG_FILE="watchdog.log"
CRASH_LOG="crash_history.log"

# Bots to monitor
declare -A BOTS=(
    ["make_money_now"]="scripts/make_money_now.py"
    ["practical_monitor"]="practical_monitor_bot.py"
    ["next_gen_trader"]="next_gen_trading_bot.py"
)

# Required bots (will be auto-restarted)
REQUIRED_BOTS=("make_money_now" "practical_monitor")

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
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] CRASH: $bot - $reason" >> "$CRASH_LOG"
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
    
    log_message "🚀 Starting $bot ($script)..."
    
    # Check restart limits
    local current_time=$(date +%s)
    local last_restart=${LAST_RESTART_TIME[$bot]}
    local hour_ago=$((current_time - 3600))
    
    # Count restarts in last hour
    local recent_restarts=0
    if [ -f "$CRASH_LOG" ]; then
        recent_restarts=$(grep -c "$bot" "$CRASH_LOG" | awk -v start="$hour_ago" '
            BEGIN {count=0}
            $0 ~ bot && $2 >= start {count++}
            END {print count}
        ' bot="$bot")
    fi
    
    if [ "$recent_restarts" -ge "$MAX_RESTARTS_PER_HOUR" ]; then
        log_message "🚨 $bot exceeded restart limit ($MAX_RESTARTS_PER_HOUR/hour), waiting..."
        return 1
    fi
    
    # Start the bot
    if [[ "$script" == scripts/* ]]; then
        # For scripts in scripts/ directory, run from parent
        (cd "$(dirname "$script")/.." && python3 "$(basename "$script")" > "${bot}_output.log" 2>&1 &)
    else
        # For scripts in current directory
        python3 "$script" > "${bot}_output.log" 2>&1 &
    fi
    
    local pid=$!
    RESTART_COUNTS[$bot]=$((RESTART_COUNTS[$bot] + 1))
    LAST_RESTART_TIME[$bot]=$current_time
    
    sleep 3  # Give it time to start
    
    if check_bot_running "$bot" | grep -q "RUNNING"; then
        log_message "✅ $bot started successfully (PID: $pid)"
        return 0
    else
        log_message "❌ $bot failed to start"
        log_crash "$bot" "Failed to start"
        return 1
    fi
}

stop_bot() {
    local bot=$1
    local result=$(check_bot_running "$bot")
    
    if echo "$result" | grep -q "RUNNING"; then
        local pid=$(echo "$result" | cut -d: -f2)
        log_message "🛑 Stopping $bot (PID: $pid)..."
        kill "$pid" 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if pgrep -f "${BOTS[$bot]}" > /dev/null; then
            kill -9 "$pid" 2>/dev/null
            log_message "⚠️ Force killed $bot"
        fi
        
        log_message "✅ $bot stopped"
    else
        log_message "ℹ️ $bot is not running"
    fi
}

print_status() {
    echo ""
    echo "📊 BOT STATUS - $(date '+%H:%M:%S')"
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
        
        local required=""
        for req in "${REQUIRED_BOTS[@]}"; do
            if [ "$req" = "$bot" ]; then
                required="[REQUIRED]"
                break
            fi
        done
        
        printf "%-20s %-12s %-10s Restarts: %-2d %s\n" \
            "$bot" "$status" "$required" "${RESTART_COUNTS[$bot]}" "$extra"
    done
    
    echo "=========================================="
}

# Main loop
log_message "🐕 Watchdog started"
print_status

# Initial start of required bots
for bot in "${REQUIRED_BOTS[@]}"; do
    if ! check_bot_running "$bot" | grep -q "RUNNING"; then
        start_bot "$bot"
    fi
done

cycle=0
while true; do
    cycle=$((cycle + 1))
    
    # Print status every 10 cycles
    if [ $((cycle % 10)) -eq 0 ]; then
        print_status
    fi
    
    # Check each bot
    for bot in "${!BOTS[@]}"; do
        # Skip if not required and not running
        is_required=0
        for req in "${REQUIRED_BOTS[@]}"; do
            if [ "$req" = "$bot" ]; then
                is_required=1
                break
            fi
        done
        
        if [ "$is_required" -eq 0 ]; then
            continue
        fi
        
        # Check if running
        if ! check_bot_running "$bot" | grep -q "RUNNING"; then
            log_message "⚠️ $bot is not running, restarting..."
            start_bot "$bot"
        fi
    done
    
    # Wait for next check
    sleep "$CHECK_INTERVAL"
done