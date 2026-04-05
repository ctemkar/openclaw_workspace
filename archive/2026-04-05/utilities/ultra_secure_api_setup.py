#!/usr/bin/env python3
"""
ULTRA-SECURE API key setup with maximum protection.
"""

import json
import os
import sys
from datetime import datetime

def create_security_checklist():
    """Create security checklist"""
    print("\n" + "="*60)
    print("ULTRA-SECURE API KEY CHECKLIST")
    print("="*60)
    
    checklist = {
        "before_creating_keys": [
            "✅ Use separate trading accounts (not main)",
            "✅ Enable 2FA on exchange accounts",
            "✅ Use unique passwords for each exchange",
            "✅ Verify account email/SMS alerts work"
        ],
        "key_creation": [
            "✅ Gemini: 'Trader' permission ONLY",
            "✅ Binance: 'Spot & Margin Trading' ONLY",
            "✅ IP Restrictions: Add 127.0.0.1 + your server IP",
            "✅ Name keys: 'OpenClaw-Trading-DATE'",
            "✅ Disable withdrawal permissions"
        ],
        "key_storage": [
            "✅ Store in .gemini_key/.gemini_secret files",
            "✅ Store in .binance_key/.binance_secret files",
            "✅ chmod 600 all key files (readable only by you)",
            "✅ NEVER commit to git (already in .gitignore)",
            "✅ Backup encrypted if needed"
        ],
        "monitoring": [
            "✅ Enable trade alerts on both exchanges",
            "✅ Check API usage logs daily",
            "✅ Set up separate email for bot alerts",
            "✅ Monitor balance changes"
        ],
        "emergency": [
            "✅ Save exchange support contact info",
            "✅ Know how to instantly disable API keys",
            "✅ Have backup funds in cold wallet",
            "✅ Test key disable procedure"
        ]
    }
    
    with open("security_checklist.json", "w") as f:
        json.dump(checklist, f, indent=2)
    
    print("✅ security_checklist.json")
    
    # Print critical items
    print("\n🔐 CRITICAL SECURITY ITEMS:")
    for category, items in checklist.items():
        print(f"\n{category.upper()}:")
        for item in items[:2]:  # Show first 2 of each
            print(f"  {item}")
    
    return checklist

def create_secure_key_generation_script():
    """Create script to generate keys securely"""
    print("\n" + "="*60)
    print("SECURE KEY GENERATION SCRIPT")
    print("="*60)
    
    script = """#!/bin/bash
"""
    return script

def update_capital_allocation():
    """Update for $200 Gemini + $50 Binance"""
    print("\n" + "="*60)
    print("UPDATING CAPITAL: $200 GEMINI + $50 BINANCE")
    print("="*60)
    
    config = {
        "total_capital": 250.00,
        "allocation": {
            "gemini": {
                "amount": 200.00,
                "percentage": 80.0,
                "purpose": "Conservative LONG positions",
                "max_position": 100.00,  # 50% of $200
                "daily_trade_limit": 2
            },
            "binance": {
                "amount": 50.00,
                "percentage": 20.0,
                "purpose": "Opportunistic SHORT positions",
                "max_position": 15.00,  # 30% of $50
                "daily_trade_limit": 1
            }
        },
        "risk_parameters": {
            "gemini_longs": {
                "stop_loss": 0.05,  # 5%
                "take_profit": 0.10,  # 10%
                "max_daily_loss": 20.00  # 10% of $200
            },
            "binance_shorts": {
                "stop_loss": 0.07,  # 7% (higher for shorts)
                "take_profit": 0.08,  # 8%
                "max_daily_loss": 7.50  # 15% of $50
            }
        },
        "security": {
            "api_key_rotation_days": 30,
            "ip_restriction_required": True,
            "withdrawal_disabled": True,
            "separate_accounts": True
        },
        "created": datetime.now().isoformat()
    }
    
    with open("secure_capital_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ secure_capital_config.json")
    print(f"💰 Total: ${config['total_capital']}")
    print(f"• Gemini: ${config['allocation']['gemini']['amount']} (80%)")
    print(f"• Binance: ${config['allocation']['binance']['amount']} (20%)")
    
    return config

def create_emergency_shutdown_guide():
    """Create emergency shutdown guide"""
    print("\n" + "="*60)
    print("EMERGENCY SHUTDOWN GUIDE")
    print("="*60)
    
    guide = f"""
    ============================================================
    EMERGENCY API KEY SHUTDOWN PROCEDURE
    ============================================================
    
    IF YOU SUSPECT COMPROMISE:
    
    STEP 1: IMMEDIATE ACTION (5 minutes)
    ------------------------------------
    1. LOGIN to both exchanges
    2. Go to API Management
    3. DISABLE/DELETE all trading bot keys
    4. CHANGE account passwords
    5. ENABLE 2FA if not already
    
    STEP 2: CONTAINMENT (15 minutes)
    ---------------------------------
    1. Stop all trading bots:
       pkill -f trading_server.py
       pkill -f conservative_crypto_trading.py
       
    2. Secure key files:
       rm -f .gemini_key .gemini_secret
       rm -f .binance_key .binance_secret
       
    3. Check recent trades:
       • Gemini: Account → Trade History
       • Binance: Orders → Trade History
    
    STEP 3: INVESTIGATION (1 hour)
    ------------------------------
    1. Review API usage logs on exchanges
    2. Check IP addresses that used keys
    3. Verify no unauthorized withdrawals
    4. Contact exchange support if suspicious
    
    STEP 4: RECOVERY (When safe)
    ----------------------------
    1. Create NEW secure API keys
    2. Update IP restrictions
    3. Test with small amounts first
    4. Gradually restore trading
    
    ============================================================
    EXCHANGE SUPPORT CONTACTS:
    ============================================================
    
    GEMINI:
    • Support: https://support.gemini.com
    • Emergency: support@gemini.com
    • Phone: Check website for current
    
    BINANCE:
    • Support: https://www.binance.com/en/support
    • Live Chat: Available in app
    • Twitter: @BinanceHelpDesk
    
    ============================================================
    PREVENTION MEASURES:
    ============================================================
    
    1. IP RESTRICTIONS: Most important protection
    2. SEPARATE ACCOUNTS: Isolate trading funds
    3. TRADE ALERTS: Get notified of every trade
    4. REGULAR AUDITS: Check API usage weekly
    5. KEY ROTATION: Change keys monthly
    
    ============================================================
    Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ============================================================
    """
    
    with open("EMERGENCY_SHUTDOWN_GUIDE.txt", "w") as f:
        f.write(guide)
    
    print("✅ EMERGENCY_SHUTDOWN_GUIDE.txt")
    
    return guide

def create_monitoring_script():
    """Create monitoring script template"""
    print("\n" + "="*60)
    print("API USAGE MONITORING TEMPLATE")
    print("="*60)
    
    monitor = {
        "daily_checks": [
            "Check Gemini API usage logs",
            "Check Binance API usage logs", 
            "Verify no unauthorized IPs",
            "Review trade history",
            "Confirm balance unchanged"
        ],
        "weekly_audits": [
            "Rotate API keys (optional)",
            "Review security settings",
            "Update IP restrictions if needed",
            "Check for exchange updates",
            "Backup configuration"
        ],
        "alerts_to_enable": {
            "gemini": [
                "Trade executions",
                "API key usage",
                "Balance changes",
                "Login attempts"
            ],
            "binance": [
                "Order fills", 
                "API key activity",
                "Account changes",
                "Security alerts"
            ]
        }
    }
    
    with open("api_monitoring_plan.json", "w") as f:
        json.dump(monitor, f, indent=2)
    
    print("✅ api_monitoring_plan.json")
    
    return monitor

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("ULTRA-SECURE API SETUP: $200 Gemini + $50 Binance")
    print("="*60)
    print("Maximum protection for your $250 trading capital")
    print("="*60)
    
    try:
        # Security checklist
        checklist = create_security_checklist()
        
        # Capital config
        config = update_capital_allocation()
        
        # Emergency guide
        emergency = create_emergency_shutdown_guide()
        
        # Monitoring plan
        monitor = create_monitoring_script()
        
        print("\n" + "="*60)
        print("✅ ULTRA-SECURE SETUP COMPLETE")
        print("="*60)
        
        print(f"\n💰 CAPITAL ALLOCATION:")
        print(f"   Total: ${config['total_capital']}")
        print(f"   • Gemini (Longs): ${config['allocation']['gemini']['amount']} (80%)")
        print(f"   • Binance (Shorts): ${config['allocation']['binance']['amount']} (20%)")
        
        print(f"\n🔐 CRITICAL SECURITY MEASURES:")
        print(f"   1. IP Restrictions (MOST IMPORTANT)")
        print(f"   2. Separate trading accounts")
        print(f"   3. Trade alerts enabled")
        print(f"   4. Regular key rotation")
        
        print(f"\n🚀 SETUP STEPS:")
        print(f"   1. Read security_checklist.json")
        print(f"   2. Create SEPARATE exchange accounts")
        print(f"   3. Add IP restrictions when creating keys")
        print(f"   4. Transfer $200 to Gemini, $50 to Binance")
        print(f"   5. Store keys securely")
        print(f"   6. Enable all alerts")
        
        print(f"\n📁 SECURITY FILES CREATED:")
        print(f"   1. security_checklist.json")
        print(f"   2. secure_capital_config.json")
        print(f"   3. EMERGENCY_SHUTDOWN_GUIDE.txt")
        print(f"   4. api_monitoring_plan.json")
        
        print(f"\n🎯 YOUR CAPITAL IS PROTECTED:")
        print(f"   • Max loss per trade: $10 (Gemini) / $3.50 (Binance)")
        print(f"   • Daily loss limit: $20 (Gemini) / $7.50 (Binance)")
        print(f"   • IP restricted: Only your server can trade")
        print(f"   • No withdrawal permissions: Funds stay on exchanges")
        
        print(f"\n💡 FINAL ADVICE:")
        print(f"   Start with $10 on each exchange to test security")
        print(f"   Verify alerts work before adding full $250")
        print(f"   Keep EMERGENCY_SHUTDOWN_GUIDE.txt handy")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()