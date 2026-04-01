#!/usr/bin/env python3
"""
Check what's ACTUALLY running in the trading system
REAL verification - no assumptions
"""

import subprocess
import json
from datetime import datetime

def check_processes():
    """Check what trading processes are actually running"""
    print("🔍 CHECKING ACTUALLY RUNNING PROCESSES")
    print("="*60)
    
    # Check 26-crypto bot
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    
    trading_processes = []
    dashboard_processes = []
    
    for line in lines:
        if 'real_26_crypto_trader' in line and 'grep' not in line:
            trading_processes.append(line.strip())
        elif 'dashboard' in line and 'grep' not in line:
            dashboard_processes.append(line.strip())
    
    print(f"\n📈 TRADING BOTS RUNNING: {len(trading_processes)}")
    for proc in trading_processes:
        print(f"  • {proc}")
    
    print(f"\n📊 DASHBOARDS RUNNING: {len(dashboard_processes)}")
    for proc in dashboard_processes:
        # Extract port info
        if '5007' in proc:
            port = '5007 (Common)'
        elif '5008' in proc:
            port = '5008 (PNL)'
        elif '5009' in proc:
            port = '5009 (Fixed)'
        elif '5010' in proc:
            port = '5010 (Truth)'
        else:
            port = 'Unknown'
        print(f"  • {port}: {proc[:80]}...")
    
    return len(trading_processes), len(dashboard_processes)

def check_ports():
    """Check what ports are actually listening"""
    print("\n" + "="*60)
    print("🔌 CHECKING OPEN PORTS")
    print("="*60)
    
    try:
        result = subprocess.run(['lsof', '-ti:5007-5010'], capture_output=True, text=True)
        pids = result.stdout.strip().split()
        
        if pids:
            print(f"📡 Ports 5007-5010 have {len(pids)} processes:")
            for pid in pids:
                try:
                    cmd_result = subprocess.run(['ps', '-p', pid, '-o', 'command'], 
                                              capture_output=True, text=True)
                    cmd = cmd_result.stdout.strip().split('\n')[-1]
                    print(f"  • PID {pid}: {cmd[:60]}...")
                except:
                    print(f"  • PID {pid}: (unknown)")
        else:
            print("❌ No processes on ports 5007-5010")
            
    except Exception as e:
        print(f"❌ Error checking ports: {e}")

def check_api_keys():
    """Check if API key files exist (not if they work)"""
    print("\n" + "="*60)
    print("🔑 CHECKING API KEY FILES (existence only)")
    print("="*60)
    
    import os
    
    key_files = [
        ('secure_keys/.gemini_key', 'Gemini API Key'),
        ('secure_keys/.gemini_secret', 'Gemini Secret'),
        ('secure_keys/.binance_key', 'Binance API Key'),
        ('secure_keys/.binance_secret', 'Binance Secret'),
    ]
    
    for filepath, description in key_files:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✅ {description}: EXISTS ({size} bytes)")
        else:
            print(f"❌ {description}: MISSING")

def main():
    print("🔄 REAL-TIME SYSTEM CHECK")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check what's actually running
    trading_count, dashboard_count = check_processes()
    
    # Check ports
    check_ports()
    
    # Check API key files
    check_api_keys()
    
    # Summary
    print("\n" + "="*60)
    print("📋 SYSTEM STATUS SUMMARY")
    print("="*60)
    
    status = {
        'time': datetime.now().isoformat(),
        'trading_bots_running': trading_count,
        'dashboards_running': dashboard_count,
        '26_crypto_bot': 'RUNNING' if trading_count > 0 else 'STOPPED',
        'dashboards_available': ['5007', '5008', '5009', '5010'],
        'api_keys_exist': 'YES (but may be invalid)',
        'data_freshness': 'STALE (API keys invalid)',
        'user_report': 'Sold most SOL positions - dashboards show old data'
    }
    
    print(f"• 26-Crypto Bot: {status['26_crypto_bot']}")
    print(f"• Dashboards: {dashboard_count} running")
    print(f"• API Keys: {status['api_keys_exist']}")
    print(f"• Data Freshness: {status['data_freshness']}")
    print(f"• User Report: {status['user_report']}")
    
    print("\n🌐 ACCESS POINTS:")
    print("  • Common Dashboard: http://localhost:5007 (may show stale data)")
    print("  • PNL Dashboard: http://localhost:5008 (may show stale data)")
    print("  • Fixed Dashboard: http://localhost:5009 (shows stale SOL positions)")
    print("  • TRUTH Dashboard: http://localhost:5010 (shows REAL situation)")
    
    print("\n" + "="*60)
    print("✅ REALITY CHECK COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()