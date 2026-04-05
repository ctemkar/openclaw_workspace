#!/usr/bin/env python3
"""
FIX GEMINI NONCE STORAGE
- Converts stored millisecond nonce to microseconds
- Ensures nonce always increases significantly
"""

import json
import os
import time

def fix_nonce_storage():
    """Fix the gemini_nonce.json file"""
    
    nonce_file = "gemini_nonce.json"
    
    if not os.path.exists(nonce_file):
        print(f"❌ No nonce file found: {nonce_file}")
        print("✅ Creating new nonce file with microsecond nonce...")
        
        # Create new file with current microsecond nonce
        current_nonce = int(time.time() * 1000000)
        data = {"last_nonce": current_nonce}
        
        with open(nonce_file, 'w') as f:
            json.dump(data, f)
        
        print(f"✅ Created {nonce_file} with nonce: {current_nonce}")
        return True
    
    # Read existing nonce
    with open(nonce_file, 'r') as f:
        data = json.load(f)
    
    old_nonce = data.get('last_nonce', 0)
    
    print(f"📊 Current stored nonce: {old_nonce}")
    print(f"📊 Current time (seconds): {time.time()}")
    print(f"📊 Current time (milliseconds): {int(time.time() * 1000)}")
    print(f"📊 Current time (microseconds): {int(time.time() * 1000000)}")
    
    # Check if nonce is in milliseconds or microseconds
    if old_nonce < 1000000000000:  # Less than 1 trillion (likely milliseconds)
        print(f"🔍 Nonce appears to be in MILLISECONDS")
        
        # Convert to microseconds
        new_nonce = old_nonce * 1000
        print(f"🔧 Converting: {old_nonce} ms → {new_nonce} μs")
        
        # Add a buffer to ensure it's higher than current time
        current_micro = int(time.time() * 1000000)
        if new_nonce < current_micro:
            new_nonce = current_micro + 1000000  # Add 1 second buffer
            print(f"🔧 Adjusting to: {new_nonce} μs (current + 1 sec)")
        
        data['last_nonce'] = new_nonce
        
        # Write back
        with open(nonce_file, 'w') as f:
            json.dump(data, f)
        
        print(f"✅ Fixed nonce storage: {new_nonce} μs")
        return True
    else:
        print(f"✅ Nonce already in MICROSECONDS: {old_nonce}")
        
        # Still check if it's significantly higher than current time
        current_micro = int(time.time() * 1000000)
        if old_nonce <= current_micro:
            print(f"⚠️  Nonce ({old_nonce}) ≤ current time ({current_micro})")
            
            # Increment significantly
            new_nonce = current_micro + 10000000  # Add 10 seconds buffer
            data['last_nonce'] = new_nonce
            
            with open(nonce_file, 'w') as f:
                json.dump(data, f)
            
            print(f"✅ Updated nonce to: {new_nonce} μs")
            return True
        
        return False

def test_nonce_generation():
    """Test nonce generation"""
    print("\n" + "="*60)
    print("🧪 TESTING NONCE GENERATION")
    print("="*60)
    
    # Generate 5 nonces quickly
    print("Generating 5 nonces in rapid succession:")
    nonces = []
    for i in range(5):
        nonce = int(time.time() * 1000000)
        nonces.append(nonce)
        print(f"  Nonce {i+1}: {nonce}")
        time.sleep(0.001)  # 1ms delay
    
    # Check for uniqueness
    unique_nonces = len(set(nonces))
    print(f"\n📊 Unique nonces: {unique_nonces}/5")
    
    if unique_nonces == 5:
        print("✅ All nonces are unique!")
    else:
        print("❌ Some nonces are duplicates!")
        
        # Show duplicates
        from collections import Counter
        counts = Counter(nonces)
        for nonce, count in counts.items():
            if count > 1:
                print(f"  Nonce {nonce} appears {count} times")

def main():
    """Main function"""
    print("🔧 FIX GEMINI NONCE STORAGE")
    print("="*60)
    print("Problem: Stored nonce is in milliseconds, causing collisions")
    print("Solution: Convert to microseconds and ensure significant increments")
    print("="*60)
    
    # Fix nonce storage
    fixed = fix_nonce_storage()
    
    if fixed:
        print("\n" + "="*60)
        print("✅ NONCE STORAGE FIXED!")
        print("="*60)
        
        # Show the fixed file
        with open("gemini_nonce.json", 'r') as f:
            data = json.load(f)
        print(f"Updated nonce: {data['last_nonce']}")
        
        # Test nonce generation
        test_nonce_generation()
        
        print("\n" + "="*60)
        print("🎯 NEXT STEPS:")
        print("1. Restart the trading bot: python3 final_fixed_bot.py")
        print("2. The bot will now use the fixed microsecond nonce")
        print("3. Monitor real_trades.log for Gemini API success")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("⚠️  NO FIX NEEDED")
        print("="*60)
        print("Nonce storage already in good state")
        print("="*60)

if __name__ == "__main__":
    main()