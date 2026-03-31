#!/usr/bin/env python3
import requests

print("Checking ALL potential dashboards...")

# Check common ports
ports = [5000, 5001, 5002, 5003, 5004, 5005, 8080, 8081, 3000, 3001]

for port in ports:
    try:
        response = requests.get(f"http://localhost:{port}", timeout=2)
        if response.status_code == 200:
            html = response.text
            
            # Check for dashboard indicators
            is_dashboard = False
            indicators = []
            
            if "SIMULATION" in html:
                indicators.append("SIMULATION")
                is_dashboard = True
            if "REAL TRADING" in html:
                indicators.append("REAL TRADING")
                is_dashboard = True
            if "Max Daily Trades" in html:
                indicators.append("Max Daily Trades")
                is_dashboard = True
            if "Risk Management" in html:
                indicators.append("Risk Management")
                is_dashboard = True
            if "System Status" in html:
                indicators.append("System Status")
                is_dashboard = True
            
            if is_dashboard:
                print(f"\n🚨 FOUND DASHBOARD ON PORT {port}:")
                print(f"   Indicators: {', '.join(indicators)}")
                
                # Extract key info
                import re
                
                # Check for simulation
                if "SIMULATION" in html:
                    sim_match = re.search(r'Execution Mode:(.*?)</p>', html, re.DOTALL)
                    if sim_match:
                        print(f"   Execution Mode: {sim_match.group(1).strip()}")
                
                # Check for max daily trades
                trades_match = re.search(r'Max Daily Trades.*?>(\d+)<', html, re.DOTALL)
                if trades_match:
                    print(f"   Max Daily Trades: {trades_match.group(1)}")
                
                # Check for position size
                pos_match = re.search(r'Position Size.*?>(\d+)%<', html, re.DOTALL)
                if pos_match:
                    print(f"   Position Size: {pos_match.group(1)}%")
                
                # Check for strategy
                strat_match = re.search(r'Strategy:(.*?)</p>', html, re.DOTALL)
                if strat_match:
                    print(f"   Strategy: {strat_match.group(1).strip()}")
                    
    except:
        pass

print("\n" + "="*60)
print("If you're seeing 'SIMULATION' and 'Max Daily Trades: 2',")
print("it's coming from ONE of these dashboards above!")
print("="*60)