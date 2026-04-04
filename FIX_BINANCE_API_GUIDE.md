# 🚨 URGENT: FIX BINANCE API KEY

## **PROBLEM:**
Crypto trading bot is **NOT TRADING** because Binance API key is invalid:
```
"Invalid API-key, IP, or permissions for action"
```

## **SOLUTION:**
You need to **REGENERATE BINANCE API KEY** and update the `.env` file.

## **STEP-BY-STEP GUIDE:**

### **1. LOGIN TO BINANCE:**
1. Go to https://www.binance.com
2. Login to your account
3. Go to **API Management**

### **2. CREATE NEW API KEY:**
1. Click **"Create API"**
2. Name it: `OpenClaw_Trading_Bot`
3. **ENABLE:** Spot & Margin Trading
4. **DISABLE:** Withdrawals (for security)
5. Click **"Create"**

### **3. GET API KEY & SECRET:**
1. **API Key:** Copy the generated key
2. **Secret Key:** Copy the secret (only shown once!)
3. **Save both securely**

### **4. UPDATE .ENV FILE:**
Replace these lines in `.env`:
```bash
BINANCE_API_KEY=YOUR_NEW_API_KEY_HERE
BINANCE_API_SECRET=YOUR_NEW_SECRET_KEY_HERE
```

### **5. RESTART BOT:**
```bash
# Kill current bot
kill 43093

# Restart with new API key
python3 practical_profit_bot.py > practical_profit_output.log 2>&1 &
```

## **VERIFICATION:**
After updating, check:
1. Bot logs for "Asset check error" - should be GONE
2. Bot should show actual MANA balance (not 0.00)
3. Bot should start trading when spread > 0.5%

## **⚠️ IMPORTANT NOTES:**
- **Binance may block Thailand IPs** - If still getting errors, try VPN
- **API keys expire** - May need to regenerate periodically
- **Keep secret secure** - Never share or commit to git

## **🚀 EXPECTED RESULT:**
Once API key is fixed:
- ✅ Bot shows actual MANA balance (176.97+)
- ✅ No more "Invalid API-key" errors
- ✅ Bot starts trading when spread > 0.5%
- ✅ REAL money starts flowing again

## **📞 NEED HELP?**
If Binance blocks Thailand:
1. Try VPN (US/Europe server)
2. Contact Binance support
3. Consider alternative exchange (Kraken, Coinbase)

**TIME TO FIX: ~5 minutes**
**IMPACT: NO TRADING UNTIL FIXED**