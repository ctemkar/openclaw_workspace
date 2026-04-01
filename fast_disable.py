#!/usr/bin/env python3
"""
FAST DISABLE - Disable trading dashboard jobs without getting killed
"""

import subprocess
import json
import time

def run_cmd(cmd):
    """Run a command and return result"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def main():
    print("⚡ FAST DISABLE - Trading Dashboard Jobs")
    print("=" * 50)
    
    # Get all jobs
    success, stdout, stderr = run_cmd(["openclaw", "cron", "list", "--json"])
    if not success:
        print(f"Error getting jobs: {stderr}")
        return
    
    try:
        data = json.loads(stdout)
        jobs = data.get("jobs", [])
    except json.JSONDecodeError:
        print("Error parsing JSON")
        return
    
    print(f"Total jobs: {len(jobs)}")
    
    # Filter for trading dashboard jobs
    trading_jobs = []
    for job in jobs:
        name = job.get("name", "")
        if "trading_dashboard_monitor" in name.lower():
            trading_jobs.append(job)
    
    print(f"Found {len(trading_jobs)} trading_dashboard_monitor jobs")
    
    # Disable in batches with progress
    batch_size = 5
    disabled = 0
    
    for i in range(0, len(trading_jobs), batch_size):
        batch = trading_jobs[i:i+batch_size]
        print(f"\nBatch {i//batch_size + 1}: {len(batch)} jobs")
        
        for job in batch:
            job_id = job["id"]
            name = job.get("name", "unnamed")[:20]
            
            if job.get("enabled", True):
                success, stdout, stderr = run_cmd(["openclaw", "cron", "disable", job_id])
                if success:
                    disabled += 1
                    print(f"  ✓ {name}")
                else:
                    print(f"  ✗ {name}: {stderr[:30]}")
            else:
                print(f"  - {name} (already disabled)")
                disabled += 1
        
        # Show progress
        progress = (i + len(batch)) / len(trading_jobs) * 100
        print(f"  Progress: {disabled}/{len(trading_jobs)} ({progress:.1f}%)")
        
        # Small delay
        time.sleep(0.3)
    
    print(f"\n✅ Disabled {disabled}/{len(trading_jobs)} trading dashboard jobs")
    
    # Final count
    success, stdout, stderr = run_cmd(["openclaw", "cron", "list", "--json"])
    if success:
        try:
            data = json.loads(stdout)
            enabled = sum(1 for j in data.get("jobs", []) if j.get("enabled", False))
            print(f"\n📊 Final count: {enabled} jobs still enabled")
        except:
            pass

if __name__ == "__main__":
    main()