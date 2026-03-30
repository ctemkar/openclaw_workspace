#!/usr/bin/env python3
"""
Add Gemini secret via command line argument
Usage: python3 add_gemini_secret_cli.py "YOUR_SECRET_HERE"
"""

import os
import sys

def add_gemini_secret(secret):
    """Add Gemini secret"""
    print("\n" + "="*60)
    print("🔑 ADDING GEMINI SECRET")
    print("="*60)
    
    # Check key exists
    if not os.path.exists("secure_keys/.gemini_key"):
        print("❌ Gemini key file not found!")
        return False
    
    with open("secure_keys/.gemini_key", 'r') as f:
        gemini_key = f.read().strip()
    
    print(f"✅ Gemini Key: {gemini_key[:15]}...")
    print(f"📋 Secret to add: {secret[:10]}... ({len(secret)} chars)")
    
    # Ensure secure directory
    os.makedirs("secure_keys", exist_ok=True)
    
    # Save secret
    with open("secure_keys/.gemini_secret", 'w') as f:
        f.write(secret)
    
    # Set permissions
    os.chmod("secure_keys/.gemini_secret", 0o600)
    
    # Update symlink
    if os.path.exists(".gemini_secret"):
        os.remove(".gemini_secret")
    os.symlink("secure_keys/.gemini_secret", ".gemini_secret")
    
    print("\n✅ GEMINI SECRET ADDED!")
    print(f"   File: secure_keys/.gemini_secret")
    print(f"   Permissions: chmod 600")
    print(f"   Key: {gemini_key[:10]}...")
    print(f"   Secret: {secret[:10]}...")
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 add_gemini_secret_cli.py \"YOUR_GEMINI_SECRET\"")
        print("\nExample:")
        print("  python3 add_gemini_secret_cli.py \"2pXgR9kL8zqY7wV5tS3uM6nB4cD1fG8hJ2\"")
        sys.exit(1)
    
    secret = sys.argv[1].strip()
    
    if len(secret) < 30:
        print(f"⚠️ Warning: Secret is only {len(secret)} characters")
        print("Gemini secrets are typically ~40 characters")
        confirm = input("Continue anyway? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Cancelled")
            sys.exit(0)
    
    success = add_gemini_secret(secret)
    
    if success:
        print("\n🚀 Next: Add Binance secret")
        print("   python3 add_binance_secret_cli.py \"YOUR_BINANCE_SECRET\"")
        print("\n💰 Then deposit: $200 to Gemini, $50 to Binance")
        print("🎯 Then activate: ./activate_real_system_now.sh")
    
    print("="*60)

if __name__ == "__main__":
    main()