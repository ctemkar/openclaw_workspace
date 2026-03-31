# 🚀 OpenClaw with Ollama Models

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
