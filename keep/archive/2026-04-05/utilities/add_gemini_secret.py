#!/usr/bin/env python3
"""
Add ONLY Gemini secret (key already exists)
"""

import os
import sys

print("\n" + "="*60)
print("🔑 ADD GEMINI SECRET ONLY")
print("="*60)
print("Gemini key already exists, just need secret")
print("="*60)

# Check current Gemini key
if os.path.exists("secure_keys/.gemini_key"):
    with open("secure_keys/.gemini_key", 'r') as f:
        gemini_key = f.read().strip()
    print(f"✅ Existing Gemini Key: {gemini_key[:15]}...")
else:
    print("❌ Gemini key file not found!")
    print("   Run: ./setup_keys_script.sh first")
    sys.exit(1)

# Check current Gemini secret
if os.path.exists("secure_keys/.gemini_secret"):
    with open("secure_keys/.gemini_secret", 'r') as f:
        current_secret = f.read().strip()
    if current_secret:
        print(f"\n📄 Current Gemini Secret: '{current_secret}'")
        print(f"   Length: {len(current_secret)} characters")
        replace = input("\n🔧 Replace existing secret? (yes/no): ").strip().lower()
        if replace != 'yes':
            print("✅ Keeping existing secret")
            sys.exit(0)
    else:
        print("\n❌ Gemini Secret: EMPTY FILE")
else:
    print("\n❌ Gemini Secret: FILE NOT FOUND")

print("\n" + "="*60)
print("✏️ ENTER GEMINI SECRET (Visible):")
print("="*60)
print("1. Go to gemini.com → API Settings")
print("2. Click 'Show' next to your secret")
print("3. Copy EXACT 40-character secret")
print("4. Paste below (you'll see it)")
print("="*60)
print()

new_secret = input("Gemini Secret: ").strip()

print(f"\n📋 YOU ENTERED:")
print(f"   Secret: '{new_secret}'")
print(f"   Length: {len(new_secret)} characters")

print("\n🔍 EXPECTED FORMAT:")
print("   • ~40 characters")
print("   • Example: 2pXgR9kL8zqY7wV5tS3uM6nB4cD1fG8hJ2")
print("   • No spaces at start/end")

confirm = input("\n✅ Is this correct? (yes/no): ").strip().lower()

if confirm == 'yes':
    # Ensure secure directory exists
    os.makedirs("secure_keys", exist_ok=True)
    
    # Save secret
    with open("secure_keys/.gemini_secret", 'w') as f:
        f.write(new_secret)
    
    # Set secure permissions
    os.chmod("secure_keys/.gemini_secret", 0o600)
    
    # Update symlink
    if os.path.exists(".gemini_secret"):
        os.remove(".gemini_secret")
    os.symlink("secure_keys/.gemini_secret", ".gemini_secret")
    
    print("\n" + "="*60)
    print("✅ GEMINI SECRET ADDED!")
    print("="*60)
    print(f"   Key: {gemini_key[:10]}...")
    print(f"   Secret: {new_secret[:10]}... ({len(new_secret)} chars)")
    print("   File: secure_keys/.gemini_secret")
    print("   Permissions: chmod 600")
    
    print("\n🚀 Test connection:")
    print("   python3 test_real_connections.py")
    
    print("\n💰 Next: Deposit $200 to Gemini account")
    
else:
    print("\n❌ Secret not saved. Run script again.")

print("="*60)