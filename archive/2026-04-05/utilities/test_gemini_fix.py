#!/usr/bin/env python3
"""
Test script to verify multi_llm_trading_bot Gemini fix
"""

import re

def test_gemini_order_fix():
    """Test that Gemini orders are properly fixed"""
    with open('multi_llm_trading_bot_properly_fixed.py', 'r') as f:
        content = f.read()
    
    print("🔍 Testing Gemini order fix...")
    
    # Find all create_order calls
    create_order_calls = re.findall(r'create_order\(.*?\)', content, re.DOTALL)
    
    print(f"Total create_order calls: {len(create_order_calls)}")
    
    # Check each call
    gemini_calls = []
    for call in create_order_calls:
        # Get context to see if it's for Gemini
        idx = content.find(call)
        context_start = max(0, idx - 100)
        context_end = min(len(content), idx + len(call) + 100)
        context = content[context_start:context_end]
        
        if 'gemini' in context.lower() and 'binance' not in context.lower():
            gemini_calls.append((call, context))
    
    print(f"Gemini create_order calls: {len(gemini_calls)}")
    
    all_good = True
    for i, (call, context) in enumerate(gemini_calls):
        print(f"\nGemini call {i+1}:")
        print(f"  Call: {call[:60]}...")
        
        # Check for type='limit'
        if "type='limit'" in call or 'type="limit"' in call:
            print("  ✅ Uses limit orders")
        else:
            print("  🚨 NOT using limit orders!")
            all_good = False
        
        # Check for price parameter
        if 'price=' in call:
            print("  ✅ Has price parameter")
        else:
            print("  🚨 Missing price parameter!")
            all_good = False
    
    if all_good:
        print("\n🎉 ALL Gemini orders are properly fixed!")
        print("   • Using limit orders")
        print("   • Have price parameter")
        return True
    else:
        print("\n🚨 Some Gemini orders still need fixing")
        return False

if __name__ == "__main__":
    success = test_gemini_order_fix()
    exit(0 if success else 1)