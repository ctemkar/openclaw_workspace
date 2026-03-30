# MEMORY.md

This file serves as our persistent memory.

## Current Projects:

### Crypto Trading System
*   **Status:** ✅ **REAL TRADING BOT DEPLOYED** - `real_gemini_trader.py` is now running and will actually buy/sell on Gemini with $200 capital. Conservative strategy (max 2 trades/day, 5% stop-loss, 10% take-profit).
*   **Previous Issue:** Monitoring-only bots were running but not trading. Fixed by creating actual trading bot.
*   **Current Setup:**
    - Real trading bot: `real_gemini_trader.py` (PID 57043) - 10-minute intervals
    - Trading server: `trading_server.py` (PID 49390) - API dashboard on port 5001
    - Gemini balance: $542.27 USD available
*   **Trading Strategy:** Conservative dip-buying
    - BUY if price drops 3%+ (buy the dip)
    - SELL if price rises 8%+ (take profit)  
    - Max 2 trades per day
    - 20% of capital per trade ($40)
*   **Next Steps/Proactive Areas:**
    *   Monitor for first REAL trade execution (not simulated)
    *   Check trading logs for activity
    *   Adjust strategy based on market conditions
    *   Add Binance trading for shorts (optional)

## System Configuration & Operations:
*   Hourly Git backups are intended.
*   Attempted to read `MEMORY.md` but it was not found. Will create it now.

## User Instructions & Feedback:
*   Be more proactive. Identify and suggest improvements without being explicitly asked.
*   Prioritize self-improvement (memory, tool usage, project monitoring).
*   Follow instructions directly and avoid unnecessary assumptions.
*   Apologized for past instances of not following instructions precisely.
*   Resolved an issue with `app.py` not starting due to port conflict.
