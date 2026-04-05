#!/usr/bin/env python3
import requests
import time

print('🔍 VERIFYING P&L IS PULLED UP TO TOP')
print('=' * 60)

time.sleep(3)

try:
    response = requests.get('http://localhost:5007/', timeout=5)
    html = response.text
    
    # Find positions of key sections
    pnl_pos = html.find('P&L INFORMATION')
    positions_pos = html.find('CURRENT POSITIONS')
    capital_pos = html.find('CAPITAL SUMMARY')
    
    print(f'📊 SECTION POSITIONS IN HTML:')
    print(f'   • P&L INFORMATION: Position {pnl_pos:,}')
    print(f'   • CURRENT POSITIONS: Position {positions_pos:,}')
    print(f'   • CAPITAL SUMMARY: Position {capital_pos:,}')
    
    if pnl_pos > 0 and positions_pos > 0:
        if pnl_pos < positions_pos:
            print('✅ SUCCESS: P&L INFORMATION is BEFORE CURRENT POSITIONS (pulled up!)')
        else:
            print('❌ FAIL: P&L INFORMATION is AFTER CURRENT POSITIONS')
    
    if pnl_pos > 0 and capital_pos > 0:
        if pnl_pos < capital_pos:
            print('✅ SUCCESS: P&L INFORMATION is BEFORE CAPITAL SUMMARY')
        else:
            print('❌ FAIL: P&L INFORMATION is AFTER CAPITAL SUMMARY')
    
    # Show what comes right after the header
    print('\n📄 FIRST 500 CHARS AFTER HEADER:')
    header_end = html.find('</h1>') + 5
    snippet = html[header_end:header_end+500]
    
    # Clean up the snippet
    lines = snippet.split('\n')
    for line in lines:
        if line.strip():
            print(f'   {line.strip()[:100]}')
    
    # Check for P&L data cards
    print('\n🔍 CHECKING FOR P&L DATA CARDS:')
    if 'data-card' in html and 'CUMULATIVE P&L' in html:
        print('✅ P&L data cards found')
        
        # Extract P&L section
        start = html.find('P&L INFORMATION')
        end = html.find('CURRENT POSITIONS', start)
        pnl_section = html[start:end] if end > start else html[start:start+800]
        
        print('\n📊 P&L SECTION CONTENT (first 10 lines):')
        lines = pnl_section.split('\n')
        for line in lines[:15]:
            if line.strip():
                print(f'   {line.strip()[:80]}')
    else:
        print('❌ P&L data cards not found')
        
except Exception as e:
    print(f'❌ Error: {e}')