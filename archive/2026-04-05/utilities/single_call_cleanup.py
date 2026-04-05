#!/usr/bin/env python3
"""
SINGLE CALL CLEANUP - Get all data once, process internally, make minimal external calls
"""

import subprocess
import json
import time

print("🔄 SINGLE CALL CLEANUP - Minimizing external commands")
print("=" * 60)

# STEP 1: Get ALL data in ONE call
print("1. Fetching all cron jobs (single call)...")
try:
    result = subprocess.run(
        ["openclaw", "cron", "list", "--json"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        exit(1)
        
    data = json.loads(result.stdout)
    jobs = data.get("jobs", [])
    print(f"   ✓ Got {len(jobs)} jobs")
    
except Exception as e:
    print(f"Error: {e}")
    exit(1)

# STEP 2: Find trading dashboard jobs
print("2. Finding trading dashboard jobs...")
trading_jobs = []
for job in jobs:
    name = job.get("name", "")
    payload = job.get("payload", {})
    message = str(payload.get("message", "")) + str(payload.get("text", ""))
    
    if ("trading_dashboard_monitor" in name.lower() or 
        "localhost:5001" in str(payload).lower() or
        "localhost:5001" in message.lower()):
        trading_jobs.append(job)

print(f"   ✓ Found {len(trading_jobs)} trading dashboard jobs")

# STEP 3: Disable them with minimal calls
print("3. Disabling jobs (minimal external calls)...")
disabled = 0
total = len(trading_jobs)

for i, job in enumerate(trading_jobs):
    job_id = job["id"]
    name = job.get("name", "unnamed")[:20]
    
    # Skip if already disabled
    if not job.get("enabled", True):
        print(f"   - [{i+1}/{total}] {name}: already disabled")
        disabled += 1
        continue
    
    # Try to disable
    try:
        # Use edit command with --disable flag
        cmd = ["openclaw", "cron", "edit", job_id, "--disable"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            disabled += 1
            print(f"   ✓ [{i+1}/{total}] {name}: disabled")
        else:
            print(f"   ✗ [{i+1}/{total}] {name}: failed - {result.stderr[:50]}")
            
    except Exception as e:
        print(f"   ✗ [{i+1}/{total}] {name}: error - {str(e)[:50]}")
    
    # Very small delay every 10 jobs
    if (i + 1) % 10 == 0:
        time.sleep(0.1)

print(f"\n✅ Disabled {disabled}/{total} trading dashboard jobs")

# STEP 4: Final count
print("\n4. Final count...")
try:
    result = subprocess.run(
        ["openclaw", "cron", "list", "--json"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        enabled = sum(1 for j in data.get("jobs", []) if j.get("enabled", False))
        total_jobs = len(data.get("jobs", []))
        print(f"   Total jobs: {total_jobs}")
        print(f"   Still enabled: {enabled}")
        print(f"   Disabled: {total_jobs - enabled}")
        
except Exception as e:
    print(f"   Error getting final count: {e}")

print("\n" + "=" * 60)
print("🎉 CLEANUP COMPLETE!")
print("\nNext steps:")
print("1. Check OpenRouter billing for potential refund")
print("2. Monitor that no new duplicate jobs appear")
print("3. Consider deleting disabled jobs after verification")