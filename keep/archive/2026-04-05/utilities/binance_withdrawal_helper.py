#!/usr/bin/env python3
"""
BINANCE WITHDRAWAL HELPER
Guide for withdrawing USDT from Binance to Gemini
"""

import json
import os
from datetime import datetime

print("="*70)
print("💰 BINANCE TO GEMINI WITHDRAWAL HELPER")
print("="*70)

def create_withdrawal_guide():
    """Create step-by-step withdrawal guide"""
    
    print("\n📋 PREREQUISITES:")
    print("  1. Gemini account with USDT trading enabled")
    print("  2. Binance account with verified withdrawal")
    print("  3. Both accounts should be under same name/KYC")
    print("  4. Note: Cross-exchange transfers are YOUR responsibility")
    
    print("\n🔧 STEP 1: GET GEMINI USDT DEPOSIT ADDRESS")
    print("  Manual steps:")
    print("  1. Log into Gemini website/app")
    print("  2. Go to USDT wallet")
    print("  3. Click 'Deposit'")
    print("  4. Select USDT (ERC-20 or preferred network)")
    print("  5. Copy the deposit address and memo (if required)")
    
    print("\n🔧 STEP 2: INITIATE BINANCE WITHDRAWAL")
    print("  Manual steps:")
    print("  1. Log into Binance website/app")
    print("  2. Go to USDT wallet")
    print("  3. Click 'Withdraw'")
    print("  4. Select USDT")
    print("  5. Paste Gemini deposit address")
    print("  6. Enter memo (if Gemini requires)")
    print("  7. Enter amount: $67.15 (leaving $3 for fee)")
    print("  8. Confirm network matches (ERC-20 usually)")
    print("  9. Complete 2FA/verification")
    
    print("\n⚠️  IMPORTANT WARNINGS:")
    print("  • DOUBLE CHECK addresses - crypto transfers are irreversible")
    print("  • Use correct network (ERC-20 recommended)")
    print("  • Include memo if Gemini requires it")
    print("  • Start with small test amount first ($1)")
    print("  • Wait for confirmation before sending full amount")
    
    print("\n💰 ESTIMATED AMOUNTS:")
    print(f"  Binance balance: $70.15 USDT")
    print(f"  Withdrawal fee: ~$3.00 (Binance charges)")
    print(f"  Network fee: ~$1-5 (varies)")
    print(f"  Total fees: ~$4-8")
    print(f"  Net to Gemini: ~$62-66 USDT")
    print(f"  Gemini would have: ~${563.08 + 62:.2f}-${563.08 + 66:.2f} total")
    
    print("\n⏱️  TIMELINE:")
    print("  • Test transfer: 10-30 minutes")
    print("  • Full transfer: 10-60 minutes")
    print("  • Gemini processing: 1-3 confirmations")
    
    print("\n📊 ALTERNATIVE: KEEP ON BINANCE")
    print("  If you want to keep funds on Binance for future:")
    print("  • Research VPN solutions for Thailand")
    print("  • Consider spot trading (may work without VPN)")
    print("  • Wait for regulatory changes")
    
    # Create guide file
    guide = {
        'timestamp': datetime.now().isoformat(),
        'binance_balance': 70.15,
        'gemini_cash': 563.08,
        'steps': {
            'step1': 'Get Gemini USDT deposit address',
            'step2': 'Initiate Binance withdrawal',
            'step3': 'Verify test transfer',
            'step4': 'Send full amount'
        },
        'estimated_fees': {
            'withdrawal_fee': 3.00,
            'network_fee_low': 1.00,
            'network_fee_high': 5.00,
            'total_fees_low': 4.00,
            'total_fees_high': 8.00
        },
        'estimated_net': {
            'low': 62.15,
            'high': 66.15
        },
        'warnings': [
            'Double check addresses',
            'Use correct network',
            'Include memo if required',
            'Test with small amount first'
        ]
    }
    
    guide_file = 'trading_data/binance_withdrawal_guide.json'
    with open(guide_file, 'w') as f:
        json.dump(guide, f, indent=2)
    
    print(f"\n📄 Withdrawal guide saved to: {guide_file}")

def check_gemini_usdt_support():
    """Check if Gemini supports USDT and get details"""
    print("\n🔍 GEMINI USDT SUPPORT CHECK:")
    print("  Gemini typically supports:")
    print("  • USDT on Ethereum (ERC-20)")
    print("  • May require memo/tag for exchange deposits")
    print("  • Trading pairs: USDT/USD, USDT/BTC, etc.")
    
    print("\n💡 RECOMMENDATION:")
    print("  After withdrawal to Gemini:")
    print("  1. Trade USDT to USD (if needed)")
    print("  2. Use USD for Gemini-only trading bot")
    print("  3. Or keep USDT for potential future use")
    
    print("\n📈 POST-WITHDRAWAL STRATEGY:")
    print(f"  Current Gemini cash: $563.08")
    print(f"  After withdrawal: ~$625-629 total")
    print(f"  Trading bot capital: Increases by ~11%")
    print(f"  Position sizes: Can increase proportionally")

def main():
    create_withdrawal_guide()
    check_gemini_usdt_support()
    
    print("\n" + "="*70)
    print("🎯 DECISION TIME:")
    print("="*70)
    print("OPTION A: WITHDRAW TO GEMINI")
    print("  Pros: Consolidation, no restrictions, simpler")
    print("  Cons: Fees (~$4-8), irreversible, manual process")
    
    print("\nOPTION B: VPN SOLUTION")
    print("  Pros: Keep Binance access, futures trading")
    print("  Cons: Against ToS?, VPN reliability, complexity")
    
    print("\nOPTION C: LEAVE IDLE")
    print("  Pros: No action needed")
    print("  Cons: $70 not earning, inflation, opportunity cost")
    
    print("\n" + "="*70)
    print("💡 MY RECOMMENDATION:")
    print("  Withdraw $67 to Gemini, keep $3 on Binance")
    print("  Reasons:")
    print("  1. Consolidates 95% of funds")
    print("  2. Eliminates geographic restrictions")
    print("  3. Simpler single-exchange management")
    print("  4. Can still revisit Binance later with $3")
    print("="*70)
    
    print("\n📋 READY WHEN YOU ARE:")
    print("  1. Tell me your decision (Withdraw/VPN/Idle)")
    print("  2. If withdraw: I'll help with any questions")
    print("  3. If VPN: I'll research Thailand VPN options")
    print("  4. Either way: Update trading strategy accordingly")
    print("="*70)

if __name__ == "__main__":
    main()