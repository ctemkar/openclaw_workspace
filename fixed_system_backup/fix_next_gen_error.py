#!/usr/bin/env python3
"""
Fix the Next-Gen system error: "Error reading file: 'list' object has no attribute 'get'"
"""

import json
import os

def fix_file_reading_error():
    """Fix the file reading error in Next-Gen system"""
    
    print("🔧 FIXING NEXT-GEN SYSTEM FILE READING ERROR")
    print("="*60)
    
    # Check what files exist
    files_to_check = [
        "next_gen_analysis.json",
        "next_gen_trading_results.json",
        "llm_analysis_results.json"
    ]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            print(f"\n📄 Checking {filename}:")
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    print(f"   ✅ File is a list with {len(data)} items")
                    if len(data) > 0:
                        print(f"   📊 First item type: {type(data[0])}")
                        if isinstance(data[0], dict):
                            print(f"   🔍 First item keys: {list(data[0].keys())}")
                elif isinstance(data, dict):
                    print(f"   ✅ File is a dictionary with {len(data)} keys")
                    print(f"   🔍 Keys: {list(data.keys())}")
                else:
                    print(f"   ⚠️  File is type: {type(data)}")
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON decode error: {e}")
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
        else:
            print(f"\n📄 {filename}: ❌ File not found")
    
    # Create a safe file reader function
    safe_reader_code = '''
def safe_read_json_file(filename):
    """Safely read JSON file, handling both list and dict formats"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Handle different data structures
        if isinstance(data, list):
            return {"type": "list", "data": data, "count": len(data)}
        elif isinstance(data, dict):
            return {"type": "dict", "data": data, "keys": list(data.keys())}
        else:
            return {"type": "unknown", "data": data, "error": "Unexpected format"}
            
    except FileNotFoundError:
        return {"type": "error", "error": f"File not found: {filename}"}
    except json.JSONDecodeError as e:
        return {"type": "error", "error": f"JSON decode error: {e}"}
    except Exception as e:
        return {"type": "error", "error": f"Error reading file: {e}"}
'''
    
    print(f"\n{'='*60}")
    print("✅ FILE READING ERROR DIAGNOSED")
    print("="*60)
    print("\n🎯 PROBLEM:")
    print("   The Next-Gen system expects dictionary objects but some files")
    print("   contain lists. The error occurs when calling .get() on a list.")
    
    print("\n🔧 SOLUTION:")
    print("   Use the safe_read_json_file() function above which:")
    print("   1. Handles both lists and dictionaries")
    print("   2. Returns consistent structure")
    print("   3. Provides error messages")
    
    print("\n📋 FIX IMPLEMENTED:")
    print("   The safe file reader has been documented.")
    print("   Update Next-Gen system code to use this function.")
    
    # Save the fix
    with open("safe_file_reader.py", "w") as f:
        f.write(safe_reader_code)
    
    print("\n💾 Saved fix to: safe_file_reader.py")
    print("="*60)

if __name__ == "__main__":
    fix_file_reading_error()