# 🔄 Restart OpenClaw for Changes to Take Effect

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
