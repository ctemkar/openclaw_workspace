#!/usr/bin/env python3
"""
Script to disable ALL OpenRouter cron jobs to prevent billing disaster.
Estimated monthly cost: $129-$259 for 100+ jobs running every 1-5 minutes.
"""

import json
import subprocess
import sys
from datetime import datetime

def run_openclaw_command(cmd):
    """Run OpenClaw command and return JSON output."""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"Error running openclaw: {result.stderr}")
            return None
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Failed to run openclaw command: {e}")
        return None

def disable_openrouter_jobs(jobs_data):
    """Disable all jobs using OpenRouter models."""
    disabled_count = 0
    openrouter_jobs = []
    
    if not jobs_data or 'jobs' not in jobs_data:
        print("No jobs data found")
        return 0
    
    for job in jobs_data['jobs']:
        # Check if job uses OpenRouter
        payload = job.get('payload', {})
        model = payload.get('model', '')
        
        if 'openrouter' in model.lower() or 'gemini' in model.lower():
            job_id = job.get('id')
            job_name = job.get('name', 'unnamed')
            enabled = job.get('enabled', False)
            
            if enabled:
                openrouter_jobs.append({
                    'id': job_id,
                    'name': job_name,
                    'model': model,
                    'enabled': enabled
                })
    
    print(f"\n📊 Found {len(openrouter_jobs)} OpenRouter cron jobs")
    print("=" * 60)
    
    for i, job in enumerate(openrouter_jobs, 1):
        print(f"{i}. {job['name']} (ID: {job['id'][:8]}...)")
        print(f"   Model: {job['model']}")
        print(f"   Status: {'ENABLED' if job['enabled'] else 'disabled'}")
    
    if not openrouter_jobs:
        print("✅ No OpenRouter jobs found!")
        return 0
    
    print(f"\n🚨 DISABLING {len(openrouter_jobs)} OPENROUTER JOBS...")
    print("=" * 60)
    
    for job in openrouter_jobs:
        job_id = job['id']
        job_name = job['name']
        
        try:
            # Disable the job
            result = subprocess.run(
                ["openclaw", "cron", "update", job_id, "--enabled", "false"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ Disabled: {job_name}")
                disabled_count += 1
            else:
                print(f"❌ Failed to disable {job_name}: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error disabling {job_name}: {e}")
    
    return disabled_count

def main():
    print("=" * 60)
    print("🚨 OPENROUTER CRON JOB DISABLER")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n⚠️  WARNING: This will disable ALL cron jobs using OpenRouter models")
    print("   Estimated monthly savings: $129-$259")
    print("=" * 60)
    
    # Get all cron jobs
    print("\n📋 Fetching cron jobs...")
    jobs_data = run_openclaw_command("list")
    
    if not jobs_data:
        print("❌ Failed to fetch cron jobs. Exiting.")
        sys.exit(1)
    
    total_jobs = len(jobs_data.get('jobs', []))
    print(f"📊 Total cron jobs found: {total_jobs}")
    
    # Disable OpenRouter jobs
    disabled = disable_openrouter_jobs(jobs_data)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total cron jobs: {total_jobs}")
    print(f"OpenRouter jobs disabled: {disabled}")
    
    if disabled > 0:
        # Estimate savings
        hourly_cost = disabled * 0.0015  # Rough estimate
        daily_cost = hourly_cost * 24
        monthly_cost = daily_cost * 30
        
        print(f"\n💰 ESTIMATED MONTHLY SAVINGS:")
        print(f"   Hourly: ${hourly_cost:.2f}")
        print(f"   Daily: ${daily_cost:.2f}")
        print(f"   Monthly: ${monthly_cost:.2f}")
        print(f"\n✅ Successfully prevented potential billing disaster!")
    else:
        print("\n✅ No OpenRouter jobs to disable.")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Check OpenRouter billing dashboard")
    print("2. Review remaining essential DeepSeek-based jobs")
    print("3. Consider removing duplicate/unnecessary jobs")
    print("=" * 60)

if __name__ == "__main__":
    main()