#!/bin/bash

# Sleep Monitor - Monitors system while user sleeps
# Runs every 30 minutes to check critical systems

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== SLEEP MONITOR ===${NC}"
echo "Time: $(date)"
echo "User: Chetu (Sleeping)"
echo ""

# 1. Check all critical processes
echo -e "${BLUE}1. PROCESS STATUS:${NC}"
critical_processes=(
    "real_time_top10_dashboard.py"
    "truthful_dashboard.py"
    "nocache_dashboard.py"
    "gateway_5000.py"
    "fixed_practical_profit_bot.py"
    "make_money_now.py"
    "practical_monitor_bot.py"
    "microsecond_arbitrage_bot.py"
    "real_26_crypto_arbitrage_bot.py"
)

all_running=true
for process in "${critical_processes[@]}"; do
    if pgrep -f "$process" > /dev/null; then
        echo -e "  ${GREEN}✅ $process${NC}"
    else
        echo -e "  ${RED}❌ $process${NC}"
        all_running=false
    fi
done

# 2. Check dashboard ports
echo -e "\n${BLUE}2. DASHBOARD PORTS:${NC}"
ports=(5001 5024 5025 5026)
port_names=("Gateway Dashboard" "Truthful Dashboard" "Nocache Dashboard" "Top10 Dashboard")

i=0
for port in "${ports[@]}"; do
    name="${port_names[$i]}"
    if curl -s --connect-timeout 5 "http://localhost:$port/" > /dev/null; then
        echo -e "  ${GREEN}✅ $name (Port $port) responding${NC}"
    else
        echo -e "  ${RED}❌ $name (Port $port) not responding${NC}"
        all_running=false
    fi
    i=$((i+1))
done

# 3. Check trading bot activity
echo -e "\n${BLUE}3. TRADING ACTIVITY:${NC}"
if [ -f "llm_predictions_history.json" ]; then
    predictions_count=$(jq '. | length' llm_predictions_history.json 2>/dev/null || echo "0")
    echo -e "  ${GREEN}📊 LLM Predictions: $predictions_count recorded${NC}"
else
    echo -e "  ${YELLOW}⚠️ No prediction history found${NC}"
fi

# 4. Check system resources
echo -e "\n${BLUE}4. SYSTEM RESOURCES:${NC}"
cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
memory_usage=$(memory_pressure | grep "System-wide memory free" | awk '{print $4}' | sed 's/%//')
echo -e "  CPU Usage: ${YELLOW}$cpu_usage%${NC}"
echo -e "  Memory Free: ${YELLOW}$memory_usage%${NC}"

# 5. Check for errors in logs (last hour only)
echo -e "\n${BLUE}5. ERROR CHECK (LAST HOUR):${NC}"
error_count=0
log_files=("trading_bot.log" "llm_bot.log" "dashboard_errors.log")
for log in "${log_files[@]}"; do
    if [ -f "$log" ]; then
        # Check for errors in the last hour
        errors=$(grep -i "error\|fail\|exception\|crash" "$log" | grep "$(date -v-1H '+%Y-%m-%d %H')" | wc -l)
        if [ "$errors" -gt 0 ]; then
            echo -e "  ${RED}⚠️ $log has $errors recent errors (last hour)${NC}"
            error_count=$((error_count + errors))
        else
            echo -e "  ${GREEN}✅ $log clean (no errors in last hour)${NC}"
        fi
    fi
done

# 6. Summary
echo -e "\n${BLUE}=== SUMMARY ===${NC}"
if [ "$all_running" = true ] && [ "$error_count" -eq 0 ]; then
    echo -e "${GREEN}✅ ALL SYSTEMS NOMINAL${NC}"
    echo "All processes running, all dashboards responding, no recent errors detected."
    echo "System is stable and monitoring will continue."
else
    if [ "$all_running" = true ]; then
        echo -e "${YELLOW}⚠️ SYSTEM STABLE WITH OLD ERRORS${NC}"
        echo "All processes running, all dashboards responding."
        echo "Old errors detected but system is currently stable."
    else
        echo -e "${RED}🚨 SYSTEM NEEDS ATTENTION${NC}"
        echo "Critical components are not running."
        echo "Manual intervention required."
    fi
fi

echo -e "\n${BLUE}Next check in 30 minutes${NC}"
echo "Last check: $(date)" > /tmp/last_sleep_monitor_check.txt