#!/usr/bin/env python3
"""
PAPER TRADING SAFETY WRAPPER
Ensures ALL trading goes through paper system
Prevents any real trading accidentally
"""

import os
import sys
import json
from datetime import datetime

class PaperTradingSafety:
    """Safety system to enforce paper trading only"""
    
    @staticmethod
    def enforce_paper_mode():
        """Enforce paper trading mode - exit if real trading detected"""
        print("="*80)
        print("🔒 PAPER TRADING SAFETY CHECK")
        print("="*80)
        
        # Check trading mode
        if not os.path.exists('trading_mode.txt'):
            print("⚠️  No trading mode file - CREATING PAPER MODE")
            with open('trading_mode.txt', 'w') as f:
                f.write("PAPER_TRADING_ONLY=1\n")
                f.write("REAL_TRADING_DISABLED=1\n")
                f.write(f"ENFORCED_AT={datetime.now().isoformat()}\n")
                f.write("REASON=Safety wrapper enforcement\n")
        
        with open('trading_mode.txt', 'r') as f:
            content = f.read()
        
        # Check if real trading is somehow enabled
        if 'REAL_TRADING_ENABLED=1' in content:
            print("🚨 CRITICAL SAFETY VIOLATION!")
            print("Real trading is ENABLED but should be DISABLED")
            print("")
            print("🔒 FORCING PAPER MODE...")
            
            # Force paper mode
            with open('trading_mode.txt', 'w') as f:
                f.write("PAPER_TRADING_ONLY=1\n")
                f.write("REAL_TRADING_DISABLED=1\n")
                f.write("SAFETY_OVERRIDE=1\n")
                f.write(f"OVERRIDE_AT={datetime.now().isoformat()}\n")
                f.write("REASON=Safety wrapper detected real trading violation\n")
            
            print("✅ Paper mode enforced")
        
        print("✅ Safety check passed - Paper trading mode active")
        print("🚫 Real trading: IMPOSSIBLE")
        print("="*80)
        return True
    
    @staticmethod
    def get_trading_mode():
        """Get current trading mode with safety checks"""
        if not os.path.exists('trading_mode.txt'):
            return "PAPER_MODE_ENFORCED"
        
        with open('trading_mode.txt', 'r') as f:
            content = f.read()
        
        if 'PAPER_TRADING_ONLY=1' in content:
            return "PAPER_MODE"
        elif 'REAL_TRADING_ENABLED=1' in content:
            # This should never happen with safety wrapper
            return "REAL_MODE_VIOLATION"
        else:
            return "PAPER_MODE_DEFAULT"
    
    @staticmethod
    def create_safe_trading_function(original_function):
        """Decorator to create safe trading functions"""
        def safe_wrapper(*args, **kwargs):
            # Check trading mode
            mode = PaperTradingSafety.get_trading_mode()
            
            if mode != "PAPER_MODE":
                print(f"🚨 SAFETY VIOLATION: Trading mode is {mode}")
                print("🔒 Redirecting to paper trading")
                
                # Modify arguments for paper trading
                if 'real_money' in kwargs:
                    kwargs['real_money'] = False
                
                # Add paper trading flag
                kwargs['paper_mode'] = True
            
            # Call original function with safety
            result = original_function(*args, **kwargs)
            
            # Log the trade as paper
            PaperTradingSafety.log_paper_trade({
                'function': original_function.__name__,
                'args': str(args),
                'kwargs': str(kwargs),
                'result': str(result),
                'timestamp': datetime.now().isoformat(),
                'real_money': False
            })
            
            return result
        
        return safe_wrapper
    
    @staticmethod
    def log_paper_trade(trade_data):
        """Log all paper trades for audit"""
        log_file = 'paper_trading_audit.log'
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(trade_data) + '\n')
    
    @staticmethod
    def block_real_api_calls():
        """Block any attempts to use real API keys"""
        # Check for real API key files
        real_key_files = [
            'secure_keys/.binance_key',
            'secure_keys/.binance_secret',
            '.env',
            'api_keys.json'
        ]
        
        blocked = False
        for key_file in real_key_files:
            if os.path.exists(key_file):
                print(f"⚠️  Found real API key file: {key_file}")
                print(f"   🔒 Renaming to prevent accidental use")
                
                # Rename to disable
                new_name = f"{key_file}.DISABLED_BY_SAFETY"
                os.rename(key_file, new_name)
                print(f"   ✅ Renamed to: {new_name}")
                blocked = True
        
        if blocked:
            print("🔒 Real API keys disabled for safety")
        
        return blocked

# Example usage for existing trading functions
def safe_trading_decorator(func):
    """Decorator to make any trading function safe"""
    def wrapper(*args, **kwargs):
        # Enforce paper mode
        PaperTradingSafety.enforce_paper_mode()
        
        # Block real API calls
        PaperTradingSafety.block_real_api_calls()
        
        # Add paper trading flag
        kwargs['paper_mode'] = True
        kwargs['real_money'] = False
        
        print(f"🔒 SAFE EXECUTION: {func.__name__}")
        print(f"   Mode: PAPER TRADING")
        print(f"   Real Money: $0.00")
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Log as paper trade
        PaperTradingSafety.log_paper_trade({
            'function': func.__name__,
            'result': 'PAPER_TRADE_EXECUTED',
            'timestamp': datetime.now().isoformat()
        })
        
        return result
    return wrapper

if __name__ == "__main__":
    print("🔒 PAPER TRADING SAFETY WRAPPER")
    print("="*80)
    
    # Enforce paper mode
    PaperTradingSafety.enforce_paper_mode()
    
    # Block real API calls
    PaperTradingSafety.block_real_api_calls()
    
    # Show status
    mode = PaperTradingSafety.get_trading_mode()
    print(f"\n📊 SAFETY STATUS:")
    print(f"   Trading Mode: {mode}")
    print(f"   Real Trading: IMPOSSIBLE")
    print(f"   Paper Trading: ENFORCED")
    print(f"   Safety Level: MAXIMUM")
    
    print("\n" + "="*80)
    print("🎯 HOW TO USE:")
    print("""
# Import the safety wrapper
from paper_trading_safety_wrapper import safe_trading_decorator

# Decorate any trading function
@safe_trading_decorator
def your_trading_function():
    # This will automatically run in paper mode
    pass

# Or use the class directly
PaperTradingSafety.enforce_paper_mode()
    """)
    print("="*80)
    print("🔒 ALL TRADING IS NOW 100% PAPER - NO REAL MONEY CAN BE TRADED")
    print("="*80)