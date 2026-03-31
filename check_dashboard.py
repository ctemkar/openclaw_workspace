#!/usr/bin/env python3
import requests
import time

print("Checking dashboard...")
time.sleep(2)  # Give it time to start

try:
    response = requests.get("http://localhost:5002", timeout=5)
    
    # Look for key sections
    html = response.text
    
    # Find execution mode
    if "REAL TRADING" in html:
        print("✅ Dashboard shows: REAL TRADING")
    elif "SIMULATION" in html:
        print("❌ Dashboard shows: SIMULATION")
    else:
        print("⚠️  Could not find execution mode")
    
    # Find strategy
    if "Strategy:" in html:
        # Extract strategy line
        lines = html.split('\n')
        for i, line in enumerate(lines):
            if "Strategy:" in line:
                print(f"📊 Strategy: {line.strip()}")
                # Check next few lines for execution mode
                for j in range(i, min(i+10, len(lines))):
                    if "Execution Mode:" in lines[j]:
                        print(f"🎯 Execution Mode: {lines[j].strip()}")
                        break
                break
    
    # Check overall
    if "status-warning" in html and "SIMULATION" not in html:
        print("✅ No more SIMULATION warnings!")
    elif "status-running" in html:
        print("✅ Dashboard shows running status")
        
except Exception as e:
    print(f"❌ Error checking dashboard: {e}")