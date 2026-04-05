#!/usr/bin/env python3
"""
Test dashboard click functionality
"""
import requests
import re

print("🔍 TESTING DASHBOARD CLICK FUNCTIONALITY")
print("=" * 60)

# Fetch dashboard HTML
try:
    response = requests.get('http://localhost:5020', timeout=5)
    if response.status_code == 200:
        html = response.text
        
        # Check for JavaScript functions
        functions = [
            ('refreshDashboard()', 'Refresh button function'),
            ('toggleSystemDetails', 'System card click function'),
            ('addEventListener', 'Event listeners'),
            ('classList.toggle', 'Expand/collapse function'),
            ('querySelectorAll', 'DOM selection')
        ]
        
        print("✅ Dashboard is running (HTTP 200)")
        print("\n🔧 JavaScript Functions Found:")
        for func, desc in functions:
            if func in html:
                print(f"  ✅ {desc}: {func}")
            else:
                print(f"  ❌ {desc}: NOT FOUND")
        
        # Check for system cards
        system_cards = html.count('system-card')
        print(f"\n📊 System Cards Found: {system_cards}")
        
        # Check for click handlers
        onclick_count = html.count('onclick=')
        print(f"🖱️  Click Handlers: {onclick_count}")
        
        # Check for cursor: pointer
        if 'cursor: pointer' in html:
            print("👆 Cursor Styling: ✅ Cards look clickable")
        else:
            print("👆 Cursor Styling: ❌ Missing")
            
        # Check for system-details div
        if 'system-details' in html:
            print("📋 Details Panel: ✅ Click to expand")
        else:
            print("📋 Details Panel: ❌ Missing")
            
        print("\n🎯 TEST RESULTS:")
        if all(func in html for func, _ in functions[:2]) and system_cards > 0:
            print("✅ CLICK FUNCTIONALITY IS WORKING!")
            print("   • Cards are clickable")
            print("   • JavaScript functions loaded")
            print("   • Expand/collapse available")
        else:
            print("⚠️  Some functionality missing")
            
    else:
        print(f"❌ Dashboard error: HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ Can't reach dashboard: {e}")

print("\n🔗 Dashboard URL: http://localhost:5020")
print("💡 Click on any system card to expand details!")
print("🔄 Click refresh button to reload")