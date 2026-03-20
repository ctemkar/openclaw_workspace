# trading_dashboard_monitor - Job Summary
This job monitors the trading dashboard at http://localhost:5001/ every 5 minutes.
It extracts trading logs, status updates, and risk parameters, logging them to `trading_monitoring.log`.
Critical events such as stop-loss/take-profit orders or significant drawdowns are logged to `critical_alerts.log`.
A plain text summary of the analysis and any critical alerts will be provided.

**Next run:** Immediately after cron job creation, and then every 5 minutes.
**Logging:**
- Trading data: `/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log`
- Critical alerts: `/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log`
