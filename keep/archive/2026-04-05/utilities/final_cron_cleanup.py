#!/usr/bin/env python3
"""
FINAL CRON CLEANUP - Disable ALL duplicate trading_dashboard_monitor jobs
"""

import subprocess
import json
import sys

def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def main():
    print("🚨 FINAL CRON CLEANUP - STOPPING THE DUPLICATION CYCLE")
    print("=" * 60)
    
    # Get all cron jobs
    stdout, stderr, code = run_command("openclaw cron list --json")
    if code != 0:
        print(f"Error getting cron jobs: {stderr}")
        return
    
    try:
        data = json.loads(stdout)
        jobs = data.get("jobs", [])
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return
    
    print(f"Found {len(jobs)} total cron jobs")
    
    # Find ALL trading_dashboard_monitor jobs
    duplicate_jobs = []
    for job in jobs:
        name = job.get("name", "")
        payload = job.get("payload", {})
        message = str(payload.get("message", "")) + str(payload.get("text", ""))
        
        # Broad matching for ANY trading dashboard monitor job
        if ("localhost:5001" in str(payload).lower() or 
            "localhost:5001" in message.lower() or
            "trading_dashboard_monitor" in name.lower() or
            "trading-dashboard" in name.lower() or
            "trading dashboard" in name.lower() or
            "monitor http://localhost:5001" in message.lower()):
            duplicate_jobs.append(job)
    
    print(f"\nFound {len(duplicate_jobs)} duplicate trading dashboard monitor jobs")
    
    # Disable them ALL
    disabled_count = 0
    for job in duplicate_jobs:
        job_id = job["id"]
        name = job.get("name", "unnamed")
        enabled = job.get("enabled", True)
        
        if enabled:
            print(f"Disabling: {name} ({job_id[:8]}...)")
            stdout, stderr, code = run_command(f"openclaw cron disable {job_id}")
            if code == 0:
                disabled_count += 1
            else:
                print(f"  Error: {stderr[:100]}")
        else:
            print(f"Already disabled: {name} ({job_id[:8]}...)")
    
    print(f"\n✅ Disabled {disabled_count} duplicate cron jobs")
    
    # List remaining enabled jobs
    print("\n📋 Remaining enabled jobs after cleanup:")
    stdout, stderr, code = run_command("openclaw cron list --json")
    if code == 0:
        try:
            data = json.loads(stdout)
            enabled_jobs = [j for j in data.get("jobs", []) if j.get("enabled", False)]
            print(f"Total enabled jobs remaining: {len(enabled_jobs)}")
            
            # Group by type
            job_types = {}
            for job in enabled_jobs:
                name = job.get("name", "unnamed")
                job_types[name] = job_types.get(name, 0) + 1
            
            for name, count in sorted(job_types.items()):
                print(f"  {name}: {count} job(s)")
        except:
            pass
    
    print("\n🔧 RECOMMENDED NEXT STEPS:")
    print("1. Check OpenRouter billing for refund request")
    print("2. Set up proper monitoring for ACTUAL dashboards (ports 5007, 5008, 5009)")
    print("3. Use DeepSeek model instead of OpenRouter")
    print("4. Monitor cron job count daily to prevent recurrence")
    print("5. Consider deleting disabled jobs after verification")

if __name__ == "__main__":
    main()