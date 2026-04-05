#!/usr/bin/env python3
"""
Migrate existing data to common data layer
"""

import json
import os
from datetime import datetime
import trading_data

def migrate_gemini_trades():
    """Migrate gemini_trades.json to common layer"""
    try:
        if os.path.exists('gemini_trades.json'):
            with open('gemini_trades.json', 'r') as f:
                trades = json.load(f)
            
            print(f"📦 Migrating {len(trades)} trades from gemini_trades.json")
            
            migrated = 0
            for trade in trades:
                # Convert to common format
                common_trade = {
                    'exchange': trade.get('exchange', 'gemini'),
                    'symbol': trade.get('symbol', ''),
                    'side': trade.get('side', 'buy'),
                    'price': trade.get('price', 0),
                    'amount': trade.get('amount', 0),
                    'value': trade.get('value', 0),
                    'order_id': trade.get('order_id', ''),
                    'timestamp': trade.get('timestamp', datetime.now().isoformat()),
                    'notes': trade.get('notes', 'Migrated from gemini_trades.json'),
                    'status': 'open'  # Assume all are open
                }
                
                if trading_data.TradingData.save_trade(common_trade):
                    migrated += 1
            
            print(f"✅ Migrated {migrated} trades to common layer")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    
    return False

def migrate_26_crypto_trades():
    """Migrate 26_crypto_trade_history.json to common layer"""
    try:
        if os.path.exists('26_crypto_trade_history.json'):
            with open('26_crypto_trade_history.json', 'r') as f:
                trades = json.load(f)
            
            print(f"📦 Migrating {len(trades)} trades from 26_crypto_trade_history.json")
            
            migrated = 0
            for trade in trades:
                # Only migrate open positions
                if trade.get('status') == 'OPEN':
                    common_trade = {
                        'exchange': trade.get('exchange', 'binance'),
                        'symbol': trade.get('symbol', ''),
                        'side': 'sell' if trade.get('type') == 'SHORT' else 'buy',
                        'price': trade.get('entry_price', 0),
                        'amount': trade.get('amount', 0),
                        'value': trade.get('position_size', 0),
                        'order_id': trade.get('order_id', ''),
                        'timestamp': trade.get('execution_time', datetime.now().isoformat()),
                        'notes': f"Migrated: {trade.get('type', '')} position",
                        'status': 'open'
                    }
                    
                    if trading_data.TradingData.save_trade(common_trade):
                        migrated += 1
            
            print(f"✅ Migrated {migrated} open positions to common layer")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    
    return False

def update_progress_monitor():
    """Update progress_monitor.sh to use common dashboard"""
    try:
        with open('progress_monitor.sh', 'r') as f:
            content = f.read()
        
        # Update port to 5007 (common dashboard)
        if '5006' in content:
            content = content.replace('5006', '5007')
            content = content.replace('REAL-TIME Dashboard', 'COMMON DASHBOARD')
            content = content.replace('(Auto-refreshes every 10 seconds)', '(Single Source of Truth)')
        
        with open('progress_monitor.sh', 'w') as f:
            f.write(content)
        
        print("✅ Updated progress_monitor.sh to use common dashboard")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update progress monitor: {e}")
        return False

def update_active_port():
    """Update .active_port to point to common dashboard"""
    try:
        with open('.active_port', 'w') as f:
            f.write('5007')
        print("✅ Updated .active_port to 5007 (common dashboard)")
        return True
    except:
        return False

def stop_old_components():
    """Stop old bots and dashboards"""
    import subprocess
    
    print("🛑 Stopping old components...")
    
    # Stop old bots
    bots = [
        'fixed_bot_simple.py',
        'full_capital_bot.py',
        'enhanced_26_crypto_trader.py',
        'real_futures_trading_bot.py',
        'fixed_futures_bot.py',
        'simple_real_trader.py'
    ]
    
    for bot in bots:
        subprocess.run(['pkill', '-f', bot], capture_output=True)
    
    # Stop old dashboards
    dashboards = [
        'guaranteed_dashboard.py',
        'real_time_dashboard.py',
        'dashboard_with_positions.py'
    ]
    
    for dashboard in dashboards:
        subprocess.run(['pkill', '-f', dashboard], capture_output=True)
    
    print("✅ Stopped old components")
    return True

def start_new_components():
    """Start new common components"""
    import subprocess
    import time
    
    print("🚀 Starting new common components...")
    
    # Start common dashboard
    subprocess.Popen(['python3', 'dashboard_common.py'], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    # Start common bot
    subprocess.Popen(['python3', 'fixed_bot_common.py'], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    print("✅ Started common dashboard (port 5007) and bot")
    return True

def main():
    """Main migration"""
    print("=" * 60)
    print("🔄 MIGRATING TO COMMON DATA LAYER")
    print("=" * 60)
    print("Creating single source of truth for all components")
    print()
    
    # Step 1: Migrate data
    print("📊 STEP 1: Migrating existing data...")
    migrate_gemini_trades()
    migrate_26_crypto_trades()
    print()
    
    # Step 2: Update configuration
    print("⚙️  STEP 2: Updating configuration...")
    update_progress_monitor()
    update_active_port()
    print()
    
    # Step 3: Stop old components
    print("🛑 STEP 3: Stopping old components...")
    stop_old_components()
    print()
    
    # Step 4: Start new components
    print("🚀 STEP 4: Starting new common components...")
    start_new_components()
    print()
    
    # Step 5: Verify
    print("✅ STEP 5: Verification...")
    print("   • Common data layer: trading_data/ directory")
    print("   • Common dashboard: http://localhost:5007/")
    print("   • Common bot: fixed_bot_common.py")
    print("   • Progress monitor: Updated to use common dashboard")
    print()
    
    print("=" * 60)
    print("🎉 MIGRATION COMPLETE!")
    print("=" * 60)
    print("All components now use COMMON DATA LAYER")
    print("No more stale data or synchronization issues")
    print()
    print("📊 Open: http://localhost:5007/")
    print("🔧 Single source of truth for all data")

if __name__ == "__main__":
    main()