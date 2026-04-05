#!/usr/bin/env python3
"""
Clean up old Binance positions to avoid confusion
Only keep active Gemini positions
"""

import json
import os
from datetime import datetime

def cleanup_positions():
    """Remove old Binance positions, keep only Gemini"""
    
    print("🧹 CLEANING UP OLD POSITIONS")
    print("=" * 60)
    
    try:
        with open('trading_data/trades.json', 'r') as f:
            trades = json.load(f)
        
        print(f"📊 Total trades before cleanup: {len(trades)}")
        
        # Keep only Gemini trades (active strategy)
        gemini_trades = [t for t in trades if t.get('exchange') == 'gemini']
        binance_trades = [t for t in trades if t.get('exchange') == 'binance']
        
        print(f"♊ Gemini trades (keeping): {len(gemini_trades)}")
        print(f"₿ Binance trades (removing): {len(binance_trades)}")
        
        # Show what we're removing
        if binance_trades:
            print("\n🔍 Binance trades being removed:")
            for trade in binance_trades:
                print(f"  • {trade.get('symbol')}: {trade.get('side')} at ${trade.get('price', 0):.4f}")
        
        # Save only Gemini trades
        with open('trading_data/trades.json', 'w') as f:
            json.dump(gemini_trades, f, indent=2)
        
        print(f"\n✅ Cleanup complete!")
        print(f"📊 Total trades after cleanup: {len(gemini_trades)}")
        print(f"🎯 Only active Gemini positions remain")
        
        # Update capital
        import trading_data
        trading_data.TradingData.update_capital()
        
        print("\n🔄 Capital recalculated based on Gemini positions only")
        
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False

def update_dashboard_note():
    """Update dashboard to reflect cleanup"""
    
    print("\n📝 UPDATING DASHBOARD NOTE")
    print("=" * 60)
    
    try:
        with open('dashboard_common.py', 'r') as f:
            content = f.read()
        
        # Remove the warning about old Binance positions
        old_warning = '''        <div class="urgent">
            <p>⚠️ <strong>NOTE:</strong> Currently only trading on ♊ GEMINI (using Binance price data)</p>
            <p>₿ Binance positions shown are OLD migrated positions from previous system</p>
        </div>'''
        
        new_warning = '''        <div class="positive">
            <p>✅ <strong>CURRENT STRATEGY:</strong> Trading only on ♊ GEMINI</p>
            <p>• Using Binance price data to detect 0.5%+ dips</p>
            <p>• Executing LONG buys on Gemini when dips detected</p>
        </div>'''
        
        content = content.replace(old_warning, new_warning)
        
        with open('dashboard_common.py', 'w') as f:
            f.write(content)
        
        print("✅ Dashboard updated to show current strategy clearly")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update dashboard: {e}")
        return False

def main():
    """Main cleanup"""
    print("🔄 CLEANING UP TRADING DATA")
    print("=" * 60)
    print("Removing confusing old Binance positions")
    print("Keeping only active Gemini strategy")
    print()
    
    if cleanup_positions():
        update_dashboard_note()
        
        print("\n" + "=" * 60)
        print("🎉 CLEANUP COMPLETE!")
        print("=" * 60)
        print("✅ Only Gemini positions remain (active strategy)")
        print("✅ Dashboard shows clear current strategy")
        print("✅ No more confusing old Binance positions")
        print()
        print("📊 Open: http://localhost:5007/")
        print("🔍 Will now show ONLY Gemini trades")
        
        # Restart dashboard
        import subprocess
        subprocess.run(['pkill', '-f', 'dashboard_common.py'], capture_output=True)
        subprocess.Popen(['python3', 'dashboard_common.py'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        print("\n🔄 Dashboard restarted with clean data")
        
    else:
        print("❌ Cleanup failed")

if __name__ == "__main__":
    main()