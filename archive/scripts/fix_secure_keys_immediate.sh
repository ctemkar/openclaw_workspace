#!/bin/bash

echo "🔐 IMMEDIATE SECURITY FIX FOR secure_keys/ DIRECTORY"
echo "===================================================="

# 1. Add secure_keys/ to .gitignore IMMEDIATELY
echo ""
echo "📝 STEP 1: Securing .gitignore"
if grep -q "secure_keys" .gitignore 2>/dev/null; then
    echo "✅ secure_keys/ already in .gitignore"
else
    echo "🚨 Adding secure_keys/ to .gitignore..."
    echo "" >> .gitignore
    echo "# API Key directories - NEVER COMMIT THESE!" >> .gitignore
    echo "secure_keys/" >> .gitignore
    echo "keys/" >> .gitignore
    echo "secrets/" >> .gitignore
    echo "*.key" >> .gitignore
    echo "*.secret" >> .gitignore
    echo "✅ Added secure_keys/ to .gitignore"
fi

# 2. Check if secure_keys/ is already in git
echo ""
echo "📝 STEP 2: Checking git status"
if git status --porcelain 2>/dev/null | grep -q "secure_keys"; then
    echo "🚨 CRITICAL: secure_keys/ is tracked by git!"
    echo "   Run: git rm --cached -r secure_keys/"
    echo "   Then: git commit -m 'Remove API keys from git'"
else
    echo "✅ secure_keys/ not tracked by git (good!)"
fi

# 3. Verify key file permissions
echo ""
echo "📝 STEP 3: Checking file permissions"
ls -la secure_keys/ 2>/dev/null | while read line; do
    if [[ "$line" == *".key"* ]] || [[ "$line" == *".secret"* ]]; then
        perms=$(echo "$line" | awk '{print $1}')
        file=$(echo "$line" | awk '{print $9}')
        if [[ "$perms" == *"rw-------"* ]] || [[ "$perms" == "-rw-------"* ]]; then
            echo "✅ $file: Secure permissions (600)"
        else
            echo "⚠️  $file: Insecure permissions ($perms)"
            echo "   Fix with: chmod 600 secure_keys/$file"
        fi
    fi
done

# 4. Create migration plan to .env
echo ""
echo "📝 STEP 4: Migration Plan to .env"
echo "Current structure:"
echo "  secure_keys/.gemini_key → GEMINI_API_KEY in .env"
echo "  secure_keys/.gemini_secret → GEMINI_API_SECRET in .env"
echo "  secure_keys/.binance_key → BINANCE_API_KEY in .env"
echo "  secure_keys/.binance_secret → BINANCE_API_SECRET in .env"

echo ""
echo "🔄 MIGRATION SCRIPT:"
cat > migrate_to_env.py << 'EOF'
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
EOF

chmod +x migrate_to_env.py
echo "✅ Created migration script: python3 migrate_to_env.py"

# 5. Create update script for Python files
echo ""
echo "📝 STEP 5: Python File Update Helper"
cat > update_python_files.py << 'EOF'
#!/usr/bin/env python3
import os
import re

def update_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern for reading from secure_keys/
    patterns = [
        (r"with open\(['\"]secure_keys/\.gemini_key['\"],", "GEMINI_API_KEY"),
        (r"with open\(['\"]secure_keys/\.gemini_secret['\"],", "GEMINI_API_SECRET"),
        (r"with open\(['\"]secure_keys/\.binance_key['\"],", "BINANCE_API_KEY"),
        (r"with open\(['\"]secure_keys/\.binance_secret['\"],", "BINANCE_API_SECRET"),
    ]
    
    modified = False
    new_content = content
    
    for pattern, env_var in patterns:
        if re.search(pattern, content):
            # Simple replacement - in real use, you'd need more careful parsing
            print(f"  Found {env_var} reference in {file_path}")
            modified = True
    
    if modified:
        # Backup original
        backup_path = file_path + '.backup'
        with open(backup_path, 'w') as f:
            f.write(content)
        
        print(f"  Created backup: {backup_path}")
        return True
    
    return False

# Example of how to update
print("Example update needed:")
print("OLD: with open('secure_keys/.gemini_key', 'r') as f:")
print("     api_key = f.read().strip()")
print("")
print("NEW: import os")
print("     api_key = os.getenv('GEMINI_API_KEY')")
print("")
print("Run this manually for each file that needs updating")

if __name__ == "__main__":
    print("This is a template script. Customize it for your needs.")
EOF

chmod +x update_python_files.py
echo "✅ Created update helper: python3 update_python_files.py"

echo ""
echo "🎯 IMMEDIATE ACTIONS:"
echo "1. Run: python3 migrate_to_env.py (move keys to .env)"
echo "2. Check: git status (ensure secure_keys/ not in git)"
echo "3. Update: chmod 600 secure_keys/* (secure permissions)"
echo "4. Test: python3 test_env_keys.py (verify .env works)"
echo ""
echo "⚠️  WARNING: Don't delete secure_keys/ until all files updated!"
echo "    The 1,000+ Python files still reference those files"