# ULTRA-SECURE API KEY STORAGE

## 🔐 SECURITY MEASURES:
1. **Directory permissions:** `chmod 700` (only owner can access)
2. **File permissions:** `chmod 600` (only owner can read/write)
3. **Git ignored:** All key files excluded from version control
4. **Symlinked:** Trading system uses symlinks for access
5. **Backup:** Store encrypted backup elsewhere

## 📁 FILES TO CREATE:

### Gemini Keys:
1. `.gemini_key` - Your Gemini API Key
2. `.gemini_secret` - Your Gemini Secret

### Binance Keys:
1. `.binance_key` - Your Binance API Key  
2. `.binance_secret` - Your Binance Secret

## 🚀 SETUP COMMANDS:

```bash
# Navigate to workspace
cd ~/.openclaw/workspace/app

# Store your ACTUAL Gemini keys (REPLACE placeholders)
echo "YOUR_ACTUAL_GEMINI_API_KEY" > secure_keys/.gemini_key
echo "YOUR_ACTUAL_GEMINI_SECRET" > secure_keys/.gemini_secret

# Store your ACTUAL Binance keys (REPLACE placeholders)
echo "YOUR_ACTUAL_BINANCE_API_KEY" > secure_keys/.binance_key
echo "YOUR_ACTUAL_BINANCE_SECRET" > secure_keys/.binance_secret

# Set ultra-secure permissions
chmod 600 secure_keys/.gemini_key secure_keys/.gemini_secret
chmod 600 secure_keys/.binance_key secure_keys/.binance_secret

# Create symlinks for trading system
ln -sf secure_keys/.gemini_key .gemini_key
ln -sf secure_keys/.gemini_secret .gemini_secret
ln -sf secure_keys/.binance_key .binance_key
ln -sf secure_keys/.binance_secret .binance_secret
```

## 🎯 KEY REQUIREMENTS:

### Gemini API Key:
- Permission: "Trader" ONLY (NOT "Fund Manager")
- IP Restrictions: Add `127.0.0.1` + your server IP
- Name: "OpenClaw-Longs-20260330"

### Binance API Key:
- Permission: "Spot & Margin Trading" ONLY
- IP Restrictions: Same IPs as Gemini
- Name: "OpenClaw-Shorts-20260330"
- ❌ NO Withdrawal permissions

## 🔍 VERIFICATION:

After adding keys, test with:
```bash
# Test Gemini
python3 test_gemini_connection.py

# Test Binance
python3 test_binance_connection.py
```

## ⚠️ SECURITY REMINDERS:
1. NEVER share these files
2. NEVER commit to git
3. Rotate keys every 30 days
4. Monitor API usage daily
5. Keep emergency shutdown guide handy

Created: 2026-03-30 22:34