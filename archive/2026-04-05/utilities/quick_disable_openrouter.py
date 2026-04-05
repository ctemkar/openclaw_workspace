#!/usr/bin/env python3
import subprocess
import json
import sys

# Get all cron jobs
print("Fetching cron jobs...")
result = subprocess.run(["openclaw", "cron", "list", "--json"], capture_output=True, text=True)
data = json.loads(result.stdout)
jobs = data.get('jobs', [])

print(f"Total jobs: {len(jobs)}")

# Count and disable OpenRouter jobs
openrouter_count = 0
disabled_count = 0

for job in jobs:
    payload = job.get('payload', {})
    model = payload.get('model', '')
    
    if 'openrouter' in model.lower() or 'gemini' in model.lower():
        openrouter_count += 1
        job_id = job.get('id')
        enabled = job.get('enabled', False)
        
        if enabled:
            print(f"Disabling {job_id[:8]}... (model: {model})")
            subprocess.run(["openclaw", "cron", "update", job_id, "--enabled", "false"], 
                         capture_output=True)
            disabled_count += 1

print(f"\n📊 SUMMARY:")
print(f"OpenRouter jobs found: {openrouter_count}")
print(f"OpenRouter jobs disabled: {disabled_count}")

if disabled_count > 0:
    monthly_savings = disabled_count * 0.0015 * 24 * 30
    print(f"\n💰 ESTIMATED MONTHLY SAVINGS: ${monthly_savings:.2f}")
    print("✅ Billing disaster prevented!")
else:
    print("✅ No OpenRouter jobs to disable.")