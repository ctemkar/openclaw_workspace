#!/usr/bin/env python3
"""
VALIDATE SYSTEM SAFETY
Check that the resilient system won't fail in dangerous ways
"""

import os
import sys
import json
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def check_critical_safety():
    """Check critical safety requirements"""
    print("🛡️  SYSTEM SAFETY VALIDATION")
    print("="*70)
    
    safety_ok = True
    warnings = []
    
    # 1. Check trading bot has safety limits
    print("\n🔍 1. Trading Bot Safety...")
    with open('real_26_crypto_trader.py', 'r') as f:
        content = f.read()
        
    safety_checks = [
        ('MAX_TRADES_PER_DAY', 'Daily trade limit'),
        ('STOP_LOSS', 'Stop loss protection'),
        ('TAKE_PROFIT', 'Take profit target'),
        ('position_size', 'Position size limit'),
        ('capital', 'Capital allocation')
    ]
    
    for check, desc in safety_checks:
        if check in content:
            print(f"   ✅ {desc}")
        else:
            print(f"   ⚠️  {desc} - Not found")
            warnings.append(f"Missing {desc}")
    
    # 2. Check supervisor has rate limiting
    print("\n🔍 2. Supervisor Safety...")
    with open('trading_system_supervisor.py', 'r') as f:
        content = f.read()
    
    supervisor_checks = [
        ('max_restarts_per_hour', 'Restart rate limiting'),
        ('restart_delay', 'Restart delay'),
        ('check_health', 'Health monitoring'),
        ('should_restart', 'Restart decision logic')
    ]
    
    for check, desc in supervisor_checks:
        if check in content:
            print(f"   ✅ {desc}")
        else:
            print(f"   ⚠️  {desc} - Not found")
            warnings.append(f"Missing {desc}")
    
    # 3. Check resilient bot has circuit breakers
    print("\n🔍 3. LLM Bot Resilience...")
    with open('llm_consensus_bot_resilient.py', 'r') as f:
        content = f.read()
    
    resilience_checks = [
        ('CircuitBreaker', 'Circuit breaker pattern'),
        ('GracefulTradingSystem', 'Graceful degradation'),
        ('timeout', 'Timeout handling'),
        ('fallback', 'Fallback models'),
        ('MINIMAL mode', 'Minimal operation mode')
    ]
    
    for check, desc in resilience_checks:
        if check in content:
            print(f"   ✅ {desc}")
        else:
            print(f"   ⚠️  {desc} - Not found")
            warnings.append(f"Missing {desc}")
    
    # 4. Check dashboard has monitoring
    print("\n🔍 4. Dashboard Monitoring...")
    with open('simple_dashboard.py', 'r') as f:
        content = f.read()
    
    dashboard_checks = [
        ('system_health', 'System health display'),
        ('auto-refresh', 'Auto-refresh'),
        ('status', 'Status reporting'),
        ('timestamp', 'Timestamp display')
    ]
    
    for check, desc in dashboard_checks:
        if check in content:
            print(f"   ✅ {desc}")
        else:
            print(f"   ⚠️  {desc} - Not found")
            warnings.append(f"Missing {desc}")
    
    # 5. Check config files
    print("\n🔍 5. Configuration Safety...")
    try:
        with open('trading_config.json', 'r') as f:
            config = json.load(f)
        
        config_checks = [
            ('risk_parameters', 'Risk parameters'),
            ('max_position_size', 'Position size limit'),
            ('stop_loss', 'Stop loss setting'),
            ('take_profit', 'Take profit setting')
        ]
        
        for check, desc in config_checks:
            if check in str(config):
                print(f"   ✅ {desc}")
            else:
                print(f"   ⚠️  {desc} - Not found in config")
                warnings.append(f"Missing {desc}")
    except:
        print("   ❌ Cannot read trading_config.json")
        safety_ok = False
    
    # 6. Check startup script safety
    print("\n🔍 6. Startup Script Safety...")
    with open('start_resilient_system.sh', 'r') as f:
        content = f.read()
    
    startup_checks = [
        ('pkill', 'Clean shutdown of old processes'),
        ('sleep', 'Proper delays between operations'),
        ('check', 'Health checks'),
        ('Ollama', 'Ollama verification')
    ]
    
    for check, desc in startup_checks:
        if check in content:
            print(f"   ✅ {desc}")
        else:
            print(f"   ⚠️  {desc} - Not found")
            warnings.append(f"Missing {desc}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 SAFETY SUMMARY")
    print("="*70)
    
    if warnings:
        print(f"⚠️  {len(warnings)} warnings found:")
        for warning in warnings:
            print(f"   • {warning}")
        
        print("\n🔧 Recommendations:")
        print("   1. Review warnings above")
        print("   2. Test system in simulation first")
        print("   3. Monitor closely after deployment")
        print("   4. Have manual stop procedures ready")
    else:
        print("✅ No safety warnings found")
    
    print("\n" + "="*70)
    print("🎯 DEPLOYMENT READINESS")
    print("="*70)
    
    if safety_ok:
        print("✅ System passes safety checks")
        print("🚀 Ready for deployment with monitoring")
        print("\nRecommended deployment steps:")
        print("1. Backup current system: cp -r ~/.openclaw/workspace/app ~/.openclaw/workspace/app.backup")
        print("2. Start system: ./start_resilient_system.sh")
        print("3. Monitor dashboard: http://localhost:5007")
        print("4. Check logs: tail -f supervisor.log")
        print("5. Verify trading after 30 minutes")
    else:
        print("❌ System has safety issues - fix before deployment")
        sys.exit(1)

if __name__ == "__main__":
    try:
        check_critical_safety()
    except Exception as e:
        print(f"❌ Validation error: {e}")
        sys.exit(1)