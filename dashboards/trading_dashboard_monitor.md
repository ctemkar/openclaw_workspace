# trading_dashboard_monitor

This agent monitors the trading dashboard at http://localhost:5001/.

It extracts and logs trading logs, status updates, and risk parameters to `./trading_monitoring.log`.

It also detects and logs critical events such as stop-loss orders, take-profit orders, and critical drawdowns to `./critical_alerts.log`.

A plain text summary of the analysis and any critical alerts is automatically delivered.