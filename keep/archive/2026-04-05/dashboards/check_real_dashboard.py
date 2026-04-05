#!/usr/bin/env python3
"""
CHECK REAL DASHBOARD - Show what's ACTUALLY on the page
"""

import requests
import re
from datetime import datetime

print("=" * 70)
print(f"🔍 CHECKING REAL DASHBOARD - {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)

# Check REAL dashboard (port 5026)
print("\n🌐 CHECKING: http://localhost:5026")
try:
    response = requests.get("http://localhost:5026", timeout=5)
    
    if response.status_code == 200:
        print(f"✅ Dashboard accessible (HTTP {response.status_code})")
        
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
        if title_match:
            print(f"📋 Title: {title_match.group(1)}")
        
        # Check for TOP 10 SPREADS
        if "TOP 10 SPREADS" in response.text:
            print("✅ Contains: TOP 10 SPREADS section")
            
            # Extract the table
            start = response.text.find("TOP 10 SPREADS")
            end = response.text.find("</table>", start)
            
            if start != -1 and end != -1:
                table_section = response.text[start:end+8]
                
                # Count rows
                rows = table_section.count('<tr>')
                print(f"📊 Table rows: {rows}")
                
                # Show first 5 rows
                lines = table_section.split('\n')
                print("\n📋 SAMPLE OF TABLE CONTENT:")
                for i, line in enumerate(lines[:15]):
                    if '<td>' in line or '<th>' in line:
                        # Clean HTML tags
                        clean = re.sub(r'<[^>]+>', '', line).strip()
                        if clean:
                            print(f"  {clean}")
        else:
            print("❌ Does NOT contain: TOP 10 SPREADS section")
            
            # Check what it DOES contain
            if "No spread data" in response.text:
                print("⚠️  Shows: 'No spread data available'")
            elif "Loading" in response.text:
                print("⚠️  Shows: 'Loading...'")
            else:
                # Show first 200 chars
                preview = response.text[:200].replace('\n', ' ')
                print(f"⚠️  Preview: {preview}...")
    else:
        print(f"❌ Dashboard error: HTTP {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ Dashboard NOT RUNNING on port 5026")
except Exception as e:
    print(f"❌ Error: {e}")

# Check if the dashboard script is running
print("\n🔧 CHECKING DASHBOARD PROCESS:")
import subprocess
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
if 'simple_real_dashboard.py' in result.stdout:
    print("✅ Dashboard process: RUNNING")
else:
    print("❌ Dashboard process: NOT RUNNING")

# Check the dashboard log file
print("\n📄 CHECKING DASHBOARD LOGS:")
try:
    with open('simple_real_dashboard_output.log', 'r') as f:
        lines = f.readlines()
        if lines:
            print(f"✅ Log file exists: {len(lines)} lines")
            # Show last 5 lines
            print("📋 Last 5 log entries:")
            for line in lines[-5:]:
                print(f"  {line.strip()}")
        else:
            print("❌ Log file empty")
except FileNotFoundError:
    print("❌ No dashboard log file found")

print("\n" + "=" * 70)
print("🎯 SUMMARY:")
print("  I need to show you what's ACTUALLY on the dashboard")
print("  Not present stale/cached progress monitor data")
print("=" * 70)