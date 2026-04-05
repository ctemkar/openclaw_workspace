#!/usr/bin/env python3
"""
Script to disable all duplicate cron jobs monitoring localhost:5001
"""

import json
import subprocess
import sys

def get_cron_jobs():
    """Get all cron jobs"""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error getting cron jobs: {e}")
        return {"jobs": []}

def disable_job(job_id):
    """Disable a specific cron job"""
    try:
        subprocess.run(
            ["openclaw", "cron", "update", job_id, "--enabled", "false"],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except Exception as e:
        print(f"Error disabling job {job_id}: {e}")
        return False

def main():
    print("Fetching all cron jobs...")
    data = get_cron_jobs()
    
    if not data.get("jobs"):
        print("No cron jobs found")
        return
    
    print(f"Found {len(data['jobs'])} cron jobs")
    
    # Filter for duplicate trading dashboard monitor jobs
    duplicate_jobs = []
    for job in data["jobs"]:
        name = job.get("name", "")
        payload = job.get("payload", {})
        message = payload.get("message", "")
        
        # Check if it's a trading dashboard monitor job
        if ("localhost:5001" in str(payload) or 
            "localhost:5001" in str(message) or
            "trading_dashboard_monitor" in name.lower() or
            "trading-monitor" in name.lower()):
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
            if disable_job(job_id):
                disabled_count += 1
        else:
            print(f"Job already disabled: {name} ({job_id})")
    
    print(f"\n✅ Disabled {disabled_count} duplicate cron jobs")
    
    # Keep only essential jobs
    essential_jobs = []
    for job in data["jobs"]:
        name = job.get("name", "")
        if "Progress Report" in name or "auto_save" in name or "progress_monitor" in name:
            essential_jobs.append(job)
    
    print(f"\nKeeping {len(essential_jobs)} essential jobs:")
    for job in essential_jobs:
        print(f"  - {job.get('name', 'unnamed')}")

if __name__ == "__main__":
    main()