#!/usr/bin/env python3
"""
FIX BINANCE ISSUES
Address geographic restrictions and optimize $70 USDT
"""

import json
import os
from datetime import datetime

print("="*70)
print("🔧 FIXING BINANCE ISSUES")
print("="*70)

def analyze_binance_situation():
    """Analyze current Binance situation and recommend solutions"""
    
    print("\n📊 CURRENT BINANCE STATUS:")
    print("  Balance: $70.15 USDT")
    print("  Open positions: 0")
    print("  Geographic restriction: Thailand blocked")
    print("  Current strategy: Gemini-only (avoiding Binance)")
    
    print("\n🚨 PROBLEMS IDENTIFIED:")
    print("1. $70 USDT sitting idle (not earning)")
    print("2. Binance API blocked in Thailand")
    print("3. Can't use futures trading without VPN")
    print("4. Money trapped on exchange")
    
    print("\n💡 POSSIBLE SOLUTIONS:")
    
    solutions = [
        {
            'name': 'VPN Solution',
            'description': 'Use VPN to access Binance from Thailand',
            'pros': ['Full Binance access', 'Can trade futures', 'Use all features'],
            'cons': ['Against Binance ToS?', 'VPN reliability', 'Account risk'],
            'priority': 'HIGH'
        },
        {
            'name': 'Withdraw to Gemini',
            'description': 'Withdraw USDT from Binance to Gemini',
            'pros': ['Consolidate funds', 'No geographic issues', 'Simpler management'],
            'cons': ['Withdrawal fees', 'Price differences', 'Transfer time'],
            'priority': 'MEDIUM'
        },
        {
            'name': 'Spot Trading Only',
            'description': 'Use Binance for spot trading (may work without VPN)',
            'pros': ['May not be blocked', 'Can use $70', 'Lower risk'],
            'cons': ['Limited to spot', 'May still be blocked', 'Less leverage'],
            'priority': 'LOW'
        },
        {
            'name': 'Keep Idle',
            'description': 'Leave $70 on Binance for future use',
            'pros': ['No action needed', 'Available if VPN solved'],
            'cons': ['Idle money', 'Inflation loss', 'Opportunity cost'],
            'priority': 'LOW'
        }
    ]
    
    return solutions

def check_withdrawal_possibility():
    """Check if we can withdraw from Binance to Gemini"""
    print("\n🔍 CHECKING WITHDRAWAL POSSIBILITY...")
    
    # Check if we have Gemini USDT address
    # This would require API access to get deposit address
    
    print("  To withdraw from Binance to Gemini:")
    print("  1. Get Gemini USDT deposit address")
    print("  2. Initiate Binance withdrawal")
    print("  3. Pay network fee (~$1-5)")
    print("  4. Wait for confirmation")
    
    # Estimated amounts
    withdrawal_fee = 3.00  # Estimated USDT withdrawal fee
    net_amount = 70.15 - withdrawal_fee
    
    print(f"\n  Estimated withdrawal:")
    print(f"    Current: $70.15 USDT")
    print(f"    Fee: ~${withdrawal_fee:.2f}")
    print(f"    Net to Gemini: ~${net_amount:.2f}")
    
    return net_amount

def create_binance_plan():
    """Create a comprehensive Binance action plan"""
    
    solutions = analyze_binance_situation()
    
    print("\n" + "="*70)
    print("🎯 RECOMMENDED BINANCE ACTION PLAN")
    print("="*70)
    
    # Recommend based on priorities
    recommended = [s for s in solutions if s['priority'] == 'HIGH'][0]
    
    print(f"\n🚀 RECOMMENDED: {recommended['name']}")
    print(f"   {recommended['description']}")
    print(f"\n   Pros:")
    for pro in recommended['pros']:
        print(f"     • {pro}")
    print(f"\n   Cons:")
    for con in recommended['cons']:
        print(f"     • {con}")
    
    # Check withdrawal option
    if recommended['name'] == 'Withdraw to Gemini':
        net_amount = check_withdrawal_possibility()
        print(f"\n   Net to Gemini: ${net_amount:.2f}")
        print(f"   Total Gemini cash would be: ${563.08 + net_amount:.2f}")
    
    print("\n" + "="*70)
    print("📋 IMMEDIATE ACTIONS:")
    print("="*70)
    
    actions = [
        "1. Decide on Binance strategy (VPN vs Withdraw)",
        "2. If VPN: Research reliable VPN for Thailand",
        "3. If Withdraw: Get Gemini USDT deposit address",
        "4. Update trading strategy based on decision",
        "5. Document decision in memory system"
    ]
    
    for action in actions:
        print(f"  {action}")
    
    print("\n💡 MY RECOMMENDATION:")
    print("  Withdraw to Gemini for now. Reasons:")
    print("  • Consolidates all funds ($633+ total)")
    print("  • No geographic restrictions")
    print("  • Simpler single-exchange strategy")
    print("  • Can revisit Binance later with VPN")
    print("="*70)
    
    # Create action plan file
    action_plan = {
        'timestamp': datetime.now().isoformat(),
        'binance_balance': 70.15,
        'gemini_cash': 563.08,
        'recommended_solution': recommended['name'],
        'withdrawal_estimate': check_withdrawal_possibility() if recommended['name'] == 'Withdraw to Gemini' else None,
        'actions': actions,
        'note': 'Binance geographic restrictions in Thailand. $70 USDT currently idle.'
    }
    
    plan_file = 'trading_data/binance_action_plan.json'
    with open(plan_file, 'w') as f:
        json.dump(action_plan, f, indent=2)
    
    print(f"\n📄 Action plan saved to: {plan_file}")
    
    # Update memory system
    update_memory_system(action_plan)

def update_memory_system(plan):
    """Update memory system with Binance plan"""
    memory_file = 'trading_data/memory.json'
    
    if os.path.exists(memory_file):
        with open(memory_file, 'r') as f:
            memories = json.load(f)
    else:
        memories = []
    
    # Add Binance issue memory
    binance_memory = {
        'id': f'binance_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'timestamp': datetime.now().isoformat(),
        'category': 'issues_fixed',
        'title': 'Binance Geographic Restrictions & $70 Idle USDT',
        'content': f'''BINANCE ISSUE: API blocked in Thailand, $70.15 USDT idle.

CURRENT STATUS:
- Balance: $70.15 USDT
- Positions: 0 (cleaned up earlier)
- Issue: Geographic restrictions prevent trading

RECOMMENDED SOLUTION: {plan['recommended_solution']}
- Withdraw to Gemini for consolidation
- Or use VPN to access Binance

ACTION PLAN: {plan['actions'][0]}''',
        'tags': ['binance', 'geographic_restrictions', 'thailand', 'idle_funds'],
        'priority': 'high',
        'accessed': 0
    }
    
    memories.append(binance_memory)
    
    with open(memory_file, 'w') as f:
        json.dump(memories, f, indent=2)
    
    print(f"✅ Added Binance issue to memory system")

def main():
    create_binance_plan()
    
    print("\n" + "="*70)
    print("🎯 NEXT STEPS FOR YOU:")
    print("="*70)
    print("1. Review the Binance action plan")
    print("2. Decide: VPN or Withdraw?")
    print("3. If withdraw: Get Gemini USDT deposit address")
    print("4. If VPN: Research Thailand-compatible VPN")
    print("5. Execute chosen solution")
    print("="*70)
    
    print("\n💡 REMINDER:")
    print(f"Current Gemini cash: $563.08")
    print(f"Current Binance USDT: $70.15")
    print(f"Total potential: $633.23 (if consolidated)")
    print("="*70)

if __name__ == "__main__":
    main()