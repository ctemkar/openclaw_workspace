# Trading Data Processing System

## Overview
A comprehensive system for fetching, processing, and analyzing trading data from the Conservative Crypto Trading System.

## Components

### 1. **fetch_trading_data.py**
- Fetches system status and trade data from the trading server
- Analyzes trading patterns and model performance
- Generates detailed reports with health assessments
- Saves reports with timestamps

### 2. **process_trading_data.sh**
- Main processing script with error handling
- Checks if trading server is running (restarts if needed)
- Executes data fetching and analysis
- Generates final summaries
- Creates log files for tracking

### 3. **cleanup_trading_reports.sh**
- Organizes reports into daily, weekly, and archive folders
- Cleans up old files (keeps last 30 days)
- Maintains system organization

## Data Flow
1. **Fetch** → Status & Trades from `localhost:5001`
2. **Analyze** → Trading patterns, model performance, health checks
3. **Report** → Generate detailed reports with recommendations
4. **Organize** → Archive old reports, keep latest summaries

## Current System Status (as of 2026-03-18 18:22)
- **Server Status**: Running
- **Capital**: $1000.00
- **Total Trades**: 12
- **Buy/Sell Ratio**: 91.7% buys, 8.3% sells
- **Fill Rate**: 83.3%
- **Issue Detected**: Heavy buy bias (91.7%)

## Scheduled Processing
The system is designed to be run on a schedule (e.g., hourly or daily). To set up regular processing:

### Option 1: Cron Job
```bash
# Run hourly
0 * * * * cd /Users/chetantemkar/.openclaw/workspace/app && ./process_trading_data.sh

# Run daily cleanup at 2 AM
0 2 * * * cd /Users/chetantemkar/.openclaw/workspace/app && ./cleanup_trading_reports.sh
```

### Option 2: OpenClaw Scheduled Reminders
Use OpenClaw's reminder system to trigger processing at regular intervals.

## Files Created
- `trading_report_YYYYMMDD_HHMMSS.txt` → Detailed analysis reports
- `trading_summary_latest.txt` → Latest summary (updated each run)
- `trading_data_processing_YYYYMMDD_HHMMSS.log` → Processing logs
- Organized in `reports/` and `logs/` directories

## Health Checks
The system performs automatic health checks:
1. Server responsiveness
2. Trade volume and patterns
3. Buy/sell balance
4. Fill rates
5. Model performance

## Recommendations Generated
Based on analysis, the system provides actionable recommendations to improve trading performance.

## Next Steps
1. Set up regular scheduling (cron or OpenClaw reminders)
2. Monitor the heavy buy bias issue
3. Review trading strategy for better balance
4. Consider adding email/Slack notifications for critical issues