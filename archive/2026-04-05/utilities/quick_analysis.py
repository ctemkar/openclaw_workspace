#!/usr/bin/env python3
import json

with open('completed_trades.json', 'r') as f:
    trades = json.load(f)

print('=== TRADE ANALYSIS ===')
print(f'Total trades: {len(trades)}')

# Separate by asset
btc_trades = [t for t in trades if 'BTC' in str(t.get('symbol', '')) or 'BTC' in str(t.get('model', ''))]
eth_trades = [t for t in trades if 'ETH' in str(t.get('symbol', '')) or 'ETH' in str(t.get('model', ''))]

print(f'\nBTC Trades: {len(btc_trades)}')
if btc_trades:
    btc_prices = [t.get('price', 0) for t in btc_trades if t.get('price')]
    avg_btc = sum(btc_prices)/len(btc_prices)
    print(f'  Average price: ${avg_btc:,.2f}')
    print(f'  Price range: ${min(btc_prices):,.2f} - ${max(btc_prices):,.2f}')
    
print(f'\nETH Trades: {len(eth_trades)}')
if eth_trades:
    eth_prices = [t.get('price', 0) for t in eth_trades if t.get('price')]
    avg_eth = sum(eth_prices)/len(eth_prices)
    print(f'  Average price: ${avg_eth:,.2f}')
    print(f'  Price range: ${min(eth_prices):,.2f} - ${max(eth_prices):,.2f}')

# Current prices
current_btc = 71150
current_eth = 2173.22

print(f'\n=== CURRENT POSITION ANALYSIS ===')
print(f'Current BTC price: ${current_btc:,.2f}')
if btc_trades:
    btc_pnl_pct = (current_btc - avg_btc) / avg_btc * 100
    print(f'  BTC P&L: {btc_pnl_pct:.2f}%')
    stop_loss_btc = avg_btc * 0.95
    print(f'  Stop-loss level (5%): ${stop_loss_btc:,.2f}')
    diff_btc = current_btc - stop_loss_btc
    print(f'  Current vs stop-loss: ${diff_btc:,.2f}')
    if diff_btc < 0:
        print(f'  ⚠️  BTC POSITION BELOW STOP-LOSS!')

print(f'\nCurrent ETH price: ${current_eth:,.2f}')
if eth_trades:
    eth_pnl_pct = (current_eth - avg_eth) / avg_eth * 100
    print(f'  ETH P&L: {eth_pnl_pct:.2f}%')
    stop_loss_eth = avg_eth * 0.95
    print(f'  Stop-loss level (5%): ${stop_loss_eth:,.2f}')
    diff_eth = current_eth - stop_loss_eth
    print(f'  Current vs stop-loss: ${diff_eth:,.2f}')
    if diff_eth < 0:
        print(f'  ⚠️  ETH POSITION BELOW STOP-LOSS!')

print(f'\n=== RECOMMENDATIONS ===')
print('1. Check if stop-loss orders were executed')
print('2. Verify actual account balances')
print('3. Review trading system stop-loss implementation')
print('4. Consider manual intervention if stop-loss failed')