#!/usr/bin/env python3
"""
Simple Trading Dashboard - Quick overview of trading system
"""

import json
import requests
import subprocess
import time
import os
from datetime import datetime
import psutil

def get_bot_status():
    """Check status of all trading bots"""
    bots = []
    
    bot_definitions = [
        {"name": "Real Gemini Trader", "process_name": "real_gemini_trader.py"},
        {"name": "Trading Server", "process_name": "trading_server.py"},
        {"name": "26 Crypto Live Bot", "process_name": "improved_26_crypto_bot.py"},
        {"name": "Binance Futures Bot", "process_name": "binance_futures_short_bot.py"},
        {"name": "Simple Crypto Bot", "process_name": "simple_26_crypto_bot"},
    ]
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            for bot_def in bot_definitions:
                if bot_def["process_name"] in cmdline:
                    create_time = datetime.fromtimestamp(proc.create_time())
                    uptime = datetime.now() - create_time
                    uptime_str = str(uptime).split('.')[0]
                    
                    bots.append({
                        "name": bot_def["name"],
                        "running": True,
                        "pid": proc.info['pid'],
                        "uptime": uptime_str
                    })
        except:
            continue
    
    return bots

def get_trading_status():
    """Get trading system status"""
    try:
        response = requests.get('http://localhost:5001/status', timeout=3)
        return response.json()
    except:
        return {"error": "Cannot connect to trading server"}

def get_recent_trades():
    """Get recent trades"""
    try:
        response = requests.get('http://localhost:5001/trades', timeout=3)
        return response.json()
    except:
        return {"error": "Cannot fetch trades"}

def display_dashboard():
    """Display the dashboard in terminal"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("="*80)
    print("🚀 REAL-TIME TRADING DASHBOARD")
    print("="*80)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Get bot status
    bots = get_bot_status()
    active_bots = len([b for b in bots if b["running"]])
    
    print(f"\n🤖 BOT STATUS ({active_bots} active)")
    print("-"*40)
    for bot in bots:
        status = "✅ RUNNING" if bot["running"] else "❌ STOPPED"
        pid_info = f"(PID: {bot['pid']})" if bot["pid"] else ""
        print(f"  {bot['name']:30} {status:15} {pid_info}")
        if bot["running"]:
            print(f"      ↳ Uptime: {bot['uptime']}")
    
    # Get trading status
    print(f"\n📈 TRADING SYSTEM")
    print("-"*40)
    status = get_trading_status()
    if "error" not in status:
        print(f"  Status: ✅ {status.get('status', 'Unknown')}")
        print(f"  Capital: ${status.get('capital', 0):.2f}")
        print(f"  Pairs: {', '.join(status.get('trading_pairs', []))}")
        risk = status.get('risk_parameters', {})
        print(f"  Risk: {risk.get('stop_loss', 0)*100}% SL, {risk.get('take_profit', 0)*100}% TP")
        print(f"  Max trades/day: {risk.get('max_trades_per_day', 0)}")
        print(f"  Last analysis: {status.get('last_analysis', 'N/A').replace('T', ' ')[:19]}")
    else:
        print(f"  ❌ {status['error']}")
    
    # Get recent trades
    print(f"\n💰 RECENT TRADES")
    print("-"*40)
    trades_data = get_recent_trades()
    if "error" not in trades_data:
        trades = trades_data.get('trades', [])
        count = trades_data.get('count', 0)
        print(f"  Total trades: {count}")
        
        for i, trade in enumerate(trades[:5], 1):
            symbol = trade.get('symbol', 'Unknown')
            side = trade.get('side', 'Unknown').upper()
            price = trade.get('price', 0)
            time_str = trade.get('time', '')
            model = trade.get('model', '')
            
            side_color = "🟢" if side.lower() == 'buy' else "🔴"
            print(f"  {i}. {side_color} {symbol:10} {side:5} ${price:,.2f}")
            if time_str or model:
                details = []
                if time_str: details.append(f"Time: {time_str}")
                if model: details.append(f"Model: {model}")
                print(f"      ↳ {' | '.join(details)}")
    else:
        print(f"  ❌ {trades_data['error']}")
    
    # Check logs for recent activity
    print(f"\n📝 RECENT ACTIVITY")
    print("-"*40)
    log_files = ["26_crypto_live_trading.log", "critical_alerts.log"]
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()[-3:]  # Last 3 lines
                    if lines:
                        print(f"  {log_file}:")
                        for line in lines[-3:]:
                            line = line.strip()
                            if line:
                                # Extract time and message
                                if ' - ' in line:
                                    time_part, msg = line.split(' - ', 1)
                                    print(f"      {time_part[-8:]} {msg[:60]}...")
                                else:
                                    print(f"      {line[:70]}...")
            except:
                pass
    
    print("\n" + "="*80)
    print("🔄 Auto-refreshing every 10 seconds (Ctrl+C to stop)")
    print("="*80)

def main():
    """Main function"""
    try:
        while True:
            display_dashboard()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == '__main__':
    main()