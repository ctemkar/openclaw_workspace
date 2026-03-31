#!/usr/bin/env python3
"""
Update system with REAL Gemini data
"""

import json
from datetime import datetime

print("🔄 UPDATING SYSTEM WITH REAL GEMINI DATA")
print("="*60)

# REAL data from Gemini API
REAL_DATA = {
    "timestamp": datetime.now().isoformat(),
    "balances": {
        "USD": 134.27,
        "BTC": 0.005981
    },
    "portfolio": {
        "cash_usd": 134.27,
        "btc_amount": 0.005981,
        "btc_price": 66805.21,
        "btc_value": 399.56,
        "total_value": 533.83
    },
    "today_trades": [
        {
            "time": "2026-03-31T09:26:52",
            "symbol": "BTC/USD",
            "side": "buy",
            "amount": 0.003991,
            "price": 67918.89,
            "cost": 271.06
        },
        {
            "time": "2026-03-31T09:34:15",
            "symbol": "BTC/USD",
            "side": "buy",
            "amount": 0.00199,
            "price": 67790.48,
            "cost": 134.90
        }
    ],
    "summary": {
        "total_spent_today": 405.97,
        "trades_count": 2,
        "btc_held": 0.005981,
        "current_btc_value": 399.56,
        "unrealized_pnl": -6.41,
        "unrealized_pnl_percent": -1.58
    }
}

# 1. Update daily_trades.json with CORRECT data
print("\n1. 📝 Updating daily_trades.json...")
with open('daily_trades.json', 'r') as f:
    daily_trades = json.load(f)

# Update trades with correct data
for i, trade in enumerate(daily_trades.get('trades', [])):
    if i < len(REAL_DATA['today_trades']):
        real_trade = REAL_DATA['today_trades'][i]
        trade['price'] = real_trade['price']
        trade['value'] = real_trade['cost']
        trade['status'] = 'open'  # Trades are OPEN, not closed!
        trade['source'] = 'GEMINI_API_CONFIRMED'
        trade['last_updated'] = datetime.now().isoformat()

# Add metadata
daily_trades['metadata'] = {
    'last_updated': datetime.now().isoformat(),
    'source': 'Gemini API via ccxt',
    'verified': True,
    'total_portfolio_value': REAL_DATA['portfolio']['total_value'],
    'notes': 'Corrected with REAL Gemini data. Trades are OPEN positions.'
}

with open('daily_trades.json', 'w') as f:
    json.dump(daily_trades, f, indent=2)
print("   ✅ Updated with REAL Gemini data")

# 2. Create accurate capital tracking file
print("\n2. 💰 Creating accurate capital tracking...")
capital_data = {
    "initial_capital": 540.00,  # Adjusted based on REAL portfolio
    "current_capital": REAL_DATA['portfolio']['total_value'],
    "cash": REAL_DATA['balances']['USD'],
    "crypto_holdings": {
        "BTC": {
            "amount": REAL_DATA['balances']['BTC'],
            "average_buy_price": 405.97 / 0.005981,  # ~$67,880
            "current_price": REAL_DATA['portfolio']['btc_price'],
            "current_value": REAL_DATA['portfolio']['btc_value'],
            "unrealized_pnl": REAL_DATA['summary']['unrealized_pnl'],
            "unrealized_pnl_percent": REAL_DATA['summary']['unrealized_pnl_percent']
        }
    },
    "today_trades": REAL_DATA['today_trades'],
    "performance": {
        "total_return": REAL_DATA['portfolio']['total_value'] - 540.00,
        "total_return_percent": (REAL_DATA['portfolio']['total_value'] - 540.00) / 540.00 * 100,
        "daily_trades": len(REAL_DATA['today_trades']),
        "daily_volume": REAL_DATA['summary']['total_spent_today']
    },
    "last_updated": datetime.now().isoformat()
}

with open('accurate_capital.json', 'w') as f:
    json.dump(capital_data, f, indent=2)
print("   ✅ Created accurate_capital.json")

# 3. Update trade_history.json
print("\n3. 📊 Updating trade_history.json...")
trade_history = {
    "trades_today": len(REAL_DATA['today_trades']),
    "last_trade_date": datetime.now().strftime('%Y-%m-%d'),
    "last_trade_time": REAL_DATA['today_trades'][-1]['time'] if REAL_DATA['today_trades'] else None,
    "total_trades_value": REAL_DATA['summary']['total_spent_today'],
    "last_updated": datetime.now().isoformat()
}

with open('trade_history.json', 'w') as f:
    json.dump(trade_history, f, indent=2)
print("   ✅ Updated trade count to 2 (REAL trades)")

print("\n" + "="*60)
print("✅ SYSTEM UPDATED WITH REAL DATA!")
print()
print("📈 REAL PORTFOLIO STATUS:")
print(f"  Total Value: ${REAL_DATA['portfolio']['total_value']:,.2f}")
print(f"  Cash: ${REAL_DATA['balances']['USD']:,.2f}")
print(f"  BTC: {REAL_DATA['balances']['BTC']:.6f} (${REAL_DATA['portfolio']['btc_value']:,.2f})")
print(f"  Today's Trades: {len(REAL_DATA['today_trades'])} (${REAL_DATA['summary']['total_spent_today']:,.2f})")
print(f"  Unrealized P&L: ${REAL_DATA['summary']['unrealized_pnl']:,.2f} ({REAL_DATA['summary']['unrealized_pnl_percent']:.1f}%)")
print()
print("🎯 NEXT: Fix logging system and resume trading!")
print("="*60)