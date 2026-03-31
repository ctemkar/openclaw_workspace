#!/usr/bin/env python3
import requests
import sys

try:
    response = requests.get('http://localhost:5007/', timeout=3)
    html = response.text
    
    if 'P&L INFORMATION' in html:
        print('✅ P&L INFORMATION section is in dashboard')
        
        # Show a preview
        start = html.find('P&L INFORMATION')
        preview = html[start:start+500]
        print('\nPreview:')
        for line in preview.split('\n'):
            if 'data-card' in line or 'data-value' in line or 'h3' in line:
                print(line[:100])
                
    else:
        print('❌ P&L INFORMATION section NOT found')
        
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)