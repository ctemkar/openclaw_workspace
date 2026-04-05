#!/usr/bin/env python3
"""
PATCH GEMINI NONCE TO USE MICROSECONDS
- Updates final_fixed_bot.py to use microseconds (1000000x)
- Prevents nonce collisions in high-frequency trading
"""

import os

def patch_final_fixed_bot():
    """Patch final_fixed_bot.py to use microsecond nonces"""
    
    file_path = "final_fixed_bot.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find and replace millisecond nonces with microsecond nonces
    changes_made = 0
    
    # Patch 1: load_last_nonce function
    if 'int(time.time() * 1000)' in content:
        content = content.replace('int(time.time() * 1000)', 'int(time.time() * 1000000)')
        changes_made += 1
        print("✅ Patched: load_last_nonce() - milliseconds → microseconds")
    
    # Patch 2: get_next_nonce function
    if 'max(self.last_nonce + 1000, int(time.time() * 1000))' in content:
        content = content.replace('max(self.last_nonce + 1000, int(time.time() * 1000))', 
                                 'max(self.last_nonce + 1000000, int(time.time() * 1000000))')
        changes_made += 1
        print("✅ Patched: get_next_nonce() - milliseconds → microseconds")
    
    # Patch 3: Add comment about microsecond fix
    if '# Gemini with file-based nonce' in content:
        # Add explanation comment
        comment = """        # Gemini with file-based nonce (MICROSECONDS)
        # Using microseconds (1000000x) instead of milliseconds (1000x)
        # Prevents nonce collisions in high-frequency trading"""
        content = content.replace('# Gemini with file-based nonce', comment)
        changes_made += 1
        print("✅ Added microsecond explanation comment")
    
    # Write patched file
    if changes_made > 0:
        backup_path = file_path + '.backup'
        os.rename(file_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Successfully patched {file_path}")
        print(f"✅ Changes made: {changes_made}")
        
        # Show the patched sections
        print("\n📋 PATCHED SECTIONS:")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '1000000' in line or 'microsecond' in line.lower():
                print(f"  Line {i+1}: {line.strip()}")
        
        return True
    else:
        print("❌ No changes needed - file already uses microseconds")
        return False

def check_current_nonce_implementation():
    """Check current nonce implementation in trading bots"""
    print("\n" + "="*60)
    print("🔍 CHECKING CURRENT NONCE IMPLEMENTATIONS")
    print("="*60)
    
    files_to_check = [
        "final_fixed_bot.py",
        "practical_profit_bot.py", 
        "real_26_crypto_arbitrage_bot.py",
        "real_26_crypto_trader.py"
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"\n📄 {file}:")
            with open(file, 'r') as f:
                content = f.read()
                
            # Check for nonce patterns
            if 'nonce' in content.lower():
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'nonce' in line.lower() or '1000' in line or 'time.time()' in line:
                        print(f"  Line {i+1}: {line.strip()}")
            else:
                print("  No nonce implementation found")

def main():
    """Main function"""
    print("🔧 PATCH GEMINI NONCE TO USE MICROSECONDS")
    print("="*60)
    print("Problem: Current bots use milliseconds (1000x)")
    print("Solution: Patch to use microseconds (1000000x)")
    print("="*60)
    
    # Check current implementation
    check_current_nonce_implementation()
    
    print("\n" + "="*60)
    print("🛠️  APPLYING PATCH")
    print("="*60)
    
    # Apply patch
    success = patch_final_fixed_bot()
    
    if success:
        print("\n" + "="*60)
        print("✅ PATCH APPLIED SUCCESSFULLY!")
        print("="*60)
        print("Next steps:")
        print("1. Restart the trading bot: python3 final_fixed_bot.py")
        print("2. Monitor real_trades.log for Gemini API errors")
        print("3. Check if nonce collisions are resolved")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("⚠️  NO PATCH APPLIED")
        print("="*60)
        print("Either:")
        print("1. File already uses microseconds")
        print("2. File doesn't exist")
        print("3. No nonce implementation found")
        print("="*60)

if __name__ == "__main__":
    main()