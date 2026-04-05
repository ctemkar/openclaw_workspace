#!/usr/bin/env python3
"""
Mass disable all duplicate cron jobs
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
    print("🚨 MASS DISABLE: Disabling ALL duplicate cron jobs...")
    
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
    
    # Filter for duplicate trading dashboard monitor jobs
    duplicate_jobs = []
    for job in jobs:
        name = job.get("name", "")
        payload = job.get("payload", {})
        message = payload.get("message", "")
        text = payload.get("text", "")
        
        # Check if it's a trading dashboard monitor job
        if ("localhost:5001" in str(payload) or 
            "localhost:5001" in str(message) or 
            "localhost:5001" in str(text) or
            "trading_dashboard_monitor" in name.lower() or
            "trading-monitor" in name.lower() or
            "trading-dashboard" in name.lower() or
            "trading_dashboard" in name.lower()):
            duplicate_jobs.append(job)
    
    print(f"\nFound {len(duplicate_jobs)} duplicate trading dashboard monitor jobs")
    
    # Disable them all
    disabled_count = 0
    for job in duplicate_jobs:
        job_id = job["id"]
        name = job.get("name", "unnamed")
        enabled = job.get("enabled", True)
        
        if enabled:
            print(f"Disabling job: {name} ({job_id})")
            stdout, stderr, code = run_command(f"openclaw cron disable {job_id}")
            if code == 0:
                disabled_count += 1
            else:
                print(f"  Error: {stderr}")
        else:
            print(f"Job already disabled: {name} ({job_id})")
    
    print(f"\n✅ Disabled {disabled_count} duplicate cron jobs")
    
    # List remaining enabled jobs
    print("\n📋 Remaining enabled jobs:")
    stdout, stderr, code = run_command("openclaw cron list --json")
    if code == 0:
        try:
            data = json.loads(stdout)
            enabled_jobs = [j for j in data.get("jobs", []) if j.get("enabled", False)]
            print(f"Total enabled jobs remaining: {len(enabled_jobs)}")
            for job in enabled_jobs:
                print(f"  - {job.get('name', 'unnamed')} ({job['id']})")
        except:
            pass

if __name__ == "__main__":
    main()