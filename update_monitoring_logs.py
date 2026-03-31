#!/usr/bin/env python3
import json
import requests
from datetime import datetime
import sys

def fetch_trading_data():
    """Fetch current trading data from all endpoints"""
    endpoints = ['/status', '/trades', '/summary']
    data = {}
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'http://localhost:5001{endpoint}', timeout=10)
            if response.status_code == 200:
                if endpoint == '/summary':
                    data[endpoint] = response.text
                else:
                    try:
                        data[endpoint] = response.json()
                    except:
                        data[endpoint] = response.text
            else:
                data[endpoint] = f"Error: HTTP {response.status_code}"
        except Exception as e:
            data[endpoint] = f"Error: {str(e)}"
    
    return data

def analyze_critical_alerts(trades_data, current_prices=None):
    """Analyze trades for critical alerts"""
    critical_alerts = []
    warning_alerts = []
    
    if not isinstance(trades_data, dict) or 'trades' not in trades_data:
        return critical_alerts, warning_alerts
    
    # Default current prices if not provided
    if current_prices is None:
        current_prices = {
            'BTC/USD': 68068.61,
            'ETH/USD': 2083.74
        }
    
    for trade in trades_data.get('trades', []):
        symbol = trade.get('symbol', '')
        entry_price = trade.get('price', 0)
        quantity = trade.get('quantity', 0)
        
        if not symbol or entry_price <= 0:
            continue
            
        # Get current price for this symbol
        current_price = current_prices.get(symbol, 0)
        if current_price <= 0:
            continue
        
        # Calculate percentage change
        pct_change = ((current_price - entry_price) / entry_price) * 100
        
        # Check for stop-loss trigger (5% for Gemini, 7% for Binance)
        # Based on the dashboard, using 5% stop-loss for analysis
        stop_loss_pct = -5.0  # 5% stop-loss
        
        # Check for take-profit trigger (10% for Gemini, 8% for Binance)
        take_profit_pct = 10.0  # 10% take-profit
        
        position_value = entry_price * quantity
        current_value = current_price * quantity
        pnl = current_value - position_value
        
        trade_info = {
            'symbol': symbol,
            'entry_price': entry_price,
            'current_price': current_price,
            'quantity': quantity,
            'pct_change': pct_change,
            'pnl': pnl,
            'time': trade.get('time', ''),
            'reason': trade.get('reason', '')
        }
        
        # Check for critical alerts
        if pct_change <= stop_loss_pct:
            critical_alerts.append({
                'type': 'STOP_LOSS_TRIGGERED',
                'message': f"{symbol} stop-loss triggered: {pct_change:.2f}% loss (entry: ${entry_price:.2f}, current: ${current_price:.2f})",
                'trade_info': trade_info
            })
        elif pct_change <= stop_loss_pct * 1.1:  # Within 10% of stop-loss
            warning_alerts.append({
                'type': 'NEAR_STOP_LOSS',
                'message': f"{symbol} near stop-loss: {pct_change:.2f}% loss (entry: ${entry_price:.2f}, current: ${current_price:.2f})",
                'trade_info': trade_info
            })
        elif pct_change >= take_profit_pct:
            critical_alerts.append({
                'type': 'TAKE_PROFIT_TRIGGERED',
                'message': f"{symbol} take-profit triggered: {pct_change:.2f}% gain (entry: ${entry_price:.2f}, current: ${current_price:.2f})",
                'trade_info': trade_info
            })
        elif pct_change >= take_profit_pct * 0.9:  # Within 90% of take-profit
            warning_alerts.append({
                'type': 'NEAR_TAKE_PROFIT',
                'message': f"{symbol} near take-profit: {pct_change:.2f}% gain (entry: ${entry_price:.2f}, current: ${current_price:.2f})",
                'trade_info': trade_info
            })
    
    return critical_alerts, warning_alerts

def extract_market_data(summary_text):
    """Extract market data from summary text"""
    market_data = {}
    
    # Simple pattern matching for key market data
    import re
    
    # Extract prices
    btc_match = re.search(r'BTC/USD.*?\$([\d,]+\.\d+)', summary_text)
    eth_match = re.search(r'ETH/USD.*?\$([\d,]+\.\d+)', summary_text)
    
    if btc_match:
        market_data['BTC/USD'] = float(btc_match.group(1).replace(',', ''))
    if eth_match:
        market_data['ETH/USD'] = float(eth_match.group(1).replace(',', ''))
    
    # Extract volume
    btc_vol_match = re.search(r'BTC 24h Volume.*?\$([\d,]+)', summary_text)
    eth_vol_match = re.search(r'ETH 24h Volume.*?\$([\d,]+)', summary_text)
    
    if btc_vol_match:
        market_data['BTC_24h_volume'] = float(btc_vol_match.group(1).replace(',', ''))
    if eth_vol_match:
        market_data['ETH_24h_volume'] = float(eth_vol_match.group(1).replace(',', ''))
    
    # Extract sentiment
    sentiment_match = re.search(r'Market Sentiment.*?([A-Z]+)', summary_text)
    if sentiment_match:
        market_data['sentiment'] = sentiment_match.group(1)
    
    return market_data

def main():
    # Fetch current data
    print("Fetching trading data...", file=sys.stderr)
    data = fetch_trading_data()
    
    # Extract trades data
    trades_data = data.get('/trades', {})
    if isinstance(trades_data, str) and trades_data.startswith('{'):
        try:
            trades_data = json.loads(trades_data)
        except:
            trades_data = {}
    
    # Extract market data from summary
    summary_text = data.get('/summary', '')
    market_data = extract_market_data(summary_text)
    
    # Get current prices for analysis
    current_prices = {
        'BTC/USD': market_data.get('BTC/USD', 68068.61),
        'ETH/USD': market_data.get('ETH/USD', 2083.74)
    }
    
    # Analyze for critical alerts
    critical_alerts, warning_alerts = analyze_critical_alerts(trades_data, current_prices)
    
    # Get system status
    status_data = data.get('/status', {})
    if isinstance(status_data, str) and status_data.startswith('{'):
        try:
            status_data = json.loads(status_data)
        except:
            status_data = {}
    
    # Prepare monitoring log
    timestamp = datetime.now().strftime('%Y-%m-%d %I:%M %p (Asia/Bangkok)')
    
    monitoring_log = f"""=== TRADING MONITORING LOG ===
Timestamp: {timestamp}
Monitoring Period: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== SYSTEM STATUS ===
- Status: {status_data.get('status', 'unknown')}
- Capital: ${status_data.get('capital', 0):.2f}
- Analysis Scheduled: {status_data.get('analysis_scheduled', 'unknown')}
- Last Analysis: {status_data.get('last_analysis', 'unknown')}
- Risk Parameters:
  * Max trades per day: {status_data.get('risk_parameters', {}).get('max_trades_per_day', 2)}
  * Stop-loss: {status_data.get('risk_parameters', {}).get('stop_loss', 0.05)*100:.1f}%
  * Take-profit: {status_data.get('risk_parameters', {}).get('take_profit', 0.1)*100:.1f}%
- Trading Pairs: {', '.join(status_data.get('trading_pairs', ['BTC/USD', 'ETH/USD']))}

=== RECENT TRADES ({trades_data.get('count', 0)} total) ===
"""
    
    # Add trade details
    for i, trade in enumerate(trades_data.get('trades', [])[:10], 1):
        monitoring_log += f"""{i}. {trade.get('symbol', 'N/A')} - {trade.get('side', 'N/A')}
   Time: {trade.get('time', 'N/A')}
   Price: ${trade.get('price', 0):.2f}
   Quantity: {trade.get('quantity', 0)}
   Reason: {trade.get('reason', 'N/A')}

"""
    
    # Add market data
    monitoring_log += f"""=== MARKET DATA ===
- BTC/USD: ${market_data.get('BTC/USD', 0):.2f}
- ETH/USD: ${market_data.get('ETH/USD', 0):.2f}
- BTC 24h Volume: ${market_data.get('BTC_24h_volume', 0):,.0f}
- ETH 24h Volume: ${market_data.get('ETH_24h_volume', 0):,.0f}
- Market Sentiment: {market_data.get('sentiment', 'UNKNOWN')}

=== ALERT SUMMARY ===
- Critical Alerts: {len(critical_alerts)}
- Warning Alerts: {len(warning_alerts)}
- Total Open Positions: {trades_data.get('count', 0)}

=== END OF MONITORING LOG ===
Log generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # Prepare critical alerts log
    alerts_log = f"""=== CRITICAL ALERTS LOG ===
Timestamp: {timestamp}
Alert Scan Period: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== CURRENT MARKET PRICES ===
- BTC/USD: ${market_data.get('BTC/USD', 0):.2f}
- ETH/USD: ${market_data.get('ETH/USD', 0):.2f}

"""
    
    if critical_alerts:
        alerts_log += "=== 🚨 CRITICAL ALERTS DETECTED ===\n\n"
        for i, alert in enumerate(critical_alerts, 1):
            trade_info = alert['trade_info']
            alerts_log += f"""🚨 CRITICAL ALERT #{i}: {alert['type']}
   Symbol: {trade_info['symbol']}
   Trade Time: {trade_info['time']}
   Entry Price: ${trade_info['entry_price']:.2f}
   Current Price: ${trade_info['current_price']:.2f}
   Change: {trade_info['pct_change']:.2f}%
   P&L: ${trade_info['pnl']:.2f}
   Quantity: {trade_info['quantity']}
   Reason: {trade_info['reason']}
   Alert: {alert['message']}
   
"""
    else:
        alerts_log += "=== ✅ NO CRITICAL ALERTS DETECTED ===\n\n"
    
    if warning_alerts:
        alerts_log += "=== ⚠️ WARNING ALERTS ===\n\n"
        for i, alert in enumerate(warning_alerts, 1):
            trade_info = alert['trade_info']
            alerts_log += f"""⚠️ WARNING ALERT #{i}: {alert['type']}
   Symbol: {trade_info['symbol']}
   Trade Time: {trade_info['time']}
   Entry Price: ${trade_info['entry_price']:.2f}
   Current Price: ${trade_info['current_price']:.2f}
   Change: {trade_info['pct_change']:.2f}%
   P&L: ${trade_info['pnl']:.2f}
   Alert: {alert['message']}
   
"""
    
    # Add risk assessment
    total_positions = trades_data.get('count', 0)
    critical_count = len(critical_alerts)
    warning_count = len(warning_alerts)
    
    if total_positions > 0:
        risk_level = "HIGH" if critical_count > 0 else "MEDIUM" if warning_count > 0 else "LOW"
        alerts_log += f"""=== RISK ASSESSMENT ===
- Total Open Positions: {total_positions}
- Critical Alerts: {critical_count}
- Warning Alerts: {warning_count}
- Safe Positions: {total_positions - critical_count - warning_count}
- Overall Risk Level: {risk_level}

"""
    
    # Add recommendations if there are alerts
    if critical_alerts or warning_alerts:
        alerts_log += "=== RECOMMENDED ACTIONS ===\n"
        if critical_alerts:
            alerts_log += "1. IMMEDIATE: Review all critical alert positions for potential exit\n"
        if warning_alerts:
            alerts_log += "2. URGENT: Monitor warning alert positions closely\n"
        alerts_log += "3. Review overall portfolio exposure and risk parameters\n"
        alerts_log += "4. Consider adjusting position sizing or stop-loss levels\n"
        alerts_log += "5. Review market conditions for affected trading pairs\n\n"
    
    alerts_log += f"""=== END OF ALERTS LOG ===
Alert generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    return {
        'monitoring_log': monitoring_log,
        'alerts_log': alerts_log,
        'critical_alerts_count': len(critical_alerts),
        'warning_alerts_count': len(warning_alerts),
        'market_data': market_data
    }

if __name__ == '__main__':
    try:
        result = main()
        
        # Write monitoring log
        with open('trading_monitoring.log', 'w') as f:
            f.write(result['monitoring_log'])
        
        # Write alerts log
        with open('critical_alerts.log', 'w') as f:
            f.write(result['alerts_log'])
        
        # Print summary
        print(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'monitoring_log_written': True,
            'alerts_log_written': True,
            'critical_alerts': result['critical_alerts_count'],
            'warning_alerts': result['warning_alerts_count'],
            'market_data': result['market_data']
        }, indent=2))
        
    except Exception as e:
        print(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }, indent=2))
        sys.exit(1)