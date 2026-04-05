#!/usr/bin/env python3
"""
Dashboard Table Generator
Creates a table showing all orders with:
1. Buy price
2. Exchange (Binance or Gemini)
3. Position type (short or long)
4. Time of transaction
5. P&L for that transaction
"""

import json
from datetime import datetime
import os

def load_gemini_trades():
    """Load Gemini trades from daily_trades.json"""
    try:
        with open('daily_trades.json', 'r') as f:
            data = json.load(f)
        return data.get('trades', [])
    except FileNotFoundError:
        print("Warning: daily_trades.json not found")
        return []

def load_binance_trades():
    """Load Binance trades from 26_crypto_trade_history.json"""
    try:
        with open('26_crypto_trade_history.json', 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("Warning: 26_crypto_trade_history.json not found")
        return []

def load_current_prices():
    """Extract current prices from positions report"""
    prices = {}
    try:
        with open('current_positions_report.txt', 'r') as f:
            content = f.read()
        
        # Parse current prices from report
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Current:' in line and '$' in line:
                # Find the symbol from previous lines
                for j in range(max(0, i-3), i):
                    if any(symbol in lines[j] for symbol in ['BTC/USD', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'DOT/USDT']):
                        symbol_line = lines[j]
                        if 'BTC/USD' in symbol_line:
                            symbol = 'BTC/USD'
                        elif 'ETH/USDT' in symbol_line:
                            symbol = 'ETH/USDT'
                        elif 'SOL/USDT' in symbol_line:
                            symbol = 'SOL/USDT'
                        elif 'XRP/USDT' in symbol_line:
                            symbol = 'XRP/USDT'
                        elif 'ADA/USDT' in symbol_line:
                            symbol = 'ADA/USDT'
                        elif 'DOT/USDT' in symbol_line:
                            symbol = 'DOT/USDT'
                        else:
                            continue
                        
                        # Extract price
                        price_str = line.split('$')[1].strip()
                        try:
                            prices[symbol] = float(price_str.replace(',', ''))
                        except:
                            pass
    except FileNotFoundError:
        print("Warning: current_positions_report.txt not found")
    
    return prices

def calculate_pnl(trade, current_prices):
    """Calculate P&L for a trade"""
    symbol = trade.get('symbol', '')
    entry_price = trade.get('price', trade.get('current_price', 0))
    position_type = trade.get('type', 'LONG' if trade.get('side') == 'buy' else 'SHORT')
    
    if symbol not in current_prices:
        return 0.0
    
    current_price = current_prices[symbol]
    
    if position_type == 'LONG':
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
    else:  # SHORT
        pnl_percent = ((entry_price - current_price) / entry_price) * 100
    
    # Calculate dollar value if we have amount
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
    
    return round(pnl_dollar, 2), round(pnl_percent, 2)

def format_table(trades):
    """Format trades into a markdown table"""
    if not trades:
        return "No trades found."
    
    headers = ["#", "Symbol", "Exchange", "Type", "Entry Price", "Time", "P&L ($)", "P&L (%)", "Status"]
    table = []
    
    for i, trade in enumerate(trades, 1):
        symbol = trade.get('symbol', 'N/A')
        exchange = trade.get('exchange', 'Gemini').upper()
        position_type = trade.get('type', 'LONG' if trade.get('side') == 'buy' else 'SHORT')
        entry_price = trade.get('price', trade.get('current_price', 0))
        time = trade.get('timestamp', trade.get('execution_time', 'N/A'))
        pnl_dollar = trade.get('pnl_dollar', 0)
        pnl_percent = trade.get('pnl_percent', 0)
        status = trade.get('status', 'OPEN')
        
        # Format time
        if time != 'N/A':
            try:
                dt = datetime.fromisoformat(time.replace('Z', '+00:00'))
                time = dt.strftime('%H:%M:%S')
            except:
                pass
        
        # Format P&L with color
        pnl_dollar_str = f"${pnl_dollar:+.2f}"
        pnl_percent_str = f"{pnl_percent:+.2f}%"
        
        if pnl_dollar > 0:
            pnl_dollar_str = f"🟢 {pnl_dollar_str}"
            pnl_percent_str = f"🟢 {pnl_percent_str}"
        elif pnl_dollar < 0:
            pnl_dollar_str = f"🔴 {pnl_dollar_str}"
            pnl_percent_str = f"🔴 {pnl_percent_str}"
        
        table.append([
            str(i),
            symbol,
            exchange,
            position_type,
            f"${entry_price:,.2f}" if entry_price else "N/A",
            time,
            pnl_dollar_str,
            pnl_percent_str,
            status
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

def main():
    print("📊 GENERATING DASHBOARD ORDER TABLE")
    print("=" * 80)
    
    # Load data
    gemini_trades = load_gemini_trades()
    binance_trades = load_binance_trades()
    current_prices = load_current_prices()
    
    # Combine and process trades
    all_trades = []
    
    # Process Gemini trades (LONG positions)
    for trade in gemini_trades:
        pnl_dollar, pnl_percent = calculate_pnl(trade, current_prices)
        all_trades.append({
            'symbol': trade['symbol'],
            'exchange': 'Gemini',
            'type': 'LONG',
            'price': trade['price'],
            'timestamp': trade['timestamp'],
            'pnl_dollar': pnl_dollar,
            'pnl_percent': pnl_percent,
            'status': trade['status'],
            'side': trade['side'],
            'amount': trade['amount']
        })
    
    # Process Binance trades (SHORT positions)
    for trade in binance_trades:
        pnl_dollar, pnl_percent = calculate_pnl(trade, current_prices)
        all_trades.append({
            'symbol': trade['symbol'],
            'exchange': 'Binance',
            'type': trade['type'],
            'price': trade['entry_price'],
            'timestamp': trade['execution_time'],
            'pnl_dollar': trade.get('unrealized_pnl', 0),
            'pnl_percent': trade.get('pnl_percent', 0),
            'status': trade['status'],
            'side': trade['side'],
            'amount': trade.get('position_size', 0)
        })
    
    # Sort by time (newest first)
    all_trades.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Generate table
    table = format_table(all_trades)
    
    # Print summary
    print(f"\n📈 TRADE SUMMARY")
    print(f"Total Orders: {len(all_trades)}")
    print(f"Gemini (LONG): {len(gemini_trades)}")
    print(f"Binance (SHORT): {len(binance_trades)}")
    
    total_pnl = sum(t['pnl_dollar'] for t in all_trades)
    print(f"\n💰 TOTAL P&L: ${total_pnl:+.2f}")
    
    print(f"\n{table}")
    
    # Save to file
    with open('dashboard_orders_table.md', 'w') as f:
        f.write("# 📊 TRADING DASHBOARD - ORDER TABLE\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Orders:** {len(all_trades)}\n")
        f.write(f"**Total P&L:** ${total_pnl:+.2f}\n\n")
        f.write(table)
    
    print(f"\n✅ Table saved to: dashboard_orders_table.md")

if __name__ == "__main__":
    main()