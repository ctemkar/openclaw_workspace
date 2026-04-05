#!/usr/bin/env python3
"""
SAFETY CHECK SYSTEM
Prevents real trading when in paper mode
All trading bots MUST import and use this
"""

import os
import json
from datetime import datetime

class TradingSafety:
    """Safety system to prevent real trading accidents"""
    
    @staticmethod
    def check_trading_mode():
        """Check if real trading is allowed"""
        safety_file = 'trading_mode.txt'
        
        # Default to PAPER mode if file doesn't exist
        if not os.path.exists(safety_file):
            print("⚠️  No trading mode file found - DEFAULTING TO PAPER MODE")
            print("🚫 REAL TRADING DISABLED FOR SAFETY")
            return False  # Paper mode
        
        # Read the safety file
        with open(safety_file, 'r') as f:
            content = f.read()
        
        # Check for paper trading mode
        if 'PAPER_TRADING_ONLY=1' in content or 'REAL_TRADING_DISABLED=1' in content:
            print("="*60)
            print("🚫 REAL TRADING DISABLED - PAPER MODE ACTIVE")
            print("="*60)
            print("This bot cannot trade with real money.")
            print("All trades will be simulated.")
            print("="*60)
            return False
        
        # Check for explicit real trading permission
        if 'REAL_TRADING_ENABLED=1' in content and 'AUTHORIZED_BY_USER=1' in content:
            print("="*60)
            print("✅ REAL TRADING ENABLED")
            print("="*60)
            print("WARNING: This bot will trade with REAL money.")
            print("Proceed with caution.")
            print("="*60)
            return True
        
        # Default to paper mode
        print("⚠️  Trading mode unclear - DEFAULTING TO PAPER MODE")
        return False
    
    @staticmethod
    def require_paper_mode():
        """Force paper mode - for testing"""
        with open('trading_mode.txt', 'w') as f:
            f.write(f"PAPER_TRADING_ONLY=1\n")
            f.write(f"REAL_TRADING_DISABLED=1\n")
            f.write(f"SAFETY_LOCK_ENABLED=1\n")
            f.write(f"LAST_UPDATED={datetime.now().isoformat()}\n")
            f.write(f"REASON=User requested paper trading mode\n")
        
        print("🔒 SAFETY LOCK ENGAGED")
        print("📝 PAPER TRADING MODE ACTIVATED")
        print("🚫 REAL TRADING DISABLED")
    
    @staticmethod
    def enable_real_trading(authorization_code="REQUIRES_USER_APPROVAL"):
        """Enable real trading (requires explicit user approval)"""
        if authorization_code != "AUTHORIZE_REAL_TRADING_NOW":
            print("❌ INVALID AUTHORIZATION CODE")
            print("🚫 REAL TRADING REMAINS DISABLED")
            print("💡 To enable real trading, provide correct authorization")
            return False
        
        with open('trading_mode.txt', 'w') as f:
            f.write(f"REAL_TRADING_ENABLED=1\n")
            f.write(f"AUTHORIZED_BY_USER=1\n")
            f.write(f"AUTHORIZATION_TIME={datetime.now().isoformat()}\n")
            f.write(f"WARNING=REAL MONEY AT RISK\n")
        
        print("="*60)
        print("⚠️  ⚠️  ⚠️  WARNING: REAL TRADING ENABLED ⚠️  ⚠️  ⚠️")
        print("="*60)
        print("This system will now trade with REAL money.")
        print("Financial losses are possible.")
        print("Proceed with extreme caution.")
        print("="*60)
        return True
    
    @staticmethod
    def get_mode_status():
        """Get current trading mode status"""
        if not os.path.exists('trading_mode.txt'):
            return "PAPER_MODE (default)"
        
        with open('trading_mode.txt', 'r') as f:
            content = f.read()
        
        if 'PAPER_TRADING_ONLY=1' in content:
            return "PAPER_MODE (enforced)"
        elif 'REAL_TRADING_ENABLED=1' in content:
            return "REAL_TRADING (authorized)"
        else:
            return "UNKNOWN (defaulting to paper)"

# Example usage for bots
def safe_trading_wrapper(func):
    """Decorator to ensure safe trading"""
    def wrapper(*args, **kwargs):
        if not TradingSafety.check_trading_mode():
            print("🔒 SAFETY CHECK FAILED - Using paper trading")
            # Modify function to use paper trading
            # This would need to be customized per bot
            return None
        return func(*args, **kwargs)
    return wrapper

if __name__ == "__main__":
    print("🔒 TRADING SAFETY SYSTEM")
    print("="*60)
    
    current_mode = TradingSafety.get_mode_status()
    print(f"Current mode: {current_mode}")
    
    # Test the safety check
    can_trade = TradingSafety.check_trading_mode()
    print(f"Can trade with real money: {can_trade}")
    
    print("\n" + "="*60)
    print("Usage in bots:")
    print("""
# At the top of your trading bot:
from safety_check import TradingSafety

if not TradingSafety.check_trading_mode():
    print("Switching to paper trading...")
    # Implement paper trading logic
    exit(0)
    
# Only reaches here if real trading is authorized
print("Real trading enabled - proceeding with caution")
    """)
    print("="*60)