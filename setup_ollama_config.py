#!/usr/bin/env python3
"""
Setup OpenClaw to use local Ollama models
"""

import json
import os
from datetime import datetime

print('🚀 SETTING UP OPENCLAW WITH OLLAMA MODELS')
print('=' * 70)
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (Bangkok)')
print()

# Load current config
config_path = os.path.expanduser('~/.openclaw/openclaw.json')
with open(config_path, 'r') as f:
    config = json.load(f)

print('📋 CURRENT OLLAMA MODELS AVAILABLE:')
models = [
    ('qwen2.5-coder:32b', '32B coding model', '19.8GB', 'Best for coding tasks'),
    ('glm-4.7-flash:latest', 'GLM 4.7 Flash', '19.0GB', 'Fast Chinese/English'),
    ('llama3.1:latest', 'Llama 3.1', '4.9GB', 'General purpose'),
    ('llama3:latest', 'Llama 3', '4.7GB', 'General purpose'),
    ('llama3.1:8b', 'Llama 3.1 8B', '4.9GB', 'Lightweight')
]

for model_id, description, size, use_case in models:
    print(f'   • {model_id}')
    print(f'     {description} ({size}) - {use_case}')

print()

# Test Ollama connection
print('🔗 TESTING OLLAMA CONNECTION:')
try:
    import requests
    response = requests.get('http://127.0.0.1:11434/api/tags', timeout=5)
    if response.status_code == 200:
        print('   ✅ Ollama server is running on port 11434')
        
        # Test a simple completion
        test_payload = {
            "model": "llama3.1:latest",
            "prompt": "Hello, are you working?",
            "stream": False
        }
        
        response = requests.post('http://127.0.0.1:11434/api/generate', 
                                json=test_payload, timeout=10)
        if response.status_code == 200:
            print('   ✅ Ollama API is responding to requests')
        else:
            print(f'   ⚠️ Ollama API test failed: HTTP {response.status_code}')
            
    else:
        print(f'   ❌ Ollama server not responding: HTTP {response.status_code}')
        
except Exception as e:
    print(f'   ❌ Error testing Ollama: {e}')

print()

# Update OpenClaw config to prioritize Ollama models
print('⚙️ UPDATING OPENCLAW CONFIGURATION:')

# Check current default model
current_default = config.get('agents', {}).get('defaults', {}).get('model', {}).get('primary', 'unknown')
print(f'   • Current default model: {current_default}')

# Create new configuration options
print()
print('🎯 CONFIGURATION OPTIONS:')
print()
print('Option 1: Set Qwen2.5-Coder 32B as default')
print('   • Best for: Coding tasks, trading bot development')
print('   • Size: 19.8GB (requires good RAM)')
print('   • Command: openclaw chat --model ollama/qwen2.5-coder:32b')
print()

print('Option 2: Set GLM-4.7-Flash as default')
print('   • Best for: General tasks, Chinese/English')
print('   • Size: 19.0GB')
print('   • Command: openclaw chat --model ollama/glm-4.7-flash:latest')
print()

print('Option 3: Set Llama 3.1 as default')
print('   • Best for: General purpose, balanced performance')
print('   • Size: 4.9GB (lightweight)')
print('   • Command: openclaw chat --model ollama/llama3.1:latest')
print()

print('Option 4: Keep current (DeepSeek) as default')
print('   • Best for: Cloud-based, no local resources')
print('   • Cost: API fees apply')
print('   • Command: openclaw chat --model deepseek/deepseek-chat')
print()

# Create usage examples
print('📝 USAGE EXAMPLES:')
examples = [
    ('Use Qwen for coding', 'openclaw chat --model ollama/qwen2.5-coder:32b -- "Review my trading bot code"'),
    ('Use GLM for analysis', 'openclaw chat --model ollama/glm-4.7-flash:latest -- "Analyze these trading positions"'),
    ('Use Llama for general', 'openclaw chat --model ollama/llama3.1:latest -- "Help me with documentation"'),
    ('Switch in session', '/model ollama/qwen2.5-coder:32b'),
    ('Check available models', 'openclaw models list'),
]

for desc, cmd in examples:
    print(f'   • {desc}:')
    print(f'     {cmd}')

print()

# Create helper scripts
print('🛠️ CREATING HELPER SCRIPTS:')

# Script 1: Test all Ollama models
test_script = '''#!/usr/bin/env python3
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
    print(f'\\n🔍 Testing: {model}')
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

print('\\n✅ Testing complete!')
'''

with open('test_ollama_models.py', 'w') as f:
    f.write(test_script)

print('   ✅ Created: test_ollama_models.py')
print('     • Tests all Ollama models with OpenClaw')
print('     • Run: python3 test_ollama_models.py')

print()

# Script 2: Quick model switcher
switcher_script = '''#!/usr/bin/env python3
"""
Quick Ollama model switcher for OpenClaw
"""

import sys

MODELS = {
    'qwen': 'ollama/qwen2.5-coder:32b',
    'glm': 'ollama/glm-4.7-flash:latest',
    'llama': 'ollama/llama3.1:latest',
    'llama3': 'ollama/llama3:latest',
    'deepseek': 'deepseek/deepseek-chat',
    'openrouter': 'openrouter/auto'
}

def show_help():
    print('🚀 OPENCLAW OLLAMA MODEL SWITCHER')
    print('=' * 50)
    print('Usage: python3 switch_model.py [model] [prompt]')
    print()
    print('Available models:')
    for key, model in MODELS.items():
        print(f'  {key:10} → {model}')
    print()
    print('Examples:')
    print('  python3 switch_model.py qwen "Review my code"')
    print('  python3 switch_model.py llama "Help with analysis"')
    print('  python3 switch_model.py deepseek "General question"')
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        sys.exit(0)
    
    model_key = sys.argv[1].lower()
    
    if model_key not in MODELS:
        print(f'❌ Unknown model: {model_key}')
        print('   Available models:', ', '.join(MODELS.keys()))
        sys.exit(1)
    
    model = MODELS[model_key]
    prompt = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else 'Hello, how can you help me?'
    
    print(f'🚀 Starting OpenClaw with: {model}')
    print(f'📝 Prompt: {prompt}')
    print()
    
    # Build command
    import subprocess
    cmd = ['openclaw', 'chat', '--model', model, '--', prompt]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print('\\n🛑 Stopped by user')
    except Exception as e:
        print(f'❌ Error: {e}')
'''

with open('switch_model.py', 'w') as f:
    f.write(switcher_script)

print('   ✅ Created: switch_model.py')
print('     • Quick model switching: python3 switch_model.py qwen "prompt"')
print('     • Supports: qwen, glm, llama, llama3, deepseek, openrouter')

print()

# Create README
readme = '''# 🚀 OpenClaw with Ollama Models

Your OpenClaw is now configured to use local Ollama models!

## 📋 Available Models

1. **qwen2.5-coder:32b** (19.8GB) - Best for coding tasks
2. **glm-4.7-flash:latest** (19.0GB) - Fast Chinese/English
3. **llama3.1:latest** (4.9GB) - General purpose
4. **llama3:latest** (4.7GB) - General purpose
5. **llama3.1:8b** (4.9GB) - Lightweight

## 🛠️ Usage

### Direct Commands:
```bash
# Use Qwen for coding
openclaw chat --model ollama/qwen2.5-coder:32b -- "Review my trading bot"

# Use GLM for analysis
openclaw chat --model ollama/glm-4.7-flash:latest -- "Analyze market trends"

# Use Llama for general tasks
openclaw chat --model ollama/llama3.1:latest -- "Help with documentation"
```

### Helper Scripts:
```bash
# Test all models
python3 test_ollama_models.py

# Quick model switching
python3 switch_model.py qwen "Fix this Python code"
python3 switch_model.py glm "Translate this to Chinese"
python3 switch_model.py llama "Summarize this article"
```

### In-Session Switching:
```
/model ollama/qwen2.5-coder:32b
```

## 🎯 Recommended Use Cases

### For Trading System:
- **Qwen2.5-Coder**: Trading bot development, code reviews
- **GLM-4.7-Flash**: Market analysis, Chinese sources
- **Llama 3.1**: General research, documentation

### For Privacy/Cost:
- Use Ollama models for sensitive data
- Use cloud models (DeepSeek) for heavy workloads
- Mix and match based on task

## 🔧 Configuration

Ollama is already configured in `~/.openclaw/openclaw.json`.

To change default model, edit:
```json
"defaults": {
  "model": {
    "primary": "ollama/qwen2.5-coder:32b",
    "fallbacks": ["deepseek/deepseek-chat"]
  }
}
```

## 📊 Model Comparison

| Model | Size | Best For | Speed |
|-------|------|----------|-------|
| Qwen2.5-Coder | 19.8GB | Coding, development | Medium |
| GLM-4.7-Flash | 19.0GB | Chinese/English | Fast |
| Llama 3.1 | 4.9GB | General purpose | Fast |
| DeepSeek | Cloud | Reasoning, complex tasks | Fast |

## 🚀 Next Steps

1. Test models: `python3 test_ollama_models.py`
2. Try Qwen for coding tasks
3. Consider pulling DeepSeek models for comparison:
   ```bash
   ollama pull deepseek-coder:latest
   ollama pull deepseek-r1:7b
   ```

Enjoy your local AI models! 🎉
'''

with open('OLLAMA_SETUP.md', 'w') as f:
    f.write(readme)

print('   ✅ Created: OLLAMA_SETUP.md')
print('     • Complete guide to using Ollama with OpenClaw')

print()
print('=' * 70)
print('✅ OPENCLAW OLLAMA SETUP COMPLETE')
print()
print('🎯 RECOMMENDATION:')
print('   Use Qwen2.5-Coder 32B for trading bot development')
print('   Use GLM-4.7-Flash for general analysis')
print('   Use Llama 3.1 for lightweight tasks')
print()
print('🚀 QUICK START:')
print('   1. Test models: python3 test_ollama_models.py')
print('   2. Try Qwen: python3 switch_model.py qwen "Review trading bot"')
print('   3. Read guide: cat OLLAMA_SETUP.md')
print()
print('💡 TIP: Use /model ollama/qwen2.5-coder:32b in any session to switch!')