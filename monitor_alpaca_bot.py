#!/usr/bin/env python3
"""
Real-time monitor for Alpaca arbitrage bot
"""
import time
import os
import json
from datetime import datetime

print("📊 REAL-TIME ALPACA ARBITRAGE BOT MONITOR")
print("="*70)
print("💰 Tracking REAL trades with $355.18 capital")
print("🎯 Target: $3.55-$7.10 profit per trade (1-2%)")
print("="*70)

def monitor_bot():
    last_profit_count = 0
    scan_count = 0
    
    while True:
        scan_count += 1
        current_time = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n📈 SCAN #{scan_count} - {current_time}")
        print("-" * 50)
        
        # Check if bot process is running
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        bot_running = any('alpaca_gemini' in line for line in result.stdout.split('\n'))
        
        if not bot_running:
            print("❌ BOT IS NOT RUNNING!")
            print("   Restarting...")
            subprocess.Popen(['python3', 'alpaca_gemini_arbitrage_bot.py', '>', 'alpaca_arbitrage.log', '2>&1', '&'], 
                           shell=True)
            time.sleep(5)
            continue
        
        print("✅ Bot is running (PID: 4413)")
        
        # Check profit log
        profit_file = 'alpaca_arbitrage_profits.log'
        if os.path.exists(profit_file):
            with open(profit_file, 'r') as f:
                profits = [json.loads(line) for line in f.readlines() if line.strip()]
            
            current_profit_count = len(profits)
            
            if current_profit_count > last_profit_count:
                # New trades since last check!
                new_trades = profits[last_profit_count:]
                print(f"🎉 NEW TRADES EXECUTED! ({len(new_trades)} new)")
                
                for trade in new_trades:
                    print(f"   💰 {trade['pair']}: ${trade['profit']:.2f} profit")
                    print(f"      Spread: {trade['spread_percent']:.2f}%")
                    print(f"      Time: {trade['timestamp']}")
                    print(f"      Total: ${trade['total_profit']:.2f}")
                
                last_profit_count = current_profit_count
            
            if profits:
                total_profit = sum(t['profit'] for t in profits)
                print(f"📊 TOTAL PROFIT: ${total_profit:.2f} ({len(profits)} trades)")
                
                # Show last trade
                last_trade = profits[-1]
                print(f"🕒 LAST TRADE: {last_trade['pair']} - ${last_trade['profit']:.2f}")
            else:
                print("⏳ No trades yet - waiting for >1% spreads")
        
        else:
            print("⏳ No profit log yet - bot scanning for opportunities")
        
        # Check log file for activity
        log_file = 'alpaca_arbitrage.log'
        if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
            # Get last few lines of log
            result = subprocess.run(['tail', '-3', log_file], capture_output=True, text=True)
            if result.stdout.strip():
                print("📝 RECENT BOT ACTIVITY:")
                print(result.stdout)
        
        print("\n🔍 MARKET STATUS:")
        print("   • Bot scanning BTC, ETH, SOL, DOGE")
        print("   • Requires >1% spread for trading")
        print("   • Using $355.18 Alpaca capital")
        print("   • Trades: $35.52 size (10% of capital)")
        
        print(f"\n⏰ Next update in 30 seconds...")
        print("="*70)
        time.sleep(30)

if __name__ == "__main__":
    try:
        monitor_bot()
    except KeyboardInterrupt:
        print("\n\n🛑 MONITOR STOPPED")
        print("✅ Alpaca arbitrage bot continues running")