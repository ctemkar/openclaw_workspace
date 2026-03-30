#!/usr/bin/env python3
import json
import subprocess
import datetime
import sys

def fetch_endpoint(endpoint):
    """Fetch data from dashboard endpoint"""
    try:
        result = subprocess.run(['curl', '-s', f'http://localhost:5001{endpoint}'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
        return None

def analyze_trading_data():
    """Analyze trading dashboard data for monitoring"""
    
    print("=== TRADING DASHBOARD MONITORING ANALYSIS ===")
    print(f"Analysis Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Current Time (Bangkok): {datetime.datetime.now().strftime('%A, %B %d, %Y — %I:%M %p')}")
    print()
    
    # Fetch status
    status_raw = fetch_endpoint('/status')
    if not status_raw:
        print("❌ ERROR: Cannot fetch status endpoint")
        return False
    
    try:
        status_data = json.loads(status_raw)
    except json.JSONDecodeError:
        print("❌ ERROR: Invalid JSON from status endpoint")
        return False
    
    # Fetch trades
    trades_raw = fetch_endpoint('/trades')
    trades_data = {}
    if trades_raw:
        try:
            trades_data = json.loads(trades_raw)
        except json.JSONDecodeError:
            print("⚠️  Warning: Invalid JSON from trades endpoint")
    
    # Fetch summary
    summary_raw = fetch_endpoint('/summary')
    
    # Fetch strategy
    strategy_raw = fetch_endpoint('/strategy')
    strategy_data = {}
    if strategy_raw:
        try:
            strategy_data = json.loads(strategy_raw)
        except json.JSONDecodeError:
            print("⚠️  Warning: Invalid JSON from strategy endpoint")
    
    # Extract key metrics
    system_status = status_data.get('status', 'unknown')
    capital = status_data.get('capital', 0)
    last_analysis = status_data.get('last_analysis', 'unknown')
    risk_params = status_data.get('risk_parameters', {})
    stop_loss = risk_params.get('stop_loss', 0.05)
    take_profit = risk_params.get('take_profit', 0.10)
    max_trades = risk_params.get('max_trades_per_day', 2)
    
    # Analyze trades
    trade_count = trades_data.get('count', 0)
    trades = trades_data.get('trades', [])
    
    print("=== SYSTEM STATUS ===")
    print(f"Status: {system_status}")
    print(f"Capital: ${capital:.2f}")
    print(f"Last Analysis: {last_analysis}")
    print(f"Port: {status_data.get('port', 'unknown')}")
    print(f"Analysis Scheduled: {status_data.get('analysis_scheduled', 'unknown')}")
    
    print("\n=== RISK PARAMETERS ===")
    print(f"Stop Loss: {stop_loss*100:.1f}%")
    print(f"Take Profit: {take_profit*100:.1f}%")
    print(f"Max Trades/Day: {max_trades}")
    
    print("\n=== TRADING ACTIVITY ===")
    print(f"Total Trades: {trade_count}")
    
    if trades:
        print(f"Recent Trades: {len(trades)}")
        
        # Categorize trades
        gemini_trades = [t for t in trades if t.get('model') == 'Gemini']
        buy_trades = [t for t in trades if t.get('side', '').lower() == 'buy']
        sell_trades = [t for t in trades if t.get('side', '').lower() == 'sell']
        
        print(f"Gemini Trades: {len(gemini_trades)}")
        print(f"Buy Trades: {len(buy_trades)}")
        print(f"Sell Trades: {len(sell_trades)}")
        
        # Check for daily limit
        if trade_count >= max_trades:
            print("⚠️  WARNING: At or exceeding daily trade limit")
        
        # Check for recent activity
        recent_trades = []
        for trade in trades[:5]:  # Check most recent 5 trades
            if 'time' in trade:
                recent_trades.append(trade)
        
        if recent_trades:
            print(f"\nMost Recent Trades:")
            for i, trade in enumerate(recent_trades[:3], 1):
                symbol = trade.get('symbol', 'Unknown')
                side = trade.get('side', 'Unknown')
                price = trade.get('price', trade.get('amount', 'N/A'))
                time = trade.get('time', 'Unknown')
                print(f"  {i}. {symbol} {side} @ {price} ({time})")
    else:
        print("No recent trades found")
    
    print("\n=== STRATEGY OVERVIEW ===")
    if strategy_data:
        print(f"Strategy: {strategy_data.get('name', 'Unknown')}")
        print(f"Description: {strategy_data.get('description', 'Unknown')}")
        print(f"Created: {strategy_data.get('created', 'Unknown')}")
        
        execution = strategy_data.get('execution', {})
        gemini = execution.get('gemini', {})
        binance = execution.get('binance', {})
        
        if gemini:
            print(f"Gemini Action: {gemini.get('action', 'Unknown')}")
            print(f"Gemini Capital/Trade: ${gemini.get('capital_per_trade', 0):.2f}")
        
        if binance:
            print(f"Binance Action: {binance.get('action', 'Unknown')}")
            print(f"Binance Capital/Trade: ${binance.get('capital_per_trade', 0):.2f}")
    else:
        print("Strategy data not available")
    
    print("\n=== HEALTH CHECKS ===")
    checks = []
    
    # Check if system is running
    if system_status == 'running':
        checks.append(("✅ System Status", "Running"))
    else:
        checks.append(("❌ System Status", f"Not running: {system_status}"))
    
    # Check last analysis time
    try:
        last_analysis_dt = datetime.datetime.fromisoformat(last_analysis.replace('Z', '+00:00'))
        now = datetime.datetime.now(datetime.timezone.utc)
        hours_since = (now - last_analysis_dt).total_seconds() / 3600
        
        if hours_since <= 2:
            checks.append(("✅ Last Analysis", f"{hours_since:.1f} hours ago"))
        elif hours_since <= 6:
            checks.append(("⚠️  Last Analysis", f"{hours_since:.1f} hours ago - getting stale"))
        else:
            checks.append(("❌ Last Analysis", f"{hours_since:.1f} hours ago - too old"))
    except Exception as e:
        checks.append(("⚠️  Last Analysis", f"Parse error: {e}"))
    
    # Check capital
    if capital >= 200:
        checks.append(("✅ Capital", f"${capital:.2f}"))
    elif capital >= 100:
        checks.append(("⚠️  Capital", f"${capital:.2f} - below optimal"))
    else:
        checks.append(("❌ Capital", f"${capital:.2f} - critically low"))
    
    # Check trade count vs limit
    if trade_count < max_trades:
        checks.append(("✅ Trade Count", f"{trade_count}/{max_trades}"))
    elif trade_count == max_trades:
        checks.append(("⚠️  Trade Count", f"{trade_count}/{max_trades} - at limit"))
    else:
        checks.append(("❌ Trade Count", f"{trade_count}/{max_trades} - exceeded limit"))
    
    for check, status in checks:
        print(f"{check}: {status}")
    
    print("\n=== CRITICAL ALERT CHECK ===")
    critical_alerts = []
    
    # Check for potential stop-loss triggers
    # (In a real system, we'd compare current prices with entry prices)
    if capital < 150:
        critical_alerts.append(f"CRITICAL: Capital below ${capital:.2f} - consider reducing position sizes")
    
    if trade_count > max_trades:
        critical_alerts.append(f"CRITICAL: Exceeded daily trade limit ({trade_count}/{max_trades})")
    
    # Check if last analysis is too old
    try:
        last_analysis_dt = datetime.datetime.fromisoformat(last_analysis.replace('Z', '+00:00'))
        now = datetime.datetime.now(datetime.timezone.utc)
        hours_since = (now - last_analysis_dt).total_seconds() / 3600
        
        if hours_since > 12:
            critical_alerts.append(f"CRITICAL: Last analysis was {hours_since:.1f} hours ago - system may be stale")
    except:
        pass
    
    if critical_alerts:
        print("🚨 CRITICAL ALERTS DETECTED:")
        for alert in critical_alerts:
            print(f"  • {alert}")
    else:
        print("✅ No critical alerts detected")
    
    print("\n=== RECOMMENDATIONS ===")
    recommendations = []
    
    # Check if we need to run analysis
    try:
        last_analysis_dt = datetime.datetime.fromisoformat(last_analysis.replace('Z', '+00:00'))
        now = datetime.datetime.now(datetime.timezone.utc)
        hours_since = (now - last_analysis_dt).total_seconds() / 3600
        
        if hours_since > 6:
            recommendations.append("Run new market analysis (last analysis > 6 hours ago)")
    except:
        recommendations.append("Check analysis schedule - unable to parse last analysis time")
    
    if trade_count >= max_trades:
        recommendations.append("Daily trade limit reached - pause trading until tomorrow")
    
    if not recommendations:
        recommendations.append("System operating within normal parameters")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    return True, critical_alerts

if __name__ == "__main__":
    success, critical_alerts = analyze_trading_data()
    
    # Log results
    log_entry = f"""
{'='*60}
TRADING MONITORING LOG - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
    
    # Capture print output
    import io
    from contextlib import redirect_stdout
    
    f = io.StringIO()
    with redirect_stdout(f):
        analyze_trading_data()
    
    log_entry += f.getvalue()
    
    # Write to monitoring log
    try:
        with open('/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log', 'a') as f:
            f.write(log_entry)
        print(f"\n✅ Log written to trading_monitoring.log")
    except Exception as e:
        print(f"\n⚠️  Could not write to log file: {e}")
    
    # Write critical alerts if any
    if critical_alerts:
        try:
            alert_entry = f"""
{'='*60}
CRITICAL ALERT - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
            for alert in critical_alerts:
                alert_entry += f"🚨 {alert}\\n"
            
            with open('/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log', 'a') as f:
                f.write(alert_entry)
            print(f"✅ Critical alerts written to critical_alerts.log")
        except Exception as e:
            print(f"⚠️  Could not write critical alerts: {e}")