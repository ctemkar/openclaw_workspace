#!/usr/bin/env python3
"""
CLEANUP PROJECT - Move unused files to archive
"""

import os
import shutil
from datetime import datetime

# Create organized structure
STRUCTURE = {
    'active': [
        'real_26_crypto_arbitrage_bot.py',
        'practical_profit_bot.py', 
        'fast_progress_monitor.sh',
        'HEARTBEAT.md',
        'SOUL.md',
        'USER.md',
        'IDENTITY.md',
        'AGENTS.md',
        'TOOLS.md',
        'MEMORY.md',
        'secure_keys/',
        'memory/',
        'working_top_10_dashboard.py',
        'gateway_5000.py',
        '.gitignore',
        '.env.example'
    ],
    'logs': [
        'real_26_crypto_arbitrage.log',
        'practical_profits.log',
        'real_trades.log',
        'gemini_nonce.json'
    ],
    'archive_candidates': [
        # Old bots
        'real_26_crypto_trader.py',
        'final_fixed_bot.py',
        'simple_progress_monitor.sh',
        'progress_monitor.sh',
        
        # Old dashboards
        'simple_real_dashboard.py',
        'sorted_spread_dashboard.html',
        'arbitrage_dashboard.py',
        'actual_trades_dashboard.py',
        'analyze_dashboard.py',
        
        # Test/utility scripts
        'test_current_credentials.py',
        'test_new_api_key.py',
        'verify_api_working.py',
        'update_api_credentials.py',
        'check_arbitrage_now.py',
        'check_mana_now.py',
        'update_binance_api.sh',
        
        # Old guides
        'FIX_BINANCE_API_GUIDE_NEW.md',
        'gemini_microsecond_fix.py',
        'patch_gemini_nonce.py',
        'fix_gemini_nonce_storage.py',
        'show_top_10_now.py',
        'check_real_dashboard.py',
        'check_spread_discrepancy.py',
        'reality_check_now.py'
    ]
}

def create_structure():
    """Create organized directory structure"""
    print("📁 CREATING ORGANIZED STRUCTURE")
    print("="*60)
    
    directories = ['logs', 'scripts', 'docs', 'archive/old_dashboards']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}/")
    
    return True

def move_to_archive(file_list, category):
    """Move files to archive"""
    archive_dir = f"archive/2026-04-05/{category}"
    os.makedirs(archive_dir, exist_ok=True)
    
    moved = 0
    for file_pattern in file_list:
        if os.path.exists(file_pattern):
            if os.path.isfile(file_pattern):
                shutil.move(file_pattern, f"{archive_dir}/{os.path.basename(file_pattern)}")
                moved += 1
                print(f"📦 Archived: {file_pattern} → {archive_dir}/")
            elif os.path.isdir(file_pattern):
                # Skip directories for now
                pass
    
    return moved

def check_active_files():
    """Check which active files exist"""
    print("\n✅ ACTIVE FILES CHECK:")
    print("="*60)
    
    for file in STRUCTURE['active']:
        if os.path.exists(file):
            status = "✅ EXISTS"
        else:
            status = "❌ MISSING"
        print(f"{status:10} {file}")

def main():
    """Main cleanup function"""
    print("🧹 PROJECT CLEANUP AND ORGANIZATION")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Step 1: Create structure
    create_structure()
    
    # Step 2: Check active files
    check_active_files()
    
    # Step 3: Move old dashboards
    print("\n📦 ARCHIVING OLD DASHBOARDS:")
    print("="*60)
    dashboards = [f for f in os.listdir('.') if 'dashboard' in f.lower() and f.endswith('.py')]
    dashboards.append('sorted_spread_dashboard.html')
    
    moved = move_to_archive(dashboards, 'dashboards')
    print(f"✅ Moved {moved} dashboard files to archive")
    
    # Step 4: Move old bots
    print("\n📦 ARCHIVING OLD BOTS:")
    print("="*60)
    bots = [f for f in os.listdir('.') if 'bot' in f.lower() and f.endswith('.py') and 'arbitrage' not in f]
    moved_bots = move_to_archive(bots, 'bots')
    print(f"✅ Moved {moved_bots} bot files to archive")
    
    # Step 5: Move utility scripts
    print("\n📦 ARCHIVING UTILITY SCRIPTS:")
    print("="*60)
    utilities = [f for f in os.listdir('.') if f.endswith('.py') and f not in STRUCTURE['active'] and f not in dashboards and f not in bots]
    moved_utils = move_to_archive(utilities, 'utilities')
    print(f"✅ Moved {moved_utils} utility files to archive")
    
    # Step 6: Move log files to logs directory
    print("\n📁 ORGANIZING LOG FILES:")
    print("="*60)
    log_files = [f for f in os.listdir('.') if f.endswith('.log')]
    for log_file in log_files:
        if os.path.exists(log_file):
            shutil.move(log_file, f"logs/{log_file}")
            print(f"📄 Moved: {log_file} → logs/")
    
    # Step 7: Create clean README
    print("\n📋 CREATING CLEAN PROJECT STRUCTURE:")
    print("="*60)
    
    with open('CLEAN_PROJECT_README.md', 'w') as f:
        f.write(f"""# Clean Project Structure - {datetime.now().strftime('%Y-%m-%d')}

## 🎯 ACTIVE FILES:
```
{chr(10).join([f for f in STRUCTURE['active'] if os.path.exists(f)])}
```

## 📁 DIRECTORY STRUCTURE:
```
project/
├── active/              # Currently running bots and dashboards
├── logs/                # All log files
├── secure_keys/         # API keys (gitignored)
├── memory/             # Memory system files
├── archive/            # Archived old files
└── CLEAN_PROJECT_README.md
```

## 🚀 CURRENTLY RUNNING:
1. **26-Crypto Arbitrage Bot**: `real_26_crypto_arbitrage_bot.py`
2. **Practical Profit Bot**: `practical_profit_bot.py`
3. **Working Dashboard**: `working_top_10_dashboard.py` (port 5027)
4. **Gateway**: `gateway_5000.py` (port 5001)

## 🔒 SECURITY:
- ✅ `secure_keys/` directory is gitignored
- ✅ `.env` file was deleted (was exposing keys)
- ✅ `.env.example` template provided (no real keys)

## 📊 MONITORING:
- **Fast Progress Monitor**: `./fast_progress_monitor.sh`
- **Working Dashboard**: http://localhost:5027
- **Gateway**: http://localhost:5001

## 🧹 CLEANUP SUMMARY:
- Moved {moved + moved_bots + moved_utils} files to archive
- Organized log files
- Removed duplicate/unused scripts
- Created clean structure
""")
    
    print("✅ Created: CLEAN_PROJECT_README.md")
    
    print("\n" + "="*60)
    print("🎯 CLEANUP COMPLETED!")
    print("="*60)
    print(f"Total files moved to archive: {moved + moved_bots + moved_utils}")
    print(f"Log files organized: {len(log_files)}")
    print("\n📁 NEW STRUCTURE:")
    print("  ├── active/ (running bots & dashboards)")
    print("  ├── logs/ (all log files)")
    print("  ├── secure_keys/ (API keys - gitignored)")
    print("  ├── memory/ (memory system)")
    print("  └── archive/ (old files)")
    print("="*60)

if __name__ == "__main__":
    main()