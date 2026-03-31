#!/usr/bin/env python3
import requests
import json
import time
from datetime import datetime
import sys

def fetch_endpoint(endpoint):
    """Fetch data from a specific endpoint"""
    try:
        url = f"http://localhost:5001{endpoint}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
    except Exception as e:
        return f"Error fetching {endpoint}: {e}"

def extract_trading_data():
    """Extract trading data from all endpoints"""
    print("=== Trading Dashboard Monitoring ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Fetch all endpoints
    endpoints = ['/status', '/analysis', '/trades', '/strategy', '/summary']
    data = {}
    
    for endpoint in endpoints:
        print(f"\n--- {endpoint.upper()} ---")
        result = fetch_endpoint(endpoint)
        data[endpoint] = result
        
        if isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(result)
    
    return data

def analyze_critical_events(data):
    """Analyze data for critical events like stop-loss/take-profit triggers"""
    critical_alerts = []
    
    # Check status for critical conditions
    if '/status' in data and isinstance(data['/status'], dict):
        status = data['/status']
        
        # Check for drawdown warnings
        if 'drawdown_warning' in str(status).lower() or 'drawdown' in str(status):
            critical_alerts.append("⚠️ Drawdown warning detected in system status")
        
        # Check for stop-loss triggers
        if 'stop_loss' in str(status).lower() or 'sl' in str(status).lower():
            critical_alerts.append("🛑 Stop-loss order triggered")
        
        # Check for take-profit triggers
        if 'take_profit' in str(status).lower() or 'tp' in str(status).lower():
            critical_alerts.append("✅ Take-profit order triggered")
    
    # Check trades for critical events
    if '/trades' in data:
        trades_data = data['/trades']
        if isinstance(trades_data, dict) and 'trades' in trades_data:
            for trade in trades_data['trades']:
                trade_str = str(trade).lower()
                if 'stop' in trade_str and 'loss' in trade_str:
                    critical_alerts.append(f"🛑 Stop-loss in trade: {trade}")
                if 'take' in trade_str and 'profit' in trade_str:
                    critical_alerts.append(f"✅ Take-profit in trade: {trade}")
                if 'drawdown' in trade_str:
                    critical_alerts.append(f"⚠️ Drawdown in trade: {trade}")
    
    # Check summary for risk parameters
    if '/summary' in data and isinstance(data['/summary'], dict):
        summary = data['/summary']
        
        # Check equity vs capital
        if 'equity' in summary and 'capital' in summary:
            equity = float(str(summary['equity']).replace('$', '').replace(',', ''))
            capital = float(str(summary['capital']).replace('$', '').replace(',', ''))
            drawdown_pct = ((capital - equity) / capital) * 100
            
            if drawdown_pct > 5:  # More than 5% drawdown
                critical_alerts.append(f"⚠️ Significant drawdown: {drawdown_pct:.1f}% (Equity: ${equity:.2f}, Capital: ${capital:.2f})")
            
            if drawdown_pct > 10:  # Critical drawdown
                critical_alerts.append(f"🚨 CRITICAL DRAWDOWN: {drawdown_pct:.1f}% - Immediate attention required!")
    
    return critical_alerts

def main():
    # Extract trading data
    data = extract_trading_data()
    
    # Analyze for critical events
    critical_alerts = analyze_critical_events(data)
    
    # Log to trading_monitoring.log
    with open('trading_monitoring.log', 'a') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Monitoring timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n\n")
        
        for endpoint, content in data.items():
            f.write(f"{endpoint.upper()}:\n")
            if isinstance(content, dict):
                f.write(json.dumps(content, indent=2))
            else:
                f.write(str(content))
            f.write("\n\n")
    
    # Log critical alerts to separate file
    if critical_alerts:
        with open('critical_alerts.log', 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Alert timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
            for alert in critical_alerts:
                f.write(f"{alert}\n")
            f.write("\n")
    
    # Generate summary
    print(f"\n{'='*60}")
    print("MONITORING SUMMARY")
    print(f"{'='*60}")
    print(f"Monitoring completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Data logged to: trading_monitoring.log")
    
    if critical_alerts:
        print(f"\n🚨 CRITICAL ALERTS DETECTED ({len(critical_alerts)}):")
        for alert in critical_alerts:
            print(f"  • {alert}")
        print(f"Alerts logged to: critical_alerts.log")
    else:
        print(f"\n✅ No critical alerts detected")
        print("System appears to be operating within normal parameters")
    
    # Return summary for cron delivery
    summary_text = f"Trading Dashboard Monitoring - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    summary_text += f"Data extracted from 5 endpoints and logged to trading_monitoring.log\n"
    
    if critical_alerts:
        summary_text += f"\nCRITICAL ALERTS ({len(critical_alerts)}):\n"
        for alert in critical_alerts:
            summary_text += f"• {alert}\n"
        summary_text += f"\nAlerts logged to critical_alerts.log"
    else:
        summary_text += f"\nNo critical alerts detected. System operating normally."
    
    print(f"\n{'='*60}")
    print("SUMMARY FOR DELIVERY:")
    print(f"{'='*60}")
    print(summary_text)
    
    # Also write summary to file for reference
    with open('monitoring_summary.txt', 'w') as f:
        f.write(summary_text)

if __name__ == "__main__":
    main()