#!/usr/bin/env python3
import requests

try:
    response = requests.get('http://localhost:5007/', timeout=5)
    html = response.text
    
    # Find the P&L section
    if 'P&L INFORMATION' in html:
        start = html.find('P&L INFORMATION')
        # Get 500 chars before and 1000 chars after
        before = html[max(0, start-500):start]
        after = html[start:start+1000]
        
        print('✅ P&L INFORMATION SECTION FOUND')
        print('=' * 60)
        
        # Show what comes before P&L
        print('\n📄 WHAT COMES BEFORE P&L:')
        lines = before.split('\n')
        for line in lines[-10:]:  # Last 10 lines before P&L
            if line.strip():
                print(f'   ...{line.strip()[:80]}')
        
        print('\n📊 P&L SECTION CONTENT:')
        lines = after.split('\n')
        for i, line in enumerate(lines[:20]):  # First 20 lines of P&L section
            if line.strip():
                print(f'   {line.strip()[:100]}')
        
        # Check if P&L is near the top
        pnl_position = html.find('P&L INFORMATION')
        total_length = len(html)
        percentage = (pnl_position / total_length) * 100
        
        print(f'\n📍 P&L POSITION: {pnl_position:,} chars into {total_length:,} chars ({percentage:.1f}% of page)')
        
        if percentage < 30:
            print('   ✅ P&L is near the top of the page')
        elif percentage < 60:
            print('   ⚠️ P&L is in the middle of the page')
        else:
            print('   ❌ P&L is near the bottom - should be moved up')
            
    else:
        print('❌ P&L INFORMATION section NOT found')
        
except Exception as e:
    print(f'❌ Error: {e}')