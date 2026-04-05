#!/usr/bin/env python3
"""
Test P&L display in dashboard
"""

import requests
import time

print('🔍 TESTING P&L DISPLAY IN DASHBOARD')
print('=' * 60)

# Wait for dashboard to start
time.sleep(3)

try:
    response = requests.get('http://localhost:5007/', timeout=5)
    html = response.text
    
    # Check for P&L INFORMATION section
    if 'P&L INFORMATION' in html:
        print('✅ P&L INFORMATION section found')
        
        # Extract the P&L section
        start = html.find('P&L INFORMATION')
        end = html.find('💰 CAPITAL SUMMARY', start)
        pnl_section = html[start:end] if end > start else html[start:start+2000]
        
        # Check for key elements
        checks = [
            ('CUMULATIVE P&L', 'Cumulative P&L'),
            ('GEMINI P&L', 'Gemini P&L'),
            ('BINANCE P&L', 'Binance P&L'),
            ('SHORT TRADES', 'Short trades status'),
            ('$-415.32', 'Cumulative loss amount'),
            ('$+0.45', 'Gemini profit'),
            ('$-3.83', 'Binance loss'),
            ('0 OPEN', 'Short trades count')
        ]
        
        for check, description in checks:
            if check in pnl_section:
                print(f'   ✅ {description}: Found')
            else:
                print(f'   ❌ {description}: Missing')
        
        # Show what we found
        print('\n📊 EXTRACTED P&L SECTION:')
        lines = pnl_section.split('\n')
        for line in lines[:30]:  # Show first 30 lines
            if any(keyword in line for keyword in ['CUMULATIVE', 'GEMINI', 'BINANCE', 'SHORT', 'data-value', 'data-card']):
                print(f'   {line[:100]}...' if len(line) > 100 else f'   {line}')
                
    else:
        print('❌ P&L INFORMATION section NOT found in dashboard')
        print('Looking for "P&L INFORMATION" in HTML...')
        
except Exception as e:
    print(f'❌ Error accessing dashboard: {e}')

print()
print('📊 Also check:')
print('   • Updated server: http://localhost:5001/')
print('   • Common dashboard: http://localhost:5007/')
print()
print('✅ READY FOR NEXT REQUEST')