#!/bin/bash

# Emergency Alert - Sends critical alerts if systems fail
# Called by sleep monitor when critical issues detected

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}🚨 EMERGENCY ALERT 🚨${NC}"
echo "Time: $(date)"
echo "User: Chetu (Sleeping)"
echo ""

# Check most critical processes
critical_failures=0

# 1. Trading bot
if ! pgrep -f "real_26_crypto_trader.py" > /dev/null; then
    echo -e "${RED}❌ CRITICAL: Trading bot is not running!${NC}"
    critical_failures=$((critical_failures + 1))
fi

# 2. LLM consensus bot
if ! pgrep -f "llm_consensus_bot.py" > /dev/null; then
    echo -e "${RED}❌ CRITICAL: LLM consensus bot is not running!${NC}"
    critical_failures=$((critical_failures + 1))
fi

# 3. Main dashboard
if ! curl -s --connect-timeout 5 "http://localhost:5007/" > /dev/null; then
    echo -e "${RED}❌ CRITICAL: Main dashboard (port 5007) is down!${NC}"
    critical_failures=$((critical_failures + 1))
fi

# 4. Real-time trades dashboard
if ! curl -s --connect-timeout 5 "http://localhost:5011/" > /dev/null; then
    echo -e "${RED}❌ CRITICAL: Real-time dashboard (port 5011) is down!${NC}"
    critical_failures=$((critical_failures + 1))
fi

# Alert level
if [ "$critical_failures" -ge 2 ]; then
    echo -e "\n${RED}🚨🚨🚨 MULTIPLE CRITICAL FAILURES DETECTED! 🚨🚨🚨${NC}"
    echo "System requires immediate attention!"
    echo "Failures: $critical_failures critical systems down"
    
    # Try to restart critical systems
    echo -e "\n${YELLOW}⚠️ Attempting automatic recovery...${NC}"
    
    # Restart trading bot if down
    if ! pgrep -f "real_26_crypto_trader.py" > /dev/null; then
        echo "Restarting trading bot..."
        cd /Users/chetantemkar/.openclaw/workspace/app
        nohup python3 real_26_crypto_trader.py > trading_bot_restart.log 2>&1 &
        sleep 5
        if pgrep -f "real_26_crypto_trader.py" > /dev/null; then
            echo -e "${YELLOW}✅ Trading bot restarted${NC}"
        else
            echo -e "${RED}❌ Failed to restart trading bot${NC}"
        fi
    fi
    
    # Restart main dashboard if down
    if ! curl -s --connect-timeout 5 "http://localhost:5007/" > /dev/null; then
        echo "Restarting main dashboard..."
        cd /Users/chetantemkar/.openclaw/workspace/app
        nohup python3 original_dashboard_fixed.py --port 5007 > dashboard_restart.log 2>&1 &
        sleep 5
        if curl -s --connect-timeout 5 "http://localhost:5007/" > /dev/null; then
            echo -e "${YELLOW}✅ Main dashboard restarted${NC}"
        else
            echo -e "${RED}❌ Failed to restart main dashboard${NC}"
        fi
    fi
    
elif [ "$critical_failures" -eq 1 ]; then
    echo -e "\n${YELLOW}⚠️ SINGLE CRITICAL FAILURE DETECTED${NC}"
    echo "One critical system is down. Monitoring will continue."
    
elif [ "$critical_failures" -eq 0 ]; then
    echo -e "\n${YELLOW}✅ No critical failures detected${NC}"
    echo "All critical systems are running."
fi

# Log the alert
echo -e "\nAlert logged at: $(date)" >> /tmp/emergency_alerts.log
echo "Critical failures: $critical_failures" >> /tmp/emergency_alerts.log
echo "---" >> /tmp/emergency_alerts.log