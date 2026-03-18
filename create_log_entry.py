#!/usr/bin/env python3
import json
import sys
from datetime import datetime

def create_log_entry(data):
    """Create a formatted log entry from monitoring data"""
    
    # Get current BTC price from trades analysis
    btc_current_price = data['trading_data']['price_analysis']['btc_price_range'][0]  # Current is the lower bound
    eth_current_price = data['trading_data']['price_analysis']['eth_price_range'][0]  # Current is the lower bound
    
    log_entry = f"""
=== TRADING MONITORING LOG ===
Timestamp: {data['timestamp']}

DASHBOARD STATUS:
- Dashboard: {'✓ Reachable' if data['dashboard_status']['reachable'] else '✗ Unreachable'}
- Trading API: {'✓ Reachable' if data['dashboard_status']['trading_api_reachable'] else '✗ Unreachable'}

TRADING DATA:
- Total Trades: {data['trading_data']['total_trades']}
- BTC Trades: {data['trading_data']['trades_by_asset']['BTC']}
- ETH Trades: {data['trading_data']['trades_by_asset']['ETH']}
- SOL Trades: {data['trading_data']['trades_by_asset']['SOL']}
- BTC Price: ${btc_current_price:,.2f}
- ETH Price: ${eth_current_price:,.2f}

STRATEGY STATUS:
- Capital: ${data['strategy_analysis']['capital']:,.2f}
- Stop Loss: {data['strategy_analysis']['stop_loss_percent']}%
- Take Profit: {data['strategy_analysis']['take_profit_percent']}%
- Today's Trades: {data['strategy_analysis']['today_trades_executed']}/{data['strategy_analysis']['today_trades_limit']}
- Available Capital: ${data['strategy_analysis']['available_capital']:,.2f}

RISK ASSESSMENT:
- BTC Drawdown: {data['risk_assessment']['current_conditions']['btc_drawdown_percent']:.2f}%
- Stop Loss Triggered: {'YES ⚠️' if data['risk_assessment']['current_conditions']['stop_loss_triggered'] else 'No ✓'}
- Take Profit Triggered: {'YES ✅' if data['risk_assessment']['current_conditions']['take_profit_triggered'] else 'No'}
- Max Daily Trades: {'Reached ⚠️' if data['risk_assessment']['current_conditions']['max_daily_trades_reached'] else 'Available'}

ALERTS:"""
    
    if data['alerts']['critical_alerts']:
        log_entry += "\n" + "\n".join([f"- ⚠️ CRITICAL: {alert}" for alert in data['alerts']['critical_alerts']])
    else:
        log_entry += "\n- No critical alerts"
    
    if data['alerts']['warnings']:
        log_entry += "\n" + "\n".join([f"- ⚠️ WARNING: {alert}" for alert in data['alerts']['warnings']])
    
    if data['alerts']['info']:
        log_entry += "\n" + "\n".join([f"- ℹ️ INFO: {alert}" for alert in data['alerts']['info']])
    
    return log_entry

if __name__ == "__main__":
    # Read data from stdin
    data = json.load(sys.stdin)
    print(create_log_entry(data))