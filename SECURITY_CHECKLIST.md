# 🔒 SECURITY CHECKLIST

## NEVER COMMIT THESE TO VERSION CONTROL:

### ❌ BAD - Hardcoded secrets (NEVER DO THIS):
```python
# ❌ BAD - Hardcoded token
TOKEN = "8682526051:AAEITwha34khnpfGf1U-miGT0mFRsz7GKog"

# ❌ BAD - Hardcoded API keys
API_KEY = "your_api_key_here"
API_SECRET = "your_secret_here"
```

### ✅ GOOD - Use environment variables:
```python
# ✅ GOOD - Environment variables
import os
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
```

### ✅ GOOD - Use .env files (add to .gitignore!):
```bash
# .env file (ADD TO .GITIGNORE!)
TELEGRAM_BOT_TOKEN=your_actual_token_here
BINANCE_API_KEY=your_actual_key_here
BINANCE_API_SECRET=your_actual_secret_here
```

### ✅ GOOD - Provide .env.example (safe to commit):
```bash
# .env.example file (SAFE TO COMMIT)
TELEGRAM_BOT_TOKEN=your_bot_token_here
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
```

## FILES TO ADD TO .GITIGNORE:

1. **Secret files:**
   - `.env`
   - `.env.local`
   - `*.env`
   - `secrets/`
   - `keys/`
   - `tokens/`

2. **Trading system files with potential secrets:**
   - `*_trading_bot.py`
   - `*_consensus_trading_system.py`
   - `*_profit_trading_system.py`

3. **Audit logs and data:**
   - `*_audit.json`
   - `*_trades.log`
   - `real_trading_data/`

## SECURITY AUDIT COMMANDS:

```bash
# Check for hardcoded secrets
grep -r "=.*['\"].*['\"]" . --include="*.py" | grep -i "key\|secret\|token\|password"

# Check for .env files
find . -name ".env" -o -name ".env.*"

# Check git status for sensitive files
git status

# Check what's in staging
git diff --cached --name-only
```

## IMMEDIATE ACTIONS IF SECRETS FOUND:

1. **Remove from git tracking:**
   ```bash
   git rm --cached filename_with_secrets.py
   ```

2. **Add to .gitignore:**
   ```bash
   echo "filename_with_secrets.py" >> .gitignore
   ```

3. **Use environment variables instead:**
   - Replace hardcoded values with `os.getenv('VARIABLE_NAME')`
   - Create `.env.example` template
   - Document in README how to set environment variables

## REMEMBER:
- **Never commit secrets to version control**
- **Use environment variables for all secrets**
- **Add `.env` to `.gitignore`**
- **Provide `.env.example` as a template**
- **Regularly audit for hardcoded secrets**
