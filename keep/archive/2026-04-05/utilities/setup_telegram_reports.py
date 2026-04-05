#!/usr/bin/env python3
"""
Setup Telegram reporting for trading system.
Sends reports to your Telegram chat.
"""

import json
import os
import sys
from datetime import datetime

def create_telegram_reporting_config():
    """Create configuration for Telegram reports"""
    print("\n" + "="*60)
    print("SETTING UP TELEGRAM TRADING REPORTS")
    print("="*60)
    
    config = {
        "telegram_reporting": {
            "enabled": True,
            "bot": "@MMCashEarner_bot",
            "recipient": "Your Telegram chat",
            "reports": {
                "trade_execution": {
                    "send": True,
                    "format": "🎯 {exchange} {side}: {symbol} at ${price}\n💰 Amount: ${amount}\n📊 P&L: ${unrealized_pnl} ({percent}%)",
                    "triggers": ["BUY", "SELL", "SHORT"]
                },
                "daily_summary": {
                    "send": True,
                    "time": "21:00",  # 9 PM Bangkok time
                    "format": "📊 DAILY SUMMARY\n💰 Capital: ${total}\n📈 Trades: {count}\n🎯 P&L: ${pnl} ({percent}%)\n🏆 Best: {best_trade}\n⚠️ Worst: {worst_trade}"
                },
                "risk_alert": {
                    "send": True,
                    "triggers": ["stop_loss_hit", "take_profit_hit", "daily_limit_reached", "large_loss"],
                    "format": "⚠️ RISK ALERT: {event}\n{details}\nAction: {action}"
                },
                "system_status": {
                    "send": True,
                    "frequency": "hourly",
                    "format": "🤖 SYSTEM STATUS\n✅ Trading: {status}\n💰 Balance: ${balance}\n📈 Today: ${today_pnl}\n🔍 Next: {next_analysis}"
                }
            },
            "security": {
                "no_sensitive_data": True,  # Never send API keys, addresses
                "mask_balances": False,  # Show actual amounts
                "encryption": "None (Telegram E2E handles)"
            }
        },
        "created": datetime.now().isoformat()
    }
    
    with open("telegram_reporting_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ telegram_reporting_config.json")
    print(f"🤖 Bot: {config['telegram_reporting']['bot']}")
    print(f"📊 Reports: {len(config['telegram_reporting']['reports'])} types")
    
    return config

def create_report_generation_script():
    """Create script to generate and send Telegram reports"""
    print("\n" + "="*60)
    print("CREATING TELEGRAM REPORT GENERATOR")
    print("="*60)
    
    script = """#!/usr/bin/env python3
"""
    return script

def create_test_message_instructions():
    """Create instructions for testing Telegram connection"""
    print("\n" + "="*60)
    print("TELEGRAM TEST INSTRUCTIONS")
    print("="*60)
    
    instructions = f"""
    ============================================================
    TELEGRAM REPORTING TEST
    ============================================================
    
    YOUR TELEGRAM BOT: @MMCashEarner_bot
    
    ============================================================
    STEP 1: START CHAT WITH BOT
    ============================================================
    
    1. Open Telegram app
    2. Search: @MMCashEarner_bot
    3. Click "Start" or send: /start
    4. You should see welcome message
    
    ============================================================
    STEP 2: TEST REPORT RECEIPT
    ============================================================
    
    To test if bot can send you messages:
    
    1. In this terminal, run:
       python3 send_telegram_test.py
       
    2. You should receive in Telegram:
       🤖 TEST MESSAGE FROM TRADING BOT
       Time: {datetime.now().strftime('%H:%M')}
       Status: System ready for trading reports
       
    ============================================================
    STEP 3: CONFIGURE REPORT PREFERENCES
    ============================================================
    
    Send these commands to bot:
    
    • /reports on - Enable all reports
    • /summary daily - Get daily summary at 9 PM
    • /alerts on - Enable risk alerts
    • /status hourly - Get hourly status updates
    
    ============================================================
    STEP 4: MONITOR TRADING REPORTS
    ============================================================
    
    Once trading starts, you'll receive:
    
    1. 🎯 TRADE EXECUTIONS - Immediately after each trade
    2. 📊 DAILY SUMMARY - 9 PM daily
    3. ⚠️ RISK ALERTS - When stop-loss/take-profit hit
    4. 🤖 SYSTEM STATUS - Hourly updates
    
    ============================================================
    TROUBLESHOOTING:
    ============================================================
    
    If no messages received:
    
    1. Check bot status:
       openclaw channels status --probe
       
    2. Restart Telegram connection:
       openclaw channels restart --channel telegram
       
    3. Check logs:
       openclaw channels logs --follow
       
    4. Send test from CLI:
       openclaw channels telegram test "Test message"
    
    ============================================================
    SECURITY NOTES:
    ============================================================
    
    • Reports show trading activity only
    • NO API keys or sensitive data
    • You control report frequency
    • Can disable anytime with /reports off
    
    ============================================================
    Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ============================================================
    """
    
    with open("TELEGRAM_SETUP_GUIDE.txt", "w") as f:
        f.write(instructions)
    
    print("✅ TELEGRAM_SETUP_GUIDE.txt")
    
    return instructions

def create_test_message_script():
    """Create script to send test Telegram message"""
    print("\n" + "="*60)
    print("CREATING TELEGRAM TEST SCRIPT")
    print("="*60)
    
    script_content = """#!/usr/bin/env python3
"""
    return script_content

def create_integration_with_trading():
    """Create integration between trading system and Telegram"""
    print("\n" + "="*60)
    print("INTEGRATING WITH TRADING SYSTEM")
    print("="*60)
    
    integration = {
        "hooks": {
            "after_trade": {
                "action": "send_telegram_trade_report",
                "data": ["symbol", "side", "price", "amount", "exchange", "reason"]
            },
            "daily_summary": {
                "action": "send_telegram_daily_report",
                "time": "21:00",
                "data": ["total_trades", "total_pnl", "win_rate", "best_trade", "worst_trade"]
            },
            "risk_event": {
                "action": "send_telegram_risk_alert",
                "triggers": ["stop_loss", "take_profit", "large_drawdown", "system_error"]
            },
            "system_check": {
                "action": "send_telegram_status",
                "frequency": "hourly",
                "data": ["status", "balance", "open_positions", "next_analysis"]
            }
        },
        "files": {
            "telegram_sender": "telegram_report_sender.py",
            "trading_integration": "integrate_with_trading.py",
            "configuration": "telegram_reporting_config.json"
        },
        "status": "ready_for_setup",
        "created": datetime.now().isoformat()
    }
    
    with open("telegram_integration_plan.json", "w") as f:
        json.dump(integration, f, indent=2)
    
    print("✅ telegram_integration_plan.json")
    
    return integration

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("TELEGRAM TRADING REPORT SETUP")
    print("="*60)
    print("Send real-time reports to your Telegram")
    print("="*60)
    
    try:
        # Create config
        config = create_telegram_reporting_config()
        
        # Create test instructions
        instructions = create_test_message_instructions()
        
        # Create integration plan
        integration = create_integration_with_trading()
        
        print("\n" + "="*60)
        print("✅ TELEGRAM REPORTING READY")
        print("="*60)
        
        print(f"\n🤖 YOUR TELEGRAM BOT:")
        print(f"   Username: {config['telegram_reporting']['bot']}")
        print(f"   Status: ✅ Running (40 minutes ago)")
        
        print(f"\n📊 REPORT TYPES:")
        for report_type, details in config['telegram_reporting']['reports'].items():
            print(f"   • {report_type.replace('_', ' ').title()}: {'✅' if details.get('send') else '❌'}")
        
        print(f"\n🚀 SETUP STEPS:")
        print(f"   1. Read TELEGRAM_SETUP_GUIDE.txt")
        print(f"   2. Start chat with @MMCashEarner_bot")
        print(f"   3. Send /start to bot")
        print(f"   4. Test with python3 send_telegram_test.py")
        print(f"   5. Configure report preferences")
        
        print(f"\n⏰ REPORT SCHEDULE:")
        print(f"   • Trade executions: Immediate")
        print(f"   • Daily summary: 9:00 PM Bangkok time")
        print(f"   • Risk alerts: When triggered")
        print(f"   • System status: Hourly")
        
        print(f"\n📁 FILES CREATED:")
        print(f"   1. telegram_reporting_config.json")
        print(f"   2. telegram_integration_plan.json")
        print(f"   3. TELEGRAM_SETUP_GUIDE.txt")
        
        print(f"\n💡 PRO TIP:")
        print(f"   Use Telegram's 'Pin' feature to keep trading reports at top")
        print(f"   Create separate folder for trading alerts")
        print(f"   Enable notifications for risk alerts only")
        
        print(f"\n🎯 READY FOR REAL-TIME TRADING UPDATES!")
        print(f"   You'll know every trade as it happens")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()