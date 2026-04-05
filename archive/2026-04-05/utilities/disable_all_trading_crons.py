#!/usr/bin/env python3
"""
Disable ALL trading dashboard monitor cron jobs
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
    print("🚨 DISABLING ALL TRADING DASHBOARD MONITOR JOBS...")
    
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
    
    # Filter for trading dashboard monitor jobs
    trading_jobs = []
    for job in jobs:
        if not job.get("enabled", True):
            continue
            
        name = job.get("name", "").lower()
        payload = job.get("payload", {})
        message = str(payload.get("message", "")).lower()
        text = str(payload.get("text", "")).lower()
        
        # Check if it's a trading dashboard monitor job
        if ("trading" in name or 
            "localhost:5001" in message or 
            "localhost:5001" in text or
            "5001" in message or
            "5001" in text):
            trading_jobs.append(job)
    
    print(f"\nFound {len(trading_jobs)} trading dashboard monitor jobs to disable")
    
    # Disable them all
    disabled_count = 0
    for job in trading_jobs:
        job_id = job["id"]
        name = job.get("name", "unnamed")
        
        print(f"Disabling job: {name} ({job_id})")
        stdout, stderr, code = run_command(f"openclaw cron disable {job_id}")
        if code == 0:
            disabled_count += 1
        else:
            print(f"  Error: {stderr}")
    
    print(f"\n✅ Disabled {disabled_count} trading dashboard monitor jobs")
    
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