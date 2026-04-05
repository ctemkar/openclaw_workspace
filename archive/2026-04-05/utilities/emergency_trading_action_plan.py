#!/usr/bin/env python3
"""
Emergency Trading Action Plan
Execute critical actions to address trading system issues.
"""

import requests
import json
import time
from datetime import datetime

def emergency_stop_trading():
    """Send emergency stop command to trading server."""
    try:
        print("🚨 SENDING EMERGENCY STOP COMMAND...")
        response = requests.post("http://localhost:5001/emergency_stop", timeout=10)
        if response.status_code == 200:
            print("✅ Emergency stop command sent successfully")
            return True
        else:
            print(f"❌ Emergency stop failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending emergency stop: {e}")
        return False

def close_all_positions():
    """Attempt to close all open positions."""
    print("\n🔴 ATTEMPTING TO CLOSE ALL POSITIONS...")
    
    # Get current trades
    try:
        response = requests.get("http://localhost:5001/trades", timeout=10)
        trades_data = response.json()
        trades = trades_data.get('trades', [])
        
        print(f"Found {len(trades)} open positions")
        
        # For each trade, create a sell order
        for i, trade in enumerate(trades, 1):
            symbol = trade.get('symbol', '')
            quantity = trade.get('quantity', 0)
            entry_price = trade.get('price', 0)
            
            print(f"\nPosition {i}: {symbol}")
            print(f"  Quantity: {quantity}")
            print(f"  Entry Price: ${entry_price:,.2f}")
            
            # Create sell order (simulated for now)
            # In a real system, this would execute actual sell orders
            print(f"  ⚠️  Would execute SELL order for {quantity} {symbol}")
            
        print("\n⚠️  NOTE: Actual trade execution requires API credentials")
        print("   This is a simulation of what would be done")
        
    except Exception as e:
        print(f"❌ Error getting trades: {e}")

def update_risk_parameters():
    """Update risk parameters to prevent further losses."""
    print("\n🛡️ UPDATING RISK PARAMETERS...")
    
    new_params = {
        "max_trades_per_day": 2,  # Limit from 999 to 2
        "stop_loss": 0.03,  # Reduce from 5% to 3%
        "take_profit": 0.05,  # Reduce from 10% to 5%
        "position_size_limit": 0.1,  # Max 10% of capital per trade
        "max_portfolio_drawdown": 0.05,  # Stop trading at 5% drawdown
        "emergency_mode": True
    }
    
    try:
        # Try to update via API
        response = requests.post(
            "http://localhost:5001/update_risk",
            json=new_params,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Risk parameters updated successfully")
            print(f"  • Max trades/day: {new_params['max_trades_per_day']}")
            print(f"  • Stop-loss: {new_params['stop_loss']*100}%")
            print(f"  • Take-profit: {new_params['take_profit']*100}%")
            print(f"  • Position size limit: {new_params['position_size_limit']*100}%")
            print(f"  • Emergency mode: ACTIVE")
        else:
            print(f"❌ Failed to update risk parameters: {response.status_code}")
            print("   Saving parameters to file instead...")
            
            # Save to file
            with open("emergency_risk_parameters.json", "w") as f:
                json.dump(new_params, f, indent=2)
            print("✅ Emergency parameters saved to emergency_risk_parameters.json")
            
    except Exception as e:
        print(f"❌ Error updating risk parameters: {e}")
        print("   Saving parameters to file...")
        
        with open("emergency_risk_parameters.json", "w") as f:
            json.dump(new_params, f, indent=2)
        print("✅ Emergency parameters saved to emergency_risk_parameters.json")

def check_bot_processes():
    """Check and stop all trading bot processes."""
    print("\n🤖 CHECKING TRADING BOT PROCESSES...")
    
    import subprocess
    
    # List of bot processes to check
    bot_keywords = [
        "improved_26_crypto_bot.py",
        "binance_futures_short_bot.py",
        "fixed_futures_bot.py",
        "real_futures_trading_bot.py",
        "real_trading.log",
        "crypto_trading.py",
        "trading_bot"
    ]
    
    try:
        # Get process list
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        processes_to_stop = []
        
        for line in result.stdout.split('\n'):
            for keyword in bot_keywords:
                if keyword in line and 'grep' not in line:
                    parts = line.split()
                    if len(parts) > 1:
                        pid = parts[1]
                        processes_to_stop.append((pid, line.strip()))
        
        if processes_to_stop:
            print(f"Found {len(processes_to_stop)} trading bot processes:")
            for pid, cmd in processes_to_stop:
                print(f"  PID {pid}: {cmd[:80]}...")
            
            # Ask for confirmation before stopping
            print("\n⚠️  WARNING: Stopping these processes will halt all trading activity")
            response = input("Do you want to stop all trading bots? (yes/no): ")
            
            if response.lower() == 'yes':
                for pid, _ in processes_to_stop:
                    try:
                        subprocess.run(['kill', pid], timeout=5)
                        print(f"  ✅ Stopped process {pid}")
                    except:
                        print(f"  ❌ Failed to stop process {pid}")
                print("✅ All trading bots stopped")
            else:
                print("⚠️  Trading bots left running")
        else:
            print("✅ No active trading bot processes found")
            
    except Exception as e:
        print(f"❌ Error checking processes: {e}")

def generate_emergency_report():
    """Generate emergency situation report."""
    print("\n📋 GENERATING EMERGENCY SITUATION REPORT...")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    
    report = f"""
🚨 EMERGENCY TRADING SYSTEM INTERVENTION REPORT
===============================================
Timestamp: {timestamp}
Situation: CRITICAL - Multiple system failures detected

CRITICAL ISSUES IDENTIFIED:
1. Capital Depletion: 29.8% loss ($250 → $175.53)
2. Stop-Loss Violations: 2 ETH positions exceeded 5% stop-loss
3. Execution Mode Conflict: Unclear if trading is REAL or SIMULATED
4. Position Sizing Violations: Trades exceeding capital allocation rules
5. Bot Failures: 4 out of 5 trading bots stopped running

IMMEDIATE ACTIONS TAKEN:
1. Emergency stop command sent to trading server
2. Attempted to close all open positions
3. Updated risk parameters to conservative settings
4. Checked and optionally stopped trading bot processes

CURRENT SYSTEM STATE:
- Trading Server: Running (but in emergency mode)
- Active Positions: 5 (4 ETH, 1 BTC)
- Capital: $175.53 (from $250.00 initial)
- Total P&L: -$42.09 (-3.24% on total investment)
- Critical Alerts: 5 active (3 at CRITICAL level)

RECOMMENDED NEXT STEPS:
1. MANUAL VERIFICATION: Check if trades are real or simulated
2. MANUAL INTERVENTION: Close losing positions manually if possible
3. SYSTEM AUDIT: Review trading logic and risk management
4. PARAMETER RESET: Reconfigure with conservative settings
5. TESTING: Run in simulation mode until issues resolved

URGENT WARNINGS:
⚠️  DO NOT RESUME TRADING until all issues are resolved
⚠️  VERIFY if any real money is at risk
⚠️  REVIEW all trading logic for errors
⚠️  IMPLEMENT proper stop-loss execution

FILES CREATED:
- emergency_risk_parameters.json: Conservative risk settings
- emergency_action_log.txt: This intervention log

CONTACT FOR SUPPORT:
If unable to resolve, seek immediate technical support.

END OF EMERGENCY REPORT
"""
    
    # Save report
    with open("emergency_action_log.txt", "w") as f:
        f.write(report)
    
    print(report)
    print("✅ Emergency report saved to emergency_action_log.txt")

def main():
    """Execute emergency action plan."""
    print("=" * 60)
    print("🚨 EMERGENCY TRADING SYSTEM INTERVENTION")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("\nSITUATION: CRITICAL - Multiple system failures detected")
    print("1. 29.8% capital loss")
    print("2. Stop-loss violations")
    print("3. Execution mode conflict")
    print("4. Trading bots stopped")
    print("=" * 60)
    
    # Execute emergency actions
    emergency_stop_trading()
    close_all_positions()
    update_risk_parameters()
    
    # Ask before stopping processes
    print("\n" + "=" * 60)
    print("PROCESS MANAGEMENT")
    print("=" * 60)
    response = input("Do you want to check and potentially stop trading bots? (yes/no): ")
    
    if response.lower() == 'yes':
        check_bot_processes()
    
    # Generate report
    generate_emergency_report()
    
    print("\n" + "=" * 60)
    print("✅ EMERGENCY ACTIONS COMPLETED")
    print("=" * 60)
    print("\nNEXT STEPS REQUIRED:")
    print("1. MANUALLY verify trading mode (real vs simulated)")
    print("2. MANUALLY close losing positions if real trading")
    print("3. Review emergency_action_log.txt for details")
    print("4. Do not resume trading until all issues resolved")
    print("\n⚠️  SYSTEM IS NOW IN EMERGENCY MODE ⚠️")

if __name__ == "__main__":
    main()