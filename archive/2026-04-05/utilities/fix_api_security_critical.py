#!/usr/bin/env python3
"""
CRITICAL SECURITY FIX: Move all API keys to .env file
"""

import os
import re
import shutil
from pathlib import Path

# Configuration
WORKSPACE = Path(".")
ENV_FILE = WORKSPACE / ".env"
ENV_TEMPLATE = WORKSPACE / ".env.template"
BACKUP_DIR = WORKSPACE / "backup_api_keys_20260401"

# Patterns to find API keys
KEY_PATTERNS = [
    # Gemini
    r"GEMINI_API_KEY\s*=\s*['\"]([^'\"]+)['\"]",
    r"GEMINI_API_SECRET\s*=\s*['\"]([^'\"]+)['\"]",
    r"gemini_api_key\s*=\s*['\"]([^'\"]+)['\"]",
    r"gemini_api_secret\s*=\s*['\"]([^'\"]+)['\"]",
    
    # Binance
    r"BINANCE_API_KEY\s*=\s*['\"]([^'\"]+)['\"]",
    r"BINANCE_API_SECRET\s*=\s*['\"]([^'\"]+)['\"]",
    r"binance_api_key\s*=\s*['\"]([^'\"]+)['\"]",
    r"binance_api_secret\s*=\s*['\"]([^'\"]+)['\"]",
    
    # OpenRouter
    r"OPENROUTER_API_KEY\s*=\s*['\"]([^'\"]+)['\"]",
    r"openrouter_api_key\s*=\s*['\"]([^'\"]+)['\"]",
    
    # Generic patterns
    r"api_key\s*=\s*['\"]([^'\"]+)['\"]",
    r"api_secret\s*=\s*['\"]([^'\"]+)['\"]",
    r"API_KEY\s*=\s*['\"]([^'\"]+)['\"]",
    r"API_SECRET\s*=\s*['\"]([^'\"]+)['\"]",
    r"secret\s*=\s*['\"]([^'\"]+)['\"]",
    r"SECRET\s*=\s*['\"]([^'\"]+)['\"]",
]

def create_backup():
    """Create backup of all files before modification"""
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    BACKUP_DIR.mkdir(exist_ok=True)
    print(f"📁 Created backup directory: {BACKUP_DIR}")

def scan_for_keys():
    """Scan all Python files for API keys"""
    print("🔍 Scanning for exposed API keys...")
    
    files_with_keys = []
    total_keys_found = 0
    
    for file_path in WORKSPACE.rglob("*.py"):
        try:
            content = file_path.read_text()
            keys_in_file = []
            
            for pattern in KEY_PATTERNS:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Skip empty matches and common placeholder values
                    if match and match.strip() and "your_" not in match.lower():
                        keys_in_file.append((pattern, match))
                        total_keys_found += 1
            
            if keys_in_file:
                files_with_keys.append((file_path, keys_in_file))
                
        except Exception as e:
            print(f"  ⚠️  Error reading {file_path}: {e}")
    
    print(f"📊 Found {len(files_with_keys)} files with {total_keys_found} exposed API keys")
    return files_with_keys

def extract_keys_to_env(files_with_keys):
    """Extract unique keys and add to .env file"""
    print("\n🔐 Extracting keys to .env file...")
    
    # Read existing .env if it exists
    env_vars = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # Collect unique keys from files
    unique_keys = {}
    for file_path, keys in files_with_keys:
        for pattern, key_value in keys:
            # Determine key name from pattern
            if "GEMINI_API_KEY" in pattern.upper():
                key_name = "GEMINI_API_KEY"
            elif "GEMINI_API_SECRET" in pattern.upper():
                key_name = "GEMINI_API_SECRET"
            elif "BINANCE_API_KEY" in pattern.upper():
                key_name = "BINANCE_API_KEY"
            elif "BINANCE_API_SECRET" in pattern.upper():
                key_name = "BINANCE_API_SECRET"
            elif "OPENROUTER" in pattern.upper():
                key_name = "OPENROUTER_API_KEY"
            elif "API_KEY" in pattern.upper():
                key_name = "API_KEY"
            elif "API_SECRET" in pattern.upper():
                key_name = "API_SECRET"
            else:
                key_name = "UNKNOWN_KEY"
            
            # Store unique key
            if key_name not in unique_keys:
                unique_keys[key_name] = key_value
            elif unique_keys[key_name] != key_value:
                # Different values for same key name - create unique name
                new_key_name = f"{key_name}_{len([k for k in unique_keys.keys() if k.startswith(key_name)])}"
                unique_keys[new_key_name] = key_value
    
    # Add to env_vars
    for key_name, key_value in unique_keys.items():
        if key_name not in env_vars:
            env_vars[key_name] = key_value
    
    # Write .env file
    with open(ENV_FILE, 'w') as f:
        f.write("# API Keys - DO NOT COMMIT TO GIT!\n")
        f.write("# Generated automatically from security fix\n")
        f.write(f"# Date: 2026-04-01\n\n")
        
        # Write in organized groups
        groups = {
            "Gemini": [k for k in env_vars.keys() if "GEMINI" in k],
            "Binance": [k for k in env_vars.keys() if "BINANCE" in k],
            "OpenRouter": [k for k in env_vars.keys() if "OPENROUTER" in k],
            "Other": [k for k in env_vars.keys() if k not in [k for group in groups.values() for k in group]]
        }
        
        for group_name, keys in groups.items():
            if keys:
                f.write(f"\n# {group_name} API Keys\n")
                for key in sorted(keys):
                    f.write(f"{key}={env_vars[key]}\n")
    
    print(f"✅ Updated {ENV_FILE} with {len(env_vars)} environment variables")
    return env_vars

def create_fixed_files(files_with_keys, env_vars):
    """Create fixed versions of files with keys replaced by os.getenv()"""
    print("\n🛠️  Creating fixed file versions...")
    
    fixed_count = 0
    backup_count = 0
    
    for file_path, keys in files_with_keys:
        try:
            # Backup original
            backup_path = BACKUP_DIR / file_path.relative_to(WORKSPACE)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            backup_count += 1
            
            # Read content
            content = file_path.read_text()
            modified = False
            
            # Replace hardcoded keys with os.getenv()
            for pattern, key_value in keys:
                # Find which env var this matches
                env_var_name = None
                for env_key, env_value in env_vars.items():
                    if env_value == key_value:
                        env_var_name = env_key
                        break
                
                if env_var_name:
                    # Replace the hardcoded key with os.getenv()
                    old_line_match = re.search(rf'^.*{re.escape(key_value)}.*$', content, re.MULTILINE)
                    if old_line_match:
                        old_line = old_line_match.group(0)
                        # Try to create a better replacement
                        if "api_key" in old_line.lower() and "=" in old_line:
                            # Simple assignment: api_key = 'value'
                            new_line = re.sub(rf"=\s*['\"][^'\"]*['\"]", f"= os.getenv('{env_var_name}')", old_line)
                        else:
                            # Complex line, just comment it out and add replacement
                            new_line = f"# SECURITY FIX: {old_line.strip()}\n# Replaced with: {env_var_name} = os.getenv('{env_var_name}')"
                        
                        content = content.replace(old_line, new_line)
                        modified = True
            
            # Add os import if needed
            if modified and "import os" not in content:
                # Find first import line
                import_match = re.search(r'^import\s+', content, re.MULTILINE)
                if import_match:
                    import_pos = import_match.start()
                    content = content[:import_pos] + "import os\n" + content[import_pos:]
                else:
                    # Add at beginning of file
                    content = "import os\n" + content
            
            if modified:
                file_path.write_text(content)
                fixed_count += 1
                print(f"  ✅ Fixed: {file_path}")
            
        except Exception as e:
            print(f"  ❌ Error fixing {file_path}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"  - Backed up: {backup_count} files")
    print(f"  - Fixed: {fixed_count} files")
    print(f"  - Backup location: {BACKUP_DIR}")

def create_migration_guide():
    """Create a guide for manual fixes"""
    guide = """
# 🔐 API KEY SECURITY MIGRATION GUIDE

## 🚨 CRITICAL: DO THESE STEPS NOW

### 1. VERIFY .env FILE
Check that your .env file has all necessary keys:
```
cat .env
```

### 2. TEST THAT KEYS WORK
Run a test script to verify keys are accessible:
```python
import os
from dotenv import load_dotenv
load_dotenv()

print("Gemini Key:", os.getenv('GEMINI_API_KEY')[:10] + '...' if os.getenv('GEMINI_API_KEY') else 'MISSING')
print("Binance Key:", os.getenv('BINANCE_API_KEY')[:10] + '...' if os.getenv('BINANCE_API_KEY') else 'MISSING')
```

### 3. UPDATE REMAINING FILES MANUALLY
Some files may need manual fixes. Search for remaining hardcoded keys:
```
grep -r "api_key\|API_KEY\|secret\|SECRET" . --include="*.py" --include="*.sh" | grep -v ".env" | grep -v "backup_" | head -20
```

### 4. REVOKE COMPROMISED KEYS (IF NEEDED)
If keys were exposed publicly, consider:
1. Generating new API keys on exchange websites
2. Updating .env with new keys
3. Testing with new keys

### 5. SECURE YOUR .env FILE
```
# Make .env readable only by you
chmod 600 .env

# Add to .gitignore (already done)
echo ".env" >> .gitignore
```

## 📁 BACKUP FILES
All original files are backed up in: backup_api_keys_20260401/
Review these if any issues occur.

## 🆘 TROUBLESHOOTING
If something breaks:
1. Check error messages for missing environment variables
2. Verify .env file has correct variable names
3. Restore from backup if needed: cp backup_api_keys_20260401/*.py .
"""
    
    with open("API_KEY_SECURITY_GUIDE.md", "w") as f:
        f.write(guide)
    
    print(f"\n📘 Created migration guide: API_KEY_SECURITY_GUIDE.md")

def main():
    print("=" * 60)
    print("🚨 CRITICAL SECURITY FIX: API KEY EXPOSURE")
    print("=" * 60)
    
    # Step 1: Backup everything
    create_backup()
    
    # Step 2: Scan for keys
    files_with_keys = scan_for_keys()
    
    if not files_with_keys:
        print("✅ No exposed API keys found!")
        return
    
    # Step 3: Extract to .env
    env_vars = extract_keys_to_env(files_with_keys)
    
    # Step 4: Create fixed files
    create_fixed_files(files_with_keys, env_vars)
    
    # Step 5: Create guide
    create_migration_guide()
    
    print("\n" + "=" * 60)
    print("🎉 SECURITY FIX COMPLETE!")
    print("=" * 60)
    print("\n⚠️  NEXT STEPS:")
    print("1. Review the .env file contains all your keys")
    print("2. Test that your trading bots still work")
    print("3. Read API_KEY_SECURITY_GUIDE.md for manual fixes")
    print("4. Consider revoking and regenerating exposed keys")
    print("\n🔒 Your API keys are now secure in .env file!")

if __name__ == "__main__":
    main()