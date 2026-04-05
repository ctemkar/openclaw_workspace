#!/usr/bin/env python3
"""
Verify OpenClaw is using Ollama/Qwen as default
"""

import subprocess
import json
import os

print('🔍 VERIFYING OPENCLAW OLLAMA SETUP')
print('=' * 60)

# Test 1: Check config
config_path = os.path.expanduser('~/.openclaw/openclaw.json')
with open(config_path, 'r') as f:
    config = json.load(f)

default_model = config.get('agents', {}).get('defaults', {}).get('model', {}).get('primary', 'unknown')
print(f'1. Config check: {default_model}')

if 'ollama/qwen2.5-coder:32b' in default_model:
    print('   ✅ Config correctly set to Ollama/Qwen')
else:
    print('   ❌ Config not set to Ollama/Qwen')

print()

# Test 2: Test Ollama connection
print('2. Testing Ollama connection:')
try:
    import requests
    response = requests.get('http://127.0.0.1:11434/api/tags', timeout=5)
    if response.status_code == 200:
        models = response.json().get('models', [])
        model_names = [m.get('name', '') for m in models]
        
        if 'qwen2.5-coder:32b' in ' '.join(model_names):
            print('   ✅ Qwen2.5-Coder 32B is available in Ollama')
        else:
            print('   ❌ Qwen2.5-Coder 32B not found in Ollama')
            
        print(f'   • Available models: {", ".join(model_names)}')
    else:
        print(f'   ❌ Ollama not responding: HTTP {response.status_code}')
        
except Exception as e:
    print(f'   ❌ Error testing Ollama: {e}')

print()

# Test 3: Quick OpenClaw test
print('3. Quick OpenClaw test (will timeout after 10s):')
test_prompt = "What is 2+2? Answer with just the number."

try:
    # Run with timeout
    cmd = ['openclaw', 'chat', '--', test_prompt]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        print('   ✅ OpenClaw responded successfully')
        print(f'   • Response: {result.stdout[:100]}...')
    else:
        print(f'   ⚠️ OpenClaw returned error: {result.stderr[:100]}')
        
except subprocess.TimeoutExpired:
    print('   ⏱️ OpenClaw test timed out (10s) - model might be loading')
except Exception as e:
    print(f'   ❌ Error testing OpenClaw: {e}')

print()
print('=' * 60)
print('🎯 NEXT STEPS:')
print('1. Restart OpenClaw gateway for changes to take effect:')
print('   openclaw gateway restart')
print()
print('2. Test with a real prompt:')
print('   openclaw chat -- "Review my trading bot code"')
print()
print('3. Switch models on the fly:')
print('   /model ollama/glm-4.7-flash:latest')
print('   /model deepseek/deepseek-chat')
print()
print('✅ Verification complete!')
