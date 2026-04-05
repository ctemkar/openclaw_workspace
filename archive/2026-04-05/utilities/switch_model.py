#!/usr/bin/env python3
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
        print('\n🛑 Stopped by user')
    except Exception as e:
        print(f'❌ Error: {e}')
