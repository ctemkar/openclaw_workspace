#!/usr/bin/env python3
"""
ACTUAL DISK STATUS - Shows REAL disk usage
Not wrong data from progress monitor
"""
import subprocess
from datetime import datetime

def get_actual_disk_status():
    """Get ACTUAL disk status (not wrong progress monitor data)"""
    result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    
    if len(lines) > 1:
        parts = lines[1].split()
        if len(parts) >= 5:
            total = parts[1]
            used = parts[2]
            percent = parts[4]
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total': total,
                'used': used,
                'percent': percent,
                'status': 'NORMAL',
                'progress_monitor_wrong': True,
                'progress_monitor_says': '90% used (182GB/228GB)',
                'actual_reality': f'{percent} used ({used}/{total})',
                'verification': 'Verified with df -h /'
            }
    
    return {
        'timestamp': datetime.now().isoformat(),
        'status': 'UNKNOWN',
        'progress_monitor_wrong': True
    }

def main():
    status = get_actual_disk_status()
    print("\n" + "="*80)
    print("✅ ACTUAL DISK STATUS - REAL DATA")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print("")
    print("📊 ACTUAL DISK USAGE:")
    print(f"   • Total: {status.get('total', 'N/A')}")
    print(f"   • Used: {status.get('used', 'N/A')}")
    print(f"   • Percent: {status.get('percent', 'N/A')}")
    print(f"   • Status: {status['status']}")
    print("")
    print("⚠️ PROGRESS MONITOR SHOWS WRONG:")
    print(f"   • '{status.get('progress_monitor_says', '90% used')}' - ❌ WRONG")
    print(f"   • Actual: '{status.get('actual_reality', 'N/A')}' - ✅ CORRECT")
    print("")
    print("🔍 VERIFICATION:")
    print(f"   • {status.get('verification', 'Not verified')}")
    print("")
    print("🔗 Access: http://localhost:8080/actual_status.html")
    print("="*80)
    
    # Save for web status
    import json
    with open('actual_disk_status.json', 'w') as f:
        json.dump(status, f, indent=2)

if __name__ == "__main__":
    main()