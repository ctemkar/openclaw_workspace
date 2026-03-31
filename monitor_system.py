#!/usr/bin/env python3
"""
Monitor the trading system and identify improvements
"""

import subprocess
import json
import time
import psutil
from datetime import datetime

print('🔍 TRADING SYSTEM MONITOR & IMPROVEMENT ANALYSIS')
print('=' * 70)
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (Bangkok)')
print()

# 1. CHECK PROCESS STATUS
print('📊 1. PROCESS STATUS:')
processes = {
    'real_26_crypto_trader.py': '26-crypto aggressive trading',
    'fixed_bot_common.py': 'Common bot with 1.0% thresholds',
    'dashboard_common.py': 'Main dashboard with P&L at top',
    'updated_trading_server.py': 'Trading server API',
    'simple_pnl_dashboard.py': 'Simple P&L dashboard',
    'bulletproof_dashboard.py': 'Bulletproof dashboard',
    'simple_dashboard_fixed.py': 'Simple fixed dashboard'
}

for proc_name, description in processes.items():
    try:
        result = subprocess.run(['pgrep', '-f', proc_name], capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f'   ✅ {proc_name}: {len(pids)} process(es) - {description}')
            
            # Check CPU/Memory for each PID
            for pid in pids:
                if pid:
                    try:
                        p = psutil.Process(int(pid))
                        cpu = p.cpu_percent(interval=0.1)
                        mem = p.memory_info().rss / 1024 / 1024  # MB
                        print(f'      PID {pid}: CPU {cpu:.1f}%, MEM {mem:.1f}MB')
                    except:
                        pass
        else:
            print(f'   ❌ {proc_name}: NOT RUNNING - {description}')
    except Exception as e:
        print(f'   ⚠️ {proc_name}: Error checking - {e}')

print()

# 2. CHECK DASHBOARD RESPONSIVENESS
print('🌐 2. DASHBOARD RESPONSIVENESS:')
dashboards = [
    ('Common Dashboard', 'http://localhost:5007/', 'Main with P&L'),
    ('Trading Server', 'http://localhost:5001/', 'API server'),
    ('Simple P&L', 'http://localhost:5008/', 'P&L focused'),
    ('Bulletproof', 'http://localhost:5002/', 'Backup'),
    ('Simple Fixed', 'http://localhost:5003/', 'Alternative')
]

for name, url, desc in dashboards:
    try:
        import requests
        start = time.time()
        response = requests.get(url, timeout=3)
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            print(f'   ✅ {name}: {url} - {elapsed:.0f}ms - {desc}')
        else:
            print(f'   ⚠️ {name}: {url} - HTTP {response.status_code} - {desc}')
    except Exception as e:
        print(f'   ❌ {name}: {url} - OFFLINE - {desc}')

print()

# 3. CHECK TRADING DATA
print('📈 3. TRADING DATA STATUS:')
try:
    import requests
    response = requests.get('http://localhost:5007/api/data', timeout=3)
    data = response.json()
    
    positions = len(data.get('positions', []))
    capital = data.get('capital', {})
    bot_status = data.get('bot_status', {})
    
    print(f'   • Open positions: {positions}')
    print(f'   • Total capital: ${capital.get("total_capital", 0):.2f}')
    print(f'   • Available Gemini: ${capital.get("available_gemini", 0):.2f}')
    print(f'   • Bot status: {bot_status.get("status", "unknown")}')
    print(f'   • Last activity: {bot_status.get("last_activity", "None")}')
    
except Exception as e:
    print(f'   ❌ Could not fetch trading data: {e}')

print()

# 4. CHECK SYSTEM RESOURCES
print('💻 4. SYSTEM RESOURCES:')
try:
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    print(f'   • CPU Usage: {cpu_percent:.1f}%')
    print(f'   • Memory: {memory.percent:.1f}% used ({memory.used/1024/1024:.0f}MB / {memory.total/1024/1024:.0f}MB)')
    print(f'   • Disk: {disk.percent:.1f}% used ({disk.used/1024/1024/1024:.1f}GB / {disk.total/1024/1024/1024:.1f}GB)')
    
    # Check if system is overloaded
    if cpu_percent > 80:
        print('   ⚠️ WARNING: High CPU usage')
    if memory.percent > 80:
        print('   ⚠️ WARNING: High memory usage')
        
except Exception as e:
    print(f'   ❌ Could not check system resources: {e}')

print()

# 5. IDENTIFY IMPROVEMENT OPPORTUNITIES
print('🚀 5. IMPROVEMENT OPPORTUNITIES:')

improvements = []

# Check for duplicate dashboards
dashboard_count = sum(1 for proc in processes.keys() if 'dashboard' in proc)
if dashboard_count > 3:
    improvements.append(f'• Reduce duplicate dashboards ({dashboard_count} running)')

# Check bot efficiency
try:
    response = requests.get('http://localhost:5007/api/data', timeout=3)
    data = response.json()
    bot_status = data.get('bot_status', {})
    
    if bot_status.get('status') == 'waiting':
        scan_interval = bot_status.get('scan_interval', 0)
        if scan_interval > 60:
            improvements.append(f'• Optimize bot scan interval (currently {scan_interval}s)')
    
    positions = data.get('positions', [])
    if len(positions) > 0:
        # Check position diversity
        symbols = set(pos.get('symbol', '') for pos in positions)
        if len(symbols) < 2:
            improvements.append(f'• Increase position diversity (only {len(symbols)} symbol(s))')
            
except:
    pass

# Check P&L data freshness
try:
    with open('system_status.json', 'r') as f:
        system_data = json.load(f)
    
    last_updated = system_data.get('capital', {}).get('last_updated', '')
    if last_updated:
        from datetime import datetime
        last_dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
        age = (datetime.now() - last_dt).total_seconds() / 60  # minutes
        
        if age > 30:
            improvements.append(f'• Update P&L data more frequently ({age:.0f} minutes old)')
            
except:
    improvements.append('• Ensure P&L data is updated regularly')

# Check trading performance
try:
    with open('daily_trades.json', 'r') as f:
        trades = json.load(f)
    
    if isinstance(trades, list):
        today_trades = [t for t in trades if t.get('timestamp', '').startswith('2026-04-01')]
        if len(today_trades) == 0:
            improvements.append('• No trades executed today - review strategy')
            
except:
    pass

# Display improvements
if improvements:
    print('   Found areas for improvement:')
    for imp in improvements:
        print(f'   {imp}')
else:
    print('   ✅ System appears well-optimized')

print()
print('=' * 70)
print('📋 NEXT STEPS:')
print('1. Monitor trading performance throughout the day')
print('2. Review P&L trends and adjust thresholds if needed')
print('3. Consider consolidating duplicate dashboard processes')
print('4. Ensure all data is updating in real-time')
print('5. Watch for trading opportunities with 1.0% thresholds')
print()
print('✅ MONITORING ACTIVE - Will report on improvements')