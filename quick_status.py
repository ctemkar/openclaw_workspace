#!/usr/bin/env python3
"""
Quick status check for trading system
"""

import subprocess
import time
import os
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
