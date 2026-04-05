#!/usr/bin/env python3
"""
Update OpenClaw default model to use Ollama
"""

import json
import os
import shutil
from datetime import datetime

print('⚙️ UPDATING OPENCLAW DEFAULT MODEL')
print('=' * 60)

config_path = os.path.expanduser('~/.openclaw/openclaw.json')

# Create backup
backup_path = config_path + '.backup-' + datetime.now().strftime('%Y%m%d-%H%M%S')
shutil.copy2(config_path, backup_path)
print(f'📁 Created backup: {backup_path}')

# Load config
with open(config_path, 'r') as f:
    config = json.load(f)

print('📋 CURRENT DEFAULT MODEL:')
current_default = config.get('agents', {}).get('defaults', {}).get('model', {}).get('primary', 'unknown')
print(f'   • Primary: {current_default}')

fallbacks = config.get('agents', {}).get('defaults', {}).get('model', {}).get('fallbacks', [])
if fallbacks:
    print(f'   • Fallbacks: {", ".join(fallbacks)}')

print()
print('🎯 SETTING NEW DEFAULT MODEL: ollama/qwen2.5-coder:32b')
print('   • Best for coding tasks (trading bot development)')
print('   • 32B parameters, 19.8GB size')
print('   • Excellent for Python, trading strategies')
print()

# Update the config
if 'agents' not in config:
    config['agents'] = {}
if 'defaults' not in config['agents']:
    config['agents']['defaults'] = {}
if 'model' not in config['agents']['defaults']:
    config['agents']['defaults']['model'] = {}

# Set new default model
config['agents']['defaults']['model']['primary'] = 'ollama/qwen2.5-coder:32b'

# Update fallbacks to include cloud models as backup
config['agents']['defaults']['model']['fallbacks'] = [
    'deepseek/deepseek-chat',
    'openrouter/anthropic/claude-haiku-3.5'
]

# Save updated config
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print('✅ CONFIG UPDATED:')
print(f'   • New primary: ollama/qwen2.5-coder:32b')
print(f'   • Fallback 1: deepseek/deepseek-chat (cloud)')
print(f'   • Fallback 2: openrouter/anthropic/claude-haiku-3.5 (cloud)')
print()

# Verify the update
print('🔍 VERIFYING UPDATE:')
with open(config_path, 'r') as f:
    updated_config = json.load(f)

new_default = updated_config.get('agents', {}).get('defaults', {}).get('model', {}).get('primary', 'unknown')
print(f'   • Verified primary: {new_default}')

if new_default == 'ollama/qwen2.5-coder:32b':
    print('   ✅ SUCCESS: Default model updated to Ollama/Qwen!')
else:
    print('   ❌ FAILED: Default model not updated')

print()

# Create a test to verify the model works
print('🧪 CREATING VERIFICATION TEST:')
test_script = '''#!/usr/bin/env python3
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
'''

with open('verify_ollama_setup.py', 'w') as f:
    f.write(test_script)

print('   ✅ Created: verify_ollama_setup.py')
print('     • Run: python3 verify_ollama_setup.py')
print('     • Verifies Ollama connection and OpenClaw config')

print()

# Create restart instructions
print('🔄 RESTART INSTRUCTIONS:')
restart_guide = '''# 🔄 Restart OpenClaw for Changes to Take Effect

The default model has been updated to `ollama/qwen2.5-coder:32b`, but you need to restart OpenClaw for the changes to take effect.

## Option 1: Restart Gateway (Recommended)
```bash
openclaw gateway restart
```

## Option 2: Full Restart
```bash
# Stop OpenClaw
openclaw gateway stop

# Wait a few seconds
sleep 3

# Start OpenClaw
openclaw gateway start
```

## Option 3: Test Without Restart
You can also test the new model without restarting:
```bash
# Explicitly use Qwen
openclaw chat --model ollama/qwen2.5-coder:32b -- "Test prompt"

# Or use the switcher script
python3 switch_model.py qwen "Test the model"
```

## Verification
After restart, verify the setup:
```bash
python3 verify_ollama_setup.py
```

## Troubleshooting
If OpenClaw doesn't start with Ollama:
1. Check Ollama is running: `ollama list`
2. Check OpenClaw logs: `tail -f ~/.openclaw/logs/*.log`
3. Revert to backup if needed: `cp ~/.openclaw/openclaw.json.backup-* ~/.openclaw/openclaw.json`
'''

with open('RESTART_GUIDE.md', 'w') as f:
    f.write(restart_guide)

print('   ✅ Created: RESTART_GUIDE.md')
print('     • Complete restart instructions')

print()
print('=' * 60)
print('✅ OPENCLAW DEFAULT MODEL UPDATED')
print()
print('🎯 NEW DEFAULT: ollama/qwen2.5-coder:32b')
print('   • Perfect for trading bot development')
print('   • Local processing (no API costs)')
print('   • 32B parameters for complex tasks')
print()
print('🚀 NEXT STEPS:')
print('   1. Restart OpenClaw: openclaw gateway restart')
print('   2. Verify: python3 verify_ollama_setup.py')
print('   3. Test: python3 switch_model.py qwen "Review trading bot"')
print()
print('💡 REMEMBER: You can always switch models with /model command!')