# 🚀 Resilient Trading System - Deployment Checklist

## ✅ PRE-DEPLOYMENT CHECKS
- [x] All Python files have valid syntax
- [x] API keys exist and are valid
- [x] Ollama is running with required models
- [x] Configuration files are valid JSON
- [x] Supervisor has rate limiting and health checks
- [x] LLM bot has circuit breakers and fallbacks
- [x] Dashboard has monitoring and auto-refresh
- [x] Startup script properly cleans up old processes

## 📋 DEPLOYMENT STEPS

### Step 1: Backup Current System
```bash
cd ~/.openclaw/workspace
cp -r app app.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created"
```

### Step 2: Start Resilient System
```bash
cd ~/.openclaw/workspace/app
./start_resilient_system.sh
```

**Expected output:**
- Supervisor starts
- Trading bot starts (PID shown)
- LLM bot starts (if Ollama available)
- Dashboard starts on port 5007

### Step 3: Verify System Status
1. **Check dashboard:** http://localhost:5007
2. **Check supervisor log:** `tail -f supervisor.log`
3. **Check trader log:** `tail -f trader_supervised.log`
4. **Check system status:** `cat system_status_supervised.json | python3 -m json.tool`

### Step 4: Monitor Initial Operation (30 minutes)
1. **First 5 minutes:** Verify all components start
2. **First 15 minutes:** Check health checks are working
3. **First 30 minutes:** Verify trading cycles are executing

## 🎯 EXPECTED BEHAVIOR

### Normal Operation
- ✅ Dashboard shows "System Health: GOOD"
- ✅ All components show "healthy" status
- ✅ Trading cycles execute every 5 minutes
- ✅ LLM analysis runs every 10 minutes (if available)
- ✅ Status file updates every 5 minutes

### Graceful Degradation (if Ollama fails)
- ✅ System switches to DEGRADED mode
- ✅ Trading continues without LLM signals
- ✅ Dashboard shows warning but remains operational
- ✅ Supervisor attempts to restart LLM bot

### Auto-Recovery (if component crashes)
- ✅ Supervisor detects dead component
- ✅ Waits restart delay (30s for trader, 60s for LLM)
- ✅ Restarts component (rate limited)
- ✅ Updates status file

## 🚨 EMERGENCY PROCEDURES

### Manual Stop
```bash
# Stop everything
pkill -f "trading_system_supervisor.py"

# Stop individual components
pkill -f "real_26_crypto_trader.py"
pkill -f "llm_consensus_bot_resilient.py"
pkill -f "simple_dashboard.py"
```

### System Recovery
1. **Check logs:** `tail -f supervisor.log`
2. **Check Ollama:** `curl http://localhost:11434/api/tags`
3. **Restart supervisor:** `python3 trading_system_supervisor.py`
4. **Monitor:** Watch dashboard and logs

### Critical Issues
1. **Trading bot stuck:** Check API keys and exchange connectivity
2. **LLM bot failing:** Check Ollama server and model availability
3. **Dashboard down:** Check port 5007 availability
4. **High restart frequency:** Check component logs for errors

## 📊 MONITORING PLAN

### First 24 Hours
- **Hour 1-2:** Continuous monitoring
- **Hour 3-6:** Check every 30 minutes
- **Hour 7-24:** Check every 2 hours

### Key Metrics to Track
1. **Component uptime** (should be >95%)
2. **Restart frequency** (should be <3/hour)
3. **Trading performance** (win rate, P&L)
4. **System health** (dashboard status)

### Alert Conditions
- ❌ Any component restarting >5 times/hour
- ❌ System in MINIMAL mode for >1 hour
- ❌ Dashboard unavailable for >5 minutes
- ❌ Trading stopped for >15 minutes

## 🔧 TROUBLESHOOTING

### Common Issues & Solutions

#### 1. Ollama Not Responding
```bash
# Restart Ollama
pkill -f "ollama"
open -a Ollama
sleep 10
curl http://localhost:11434/api/tags
```

#### 2. Dashboard Not Loading
```bash
# Check if dashboard is running
curl http://localhost:5007

# Check dashboard log
tail -f dashboard_supervised.log

# Restart dashboard via supervisor
# Press 'r dashboard-5007' in supervisor interactive mode
```

#### 3. Trading Bot Not Trading
```bash
# Check trader log
tail -f trader_supervised.log

# Check API keys
cat secure_keys/.gemini_key | head -c 20

# Check exchange connectivity
python3 -c "import ccxt; print(ccxt.gemini().fetch_ticker('BTC/USD'))"
```

#### 4. Supervisor Not Starting
```bash
# Check Python version
python3 --version

# Check dependencies
python3 -c "import psutil, requests, flask; print('Dependencies OK')"

# Check file permissions
ls -la trading_system_supervisor.py
```

## 📈 SUCCESS CRITERIA

### Immediate (First Hour)
- [ ] All components start successfully
- [ ] Dashboard is accessible
- [ ] Trading cycles begin
- [ ] Status file is created and updated

### Short-term (First Day)
- [ ] No critical failures
- [ ] Auto-recovery works when tested
- [ ] Graceful degradation functions
- [ ] Performance metrics stable

### Long-term (First Week)
- [ ] System uptime >99%
- [ ] Trading performance consistent
- [ ] No manual intervention needed
- [ ] All resilience features tested

## 🎉 DEPLOYMENT COMPLETE

**When all checks pass:**
1. System is self-healing and fault-tolerant
2. Trading continues through partial failures
3. Comprehensive monitoring in place
4. Emergency procedures documented

**Final step:** Update HEARTBEAT.md with deployment status and begin regular monitoring.

---

**Deployment Time:** $(date)  
**System Version:** Resilient v1.0  
**Status:** READY FOR DEPLOYMENT