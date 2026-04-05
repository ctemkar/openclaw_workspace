#!/usr/bin/env python3
"""
Display CUMULATIVE P&L - Shows true historical performance that never resets
"""

import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def display_cumulative_pnl():
    """Display cumulative P&L in a clear format"""
    
    print("=" * 80)
    print("📊 CUMULATIVE P&L TRACKER - HISTORICAL PERFORMANCE (NEVER RESETS)")
    print("=" * 80)
    
    # Load cumulative tracker
    tracker_path = os.path.join(BASE_DIR, 'cumulative_pnl_tracker.json')
    if not os.path.exists(tracker_path):
        print("❌ Cumulative P&L tracker not found. Run calculate_cumulative_pnl.py first.")
        return
    
    with open(tracker_path, 'r') as f:
        tracker = json.load(f)
    
    summary = tracker['performance_summary']
    
    print(f"\n💰 CAPITAL OVERVIEW:")
    print(f"   Initial Capital:      ${summary['total_initial_capital']:.2f}")
    print(f"   Current Portfolio:    ${summary['total_current_value']:.2f}")
    print(f"   Cumulative P&L:       ${summary['total_cumulative_pnl']:+.2f}")
    print(f"   Cumulative P&L %:     {summary['total_cumulative_pnl_percent']:+.2f}%")
    print(f"   Total Fees Paid:      ${summary['total_fees_paid']:.2f}")
    
    print(f"\n🎯 RECOVERY TARGET:")
    recovery_needed = summary['total_initial_capital'] - summary['total_current_value']
    recovery_percent = (recovery_needed / summary['total_current_value']) * 100
    print(f"   Need to earn:         ${recovery_needed:+.2f}")
    print(f"   Required return:      {recovery_percent:+.2f}% from current")
    
    print(f"\n📈 CURRENT PERFORMANCE:")
    print(f"   Total Trades:         {summary['total_trades']}")
    print(f"   Winning Trades:       {summary['winning_trades']}")
    print(f"   Losing Trades:        {summary['losing_trades']}")
    print(f"   Win Rate:             {summary['win_rate']:.1f}%")
    print(f"   Current Unrealized:   ${summary['total_unrealized_pnl']:+.2f}")
    
    print(f"\n📊 OPEN POSITIONS:")
    if tracker.get('unrealized_positions'):
        for i, pos in enumerate(tracker['unrealized_positions'], 1):
            side_emoji = "📈" if pos['side'].lower() == 'buy' else "📉"
            pnl_emoji = "✅" if pos.get('unrealized_pnl', 0) > 0 else "❌"
            print(f"   {i}. {side_emoji} {pos['symbol']} {pos['side'].upper()}")
            print(f"      Entry: ${pos['entry_price']:.2f}, Current: ${pos.get('current_price', pos['entry_price']):.2f}")
            print(f"      P&L: {pnl_emoji} ${pos.get('unrealized_pnl', 0):+.2f} ({pos.get('unrealized_pnl_percent', 0):+.2f}%)")
    else:
        print("   No open positions")
    
    print(f"\n📅 LAST UPDATED: {tracker['metadata']['last_updated']}")
    print("=" * 80)
    
    # Critical warning if cumulative loss is significant
    if summary['total_cumulative_pnl'] < -100:
        print("\n⚠️  CRITICAL: Significant cumulative losses.")
        print("   These losses DO NOT disappear when positions close.")
        print("   Focus on consistent profitability to recover.")
        print("=" * 80)

if __name__ == "__main__":
    display_cumulative_pnl()