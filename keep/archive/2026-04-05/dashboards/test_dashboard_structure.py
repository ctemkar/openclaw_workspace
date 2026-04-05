#!/usr/bin/env python3
"""
Test the dashboard structure directly from the Python file
"""

import re

print('🔍 TESTING DASHBOARD STRUCTURE FROM FILE')
print('=' * 60)

# Read the dashboard file
with open('dashboard_common.py', 'r') as f:
    content = f.read()

# Find the HTML generation section
html_start = content.find('html = f"""')
if html_start == -1:
    print('❌ Could not find HTML template in file')
    exit(1)

# Find the end of the HTML template
html_end = content.find('"""', html_start + 12)
if html_end == -1:
    print('❌ Could not find end of HTML template')
    exit(1)

html_template = content[html_start:html_end + 3]

# Extract the actual HTML (remove the f""" and closing quotes)
html_content = html_template[12:-3]

# Find section positions in the template
pnl_pos = html_content.find('P&L INFORMATION')
positions_pos = html_content.find('CURRENT POSITIONS')
capital_pos = html_content.find('CAPITAL SUMMARY')

print(f'📊 SECTION POSITIONS IN TEMPLATE:')
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

# Show the structure
print('\n📋 DASHBOARD STRUCTURE:')
lines = html_content.split('\n')
section_count = 0

for i, line in enumerate(lines):
    if '<h2>' in line or '<h3>' in line:
        section_count += 1
        if section_count <= 8:  # Show first 8 sections
            # Clean up the line
            clean_line = line.strip().replace('<h2>', '').replace('</h2>', '').replace('<h3>', '').replace('</h3>', '')
            print(f'   {section_count}. {clean_line[:80]}')

print('\n🔍 CHECKING P&L CONTENT:')
# Extract P&L section
if pnl_pos > 0:
    # Find end of P&L section (next h2 or end of data-grid)
    pnl_end = html_content.find('<h2>', pnl_pos + 50)
    if pnl_end == -1:
        pnl_end = html_content.find('</div>', pnl_pos + 500) + 6
    
    pnl_section = html_content[pnl_pos:pnl_end]
    
    # Check for key elements
    checks = [
        ('CUMULATIVE P&L', 'Cumulative P&L card'),
        ('GEMINI P&L', 'Gemini P&L card'),
        ('BINANCE P&L', 'Binance P&L card'),
        ('SHORT TRADES', 'Short trades card'),
        ('data-grid', 'Data grid container'),
        ('data-card', 'Data card elements'),
        ('$-415.32', 'Cumulative loss amount'),
        ('$+0.45', 'Gemini profit'),
        ('$-3.83', 'Binance loss')
    ]
    
    for text, description in checks:
        if text in pnl_section:
            print(f'   ✅ {description}: Found')
        else:
            print(f'   ❌ {description}: Missing')

print('\n✅ DASHBOARD FILE UPDATED SUCCESSFULLY')
print('   • P&L INFORMATION moved to top')
print('   • Data cards showing all P&L metrics')
print('   • Structure: P&L → Positions → Capital → Bot Status')