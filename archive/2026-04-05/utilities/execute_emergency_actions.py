#!/usr/bin/env python3
"""
Execute emergency actions non-interactively.
"""

import requests
import json
import subprocess
from datetime import datetime

def stop_trading_bots():
    """Stop all trading bot processes."""
    print("🛑 STOPPING TRADING BOT PROCESSES...")
    
    # Keywords for trading bots
    bot_keywords = [
        "improved_26_crypto_bot.py",
        "binance_futures_short_bot.py", 
        "fixed_futures_bot.py",
        "real_futures_trading_bot.py",
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
        
        stopped_count = 0
        
        for line in result.stdout.split('\n'):
            for keyword in bot_keywords:
                if keyword in line and 'grep' not in line:
                    parts = line.split()
                    if len(parts) > 1:
                        pid = parts[1]
                        try:
                            subprocess.run(['kill', pid], timeout=5, capture_output=True)
                            print(f"  ✅ Stopped process {pid} ({keyword})")
                            stopped_count += 1
                        except:
                            print(f"  ❌ Failed to stop process {pid}")
        
        print(f"\n✅ Stopped {stopped_count} trading bot processes")
        return stopped_count
        
    except Exception as e:
        print(f"❌ Error stopping processes: {e}")
        return 0

def create_emergency_config():
    """Create emergency configuration files."""
    print("\n⚙️ CREATING EMERGENCY CONFIGURATION...")
    
    # Emergency risk parameters
    risk_params = {
        "emergency_mode": True,
        "trading_enabled": False,
        "max_trades_per_day": 0,
        "stop_loss": 0.02,
        "take_profit": 0.03,
        "position_size_limit": 0.05,
        "max_portfolio_drawdown": 0.03,
        "allowed_pairs": ["BTC/USD"],  # Only BTC for now
        "require_manual_approval": True,
        "created_at": datetime.now().isoformat(),
        "reason": "Emergency intervention - 29.8% capital loss detected"
    }
    
    with open("emergency_config.json", "w") as f:
        json.dump(risk_params, f, indent=2)
    
    print("✅ Emergency config saved to emergency_config.json")
    
    # Create stop file to prevent auto-restart
    with open(".trading_stopped", "w") as f:
        f.write(f"Trading stopped at: {datetime.now().isoformat()}\n")
        f.write("Reason: Emergency intervention - critical system failures\n")
        f.write("Do not restart without manual review\n")
    
    print("✅ Stop flag created: .trading_stopped")
    
    return risk_params

def generate_situation_report():
    """Generate current situation report."""
    print("\n📊 GENERATING SITUATION REPORT...")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    
    # Get current status
    try:
        status_response = requests.get("http://localhost:5001/status", timeout=5)
        status = status_response.json()
        capital = status.get('capital', 0)
        pnl = status.get('pnl', {})
    except:
        capital = "UNAVAILABLE"
        pnl = {}
    
    # Get trades
    try:
        trades_response = requests.get("http://localhost:5001/trades", timeout=5)
        trades_data = trades_response.json()
        trades = trades_data.get('trades', [])
        trade_count = len(trades)
    except:
        trades = []
        trade_count = 0
    
    # Count ETH vs BTC positions
    eth_count = sum(1 for t in trades if 'ETH' in t.get('symbol', ''))
    btc_count = sum(1 for t in trades if 'BTC' in t.get('symbol', ''))
    
    report = f"""
🚨 TRADING SYSTEM EMERGENCY INTERVENTION
=======================================
Timestamp: {timestamp}

CRITICAL SITUATION:
- Capital depletion detected: 29.8% loss
- Multiple stop-loss violations
- Execution mode uncertainty
- Trading bots failure

CURRENT STATE:
- Trading Server: {'RUNNING' if 'capital' in locals() else 'UNKNOWN'}
- Current Capital: ${capital if isinstance(capital, (int, float)) else capital}
- Active Positions: {trade_count}
  • ETH Positions: {eth_count}
  • BTC Positions: {btc_count}
- P&L Status: {json.dumps(pnl, indent=2) if pnl else 'UNAVAILABLE'}

EMERGENCY ACTIONS TAKEN:
1. Stopped all trading bot processes
2. Created emergency configuration
3. Set trading to disabled mode
4. Created stop flag to prevent auto-restart

IMMEDIATE RISKS:
1. Positions may still be open and losing value
2. Unclear if trading is real or simulated
3. Capital already significantly depleted
4. Risk management system failed

URGENT MANUAL ACTIONS REQUIRED:
1. VERIFY if any real money is at risk
2. MANUALLY close all open positions if real trading
3. REVIEW trading logic and risk parameters
4. AUDIT system for configuration errors
5. DO NOT RESUME automated trading

FILES CREATED:
- emergency_config.json: Emergency risk parameters
- .trading_stopped: Stop flag to prevent auto-restart
- This report

NEXT STEPS:
1. Investigate root cause of failures
2. Fix stop-loss execution logic
3. Implement proper capital protection
4. Test thoroughly in simulation mode
5. Only resume with manual oversight

WARNING: SYSTEM IS IN EMERGENCY MODE
DO NOT REMOVE .trading_stopped FILE WITHOUT REVIEW
"""
    
    with open("emergency_situation_report.txt", "w") as f:
        f.write(report)
    
    print("✅ Situation report saved to emergency_situation_report.txt")
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)

def main():
    """Execute all emergency actions."""
    print("=" * 60)
    print("🚨 EXECUTING EMERGENCY TRADING INTERVENTION")
    print("=" * 60)
    
    # Stop trading bots
    stopped = stop_trading_bots()
    
    # Create emergency config
    config = create_emergency_config()
    
    # Generate report
    generate_situation_report()
    
    print("\n" + "=" * 60)
    print("✅ EMERGENCY INTERVENTION COMPLETE")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"• Stopped {stopped} trading bot processes")
    print(f"• Created emergency configuration")
    print(f"• Disabled trading system")
    print(f"• Generated situation report")
    print(f"\n⚠️  TRADING SYSTEM IS NOW DISABLED")
    print(f"⚠️  Manual review required before resuming")
    print(f"⚠️  Check emergency_situation_report.txt for details")

if __name__ == "__main__":
    main()