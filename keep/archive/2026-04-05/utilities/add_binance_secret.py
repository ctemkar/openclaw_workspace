#!/usr/bin/env python3
"""
Add/Update ONLY Binance secret (key already exists)
"""

import os
import sys

print("\n" + "="*60)
print("🔑 ADD/UPDATE BINANCE SECRET ONLY")
print("="*60)
print("Binance key already exists, update secret")
print("="*60)

# Check current Binance key
if os.path.exists("secure_keys/.binance_key"):
    with open("secure_keys/.binance_key", 'r') as f:
        binance_key = f.read().strip()
    print(f"✅ Existing Binance Key: {binance_key[:15]}...")
else:
    print("❌ Binance key file not found!")
    print("   Run: ./setup_keys_script.sh first")
    sys.exit(1)

# Check current Binance secret
if os.path.exists("secure_keys/.binance_secret"):
    with open("secure_keys/.binance_secret", 'r') as f:
        current_secret = f.read().strip()
    if current_secret:
        print(f"\n📄 Current Binance Secret: '{current_secret}'")
        print(f"   Length: {len(current_secret)} characters")
        print("\n⚠️ Previous error: 'Signature not valid'")
        print("   This secret might be wrong")
        replace = input("\n🔧 Replace with correct secret? (yes/no): ").strip().lower()
        if replace != 'yes':
            print("✅ Keeping existing secret (might still fail)")
            sys.exit(0)
    else:
        print("\n❌ Binance Secret: EMPTY FILE")
else:
    print("\n❌ Binance Secret: FILE NOT FOUND")

print("\n" + "="*60)
print("✏️ ENTER CORRECT BINANCE SECRET (Visible):")
print("="*60)
print("1. Go to binance.com → API Management")
print("2. Click 'Show' next to your secret")
print("3. Copy EXACT 64+ character secret")
print("4. Paste below (you'll see it)")
print("="*60)
print("⚠️ COMMON MISTAKES:")
print("   • Missing first/last character")
print("   • Hidden spaces before/after")
print("   • Wrong character (0 vs O, 1 vs l)")
print("="*60)
print()

new_secret = input("Binance Secret: ").strip()

print(f"\n📋 YOU ENTERED:")
print(f"   Secret: '{new_secret}'")
print(f"   Length: {len(new_secret)} characters")

print("\n🔍 EXPECTED FORMAT:")
print("   • 64+ characters")
print("   • No spaces at start/end")
print("   • Example: abc123DEF456ghi789JKL012mno345PQR678stu901VWX234yz")

confirm = input("\n✅ Is this EXACTLY correct? (yes/no): ").strip().lower()

if confirm == 'yes':
    # Ensure secure directory exists
    os.makedirs("secure_keys", exist_ok=True)
    
    # Save secret
    with open("secure_keys/.binance_secret", 'w') as f:
        f.write(new_secret)
    
    # Set secure permissions
    os.chmod("secure_keys/.binance_secret", 0o600)
    
    # Update symlink
    if os.path.exists(".binance_secret"):
        os.remove(".binance_secret")
    os.symlink("secure_keys/.binance_secret", ".binance_secret")
    
    print("\n" + "="*60)
    print("✅ BINANCE SECRET UPDATED!")
    print("="*60)
    print(f"   Key: {binance_key[:10]}...")
    print(f"   Secret: {new_secret[:10]}... ({len(new_secret)} chars)")
    print("   File: secure_keys/.binance_secret")
    print("   Permissions: chmod 600")
    
    print("\n🔌 Test connection:")
    print("   python3 test_real_connections.py")
    
    print("\n⚠️ If still fails:")
    print("   1. Verify IP restrictions: 127.0.0.1 + 115.87.79.55")
    print("   2. Check permissions: 'Spot & Margin Trading' ONLY")
    print("   3. Re-copy secret EXACTLY from Binance")
    
    print("\n💰 Next: Deposit $50 to Binance account")
    
else:
    print("\n❌ Secret not saved. Run script again.")

print("="*60)