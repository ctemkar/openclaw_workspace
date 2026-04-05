#!/usr/bin/env python3
"""
Add Binance secret via command line argument
Usage: python3 add_binance_secret_cli.py "YOUR_SECRET_HERE"
"""

import os
import sys

def add_binance_secret(secret):
    """Add Binance secret"""
    print("\n" + "="*60)
    print("🔑 ADDING BINANCE SECRET")
    print("="*60)
    
    # Check key exists
    if not os.path.exists("secure_keys/.binance_key"):
        print("❌ Binance key file not found!")
        return False
    
    with open("secure_keys/.binance_key", 'r') as f:
        binance_key = f.read().strip()
    
    print(f"✅ Binance Key: {binance_key[:15]}...")
    print(f"📋 Secret to add: {secret[:10]}... ({len(secret)} chars)")
    
    # Check if previous secret exists
    if os.path.exists("secure_keys/.binance_secret"):
        with open("secure_keys/.binance_secret", 'r') as f:
            old_secret = f.read().strip()
        print(f"📄 Replacing old secret: {old_secret[:10]}...")
    
    # Ensure secure directory
    os.makedirs("secure_keys", exist_ok=True)
    
    # Save secret
    with open("secure_keys/.binance_secret", 'w') as f:
        f.write(secret)
    
    # Set permissions
    os.chmod("secure_keys/.binance_secret", 0o600)
    
    # Update symlink
    if os.path.exists(".binance_secret"):
        os.remove(".binance_secret")
    os.symlink("secure_keys/.binance_secret", ".binance_secret")
    
    print("\n✅ BINANCE SECRET ADDED!")
    print(f"   File: secure_keys/.binance_secret")
    print(f"   Permissions: chmod 600")
    print(f"   Key: {binance_key[:10]}...")
    print(f"   Secret: {secret[:10]}...")
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 add_binance_secret_cli.py \"YOUR_BINANCE_SECRET\"")
        print("\nExample:")
        print("  python3 add_binance_secret_cli.py \"abc123DEF456ghi789JKL012mno345PQR678stu901VWX234yz\"")
        sys.exit(1)
    
    secret = sys.argv[1].strip()
    
    if len(secret) < 60:
        print(f"⚠️ Warning: Secret is only {len(secret)} characters")
        print("Binance secrets are typically 64+ characters")
        confirm = input("Continue anyway? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Cancelled")
            sys.exit(0)
    
    success = add_binance_secret(secret)
    
    if success:
        print("\n🔌 Test connection:")
        print("   python3 test_real_connections.py")
        
        print("\n⚠️ If connection fails:")
        print("   1. Verify IP restrictions: 127.0.0.1 + 115.87.79.55")
        print("   2. Check permissions: 'Spot & Margin Trading' ONLY")
        print("   3. Re-copy secret EXACTLY from Binance")
        
        print("\n💰 Deposit $50 to Binance account")
        print("🎯 Then activate: ./activate_real_system_now.sh")
    
    print("="*60)

if __name__ == "__main__":
    main()