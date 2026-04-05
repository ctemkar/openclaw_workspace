#!/usr/bin/env python3
"""
Enhanced Dashboard Table Generator
Includes additional useful columns for trading analysis.
"""

import json
from datetime import datetime
import os

def load_all_data():
    """Load all trading data from various sources"""
    data = {
        'gemini_trades': [],
        'binance_trades': [],
        'current_prices': {},
        'position_details': {}
    }
    
    # Load Gemini trades
    try:
        with open('daily_trades.json', 'r') as f:
            gemini_data = json.load(f)
            data['gemini_trades'] = gemini_data.get('trades', [])
    except FileNotFoundError:
        print("Warning: daily_trades.json not found")
    
    # Load Binance trades
    try:
        with open('26_crypto_trade_history.json', 'r') as f:
            data['binance_trades'] = json.load(f)
    except FileNotFoundError:
        print("Warning: 26_crypto_trade_history.json not found")
    
    # Load current prices from positions report
    try:
        with open('current_positions_report.txt', 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
            current_symbol = None
            for line in lines:
                # Find symbol
                if any(symbol in line for symbol in ['BTC/USD', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'DOT/USDT']):
                    if 'BTC/USD' in line:
                        current_symbol = 'BTC/USD'
                    elif 'ETH/USDT' in line:
                        current_symbol = 'ETH/USDT'
                    elif 'SOL/USDT' in line:
                        current_symbol = 'SOL/USDT'
                    elif 'XRP/USDT' in line:
                        current_symbol = 'XRP/USDT'
                    elif 'ADA/USDT' in line:
                        current_symbol = 'ADA/USDT'
                    elif 'DOT/USDT' in line:
                        current_symbol = 'DOT/USDT'
                
                # Extract current price
                if 'Current:' in line and '$' in line and current_symbol:
                    price_str = line.split('$')[1].strip()
                    try:
                        data['current_prices'][current_symbol] = float(price_str.replace(',', ''))
                    except:
                        pass
                
                # Extract position details
                if 'Quantity:' in line and current_symbol:
                    try:
                        qty_str = line.split(':')[1].strip()
                        data['position_details'][current_symbol] = {
                            'quantity': float(qty_str),
                            'symbol': current_symbol
                        }
                    except:
                        pass
    except FileNotFoundError:
        print("Warning: current_positions_report.txt not found")
    
    # Load system status for capital info
    try:
        with open('system_status.json', 'r') as f:
            system_data = json.load(f)
            data['capital'] = system_data.get('capital', {})
    except FileNotFoundError:
        print("Warning: system_status.json not found")
        data['capital'] = {}
    
    return data

def calculate_metrics(trade, data):
    """Calculate all metrics for a trade"""
    symbol = trade.get('symbol', '')
    entry_price = trade.get('price', trade.get('current_price', 0))
    position_type = trade.get('type', 'LONG' if trade.get('side') == 'buy' else 'SHORT')
    current_price = data['current_prices'].get(symbol, entry_price)
    
    # P&L calculation
    if position_type == 'LONG':
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
    else:  # SHORT
        pnl_percent = ((entry_price - current_price) / entry_price) * 100
    
    # Dollar P&L
    amount = trade.get('amount', 0)
    if amount > 0:
        if position_type == 'LONG':
            pnl_dollar = amount * (current_price - entry_price)
        else:
            pnl_dollar = amount * (entry_price - current_price)
    else:
        # Estimate from position value
        position_value = trade.get('position_value', trade.get('value', 30))
        pnl_dollar = position_value * (pnl_percent / 100)
    
    # Days held
    days_held = 0
    timestamp = trade.get('timestamp', trade.get('execution_time', ''))
    if timestamp:
        try:
            trade_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            days_held = (datetime.now() - trade_time).total_seconds() / (24 * 3600)
        except:
            pass
    
    # Position size
    position_size = trade.get('position_value', trade.get('value', 0))
    
    # Risk metrics
    capital_risk = trade.get('capital_risk', 0)
    leverage = trade.get('leverage', 1)
    
    # Stop loss and take profit
    stop_loss = trade.get('stop_loss', 0)
    take_profit = trade.get('take_profit', 0)
    
    # Calculate distance to SL/TP
    if stop_loss > 0:
        if position_type == 'LONG':
            sl_distance = ((entry_price - stop_loss) / entry_price) * 100
        else:
            sl_distance = ((stop_loss - entry_price) / entry_price) * 100
    else:
        sl_distance = 0
    
    if take_profit > 0:
        if position_type == 'LONG':
            tp_distance = ((take_profit - entry_price) / entry_price) * 100
        else:
            tp_distance = ((entry_price - take_profit) / entry_price) * 100
    else:
        tp_distance = 0
    
    return {
        'symbol': symbol,
        'exchange': trade.get('exchange', 'Gemini').upper(),
        'type': position_type,
        'entry_price': entry_price,
        'current_price': current_price,
        'quantity': amount,
        'position_size': position_size,
        'timestamp': timestamp,
        'pnl_dollar': round(pnl_dollar, 2),
        'pnl_percent': round(pnl_percent, 2),
        'days_held': round(days_held, 2),
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'sl_distance': round(sl_distance, 2),
        'tp_distance': round(tp_distance, 2),
        'capital_risk': capital_risk,
        'leverage': leverage,
        'status': trade.get('status', 'OPEN')
    }

def generate_enhanced_table(trades_data):
    """Generate enhanced markdown table with all metrics"""
    if not trades_data:
        return "No trades found."
    
    headers = [
        "#", "Symbol", "Exch", "Type", "Entry", "Current", "Qty",
        "Size", "Days", "P&L $", "P&L %", "SL Dist", "TP Dist", 
        "Risk", "Lev", "Status"
    ]
    
    table = []
    
    for i, trade in enumerate(trades_data, 1):
        # Format values
        entry_str = f"${trade['entry_price']:,.2f}" if trade['entry_price'] >= 1000 else f"${trade['entry_price']:.2f}"
        current_str = f"${trade['current_price']:,.2f}" if trade['current_price'] >= 1000 else f"${trade['current_price']:.2f}"
        
        # P&L with color
        if trade['pnl_dollar'] > 0:
            pnl_dollar_str = f"🟢 ${trade['pnl_dollar']:+.2f}"
            pnl_percent_str = f"🟢 {trade['pnl_percent']:+.2f}%"
        elif trade['pnl_dollar'] < 0:
            pnl_dollar_str = f"🔴 ${trade['pnl_dollar']:+.2f}"
            pnl_percent_str = f"🔴 {trade['pnl_percent']:+.2f}%"
        else:
            pnl_dollar_str = f"${trade['pnl_dollar']:+.2f}"
            pnl_percent_str = f"{trade['pnl_percent']:.2f}%"
        
        # SL/TP distance with warning if close
        sl_dist = trade['sl_distance']
        tp_dist = trade['tp_distance']
        
        sl_str = f"{sl_dist:.1f}%"
        if sl_dist > 0 and sl_dist < 2:
            sl_str = f"⚠️{sl_dist:.1f}%"
        
        tp_str = f"{tp_dist:.1f}%"
        if tp_dist > 0 and tp_dist < 2:
            tp_str = f"🎯{tp_dist:.1f}%"
        
        table.append([
            str(i),
            trade['symbol'],
            trade['exchange'],
            trade['type'],
            entry_str,
            current_str,
            f"{trade['quantity']:.4f}" if trade['quantity'] else "N/A",
            f"${trade['position_size']:.0f}" if trade['position_size'] else "N/A",
            f"{trade['days_held']:.1f}d",
            pnl_dollar_str,
            pnl_percent_str,
            sl_str,
            tp_str,
            f"${trade['capital_risk']:.0f}" if trade['capital_risk'] else "N/A",
            f"{trade['leverage']}x" if trade['leverage'] > 1 else "1x",
            trade['status']
        ])
    
    # Create markdown table
    col_widths = [max(len(str(row[i])) for row in [headers] + table) for i in range(len(headers))]
    
    # Header
    header_row = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    separator = "|-" + "-|-".join("-" * w for w in col_widths) + "-|"
    
    # Rows
    rows = []
    for row in table:
        rows.append("| " + " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) + " |")
    
    return "\n".join([header_row, separator] + rows)

def generate_summary(trades_data, capital_data):
    """Generate summary statistics"""
    total_trades = len(trades_data)
    winning_trades = sum(1 for t in trades_data if t['pnl_dollar'] > 0)
    losing_trades = sum(1 for t in trades_data if t['pnl_dollar'] < 0)
    total_pnl = sum(t['pnl_dollar'] for t in trades_data)
    
    # Group by exchange and type
    gemini_trades = [t for t in trades_data if t['exchange'] == 'GEMINI']
    binance_trades = [t for t in trades_data if t['exchange'] == 'BINANCE']
    
    gemini_pnl = sum(t['pnl_dollar'] for t in gemini_trades)
    binance_pnl = sum(t['pnl_dollar'] for t in binance_trades)
    
    # Risk exposure
    total_risk = sum(t['capital_risk'] for t in trades_data if t['capital_risk'])
    
    summary = f"""
## 📊 TRADING SUMMARY

### Position Overview
- **Total Positions:** {total_trades}
- **Winning:** {winning_trades} 🟢
- **Losing:** {losing_trades} 🔴
- **Win Rate:** {(winning_trades/total_trades*100):.1f}% (if {total_trades} > 0 else 0%)

### Performance by Exchange
- **Gemini (LONG):** {len(gemini_trades)} positions | P&L: ${gemini_pnl:+.2f}
- **Binance (SHORT):** {len(binance_trades)} positions | P&L: ${binance_pnl:+.2f}

### Risk Metrics
- **Total Capital at Risk:** ${total_risk:.2f}
- **Total P&L:** ${total_pnl:+.2f}
"""
    
    if capital_data:
        current_capital = capital_data.get('current', 0)
        initial_capital = capital_data.get('initial', 0)
        pnl_percent = capital_data.get('pnl_percent', 0)
        
        summary += f"""
### Capital Status
- **Initial Capital:** ${initial_capital:.2f}
- **Current Capital:** ${current_capital:.2f}
- **Cumulative P&L:** {pnl_percent:+.2f}%
- **Recovery Needed:** +{capital_data.get('recovery_percent_needed', 0):.1f}%
"""
    
    return summary

def main():
    print("📊 GENERATING ENHANCED DASHBOARD TABLE")
    print("=" * 100)
    
    # Load all data
    data = load_all_data()
    
    # Process all trades
    all_trades = []
    
    # Process Gemini trades
    for trade in data['gemini_trades']:
        trade['exchange'] = 'Gemini'
        metrics = calculate_metrics(trade, data)
        all_trades.append(metrics)
    
    # Process Binance trades
    for trade in data['binance_trades']:
        metrics = calculate_metrics(trade, data)
        all_trades.append(metrics)
    
    # Sort by time (newest first)
    all_trades.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Generate enhanced table
    table = generate_enhanced_table(all_trades)
    
    # Generate summary
    summary = generate_summary(all_trades, data.get('capital', {}))
    
    # Print everything
    print(summary)
    print("\n## 📋 ENHANCED ORDER TABLE")
    print(table)
    
    # Save to file
    with open('enhanced_dashboard.md', 'w') as f:
        f.write("# 📊 ENHANCED TRADING DASHBOARD\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(summary)
        f.write("\n## 📋 ENHANCED ORDER TABLE\n")
        f.write(table)
    
    print(f"\n✅ Enhanced dashboard saved to: enhanced_dashboard.md")
    
    # Also create a compact version for terminal display
    print("\n" + "=" * 100)
    print("📱 COMPACT VIEW (Terminal Friendly):")
    print("-" * 100)
    
    compact_headers = ["#", "Symbol", "Type", "Entry", "Current", "P&L $", "Days", "Status"]
    for trade in all_trades:
        pnl_color = "🟢" if trade['pnl_dollar'] > 0 else "🔴" if trade['pnl_dollar'] < 0 else ""
        print(f"{trade['symbol']:8} {trade['type']:6} ${trade['entry_price']:8.2f} → ${trade['current_price']:8.2f} {pnl_color}${trade['pnl_dollar']:+.2f} ({trade['pnl_percent']:+.2f}%) {trade['days_held']:.1f}d {trade['status']}")

if __name__ == "__main__":
    main()