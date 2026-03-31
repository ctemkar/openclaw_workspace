import requests
import json
import os
from datetime import datetime

LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
STATUS_URL = "http://localhost:5001/status"
TRADES_URL = "http://localhost:5001/trades"

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

def parse_and_log(status_data, trades_data):
    if not status_data:
        return

    log_entry = f"{datetime.now()}: "
    content_to_log = []
    critical_alerts = []

    # Extract and log system status
    status = status_data.get('status')
    capital = status_data.get('capital')
    timestamp = status_data.get('timestamp')
    analysis_scheduled = status_data.get('analysis_scheduled')
    last_analysis = status_data.get('last_analysis')
    trading_pairs = status_data.get('trading_pairs', [])
    
    # Extract P&L data
    pnl = status_data.get('pnl', {})
    total_pnl = pnl.get('total', {})
    binance_pnl = pnl.get('binance', {})
    gemini_pnl = pnl.get('gemini', {})
    
    # Extract risk parameters
    risk_parameters = status_data.get('risk_parameters', {})
    stop_loss = risk_parameters.get('stop_loss')
    take_profit = risk_parameters.get('take_profit')
    max_trades_per_day = risk_parameters.get('max_trades_per_day')
    
    # Log system status
    if status:
        content_to_log.append(f"System Status: {status}")
    
    if capital is not None:
        content_to_log.append(f"Capital: ${capital:.2f}")
        # Check if capital is below critical threshold
        if capital < 200:  # Critical threshold
            critical_alerts.append(f"CRITICAL: Capital below $200 threshold: ${capital:.2f}")
        elif capital < 220:  # Warning threshold
            critical_alerts.append(f"WARNING: Capital below $220 warning level: ${capital:.2f}")
    
    if timestamp:
        content_to_log.append(f"Timestamp: {timestamp}")
    
    if analysis_scheduled:
        content_to_log.append(f"Analysis Schedule: {analysis_scheduled}")
    
    if last_analysis:
        content_to_log.append(f"Last Analysis: {last_analysis}")
    
    if trading_pairs:
        content_to_log.append(f"Trading Pairs: {', '.join(trading_pairs[:5])}{'...' if len(trading_pairs) > 5 else ''}")
    
    # Log P&L data
    if total_pnl:
        content_to_log.append("=== P&L SUMMARY ===")
        unrealized = total_pnl.get('unrealized')
        realized = total_pnl.get('realized')
        total = total_pnl.get('total')
        open_positions = total_pnl.get('open_positions')
        trades = total_pnl.get('trades')
        
        if unrealized is not None:
            content_to_log.append(f"Unrealized P&L: ${unrealized:.4f}")
            if unrealized < -10:  # Critical loss threshold
                critical_alerts.append(f"CRITICAL: Large unrealized loss: ${unrealized:.4f}")
        
        if realized is not None:
            content_to_log.append(f"Realized P&L: ${realized:.4f}")
        
        if total is not None:
            content_to_log.append(f"Total P&L: ${total:.4f}")
            if total < -20:  # Critical total loss threshold
                critical_alerts.append(f"CRITICAL: Large total loss: ${total:.4f}")
        
        if open_positions is not None:
            content_to_log.append(f"Open Positions: {open_positions}")
            if open_positions > 10:  # Too many open positions
                critical_alerts.append(f"WARNING: High number of open positions: {open_positions}")
        
        if trades is not None:
            content_to_log.append(f"Total Trades: {trades}")
    
    # Log exchange-specific P&L
    if binance_pnl:
        binance_unrealized = binance_pnl.get('unrealized')
        if binance_unrealized is not None:
            content_to_log.append(f"Binance Unrealized: ${binance_unrealized:.4f}")
    
    if gemini_pnl:
        gemini_unrealized = gemini_pnl.get('unrealized')
        if gemini_unrealized is not None:
            content_to_log.append(f"Gemini Unrealized: ${gemini_unrealized:.4f}")
    
    # Log risk parameters
    if risk_parameters:
        content_to_log.append("=== RISK PARAMETERS ===")
        if stop_loss is not None:
            content_to_log.append(f"Stop Loss: {stop_loss*100:.1f}%")
        
        if take_profit is not None:
            content_to_log.append(f"Take Profit: {take_profit*100:.1f}%")
        
        if max_trades_per_day is not None:
            content_to_log.append(f"Max Trades/Day: {max_trades_per_day}")
            if max_trades_per_day > 10:  # Too many trades per day
                critical_alerts.append(f"WARNING: High max trades per day setting: {max_trades_per_day}")
    
    # Calculate drawdown if we have initial capital reference
    # Assuming initial capital was $250 based on previous logs
    INITIAL_CAPITAL = 250.0
    if capital is not None:
        drawdown = (INITIAL_CAPITAL - capital) / INITIAL_CAPITAL
        content_to_log.append(f"Drawdown from $250: {drawdown*100:.1f}%")
        if drawdown > 0.20:  # 20% drawdown threshold
            critical_alerts.append(f"CRITICAL: Drawdown exceeds 20%: {drawdown*100:.1f}%")
        elif drawdown > 0.15:  # 15% warning threshold
            critical_alerts.append(f"WARNING: Drawdown exceeds 15%: {drawdown*100:.1f}%")
    
    # Analyze trade data if available
    if trades_data and 'trades' in trades_data:
        trades_list = trades_data.get('trades', [])
        trade_count = trades_data.get('count', 0)
        
        if trades_list:
            content_to_log.append(f"\n=== TRADE HISTORY ({trade_count} trades) ===")
            
            # Analyze trade performance
            profitable_trades = 0
            losing_trades = 0
            eth_trades = 0
            btc_trades = 0
            
            for i, trade in enumerate(trades_list[:5]):  # Show first 5 trades
                symbol = trade.get('symbol', 'Unknown')
                side = trade.get('side', 'Unknown')
                price = trade.get('price', 0)
                quantity = trade.get('quantity', 0)
                reason = trade.get('reason', 'No reason provided')
                
                # Count symbol types
                if 'ETH' in symbol:
                    eth_trades += 1
                elif 'BTC' in symbol:
                    btc_trades += 1
                
                # Simple profit/loss estimation (this would need actual current prices)
                # For now, just log the trade
                content_to_log.append(f"Trade {i+1}: {side} {symbol} @ ${price:.2f} ({quantity}) - {reason[:50]}...")
            
            # Check for concentration risk
            if eth_trades > 0 and eth_trades / len(trades_list) > 0.7:  # >70% ETH concentration
                critical_alerts.append(f"WARNING: High ETH concentration in trades: {eth_trades}/{len(trades_list)} trades ({eth_trades/len(trades_list)*100:.0f}%)")
            
            if len(trades_list) > 5:
                content_to_log.append(f"... and {len(trades_list) - 5} more trades")


    # Write to main log file
    log_content = "\n".join(content_to_log)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n" + log_content + "\n---\n")

    # Write critical alerts to alert file
    if critical_alerts:
        alert_entry = f"{datetime.now()}: CRITICAL ALERTS DETECTED\n" + "\n".join(critical_alerts) + "\n---\n"
        with open(ALERT_FILE, "a") as f:
            f.write(alert_entry)
        print("Critical alerts saved.")

# --- Main execution ---
if __name__ == "__main__":
    # Ensure log directories exist
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(ALERT_FILE), exist_ok=True)

    print(f"Fetching status data from {STATUS_URL}...")
    status_data = fetch_data(STATUS_URL)
    
    print(f"Fetching trade data from {TRADES_URL}...")
    trades_data = fetch_data(TRADES_URL)
    
    if status_data:
        print("Data fetched successfully. Parsing and logging...")
        parse_and_log(status_data, trades_data)
        print("Processing complete.")
    else:
        print("Failed to fetch status data. Skipping processing.")
