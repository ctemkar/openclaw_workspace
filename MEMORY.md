# MEMORY.md

This file serves as our persistent memory.

## Current Projects:

### Crypto Trading System
*   **Status:** Dashboard/API is running (port 54213) but trading bot is currently stopped. Bot shut down gracefully after not finding buy opportunities. Last active trading was earlier today with 2 historical trades.
*   **Visuals Provided:** User shared an example of the app's UI.
*   **Current Challenge:** Port 5001 was in use when trying to start `app.py`, but was resolved. All hardcoded port references have been fixed to use dynamic port allocation.
*   **Recent Activity:** Progress monitor running every 10 minutes shows API port changes (62022 → 54213) and bot status changes.
*   **Next Steps/Proactive Areas:**
    *   Determine if bot should be restarted for continuous monitoring.
    *   Analyze performance metrics (win rates, drawdowns, profitability) of each agent.
    *   Review and adjust risk management parameters (stop-loss, take-profit).
    *   Explore new trading strategies and backtest them.
    *   Enhance automated reporting.

## System Configuration & Operations:
*   Hourly Git backups are intended.
*   Attempted to read `MEMORY.md` but it was not found. Will create it now.

## User Instructions & Feedback:
*   Be more proactive. Identify and suggest improvements without being explicitly asked.
*   Prioritize self-improvement (memory, tool usage, project monitoring).
*   Follow instructions directly and avoid unnecessary assumptions.
*   Apologized for past instances of not following instructions precisely.
*   Resolved an issue with `app.py` not starting due to port conflict.
