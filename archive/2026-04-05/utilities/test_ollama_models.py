#!/usr/bin/env python3
"""
Test all Ollama models with OpenClaw
"""

import subprocess
import time

models = [
    'ollama/qwen2.5-coder:32b',
    'ollama/glm-4.7-flash:latest',
    'ollama/llama3.1:latest',
    'ollama/llama3:latest',
    'ollama/llama3.1:8b'
]

print('🧪 TESTING OLLAMA MODELS WITH OPENCLAW')
print('=' * 60)

for model in models:
    print(f'\n🔍 Testing: {model}')
    print('-' * 40)
    
    # Simple test prompt
    test_prompt = "Hello, what is 2+2? Answer briefly."
    
    try:
        # Use subprocess to call openclaw
        cmd = ['openclaw', 'chat', '--model', model, '--', test_prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f'✅ {model} is working')
            # Extract and show first 100 chars of response
            response = result.stdout[:100] + '...' if len(result.stdout) > 100 else result.stdout
            print(f'   Response: {response.strip()}')
        else:
            print(f'❌ {model} failed: {result.stderr[:100]}')
            
    except subprocess.TimeoutExpired:
        print(f'⚠️ {model} timed out (30 seconds)')
    except Exception as e:
        print(f'❌ Error testing {model}: {e}')

print('\n✅ Testing complete!')
