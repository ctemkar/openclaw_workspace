#!/usr/bin/env python3
"""
Update trading bot to check futures wallet for USDT
"""

import os

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"
BOT_FILE = os.path.join(BASE_DIR, "simple_26_crypto_bot.py")

def update_bot_for_futures():
    """Update bot to check futures balance"""
    print("Updating trading bot to check futures wallet...")
    
    if not os.path.exists(BOT_FILE):
        print(f"❌ Bot file not found: {BOT_FILE}")
        return False
    
    with open(BOT_FILE, 'r') as f:
        content = f.read()
    
    # Find the balance checking function
    # We need to update the check_balance function
    
    # Look for the check_balance function
    if 'def check_balance' in content:
        print("✅ Found balance checking function")
        
        # Create updated version
        new_balance_func = '''
def check_balance(exchange_obj):
    """Check exchange balance - including futures"""
    try:
        balance = exchange_obj.fetch_balance()
        
        # Check USDT for Binance, USD for Gemini
        if isinstance(exchange_obj, ccxt.binance):
            # First check spot
            usdt_spot = balance.get('USDT', {}).get('free', 0)
            
            # Also try to check futures if spot is empty
            if usdt_spot < 50:
                try:
                    # Try futures account
                    futures_exchange = ccxt.binance({
                        'apiKey': exchange_obj.apiKey,
                        'secret': exchange_obj.secret,
                        'options': {'defaultType': 'future'},
                        'enableRateLimit': True
                    })
                    futures_balance = futures_exchange.fetch_balance()
                    usdt_futures = futures_balance.get('USDT', {}).get('free', 0)
                    
                    if usdt_futures > 0:
                        print(f"  ⚠️  USDT in FUTURES wallet: ${usdt_futures:.2f}")
                        print(f"  💡 Transfer to SPOT wallet for trading")
                        # Return futures balance for info, but trading needs spot
                        return usdt_futures
                except:
                    pass
            
            print(f"  USDT Balance (SPOT): ${usdt_spot:.2f}")
            return usdt_spot
            
        elif isinstance(exchange_obj, ccxt.gemini):
            usd = balance.get('USD', {}).get('free', 0)
            print(f"  USD Balance: ${usd:.2f}")
            return usd
        
        return 0
    except Exception as e:
        print(f"  Error checking balance: {e}")
        return 0
'''
        
        # Replace the function
        import re
        pattern = r'def check_balance\(exchange_obj\):.*?return 0'
        
        # Use DOTALL flag to match across multiple lines
        updated_content = re.sub(pattern, new_balance_func, content, flags=re.DOTALL)
        
        if updated_content != content:
            with open(BOT_FILE, 'w') as f:
                f.write(updated_content)
            print("✅ Bot updated to check futures wallet")
            return True
        else:
            print("⚠️  Could not update balance function")
            return False
    else:
        print("❌ Could not find check_balance function")
        return False

def create_futures_transfer_guide():
    """Create guide for transferring from futures to spot"""
    guide = """
    HOW TO TRANSFER USDT FROM FUTURES TO SPOT WALLET
    ================================================
    
    YOUR SITUATION:
    • You have $77.68 USDT
    • It's in FUTURES wallet
    • Trading bot needs it in SPOT wallet
    • Transfer takes 2 minutes
    
    STEP-BY-STEP:
    1. Go to Binance.com
    2. Click "Wallet" → "Overview"
    3. Find "USDT" in your assets list
    4. Click "Transfer" (next to USDT)
    5. Select:
       • From: Futures USDⓈ-M
       • To: Spot
       • Amount: $50.00 (or more)
    6. Click "Confirm"
    
    VERIFICATION:
    1. After transfer, check Spot wallet
    2. Should show $50+ USDT
    3. Trading bot will detect it immediately
    
    WHY THIS MATTERS:
    • Spot trading = Buying/selling actual crypto
    • Futures trading = Contracts (not actual crypto)
    • Our bot does SPOT trading
    • Needs funds in SPOT wallet
    
    ALTERNATIVE:
    If you prefer, I can update the bot to trade futures instead.
    But spot trading is safer for beginners.
    
    TIME REQUIRED: 2 minutes
    """
    
    guide_file = os.path.join(BASE_DIR, "TRANSFER_FUTURES_TO_SPOT_GUIDE.txt")
    with open(guide_file, 'w') as f:
        f.write(guide)
    
    print(f"✅ Transfer guide saved: {guide_file}")
    return guide_file

def main():
    """Main function"""
    print("FIX BINANCE FUTURES WALLET ISSUE")
    print("=" * 70)
    print("Your $77.68 USDT is in FUTURES wallet")
    print("Trading bot checks SPOT wallet")
    print("=" * 70)
    
    print("\nOPTION 1: QUICK FIX (Recommended)")
    print("  Transfer $50+ from Futures → Spot wallet")
    print("  Time: 2 minutes")
    
    print("\nOPTION 2: UPDATE BOT")
    print("  Modify bot to check futures wallet")
    print("  But futures trading is more complex")
    
    choice = input("\nChoose: (1) Transfer funds, (2) Update bot, (3) Both? [1/2/3]: ").strip()
    
    if choice in ['2', '3']:
        updated = update_bot_for_futures()
        if updated:
            print("\n✅ Bot updated to check futures wallet")
            print("   Will still need spot funds for actual trading")
    
    if choice in ['1', '3']:
        guide = create_futures_transfer_guide()
        print(f"\n📋 Transfer guide created: {guide}")
        print("\n🚀 Please transfer $50+ from Futures to Spot now")
        print("   Then the trading bot will work immediately")
    
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print("• Funds: $77.68 USDT in Futures wallet")
    print("• Needed: $50+ in Spot wallet")
    print("• Action: Transfer or update bot")
    print("• Time: 2 minutes")
    print("=" * 70)

if __name__ == "__main__":
    main()