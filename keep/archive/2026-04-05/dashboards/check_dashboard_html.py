#!/usr/bin/env python3
import requests
import sys

try:
    response = requests.get('http://localhost:5007/', timeout=5)
    html = response.text
    
    # Save to file for inspection
    with open('dashboard_output.html', 'w') as f:
        f.write(html)
    
    print('✅ Dashboard HTML saved to dashboard_output.html')
    
    # Check for P&L sections
    sections = [
        ('P&L INFORMATION', 'P&L Information section'),
        ('CUMULATIVE P&L', 'Cumulative P&L'),
        ('GEMINI P&L', 'Gemini P&L'),
        ('BINANCE P&L', 'Binance P&L'),
        ('SHORT TRADES', 'Short trades'),
        ('data-grid', 'Data grid CSS'),
        ('data-card', 'Data card CSS')
    ]
    
    print('\n🔍 CHECKING FOR P&L SECTIONS:')
    for text, description in sections:
        if text in html:
            print(f'   ✅ {description}: FOUND')
        else:
            print(f'   ❌ {description}: MISSING')
    
    # Show a snippet around where P&L should be
    print('\n📄 HTML SNIPPET AROUND CAPITAL SUMMARY:')
    if 'CAPITAL SUMMARY' in html:
        start = html.find('CAPITAL SUMMARY') - 200
        end = html.find('CAPITAL SUMMARY') + 800
        snippet = html[max(0,start):min(len(html),end)]
        
        # Clean up the snippet
        lines = snippet.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['capital', 'summary', 'table', 'tr>', '<td>', 'h2']):
                print(f'   {line[:120]}' if len(line) > 120 else f'   {line}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)