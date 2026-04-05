#!/usr/bin/env python3
"""
Mass disable all OpenRouter cron jobs to prevent billing disaster.
"""

import subprocess
import json
import sys

def get_cron_jobs():
    """Get all cron jobs from OpenClaw."""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"Error getting cron jobs: {result.stderr}")
            return None
        
        data = json.loads(result.stdout)
        return data.get('jobs', [])
    except Exception as e:
        print(f"Failed to get cron jobs: {e}")
        return None

def disable_openrouter_jobs(jobs):
    """Disable all jobs using OpenRouter models."""
    openrouter_jobs = []
    
    for job in jobs:
        payload = job.get('payload', {})
        model = payload.get('model', '')
        
        # Check if it's an OpenRouter model
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
    
    disabled_count = 0
    for job in openrouter_jobs:
        print(f"Disabling: {job['name']} (ID: {job['id'][:8]}...)")
        print(f"  Model: {job['model']}")
        
        try:
            # Disable the job
            result = subprocess.run(
                ["openclaw", "cron", "update", job['id'], "--enabled", "false"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"  ✅ Disabled")
                disabled_count += 1
            else:
                print(f"  ❌ Failed: {result.stderr[:100]}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return disabled_count, len(openrouter_jobs)

def main():
    print("=" * 60)
    print("🚨 MASS DISABLE OPENROUTER CRON JOBS")
    print("=" * 60)
    print("\n⚠️  WARNING: This will disable ALL cron jobs using OpenRouter models")
    print("   Estimated monthly savings: $129-$259")
    print("=" * 60)
    
    # Get all cron jobs
    print("\n📋 Fetching cron jobs...")
    jobs = get_cron_jobs()
    
    if not jobs:
        print("❌ Failed to fetch cron jobs. Exiting.")
        sys.exit(1)
    
    print(f"📊 Total cron jobs found: {len(jobs)}")
    
    # Disable OpenRouter jobs
    disabled, total_openrouter = disable_openrouter_jobs(jobs)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total cron jobs: {len(jobs)}")
    print(f"OpenRouter jobs found: {total_openrouter}")
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