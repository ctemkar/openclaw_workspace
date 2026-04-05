#!/usr/bin/env python3
import os
import shutil

def migrate_keys():
    print("🔐 Migrating from secure_keys/ to .env")
    
    # Read keys from secure_keys/
    keys = {}
    
    key_files = {
        'secure_keys/.gemini_key': 'GEMINI_API_KEY',
        'secure_keys/.gemini_secret': 'GEMINI_API_SECRET',
        'secure_keys/.binance_key': 'BINANCE_API_KEY',
        'secure_keys/.binance_secret': 'BINANCE_API_SECRET',
    }
    
    for file_path, env_var in key_files.items():
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                keys[env_var] = f.read().strip()
            print(f"✅ Read {env_var} from {file_path}")
        else:
            print(f"⚠️  Missing: {file_path}")
    
    # Read existing .env
    env_content = []
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.readlines()
    
    # Add keys to .env
    with open('.env', 'w') as f:
        # Keep existing content (excluding our keys)
        for line in env_content:
            if not any(key in line for key in keys.keys()):
                f.write(line)
        
        # Add our keys
        f.write('\n# Migrated from secure_keys/ directory\n')
        for env_var, value in keys.items():
            f.write(f'{env_var}={value}\n')
    
    print(f"\n✅ Added {len(keys)} keys to .env file")
    print("\n⚠️  NEXT STEPS:")
    print("1. Update Python files to use os.getenv() instead of reading files")
    print("2. Test that everything still works")
    print("3. Backup secure_keys/ directory")
    print("4. Consider deleting secure_keys/ after confirmation")

if __name__ == "__main__":
    migrate_keys()
