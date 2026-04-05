#!/usr/bin/env python3
"""
Cleanup ALL duplicate trading cron jobs
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
    print("🚨 MASSIVE CLEANUP: Disabling ALL trading-related cron jobs...")
    
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
    
    # Filter for trading-related jobs
    trading_jobs = []
    for job in jobs:
        if not job.get("enabled", True):
            continue
            
        name = job.get("name", "").lower()
        payload = job.get("payload", {})
        message = str(payload.get("message", "")).lower()
        text = str(payload.get("text", "")).lower()
        
        # Check if it's a trading-related job
        if ("trading" in name or 
            "localhost:5001" in message or 
            "localhost:5001" in text or
            "5001" in message or
            "5001" in text or
            "crypto" in name or
            "gemini" in message or
            "binance" in message or
            "exchange" in message):
            trading_jobs.append(job)
    
    print(f"\nFound {len(trading_jobs)} trading-related jobs to disable")
    
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
    
    print(f"\n✅ Disabled {disabled_count} trading-related cron jobs")
    
    # Now re-enable only essential jobs
    print("\n🔄 Re-enabling essential jobs...")
    
    essential_jobs = [
        "Progress Report",
        "auto_save",
        "progress_monitor",
        "Crypto Trading LLM Bot"
    ]
    
    # Get all jobs again to find disabled essential ones
    stdout, stderr, code = run_command("openclaw cron list --json")
    if code == 0:
        try:
            data = json.loads(stdout)
            jobs = data.get("jobs", [])
            
            enabled_count = 0
            for job in jobs:
                name = job.get("name", "")
                job_id = job["id"]
                enabled = job.get("enabled", True)
                
                if not enabled and any(essential in name for essential in essential_jobs):
                    print(f"Re-enabling essential job: {name} ({job_id})")
                    stdout, stderr, code = run_command(f"openclaw cron enable {job_id}")
                    if code == 0:
                        enabled_count += 1
                    else:
                        print(f"  Error: {stderr}")
            
            print(f"\n✅ Re-enabled {enabled_count} essential jobs")
        except:
            pass
    
    # Final status
    print("\n📋 Final status of enabled jobs:")
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