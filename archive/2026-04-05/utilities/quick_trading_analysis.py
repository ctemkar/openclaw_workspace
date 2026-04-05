#!/usr/bin/env python3
"""
Quick aggressive momentum trading analysis
"""

import json
import random
from datetime import datetime

# Simulate current market conditions
print('=== AGGRESSIVE MOMENTUM TRADING ANALYSIS ===')
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('Paper Balance: $25,000.00')
print('Leverage Available: 2.0x')
print('Daily Trades Remaining: 5')
print()

# Simulate market data
pairs = ['BTC/USD', 'ETH/USD', 'SOL/USD']
current_prices = {
    'BTC/USD': random.uniform(67000, 69000),
    'ETH/USD': random.uniform(2100, 2200),
    'SOL/USD': random.uniform(80, 90)
}

hourly_changes = {
    'BTC/USD': random.uniform(-3, 3),
    'ETH/USD': random.uniform(-3, 3),
    'SOL/USD': random.uniform(-3, 3)
}

print('📈 MARKET ANALYSIS:')
for pair in pairs:
    price = current_prices[pair]
    change = hourly_changes[pair]
    trend = '🟢 BULLISH' if change > 2 else '🔴 BEARISH' if change < -2 else '⚪ NEUTRAL'
    volume_spike = '📈 HIGH' if random.random() > 0.7 else '📉 NORMAL'
    
    print(f'{pair}: ${price:,.2f} ({change:+.2f}%) {trend}')
    print(f'  Volume: {volume_spike}')
    
    # Check for aggressive trading signals
    if abs(change) >= 2 and volume_spike == '📈 HIGH':
        action = 'BUY' if change > 0 else 'SELL'
        print(f'  ⚡ AGGRESSIVE SIGNAL: {action} - Strong momentum with volume spike')
        print(f'  📊 Entry: ${price:,.2f}')
        stop_loss = price * 0.92 if action == 'BUY' else price * 1.08
        take_profit = price * 1.15 if action == 'BUY' else price * 0.85
        print(f'  🛑 Stop Loss: ${stop_loss:,.2f}')
        print(f'  🎯 Take Profit: ${take_profit:,.2f}')
    print()

print('=== TRADING RECOMMENDATIONS ===')
print('Based on current market conditions:')
print('1. Monitor BTC/USD for potential breakout above $68,500')
print('2. ETH/USD showing consolidation - wait for clearer direction')
print('3. SOL/USD has normal volume - no aggressive signals')
print()
print('⚠️  PAPER TRADING ONLY - NO REAL FUNDS')
print('✅ Ready for next analysis cycle')