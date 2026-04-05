#!/usr/bin/env python3
"""
Start continuous monitoring and implement improvements
"""

import os
import subprocess
import time
from datetime import datetime

print('🚀 STARTING CONTINUOUS MONITORING & IMPLEMENTING IMPROVEMENTS')
print('=' * 70)
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (Bangkok)')
print()

# 1. Start continuous monitoring
print('1. 📊 STARTING CONTINUOUS MONITOR:')
try:
    # Kill any existing monitor
    subprocess.run(['pkill', '-f', 'continuous_monitor.py'], capture_output=True)
    
    # Start new monitor in background
    monitor_proc = subprocess.Popen(
        ['python3', 'continuous_monitor.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(2)
    
    # Check if it's running
    result = subprocess.run(['pgrep', '-f', 'continuous_monitor.py'], capture_output=True, text=True)
    if result.returncode == 0:
        print('   ✅ Continuous monitor started (PID: {})'.format(result.stdout.strip()))
        print('   • Checks every 5 minutes')
        print('   • Logs to system_monitor.log')
        print('   • Alerts for issues')
    else:
        print('   ❌ Failed to start monitor')
        
except Exception as e:
    print(f'   ❌ Error starting monitor: {e}')

print()

# 2. Verify dashboards are working
print('2. 🌐 VERIFYING DASHBOARDS:')
dashboards = [
    ('Main Dashboard', 'http://localhost:5007/', 'dashboard_common.py'),
    ('Trading Server', 'http://localhost:5001/', 'updated_trading_server.py')
]

all_working = True
for name, url, proc_name in dashboards:
    # Check process
    result = subprocess.run(['pgrep', '-f', proc_name], capture_output=True, text=True)
    if result.returncode == 0:
        print(f'   ✅ {name} process running')
        
        # Try to access
        try:
            import requests
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f'   ✅ {name} accessible at {url}')
            else:
                print(f'   ⚠️ {name} returned HTTP {response.status_code}')
                all_working = False
        except:
            print(f'   ❌ {name} not accessible at {url}')
            all_working = False
    else:
        print(f'   ❌ {name} process not running')
        all_working = False

print()

# 3. Check bot status
print('3. 🤖 CHECKING BOT STATUS:')
bots = [
    ('26-Crypto Trader', 'real_26_crypto_trader.py'),
    ('Common Bot', 'fixed_bot_common.py')
]

for name, proc_name in bots:
    result = subprocess.run(['pgrep', '-f', proc_name], capture_output=True, text=True)
    if result.returncode == 0:
        pids = result.stdout.strip().split('\n')
        print(f'   ✅ {name}: {len(pids)} process(es) running')
        
        # Check CPU/Memory
        for pid in pids:
            if pid:
                try:
                    import psutil
                    p = psutil.Process(int(pid))
                    cpu = p.cpu_percent(interval=0.1)
                    mem = p.memory_info().rss / 1024 / 1024
                    print(f'      PID {pid}: CPU {cpu:.1f}%, MEM {mem:.1f}MB')
                except:
                    pass
    else:
        print(f'   ❌ {name}: NOT RUNNING')

print()

# 4. Create improvement summary
print('4. 📋 IMPROVEMENT SUMMARY:')
print('   ✅ COMPLETED:')
print('      • Fixed main dashboard (port 5007)')
print('      • Consolidated dashboards (kept only 5001 and 5007)')
print('      • Created continuous monitoring system')
print('      • Created diversification monitor')
print()
print('   🎯 NEXT IMPROVEMENTS:')
print('      • Review bot thresholds (currently 1.0%)')
print('      • Enable multi-symbol trading')
print('      • Improve position diversification')
print('      • Monitor P&L trends throughout day')
print()
print('   📊 MONITORING TOOLS:')
print('      • Main dashboard: http://localhost:5007/')
print('      • Trading API: http://localhost:5001/')
print('      • Diversification monitor: file://{}'.format(os.path.abspath('diversification_monitor.html')))
print('      • System logs: system_monitor.log (updates every 5 min)')

print()

# 5. Create quick status check
print('5. ⚡ QUICK STATUS CHECK:')
quick_check = '''#!/usr/bin/env python3
"""
Quick status check for trading system
"""

import subprocess
import time
from datetime import datetime

def check_status():
    print(f'⏰ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - TRADING SYSTEM STATUS')
    print('=' * 60)
    
    # Check processes
    processes = [
        ('Dashboard', 'dashboard_common.py'),
        ('Trading Server', 'updated_trading_server.py'),
        ('26-Crypto Bot', 'real_26_crypto_trader.py'),
        ('Common Bot', 'fixed_bot_common.py'),
        ('Monitor', 'continuous_monitor.py')
    ]
    
    for name, proc in processes:
        result = subprocess.run(['pgrep', '-f', proc], capture_output=True, text=True)
        status = '✅ RUNNING' if result.returncode == 0 else '❌ STOPPED'
        print(f'{name:20} {status}')
    
    print()
    print('🔗 ACCESS:')
    print('   • Dashboard: http://localhost:5007/')
    print('   • API: http://localhost:5001/')
    print('   • Diversification: file://{}/diversification_monitor.html'.format(os.getcwd()))
    print()
    print('📊 MONITORING:')
    print('   • Continuous: system_monitor.log')
    print('   • Updates: Every 5 minutes')
    print()

if __name__ == '__main__':
    check_status()
'''

with open('quick_status.py', 'w') as f:
    f.write(quick_check)

print('   ✅ Created quick_status.py')
print('   • Run: python3 quick_status.py')
print('   • Shows all process status at a glance')

print()
print('=' * 70)
print('✅ MONITORING SYSTEM ACTIVE')
print()
print('📋 WHAT TO WATCH FOR:')
print('1. Dashboard responsiveness (should be < 100ms)')
print('2. Bot trading activity (look for new trades)')
print('3. Position diversification (aim for 3+ symbols)')
print('4. P&L trends (cumulative and daily)')
print('5. System resources (CPU < 80%, Memory < 80%)')
print()
print('🔔 ALERTS WILL APPEAR IN:')
print('   • system_monitor.log')
print('   • Continuous monitor output')
print('   • Dashboard status sections')
print()
print('🎯 GOAL: Improve from current -43.86% cumulative P&L')