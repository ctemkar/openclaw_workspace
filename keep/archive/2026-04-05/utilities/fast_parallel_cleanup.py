#!/usr/bin/env python3
"""
FAST PARALLEL CLEANUP - Use multiprocessing to disable jobs quickly
"""

import subprocess
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_job_ids():
    """Get all trading dashboard job IDs in one call"""
    print("Fetching job IDs...")
    result = subprocess.run(
        ["openclaw", "cron", "list", "--json"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return []
    
    data = json.loads(result.stdout)
    jobs = data.get("jobs", [])
    
    # Filter for trading dashboard jobs
    job_ids = []
    for job in jobs:
        name = job.get("name", "")
        if "trading_dashboard_monitor" in name.lower():
            job_ids.append(job["id"])
    
    return job_ids

def disable_job(job_id):
    """Disable a single job"""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "disable", job_id],
            capture_output=True,
            text=True,
            timeout=5
        )
        return job_id, result.returncode == 0, ""
    except Exception as e:
        return job_id, False, str(e)

def main():
    print("⚡ FAST PARALLEL CLEANUP")
    print("=" * 50)
    
    # Get all job IDs
    job_ids = get_job_ids()
    if not job_ids:
        print("No trading dashboard jobs found!")
        return
    
    print(f"Found {len(job_ids)} trading dashboard jobs")
    print(f"Starting parallel cleanup with 5 workers...")
    
    # Disable jobs in parallel
    success_count = 0
    fail_count = 0
    
    # Use ThreadPoolExecutor for parallel execution
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all jobs
        future_to_job = {executor.submit(disable_job, job_id): job_id for job_id in job_ids}
        
        # Process results as they complete
        for i, future in enumerate(as_completed(future_to_job), 1):
            job_id, success, error = future.result()
            
            if success:
                success_count += 1
                print(f"  ✓ [{i}/{len(job_ids)}] Disabled")
            else:
                fail_count += 1
                print(f"  ✗ [{i}/{len(job_ids)}] Failed: {error[:30]}")
    
    print(f"\n✅ Cleanup complete!")
    print(f"   Success: {success_count}")
    print(f"   Failed: {fail_count}")
    
    # Final count
    print("\n📊 Final status:")
    result = subprocess.run(
        ["openclaw", "cron", "list", "--json"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        enabled = sum(1 for j in data.get("jobs", []) if j.get("enabled", False))
        total = len(data.get("jobs", []))
        
        print(f"   Total jobs: {total}")
        print(f"   Still enabled: {enabled}")
        print(f"   Disabled: {total - enabled}")

if __name__ == "__main__":
    main()