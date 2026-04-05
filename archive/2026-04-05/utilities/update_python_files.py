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
