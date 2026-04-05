#!/usr/bin/env python3
import requests
import time

print('🔍 TESTING DASHBOARD ACCESS')
print('=' * 60)

urls = [
    ('Main Dashboard', 'http://localhost:5007/'),
    ('Trading API', 'http://localhost:5001/'),
    ('API Data', 'http://localhost:5007/api/data'),
    ('Trading Server', 'http://localhost:5001/api/data')
]

for name, url in urls:
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            print(f'✅ {name}: HTTP 200 in {elapsed:.2f}s')
            
            if 'api/data' in url:
                # Check data structure
                data = response.json()
                positions = len(data.get('positions', []))
                print(f'   • Positions: {positions}')
                print(f'   • Capital: ${data.get("capital", {}).get("total_capital", 0):.2f}')
        else:
            print(f'⚠️ {name}: HTTP {response.status_code} in {elapsed:.2f}s')
            
    except requests.exceptions.Timeout:
        print(f'❌ {name}: TIMEOUT after 10s')
    except requests.exceptions.ConnectionError:
        print(f'❌ {name}: CONNECTION ERROR')
    except Exception as e:
        print(f'❌ {name}: ERROR - {e}')

print()
print('📊 CHECKING P&L DISPLAY:')
try:
    response = requests.get('http://localhost:5007/', timeout=10)
    html = response.text
    
    if 'P&L INFORMATION' in html:
        print('✅ P&L INFORMATION section found in dashboard')
        
        # Check if it's at the top
        pnl_pos = html.find('P&L INFORMATION')
        positions_pos = html.find('CURRENT POSITIONS')
        
        if pnl_pos < positions_pos:
            print('✅ P&L is BEFORE positions (pulled up to top)')
        else:
            print('❌ P&L is AFTER positions (not at top)')
            
        # Check for data cards
        if 'data-card' in html and 'CUMULATIVE P&L' in html:
            print('✅ P&L data cards present')
        else:
            print('❌ P&L data cards missing')
            
    else:
        print('❌ P&L INFORMATION section NOT found')
        
except Exception as e:
    print(f'❌ Error checking P&L: {e}')