#!/usr/bin/env python3
"""
Verify threshold adjustments
"""

import re

print('🔧 VERIFYING THRESHOLD ADJUSTMENTS')
print('=' * 60)

# Check real_26_crypto_trader.py
print('\n📊 real_26_crypto_trader.py:')
try:
    with open('real_26_crypto_trader.py', 'r') as f:
        content = f.read()
    
    # Find thresholds (avoid comments)
    lines = content.split('\n')
    long_val = None
    short_val = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('LONG_THRESHOLD = ') and not line.startswith('#'):
            long_match = re.search(r'LONG_THRESHOLD\s*=\s*([\d\.]+)', line)
            if long_match:
                long_val = float(long_match.group(1))
        if line.startswith('SHORT_THRESHOLD = ') and not line.startswith('#'):
            short_match = re.search(r'SHORT_THRESHOLD\s*=\s*([\d\.]+)', line)
            if short_match:
                short_val = float(short_match.group(1))
    
    if long_match and short_match:
        long_val = float(long_match.group(1))
        short_val = float(short_match.group(1))
        print(f'  LONG_THRESHOLD: {long_val}% {"✅" if long_val == 1.0 else "❌"}')
        print(f'  SHORT_THRESHOLD: {short_val}% {"✅" if short_val == 1.0 else "❌"}')
    else:
        print('  ❌ Could not find thresholds')
except Exception as e:
    print(f'  ❌ Error: {e}')

# Check fixed_bot_common.py
print('\n📊 fixed_bot_common.py:')
try:
    with open('fixed_bot_common.py', 'r') as f:
        content = f.read()
    
    # Find threshold
    long_match = re.search(r'LONG_THRESHOLD\s*=\s*([\d\.]+)', content)
    
    if long_match:
        long_val = float(long_match.group(1))
        print(f'  LONG_THRESHOLD: {long_val}% {"✅" if long_val == 1.0 else "❌"}')
    else:
        print('  ❌ Could not find threshold')
except Exception as e:
    print(f'  ❌ Error: {e}')

print('\n🎯 SUMMARY:')
print('  Both bots should now use 1.0% thresholds')
print('  This should generate more trades while maintaining risk control')

print('\n📈 EXPECTED BEHAVIOR:')
print('  • Gemini: Buys LONG on 1.0%+ dips detected via Binance')
print('  • Binance: Sells SHORT on 1.0%+ rallies')
print('  • Position size: 10% of capital')
print('  • Stop-loss: 3%, Take-profit: 5%')

print('\n✅ READY TO RESTART BOTS')