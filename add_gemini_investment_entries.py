#!/usr/bin/env python3
"""
ADD GEMINI INVESTMENT ENTRIES
Add Gemini investment summary and cash to match Binance structure
"""

import json
from datetime import datetime

print("="*70)
print("💰 ADDING GEMINI INVESTMENT ENTRIES")
print("="*70)

def main():
    # Load current trades
    with open('trading_data/trades.json', 'r') as f:
        trades = json.load(f)
    
    print(f"Current trades: {len(trades)} entries")
    
    # Find total investment summary
    total_summary = None
    for trade in trades:
        if trade.get('symbol') == 'INVESTMENT/SUMMARY':
            total_summary = trade
            break
    
    if not total_summary:
        print("❌ ERROR: No total investment summary found!")
        return
    
    total_investment = total_summary.get('value', 946.97)
    total_current = total_summary.get('value', 946.97) + total_summary.get('pnl', 0)
    total_pnl = total_summary.get('pnl', -373.94)
    total_pnl_percent = total_summary.get('pnl_percent', -39.49)
    
    print(f"📊 TOTAL INVESTMENT:")
    print(f"  Investment: ${total_investment:.2f}")
    print(f"  Current: ${total_current:.2f}")
    print(f"  P&L: ${total_pnl:+.2f} ({total_pnl_percent:+.1f}%)")
    
    # Find Binance investment summary
    binance_summary = None
    for trade in trades:
        if trade.get('symbol') == 'BINANCE/INVESTMENT':
            binance_summary = trade
            break
    
    if not binance_summary:
        print("❌ ERROR: No Binance investment summary found!")
        return
    
    binance_investment = binance_summary.get('value', 446.97)
    binance_current = binance_summary.get('value', 446.97) + binance_summary.get('pnl', 0)
    binance_pnl = binance_summary.get('pnl', -376.82)
    binance_pnl_percent = binance_summary.get('pnl_percent', -84.3)
    
    print(f"\n📊 BINANCE INVESTMENT:")
    print(f"  Investment: ${binance_investment:.2f}")
    print(f"  Current: ${binance_current:.2f}")
    print(f"  P&L: ${binance_pnl:+.2f} ({binance_pnl_percent:+.1f}%)")
    
    # Calculate Gemini investment (total - binance)
    gemini_investment = total_investment - binance_investment
    gemini_current = total_current - binance_current
    gemini_pnl = total_pnl - binance_pnl
    gemini_pnl_percent = (gemini_pnl / gemini_investment * 100) if gemini_investment != 0 else 0
    
    print(f"\n📊 CALCULATED GEMINI INVESTMENT:")
    print(f"  Investment: ${gemini_investment:.2f}")
    print(f"  Current: ${gemini_current:.2f}")
    print(f"  P&L: ${gemini_pnl:+.2f} ({gemini_pnl_percent:+.1f}%)")
    
    # Create Gemini investment summary
    gemini_summary = {
        'exchange': 'gemini',
        'symbol': 'GEMINI/INVESTMENT',
        'side': 'summary',
        'price': 0,
        'amount': 0,
        'current_price': 0,
        'pnl': gemini_pnl,
        'pnl_percent': gemini_pnl_percent,
        'value': gemini_investment,
        'timestamp': datetime.now().isoformat(),
        'type': 'investment_summary',
        'note': f'GEMINI INVESTMENT: ${gemini_investment:.2f} estimated | CURRENT: ${gemini_current:.2f} | P&L: ${gemini_pnl:+.2f} ({gemini_pnl_percent:+.1f}%) | Active trading'
    }
    
    # Find Gemini cash (from actual positions)
    gemini_positions = [t for t in trades if t.get('exchange') == 'gemini' and t.get('type') == 'spot']
    gemini_position_value = sum(t.get('value', 0) for t in gemini_positions)
    
    # Gemini cash = Gemini current - position value
    gemini_cash_value = gemini_current - gemini_position_value
    
    gemini_cash = {
        'exchange': 'gemini',
        'symbol': 'USD/CASH',
        'side': 'cash',
        'price': 1,
        'amount': gemini_cash_value,
        'current_price': 1,
        'pnl': 0,
        'pnl_percent': 0,
        'value': gemini_cash_value,
        'timestamp': datetime.now().isoformat(),
        'type': 'cash',
        'note': f'Gemini USD cash - ${gemini_cash_value:.2f} available for trading'
    }
    
    print(f"\n💰 GEMINI CASH CALCULATION:")
    print(f"  Gemini current value: ${gemini_current:.2f}")
    print(f"  Gemini positions value: ${gemini_position_value:.2f}")
    print(f"  Gemini cash: ${gemini_cash_value:.2f}")
    
    # Rebuild trades with proper structure
    new_trades = []
    
    # 1. Total summary first
    new_trades.append(total_summary)
    
    # 2. Gemini investment summary
    new_trades.append(gemini_summary)
    
    # 3. Binance investment summary
    new_trades.append(binance_summary)
    
    # 4. Gemini positions
    for trade in trades:
        if trade.get('exchange') == 'gemini' and trade.get('type') == 'spot':
            new_trades.append(trade)
    
    # 5. Gemini cash
    new_trades.append(gemini_cash)
    
    # 6. Binance cash
    for trade in trades:
        if trade.get('symbol') == 'USDT/CASH':
            new_trades.append(trade)
    
    print(f"\n✅ NEW STRUCTURE:")
    print(f"  1. Total investment summary")
    print(f"  2. Gemini investment summary")
    print(f"  3. Binance investment summary")
    print(f"  4. Gemini positions ({len(gemini_positions)})")
    print(f"  5. Gemini cash (${gemini_cash_value:.2f})")
    print(f"  6. Binance cash ($70.15)")
    
    # Save updated trades
    with open('trading_data/trades.json', 'w') as f:
        json.dump(new_trades, f, indent=2)
    
    print(f"\n✅ Updated trades.json with {len(new_trades)} entries")
    
    # Create Gemini cash file
    gemini_cash_data = {
        'available_cash_usd': gemini_cash_value,
        'note': 'Gemini USD cash - available for trading',
        'timestamp': datetime.now().isoformat()
    }
    
    with open('trading_data/gemini_cash.json', 'w') as f:
        json.dump(gemini_cash_data, f, indent=2)
    
    print(f"📄 Gemini cash saved to: trading_data/gemini_cash.json")
    
    # Update memory
    update_memory(gemini_investment, gemini_current, gemini_pnl, gemini_cash_value)

def update_memory(investment, current, pnl, cash):
    """Update memory system"""
    memory_file = 'trading_data/memory.json'
    
    with open(memory_file, 'r') as f:
        memories = json.load(f)
    
    gemini_memory = {
        'id': f'gemini_tracking_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'timestamp': datetime.now().isoformat(),
        'category': 'system_state',
        'title': 'Gemini Investment Tracking Added',
        'content': f'''GEMINI INVESTMENT TRACKING ADDED (same as Binance):

Investment: ${investment:.2f}
Current: ${current:.2f}
P&L: ${pnl:+.2f}
Cash: ${cash:.2f}

Structure now complete:
1. Total investment summary
2. Gemini investment summary  
3. Binance investment summary
4. Gemini positions
5. Gemini cash
6. Binance cash

Total investment: $946.97 (Gemini $500 + Binance $447)''',
        'tags': ['gemini', 'investment_tracking', 'consistency', 'structure'],
        'priority': 'high',
        'accessed': 0
    }
    
    memories.append(gemini_memory)
    
    with open(memory_file, 'w') as f:
        json.dump(memories, f, indent=2)
    
    print(f"\n🧠 Added Gemini tracking to memory system")
    print(f"   Total memories: {len(memories)}")

if __name__ == "__main__":
    main()