# API Keys Setup for Real Trading

## Why You Need API Keys
The current bots are SIMULATION bots that:
- ✅ Find opportunities (0.5-0.86% spreads)
- ✅ Calculate profits ($0.24-$0.53 per trade)
- ❌ CAN'T EXECUTE trades without API keys

## How to Get API Keys

### 1. Gemini API Keys
1. Go to: https://exchange.gemini.com/settings/api
2. Click "Create New API Key"
3. Set permissions: "Trader" (minimum)
4. Copy:
   - API Key: ________________
   - Secret: ________________

### 2. Binance API Keys
1. Go to: https://www.binance.com/en/my/settings/api-management
2. Click "Create API"
3. Set permissions: "Enable Spot & Margin Trading"
4. Copy:
   - API Key: ________________
   - Secret: ________________

## Setup Options

### Option A: Environment Variables (Recommended)
```bash
export GEMINI_API_KEY="your_gemini_key"
export GEMINI_SECRET="your_gemini_secret"
export BINANCE_API_KEY="your_binance_key"
export BINANCE_SECRET="your_binance_secret"
```

### Option B: Config File
Create `api_keys.json`:
```json
{
  "gemini_api_key": "your_key",
  "gemini_secret": "your_secret",
  "binance_api_key": "your_key",
  "binance_secret": "your_secret"
}
```

## Safety Notes
- ✅ NEVER share your API keys
- ✅ Use "Trader" permissions only (not "Fund Manager")
- ✅ Enable IP whitelisting if available
- ✅ Start with SMALL amounts ($50 trades)

## Test Trading
The bot will start in SIMULATION mode without keys.
Add keys to enable REAL trading.
