#!/usr/bin/env python3
"""
NEUTRALIZE JOBS - Edit trading dashboard jobs to be harmless and disable them
"""

import subprocess
import json
import time

def run_cmd(cmd, timeout=10):
    """Run a command with timeout"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def main():
    print("🛡️  NEUTRALIZE HARMFUL CRON JOBS")
    print("=" * 60)
    
    # Get all jobs
    print("1. Fetching jobs...")
    success, stdout, stderr = run_cmd(["openclaw", "cron", "list", "--json"], timeout=30)
    if not success:
        print(f"Error: {stderr}")
        return
    
    try:
        data = json.loads(stdout)
        jobs = data.get("jobs", [])
    except json.JSONDecodeError:
        print("Error parsing JSON")
        return
    
    print(f"   Found {len(jobs)} total jobs")
    
    # Find trading dashboard jobs
    print("2. Finding trading dashboard jobs...")
    target_jobs = []
    for job in jobs:
        name = job.get("name", "")
        payload = job.get("payload", {})
        message = str(payload.get("message", "")) + str(payload.get("text", ""))
        
        if ("trading_dashboard_monitor" in name.lower() or 
            "localhost:5001" in str(payload).lower() or
            "localhost:5001" in message.lower()):
            target_jobs.append(job)
    
    print(f"   Found {len(target_jobs)} trading dashboard jobs")
    
    if len(target_jobs) == 0:
        print("No jobs to neutralize!")
        return
    
    # Neutralize them
    print("3. Neutralizing jobs (edit + disable)...")
    neutralized = 0
    
    for i, job in enumerate(target_jobs):
        job_id = job["id"]
        name = job.get("name", "unnamed")[:20]
        
        # Skip if already disabled and harmless
        if not job.get("enabled", True):
            payload = job.get("payload", {})
            if payload.get("text") == "JOB DISABLED BY CLEANUP - DO NOT RUN":
                print(f"   - [{i+1}/{len(target_jobs)}] {name}: already neutralized")
                neutralized += 1
                continue
        
        # Edit job to be harmless and disable it
        cmd = [
            "openclaw", "cron", "edit", job_id,
            "--system-event", "JOB DISABLED BY CLEANUP - DO NOT RUN",
            "--disable"
        ]
        
        success, stdout, stderr = run_cmd(cmd, timeout=15)
        
        if success:
            neutralized += 1
            print(f"   ✓ [{i+1}/{len(target_jobs)}] {name}: neutralized")
        else:
            print(f"   ✗ [{i+1}/{len(target_jobs)}] {name}: failed - {stderr[:50]}")
        
        # Small delay every 5 jobs
        if (i + 1) % 5 == 0:
            time.sleep(0.2)
    
    print(f"\n✅ Neutralized {neutralized}/{len(target_jobs)} jobs")
    
    # Final report
    print("\n4. Final report...")
    success, stdout, stderr = run_cmd(["openclaw", "cron", "list", "--json"], timeout=30)
    if success:
        try:
            data = json.loads(stdout)
            
            # Count by type
            total = len(data.get("jobs", []))
            enabled = sum(1 for j in data.get("jobs", []) if j.get("enabled", False))
            disabled = total - enabled
            
            # Count trading dashboard jobs
            trading = 0
            trading_enabled = 0
            for job in data.get("jobs", []):
                name = job.get("name", "")
                if "trading_dashboard_monitor" in name.lower():
                    trading += 1
                    if job.get("enabled", False):
                        trading_enabled += 1
            
            print(f"   Total jobs: {total}")
            print(f"   Enabled: {enabled}, Disabled: {disabled}")
            print(f"   Trading dashboard jobs: {trading}")
            print(f"   Trading dashboard enabled: {trading_enabled}")
            
        except:
            print("   Error parsing final data")
    
    print("\n" + "=" * 60)
    print("🎯 NEUTRALIZATION COMPLETE!")
    print("\nJobs have been:")
    print("1. Changed to harmless system events")
    print("2. Disabled")
    print("3. Will no longer use OpenRouter or monitor localhost:5001")
    print("\nBilling should stop immediately.")

if __name__ == "__main__":
    main()