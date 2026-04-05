#!/usr/bin/env python3
"""
Check what the LLM dashboard shows about executed trades
"""

import requests
from bs4 import BeautifulSoup
import re

print("="*70)
print("🔍 CHECKING LLM DASHBOARD FOR EXECUTED TRADES")
print("="*70)

try:
    # Fetch the dashboard
    response = requests.get('http://localhost:5007', timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for LLM reports section
        llm_section = soup.find(string=re.compile('LLM Reports', re.I))
        
        if llm_section:
            print("✅ Found LLM Reports section")
            
            # Look for tables with executed trades
            tables = soup.find_all('table')
            
            for i, table in enumerate(tables):
                table_text = table.get_text().lower()
                if 'executed' in table_text or 'filled' in table_text:
                    print(f"\n📊 Table {i} contains 'executed' or 'filled':")
                    # Get headers
                    headers = [th.get_text().strip() for th in table.find_all('th')]
                    print(f"  Headers: {headers}")
                    
                    # Get first few rows
                    rows = table.find_all('tr')[:5]
                    for row in rows:
                        cells = [td.get_text().strip() for td in row.find_all('td')]
                        if cells:
                            print(f"  Row: {cells}")
        
        # Look for any text about selling ETH or SOL
        all_text = soup.get_text()
        
        eth_sell_matches = re.findall(r'ETH.*sell|sell.*ETH', all_text, re.I)
        sol_sell_matches = re.findall(r'SOL.*sell|sell.*SOL', all_text, re.I)
        
        if eth_sell_matches:
            print(f"\n🚨 Found ETH SELL references: {len(eth_sell_matches)}")
            for match in eth_sell_matches[:3]:
                print(f"  • {match}")
        
        if sol_sell_matches:
            print(f"\n🚨 Found SOL SELL references: {len(sol_sell_matches)}")
            for match in sol_sell_matches[:3]:
                print(f"  • {match}")
        
        # Look for executed trades
        executed_matches = re.findall(r'executed.*trade|trade.*executed', all_text, re.I)
        if executed_matches:
            print(f"\n📋 Found EXECUTED trade references: {len(executed_matches)}")
            for match in executed_matches[:3]:
                print(f"  • {match}")
        
        if not (eth_sell_matches or sol_sell_matches or executed_matches):
            print("\n✅ No SELL or EXECUTED references found in dashboard")
            
    else:
        print(f"❌ Dashboard returned {response.status_code}")
        
except Exception as e:
    print(f"❌ Error checking dashboard: {e}")

print("\n" + "="*70)
print("💡 NEXT STEPS:")
print("1. Check if LLM actually recommended SELL")
print("2. Check if system logged SELL as 'executed'")
print("3. Verify actual positions vs displayed positions")
print("="*70)