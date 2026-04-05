# 🛡️ Resilient Trading System

## Overview
A fault-tolerant trading system with auto-recovery, graceful degradation, and comprehensive monitoring.

## 🚀 Quick Start

```bash
# Start the resilient system
./start_resilient_system.sh

# Or start manually
python3 trading_system_supervisor.py
```

## 📁 System Components

### 1. **Trading System Supervisor** (`trading_system_supervisor.py`)
- **Purpose**: Manages all components with auto-restart
- **Features**:
  - Process monitoring and health checks
  - Auto-restart with rate limiting
  - Graceful shutdown
  - Status reporting

### 2. **Resilient LLM Consensus Bot** (`llm_consensus_bot_resilient.py`)
- **Purpose**: AI-powered trading signals with fault tolerance
- **Features**:
  - Circuit breaker pattern for API calls
  - Graceful degradation (FULL → DEGRADED → MINIMAL modes)
  - Model fallback system
  - Exponential backoff retries
  - Timeout handling

### 3. **Consolidated Dashboard** (`simple_dashboard.py`)
- **Purpose**: Single dashboard for all monitoring
- **Features**:
  - Real-time system status
  - Portfolio overview
  - Trading statistics
  - Auto-refreshing (30s intervals)
  - Available at: `http://localhost:5007`

### 4. **26-Crypto Trading Bot** (`real_26_crypto_trader.py`)
- **Purpose**: Main trading execution
- **Features**:
  - 26 cryptocurrency monitoring
  - Gemini LONG positions
  - Binance SHORT positions (when available)
  - Aggressive trading mode

## 🛡️ Resilience Features

### Circuit Breaker Pattern
- Prevents cascading failures
- Auto-reset after recovery period
- Three states: CLOSED, OPEN, HALF_OPEN

### Graceful Degradation
- **FULL Mode**: All features available
- **DEGRADED Mode**: Conservative trading, reduced model usage
- **MINIMAL Mode**: Essential trading only, no LLM analysis

### Health Monitoring
- Process-level health checks
- HTTP endpoint verification
- Log file monitoring
- Resource usage tracking

### Auto-Recovery
- Automatic restart of failed components
- Rate limiting to prevent restart loops
- Staggered startup to avoid resource contention

## 📊 Monitoring & Logging

### Log Files
- `supervisor.log` - Supervisor activity
- `trader_supervised.log` - Trading bot logs
- `llm_supervised.log` - LLM consensus bot logs
- `dashboard_supervised.log` - Dashboard logs

### Status Files
- `system_status_supervised.json` - Current system status
- `resilient_decisions.json` - LLM trading decisions
- `trading_config.json` - Trading configuration

## 🎯 Dashboard Features

### Real-time Monitoring
- System health status
- Component status (healthy/unhealthy/dead)
- Portfolio value and P&L
- Trading statistics
- Exchange status

### API Endpoints
- `GET /` - Dashboard UI
- `GET /api/status` - JSON system status

## 🔧 Configuration

### Supervisor Configuration
Edit `trading_system_supervisor.py` to modify:
- Component startup commands
- Health check intervals
- Restart policies
- Rate limiting

### Trading Configuration
Edit `trading_config.json` to modify:
- Capital allocation
- Risk parameters
- Trading pairs

## 🚨 Emergency Procedures

### Manual Stop
```bash
# Stop supervisor and all components
pkill -f "trading_system_supervisor.py"

# Stop individual components
pkill -f "real_26_crypto_trader.py"
pkill -f "llm_consensus_bot_resilient.py"
pkill -f "simple_dashboard.py"
```

### System Recovery
1. Check logs for errors
2. Verify Ollama is running: `curl http://localhost:11434/api/tags`
3. Restart supervisor: `python3 trading_system_supervisor.py`
4. Monitor status at `http://localhost:5007`

## 📈 Performance Metrics

### Key Metrics Tracked
- Component uptime
- Restart frequency
- Health check success rate
- Trading performance
- LLM model availability

### Optimization Tips
1. Reduce LLM model count in degraded mode
2. Increase health check intervals for stable systems
3. Adjust restart delays based on component stability
4. Monitor memory usage for Ollama models

## 🔄 Update Procedures

### Adding New Components
1. Add component config to `COMPONENTS` list in supervisor
2. Implement appropriate health check
3. Test startup/shutdown procedures
4. Add to dashboard if needed

### Updating Existing Components
1. Stop supervisor
2. Update component code
3. Restart supervisor
4. Verify health checks pass

## 🎯 Success Criteria

### System Resilience
- [ ] No single point of failure
- [ ] Graceful degradation under load
- [ ] Auto-recovery from failures
- [ ] Comprehensive monitoring

### Trading Performance
- [ ] Consistent uptime (>99%)
- [ ] Quick recovery from failures (<5 minutes)
- [ ] Accurate position tracking
- [ ] Real-time dashboard updates

## 📞 Support & Troubleshooting

### Common Issues
1. **Ollama not responding**: Restart Ollama app
2. **Dashboard not loading**: Check port 5007 availability
3. **Trading bot stuck**: Check API key validity
4. **High restart frequency**: Adjust rate limiting

### Debug Commands
```bash
# Check system status
cat system_status_supervised.json | python3 -m json.tool

# Monitor logs in real-time
tail -f supervisor.log

# Check component processes
ps aux | grep -E "(python|trader|llm|dashboard)"

# Test Ollama
curl http://localhost:11434/api/tags
```

## 🚀 Future Enhancements

### Planned Features
1. **Telemetry integration** - Prometheus/Grafana
2. **Alerting system** - Slack/Telegram notifications
3. **Backtesting integration** - Historical performance analysis
4. **Multi-node deployment** - Distributed trading system
5. **Machine learning** - Adaptive trading strategies

---

**Last Updated**: April 2, 2026  
**System Version**: Resilient v1.0  
**Status**: ✅ Operational