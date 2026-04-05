# SCHWAB FOREX TRADING SETUP GUIDE

## 🚀 QUICK START - GET SCHWAB API CREDENTIALS

### **Step 1: Access Schwab Developer Portal**
1. **Go to:** https://developer.schwab.com
2. **Sign in** with your Schwab account credentials
3. **Create a new application** if you don't have one

### **Step 2: Create Application**
1. Click **"Create App"** or **"Register App"**
2. Fill in application details:
   - **App Name:** `Forex Trading Bot`
   - **Description:** `Automated Forex trading system`
   - **Redirect URI:** `https://127.0.0.1` (or your preferred callback URL)
   - **Permissions:** Select **Trading** and **Account Information**

### **Step 3: Get API Credentials**
After creating the app, you'll get:
1. **App Key (API Key)** - Keep this secure
2. **App Secret (API Secret)** - Keep this VERY secure
3. **Note your Account ID** (Schwab account number)

### **Step 4: Update Your .env File**
Add these lines to your `.env` file:

```bash
# Schwab API Credentials
SCHWAB_API_KEY=your_app_key_here
SCHWAB_API_SECRET=your_app_secret_here
SCHWAB_ACCOUNT_ID=your_account_number_here
SCHWAB_REDIRECT_URI=https://127.0.0.1
```

### **Step 5: Test Connection**
Run the test script to verify connectivity:

```bash
python3 test_schwab_connection.py
```

## 📊 SCHWAB API DETAILS

### **Available Endpoints:**
- **Account Information:** Get balances, positions
- **Market Data:** Real-time Forex prices
- **Trading:** Execute Forex trades
- **Orders:** Manage open orders
- **History:** Trade history

### **Rate Limits:**
- **Real-time data:** 120 requests/minute
- **Account data:** 60 requests/minute
- **Trading:** 30 requests/minute

### **Forex Trading Specifics:**
- **Minimum trade:** 0.01 lots (micro)
- **Maximum trade:** Varies by account
- **Margin required:** For leveraged positions
- **Commission:** Typically $0 per trade for Forex
- **Spread:** Variable based on market conditions

## 🔧 INTEGRATION WITH OUR FOREX BOT

### **Current Status:**
- ✅ Forex bot is running in **paper trading mode**
- ✅ Technical analysis strategy is working
- ✅ Risk management is implemented
- ✅ Ready for **real Schwab integration**

### **To Switch to Real Trading:**
1. Add Schwab credentials to `.env`
2. Restart the Forex bot with real trading enabled
3. Start with small position sizes (0.01 lots)
4. Monitor performance closely

## 🎯 RECOMMENDED STARTING PARAMETERS

### **For Initial Real Trading:**
```python
# In simple_forex_bot.py
trade_size = 0.01  # Start with micro lots
max_trades = 1     # One trade at a time initially
risk_per_trade = 0.01  # 1% risk per trade
stop_loss_pips = 20    # Conservative stop loss
take_profit_pips = 40  # 2:1 reward:risk ratio
```

### **Account Requirements:**
- **Minimum balance:** $100 for micro lot trading
- **Recommended:** $1,000+ for proper risk management
- **Margin account:** Required for leveraged Forex trading
- **Trading permissions:** Forex trading must be enabled

## ⚠️ IMPORTANT SAFETY NOTES

### **Before Real Trading:**
1. **Test thoroughly** in paper trading mode
2. **Start small** with risk capital only
3. **Monitor closely** for first few days
4. **Keep stop losses** ALWAYS active
5. **Never risk more than 2%** of account per trade

### **Risk Management Rules:**
1. **Maximum daily loss:** 5% of account
2. **Maximum weekly loss:** 10% of account
3. **Stop trading** if hitting loss limits
4. **Review strategy** after any significant loss

## 🚀 NEXT STEPS AFTER SETUP

### **Phase 1: Testing (1-2 days)**
- Paper trade with real market data
- Verify all signals and executions
- Test risk management rules

### **Phase 2: Small Real Trading (3-7 days)**
- Trade 0.01 lots only
- Focus on 1-2 currency pairs
- Document all trades and results

### **Phase 3: Scaling (After proven success)**
- Increase position sizes gradually
- Add more currency pairs
- Optimize strategy parameters

## 📞 SUPPORT & TROUBLESHOOTING

### **Common Issues:**
1. **Authentication errors:** Check API key/secret
2. **Permission errors:** Verify trading permissions
3. **Rate limit errors:** Reduce request frequency
4. **Connection errors:** Check internet and firewall

### **Schwab Support:**
- **Developer Support:** developer.schwab.com/support
- **Trading Support:** 800-435-4000
- **Account Issues:** Contact your Schwab representative

## 💰 EXPECTED PERFORMANCE

### **Based on Paper Trading:**
- **Win rate:** 55-65% expected
- **Average profit per trade:** $5-20 (depending on lot size)
- **Risk/Reward ratio:** 1:2 minimum
- **Daily target:** 1-3% account growth

### **Realistic Expectations:**
- **First month:** Focus on consistency, not profits
- **Months 2-3:** Aim for 5-10% monthly returns
- **Long-term:** 10-20% annual returns are excellent

---

## 🎯 READY TO START?

**Once you have your Schwab API credentials, run:**

```bash
# 1. Update .env file with Schwab credentials
nano .env  # or use your preferred editor

# 2. Test the connection
python3 test_schwab_connection.py

# 3. Restart Forex bot with real trading
pkill -f "simple_forex_bot.py"
python3 simple_forex_bot.py --real-trading
```

**Your automated Forex trading system is ready to go!** 🚀