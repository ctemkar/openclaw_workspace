#!/usr/bin/env python3
import json
from datetime import datetime

def analyze_positions():
    """Analyze existing positions from completed_trades.json"""
    try:
        with open('completed_trades.json', 'r') as f:
            trades = json.load(f)
    except FileNotFoundError:
        print("No completed trades found")
        return
    
    print("EXISTING POSITIONS ANALYSIS")
    print("=" * 50)
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Current BTC price (from previous analysis)
    current_btc_price = 73811.00
    
    btc_positions = []
    total_btc = 0
    total_cost = 0
    
    for trade in trades:
        if trade["side"] == "buy":
            amount = trade["amount"]
            price = trade["price"]
            cost = amount * price
            
            btc_positions.append({
                "amount": amount,
                "entry_price": price,
                "cost": cost
            })
            
            total_btc += amount
            total_cost += cost
    
    if not btc_positions:
        print("No existing buy positions found")
        return
    
    print(f"EXISTING BTC POSITIONS: {len(btc_positions)}")
    print("-" * 40)
    
    for i, pos in enumerate(btc_positions, 1):
        current_value = pos["amount"] * current_btc_price
        pnl = current_value - pos["cost"]
        pnl_percent = (pnl / pos["cost"]) * 100
        
        print(f"Position {i}:")
        print(f"  Amount: {pos['amount']:.8f} BTC")
        print(f"  Entry Price: ${pos['entry_price']:,.2f}")
        print(f"  Cost: ${pos['cost']:,.2f}")
        print(f"  Current Value: ${current_value:,.2f}")
        print(f"  P&L: ${pnl:,.2f} ({pnl_percent:+.2f}%)")
        print()
    
    avg_entry = total_cost / total_btc if total_btc > 0 else 0
    total_current_value = total_btc * current_btc_price
    total_pnl = total_current_value - total_cost
    total_pnl_percent = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
    
    print("TOTAL POSITION SUMMARY:")
    print(f"Total BTC: {total_btc:.8f}")
    print(f"Average Entry: ${avg_entry:,.2f}")
    print(f"Total Cost: ${total_cost:,.2f}")
    print(f"Current Value: ${total_current_value:,.2f}")
    print(f"Total P&L: ${total_pnl:,.2f} ({total_pnl_percent:+.2f}%)")
    print()
    
    # Risk analysis
    print("RISK ANALYSIS:")
    print(f"Current BTC Price: ${current_btc_price:,.2f}")
    
    stop_loss_price = avg_entry * 0.95  # 5% stop-loss
    take_profit_price = avg_entry * 1.10  # 10% take-profit
    
    print(f"5% Stop-Loss Level: ${stop_loss_price:,.2f}")
    print(f"10% Take-Profit Level: ${take_profit_price:,.2f}")
    
    distance_to_stop = ((current_btc_price - stop_loss_price) / current_btc_price) * 100
    distance_to_take = ((take_profit_price - current_btc_price) / current_btc_price) * 100
    
    print(f"Distance to Stop-Loss: {distance_to_stop:.1f}%")
    print(f"Distance to Take-Profit: {distance_to_take:.1f}%")
    print()
    
    # Recommendations
    print("RECOMMENDATIONS:")
    if current_btc_price < avg_entry:
        if current_btc_price <= stop_loss_price:
            print("⚠️ CRITICAL: STOP-LOSS TRIGGERED!")
            print("  Immediate sell recommended to limit losses")
        else:
            print("⚠️ WARNING: Position is at a loss")
            print(f"  Current loss: {abs(total_pnl_percent):.2f}%")
            print(f"  Stop-loss will trigger at: {abs(total_pnl_percent - 5):.2f}% further decline")
            print("  Monitor closely, consider selling if trend continues")
    elif current_btc_price > avg_entry:
        if current_btc_price >= take_profit_price:
            print("✅ TAKE-PROFIT TRIGGERED!")
            print("  Sell recommended to lock in profits")
        else:
            print("✅ Position is profitable")
            print(f"  Current profit: {total_pnl_percent:.2f}%")
            print("  Hold until take-profit or stop-loss triggers")
    else:
        print("➖ Position is at break-even")
        print("  Monitor market conditions")
    
    print()
    print("CONSERVATIVE STRATEGY GUIDANCE:")
    print("• Maximum 2 trades per day already executed")
    print("• Focus on managing existing positions")
    print("• No new trades recommended unless high confidence (>60%)")
    print("• Prioritize risk management over new entries")

if __name__ == "__main__":
    analyze_positions()