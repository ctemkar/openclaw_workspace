#!/usr/bin/env python3
"""
Check dashboard structure for clicking issue
"""
import requests

print("🔍 CHECKING DASHBOARD STRUCTURE")
print("=" * 60)

try:
    resp = requests.get('http://localhost:5020', timeout=10)
    html = resp.text
    
    # Look for clickable elements
    print("\n🎯 CLICKABLE ELEMENTS FOUND:")
    
    # Look for onclick attributes
    if 'onclick=' in html:
        print("✅ Found onclick attributes")
        # Extract some examples
        import re
        onclicks = re.findall(r'onclick=[\'"]([^\'"]*)[\'"]', html)
        for i, oc in enumerate(onclicks[:5]):
            print(f"   {i+1}. onclick: {oc[:50]}...")
    else:
        print("❌ No onclick attributes found")
    
    # Look for JavaScript functions
    if 'function ' in html:
        print("✅ Found JavaScript functions")
        funcs = re.findall(r'function\s+(\w+)\s*\(', html)
        for i, func in enumerate(funcs[:5]):
            print(f"   {i+1}. function: {func}()")
    
    # Look for card/title structure
    print("\n🎯 CARD/TITLE STRUCTURE:")
    # Find h2/h3 titles
    titles = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html)
    for i, title in enumerate(titles[:10]):
        print(f"   {i+1}. Title: {title.strip()}")
    
    # Look for expand/collapse functionality
    if 'expand' in html.lower() or 'collapse' in html.lower() or 'toggle' in html.lower():
        print("\n✅ Found expand/collapse/toggle functionality")
    else:
        print("\n❌ No expand/collapse functionality found")
    
    # Check if there's supposed to be clicking on titles
    print("\n🎯 WHAT 'CLICKING ON TITLE' MIGHT MEAN:")
    print("   1. Titles should expand/collapse details")
    print("   2. Clicking should show more information")
    print("   3. Might be broken JavaScript")
    
    # Check JavaScript errors
    print("\n🔧 POSSIBLE FIXES:")
    print("   1. Check browser console for JavaScript errors")
    print("   2. Look for missing JavaScript functions")
    print("   3. Check if event listeners are attached")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n📱 TO TEST: Open browser, go to http://localhost:5020")
print("   Press F12 → Console tab")
print("   Click on a title")
print("   See if JavaScript errors appear")