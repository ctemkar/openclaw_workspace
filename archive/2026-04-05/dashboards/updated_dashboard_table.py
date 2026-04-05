#!/usr/bin/env python3
"""
UPDATED Dashboard Table with ALL requested columns:
1. Buy price (Entry price)
2. Exchange (Binance or Gemini)
3. Position type (short or long)
4. Time of transaction
5. P&L for that transaction
6. PLUS: Current price, Quantity, Position value, Days held, Stop loss, Take profit, Leverage, Capital at risk
"""

import json
from datetime import datetime
import os

def load_real_data():
    """Load real trading data from all sources"""
    data = {
        'gemini_trades': [],
        'binance_trades': [],
        'current_prices': {},
        'all_trades': []
    }
    
    # Load Gemini trades (from daily_trades.json - includes BTC sale)
    try:
        with open('daily_trades.json', 'r') as f:
            gemini_data = json.load(f)
            data['gemini_trades'] = gemini_data.get('trades', [])
    except FileNotFoundError:
        print("Warning: daily_trades.json not found")
    
    # Load REAL Binance positions (from 26_crypto_trade_history.json - updated)
    try:
        with open('26_crypto_trade_history.json', 'r') as f:
            binance_data = json.load(f)
            data['binance_trades'] = binance_data
    except FileNotFoundError:
        print("Warning: 26_crypto_trade_history.json not found")
    
    # Load system status for capital info
    try:
        with open('system_status.json', 'r') as f:
            system_data = json.load(f)
            data['capital'] = system_data.get('capital', {})
            data['positions'] = system_data.get('positions', {})
    except FileNotFoundError:
        print("Warning: system_status.json not found")
    
    return data

def process_trades(data):
    """Process all trades into unified format"""
    all_trades = []
    
    # Process Gemini trades
    for trade in data['gemini_trades']:
        # Determine if it's a buy or sell
        if trade['side'] == 'buy':
            position_type = 'LONG'
            pnl_dollar = trade.get('pnl', 0)
            pnl_percent = trade.get('pnl_percent', 0)
        else:  # sell
            position_type = 'SELL'
            pnl_dollar = 0  # Sale P&L already accounted in buy trades
            pnl_percent = 0
        
        # Calculate days held
        days_held = 0
        if 'timestamp' in trade:
            try:
                entry_time = datetime.fromisoformat(trade['timestamp'].replace('Z', '+00:00'))
                if 'close_timestamp' in trade:
                    close_time = datetime.fromisoformat(trade['close_timestamp'].replace('Z', '+00:00'))
                    days_held = (close_time - entry_time).total_seconds() / (24 * 3600)
                else:
                    days_held = (datetime.now() - entry_time).total_seconds() / (24 * 3600)
            except:
                pass
        
        all_trades.append({
            'symbol': trade['symbol'],
            'exchange': 'GEMINI',
            'type': position_type,
            'entry_price': trade['price'],
            'current_price': trade.get('close_price', trade.get('price', 0)),
            'quantity': trade['amount'],
            'position_value': trade['value'],
            'timestamp': trade['timestamp'],
            'pnl_dollar': pnl_dollar,
            'pnl_percent': pnl_percent,
            'days_held': days_held,
            'stop_loss': trade.get('stop_loss', 0),
            'take_profit': trade.get('take_profit', 0),
            'capital_risk': trade.get('value', 0),
            'leverage': 1,
            'status': trade['status'],
            'notes': trade.get('notes', '')
        })
    
    # Process REAL Binance positions (from updated file)
    for trade in data['binance_trades']:
        # These are the ACTUAL losing short positions
        position_type = trade['type']
        pnl_dollar = trade.get('unrealized_pnl', 0)
        pnl_percent = trade.get('pnl_percent', 0)
        
        # Calculate days held
        days_held = 0
        if 'execution_time' in trade:
            try:
                entry_time = datetime.fromisoformat(trade['execution_time'].replace('Z', '+00:00'))
                days_held = (datetime.now() - entry_time).total_seconds() / (24 * 3600)
            except:
                pass
        
        # Calculate position value (absolute value)
        position_size = abs(trade.get('position_size', 30))
        
        all_trades.append({
            'symbol': trade['symbol'],
            'exchange': 'BINANCE',
            'type': position_type,
            'entry_price': trade.get('entry_price', trade.get('current_price', 0)),
            'current_price': trade.get('current_price', trade.get('mark_price', 0)),
            'quantity': abs(trade.get('position_size', 30) / trade.get('entry_price', 1)),
            'position_value': position_size,
            'timestamp': trade.get('execution_time', ''),
            'pnl_dollar': pnl_dollar,
            'pnl_percent': pnl_percent,
            'days_held': days_held,
            'stop_loss': trade.get('stop_loss', 0),
            'take_profit': trade.get('take_profit', 0),
            'capital_risk': position_size / 3,  # With 3x leverage, risk is 1/3 of position
            'leverage': 3,
            'status': trade['status'],
            'notes': trade.get('notes', 'ACTUAL POSITION - REAL DATA')
        })
    
    return all_trades

def generate_comprehensive_table(trades):
    """Generate comprehensive table with ALL columns"""
    if not trades:
        return "No trades found."
    
    # Define ALL columns we discussed
    headers = [
        "#", "Symbol", "Exchange", "Type", "Entry Price", "Current Price",
        "Qty", "Position Value", "Days Held", "P&L $", "P&L %", 
        "Stop Loss", "Take Profit", "Capital Risk", "Leverage", "Status", "Time"
    ]
    
    table = []
    
    for i, trade in enumerate(trades, 1):
        # Format prices
        entry_str = f"${trade['entry_price']:,.2f}" if trade['entry_price'] >= 1000 else f"${trade['entry_price']:.4f}"
        current_str = f"${trade['current_price']:,.2f}" if trade['current_price'] >= 1000 else f"${trade['current_price']:.4f}"
        
        # P&L with color
        if trade['pnl_dollar'] > 0:
            pnl_dollar_str = f"🟢 ${trade['pnl_dollar']:+.2f}"
            pnl_percent_str = f"🟢 {trade['pnl_percent']:+.2f}%"
        elif trade['pnl_dollar'] < 0:
            pnl_dollar_str = f"🔴 ${trade['pnl_dollar']:+.2f}"
            pnl_percent_str = f"🔴 {trade['pnl_percent']:+.2f}%"
        else:
            pnl_dollar_str = f"${trade['pnl_dollar']:.2f}"
            pnl_percent_str = f"{trade['pnl_percent']:.2f}%"
        
        # Stop loss and take profit
        sl_price = trade['stop_loss']
        tp_price = trade['take_profit']
        
        sl_str = f"${sl_price:,.2f}" if sl_price >= 1000 else f"${sl_price:.4f}" if sl_price > 0 else "N/A"
        tp_str = f"${tp_price:,.2f}" if tp_price >= 1000 else f"${tp_price:.4f}" if tp_price > 0 else "N/A"
        
        # Calculate SL/TP distances
        if sl_price > 0 and trade['entry_price'] > 0:
            if trade['type'] == 'SHORT':
                sl_distance = ((sl_price - trade['entry_price']) / trade['entry_price']) * 100
            else:
                sl_distance = ((trade['entry_price'] - sl_price) / trade['entry_price']) * 100
            sl_str += f" ({sl_distance:+.1f}%)"
        
        if tp_price > 0 and trade['entry_price'] > 0:
            if trade['type'] == 'SHORT':
                tp_distance = ((trade['entry_price'] - tp_price) / trade['entry_price']) * 100
            else:
                tp_distance = ((tp_price - trade['entry_price']) / trade['entry_price']) * 100
            tp_str += f" ({tp_distance:+.1f}%)"
        
        # Format time
        time_str = "N/A"
        if trade['timestamp']:
            try:
                dt = datetime.fromisoformat(trade['timestamp'].replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M:%S')
            except:
                time_str = str(trade['timestamp'])[:19]
        
        table.append([
            str(i),
            trade['symbol'],
            trade['exchange'],
            trade['type'],
            entry_str,
            current_str,
            f"{trade['quantity']:.6f}",
            f"${trade['position_value']:.2f}",
            f"{trade['days_held']:.2f}d",
            pnl_dollar_str,
            pnl_percent_str,
            sl_str,
            tp_str,
            f"${trade['capital_risk']:.2f}",
            f"{trade['leverage']}x",
            trade['status'],
            time_str
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

def generate_summary(trades, capital_data):
    """Generate summary statistics"""
    total_trades = len(trades)
    open_trades = [t for t in trades if t['status'] in ['OPEN', 'open', 'EXECUTED']]
    closed_trades = [t for t in trades if t['status'] in ['closed', 'filled', 'CLOSED']]
    
    winning_trades = [t for t in trades if t['pnl_dollar'] > 0]
    losing_trades = [t for t in trades if t['pnl_dollar'] < 0]
    
    total_pnl = sum(t['pnl_dollar'] for t in trades)
    open_pnl = sum(t['pnl_dollar'] for t in open_trades)
    closed_pnl = sum(t['pnl_dollar'] for t in closed_trades)
    
    # Group by exchange
    gemini_trades = [t for t in trades if t['exchange'] == 'GEMINI']
    binance_trades = [t for t in trades if t['exchange'] == 'BINANCE']
    
    gemini_pnl = sum(t['pnl_dollar'] for t in gemini_trades)
    binance_pnl = sum(t['pnl_dollar'] for t in binance_trades)
    
    summary = f"""
## 📊 COMPREHENSIVE TRADING DASHBOARD

### Position Overview
- **Total Trades:** {total_trades}
- **Open Positions:** {len(open_trades)}
- **Closed Positions:** {len(closed_trades)}
- **Winning Trades:** {len(winning_trades)} 🟢
- **Losing Trades:** {len(losing_trades)} 🔴
- **Win Rate:** {(len(winning_trades)/total_trades*100):.1f}% (if {total_trades} > 0)

### Performance Summary
- **Total P&L:** ${total_pnl:+.2f}
- **Open P&L:** ${open_pnl:+.2f}
- **Closed P&L:** ${closed_pnl:+.2f}

### Performance by Exchange
- **Gemini:** {len(gemini_trades)} trades | P&L: ${gemini_pnl:+.2f}
- **Binance:** {len(binance_trades)} trades | P&L: ${binance_pnl:+.2f}

### Risk Exposure
- **Total Capital at Risk:** ${sum(t['capital_risk'] for t in trades):.2f}
- **Total Position Value:** ${sum(t['position_value'] for t in trades):.2f}
- **Average Leverage:** {sum(t['leverage'] for t in trades)/len(trades):.1f}x
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
    
    # Add bot status
    summary += f"""
### Trading Bot Status
- **26-Crypto Bot:** UPDATED with improved parameters
- **New Threshold:** 3.0% drop (was 0.3%)
- **New Leverage:** 1x (was 3x)
- **Position Size:** 10% of capital (was 25%)
- **Max Positions:** 3 (was unlimited)
"""
    
    return summary

def main():
    print("📊 GENERATING UPDATED COMPREHENSIVE DASHBOARD")
    print("=" * 100)
    
    # Load real data
    data = load_real_data()
    
    # Process all trades
    all_trades = process_trades(data)
    
    # Sort by time (newest first)
    all_trades.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Generate comprehensive table
    table = generate_comprehensive_table(all_trades)
    
    # Generate summary
    summary = generate_summary(all_trades, data.get('capital', {}))
    
    # Print everything
    print(summary)
    print("\n## 📋 COMPREHENSIVE ORDER TABLE (ALL COLUMNS)")
    print(table)
    
    # Save to file
    with open('comprehensive_dashboard.md', 'w') as f:
        f.write("# 📊 COMPREHENSIVE TRADING DASHBOARD\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("**Includes ALL requested columns:**\n")
        f.write("1. Buy/Entry price\n")
        f.write("2. Exchange (Binance/Gemini)\n")
        f.write("3. Position type (short/long)\n")
        f.write("4. Time of transaction\n")
        f.write("5. P&L for that transaction\n")
        f.write("6. Current price, Quantity, Position value\n")
        f.write("7. Days held, Stop loss, Take profit\n")
        f.write("8. Capital at risk, Leverage\n\n")
        f.write(summary)
        f.write("\n## 📋 COMPREHENSIVE ORDER TABLE\n")
        f.write(table)
    
    print(f"\n✅ Comprehensive dashboard saved to: comprehensive_dashboard.md")
    
    # Also create a simplified version
    print("\n" + "=" * 100)
    print("📱 SIMPLIFIED VIEW (Key Info):")
    print("-" * 100)
    
    for trade in all_trades:
        if trade['status'] in ['OPEN', 'open', 'EXECUTED']:
            pnl_color = "🟢" if trade['pnl_dollar'] > 0 else "🔴" if trade['pnl_dollar'] < 0 else "⚪"
            print(f"{trade['symbol']:10} {trade['exchange']:8} {trade['type']:6} {pnl_color} ${trade['pnl_dollar']:+.2f} ({trade['pnl_percent']:+.2f}%) | Entry: ${trade['entry_price']:.4f} | Current: ${trade['current_price']:.4f} | Days: {trade['days_held']:.1f}")

if __name__ == "__main__":
    main()