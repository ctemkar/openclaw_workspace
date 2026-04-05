#!/usr/bin/env python3
"""
Calculate REAL trade values from Gemini data
"""

print("💰 CALCULATING REAL TRADE VALUES FROM GEMINI DATA")
print("="*60)

# Gemini data from user
trades = [
    {
        "date": "2026-03-31 09:34:15",
        "symbol": "BTCUSD",
        "side": "Buy",
        "quantity": 0.00199,  # BTC
        "price": 67790.48,    # USD
        "fee": 0.67           # USD
    },
    {
        "date": "2026-03-31 09:26:52",
        "symbol": "BTCUSD",
        "side": "Buy",
        "quantity": 0.003991,  # BTC
        "price": 67918.89,     # USD
        "fee": 1.35            # USD
    },
    {
        "date": "2026-03-30 01:39:34",
        "symbol": "MANAUSD",
        "side": "Sell",
        "quantity": 220.858895,  # MANA
        "price": 0.08049,        # USD
        "fee": 0.04              # USD
    },
    {
        "date": "2026-03-29 22:22:38",
        "symbol": "FTMUSD",
        "side": "Sell",
        "quantity": 26.65949,    # FTM
        "price": 0.0405,         # USD
        "fee": 0.00              # USD
    },
    {
        "date": "2026-03-29 ??",  # Unknown time
        "symbol": "FTMUSD",
        "side": "Sell",
        "quantity": 393.968326,   # FTM
        "price": 0.0405,          # USD
        "fee": 0.03               # USD
    }
]

print("📊 TODAY'S TRADES (March 31):")
total_buys_today = 0
total_fees_today = 0

for trade in trades[:2]:  # First 2 are today's buys
    cost = trade["quantity"] * trade["price"]
    total = cost + trade["fee"]
    
    print(f"  {trade['date']} - {trade['side']} {trade['quantity']} {trade['symbol'][:3]} @ ${trade['price']:,.2f}")
    print(f"    Cost: ${cost:,.2f} + Fee: ${trade['fee']:,.2f} = Total: ${total:,.2f}")
    
    total_buys_today += total
    total_fees_today += trade["fee"]

print(f"\n  📈 TODAY'S TOTAL: ${total_buys_today:,.2f} (Fees: ${total_fees_today:,.2f})")

print("\n💰 PREVIOUS DAYS' TRADES:")
total_sales_previous = 0
total_fees_previous = 0

for trade in trades[2:]:  # Last 3 are previous sales
    revenue = trade["quantity"] * trade["price"]
    net = revenue - trade["fee"]
    
    print(f"  {trade['date']} - {trade['side']} {trade['quantity']} {trade['symbol'][:3]} @ ${trade['price']:,.4f}")
    print(f"    Revenue: ${revenue:,.2f} - Fee: ${trade['fee']:,.2f} = Net: ${net:,.2f}")
    
    total_sales_previous += net
    total_fees_previous += trade["fee"]

print(f"\n  📈 PREVIOUS TOTAL NET: ${total_sales_previous:,.2f} (Fees: ${total_fees_previous:,.2f})")

print("\n" + "="*60)
print("🧮 CAPITAL FLOW ANALYSIS:")

# Known values
initial_capital = 250  # Starting capital
current_balance = 175.53  # Current balance

# Calculate
total_spent = total_buys_today
total_earned = total_sales_previous
net_cash_flow = total_earned - total_spent
expected_balance = initial_capital + net_cash_flow

print(f"  Initial capital: ${initial_capital:,.2f}")
print(f"  Total spent today: ${total_spent:,.2f}")
print(f"  Total earned previous days: ${total_earned:,.2f}")
print(f"  Net cash flow: ${net_cash_flow:,.2f}")
print(f"  Expected balance: ${expected_balance:,.2f}")
print(f"  Actual balance: ${current_balance:,.2f}")
print(f"  Discrepancy: ${current_balance - expected_balance:,.2f}")

print("\n" + "="*60)
print("🚨 MYSTERY STILL UNSOLVED:")
print(f"  We spent ${total_spent:,.2f} today")
print(f"  But maximum available was ~${initial_capital + total_earned:,.2f}")
print(f"  Difference: ${total_spent - (initial_capital + total_earned):,.2f}")
print("\n  POSSIBLE EXPLANATIONS:")
print("  1. Had more starting capital than $250")
print("  2. BTC bought on margin/leverage")
print("  3. Other income not shown in these trades")
print("  4. Data still incomplete/missing trades")
print("="*60)