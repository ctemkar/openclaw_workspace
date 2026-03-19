import json
import subprocess

# Get summary
result = subprocess.run(['curl', '-s', 'http://localhost:5001/summary'], capture_output=True, text=True)
summary = result.stdout

print("=== PRICE EXTRACTION ===")
print("Summary preview (first 500 chars):")
print(summary[:500])
print("\n")

# Simple extraction
lines = summary.split('\n')
btc_price = None
eth_price = None

for line in lines:
    if 'BTC/USD' in line and 'Price:' in line:
        # Look for $ followed by numbers
        import re
        match = re.search(r'\$([\d,]+\.\d+)', line)
        if match:
            btc_price = float(match.group(1).replace(',', ''))
    elif 'ETH/USD' in line and 'Price:' in line:
        import re
        match = re.search(r'\$([\d,]+\.\d+)', line)
        if match:
            eth_price = float(match.group(1).replace(',', ''))

print(f"BTC price extracted: ${btc_price}" if btc_price else "BTC price: Not found")
print(f"ETH price extracted: ${eth_price}" if eth_price else "ETH price: Not found")

# Get trades
result = subprocess.run(['curl', '-s', 'http://localhost:5001/trades'], capture_output=True, text=True)
trades = json.loads(result.stdout)

# Find entry prices
btc_entries = []
eth_entries = []

for trade in trades['trades']:
    # Check various field names
    price = trade.get('price')
    if not price:
        price = trade.get('amount')
    
    if price:
        try:
            price_val = float(price)
            # Determine which asset
            symbol = str(trade.get('symbol', trade.get('model', ''))).upper()
            if 'BTC' in symbol:
                btc_entries.append(price_val)
            elif 'ETH' in symbol:
                eth_entries.append(price_val)
        except:
            pass

print(f"\nBTC entries found: {len(btc_entries)}")
print(f"ETH entries found: {len(eth_entries)}")

if btc_entries:
    btc_highest = max(btc_entries)
    print(f"Highest BTC entry: ${btc_highest:,.2f}")
    
if eth_entries:
    eth_highest = max(eth_entries)
    print(f"Highest ETH entry: ${eth_highest:,.2f}")

# Calculate drawdown
if btc_price and btc_entries:
    btc_highest = max(btc_entries)
    btc_drawdown = (btc_price - btc_highest) / btc_highest * 100
    print(f"\nBTC drawdown: {btc_drawdown:.2f}%")
    
if eth_price and eth_entries:
    eth_highest = max(eth_entries)
    eth_drawdown = (eth_price - eth_highest) / eth_highest * 100
    print(f"ETH drawdown: {eth_drawdown:.2f}%")

# Check against stop-loss (5%)
stop_loss = 5.0
if btc_price and btc_entries:
    if btc_drawdown <= -stop_loss:
        print(f"🚨 BTC STOP-LOSS TRIGGERED: {btc_drawdown:.2f}% <= -{stop_loss}%")
    else:
        print(f"BTC within stop-loss: {btc_drawdown:.2f}% (threshold: -{stop_loss}%)")

if eth_price and eth_entries:
    if eth_drawdown <= -stop_loss:
        print(f"🚨 ETH STOP-LOSS TRIGGERED: {eth_drawdown:.2f}% <= -{stop_loss}%")
    else:
        print(f"ETH within stop-loss: {eth_drawdown:.2f}% (threshold: -{stop_loss}%)")