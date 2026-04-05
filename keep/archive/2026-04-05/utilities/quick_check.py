#!/usr/bin/env python3
import requests
import json

# Quick one-time check
with open('completed_trades.json', 'r') as f:
    trades = json.load(f)

response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd')
prices = response.json()

btc_price = prices['bitcoin']['usd']
eth_price = prices['ethereum']['usd']

print('Current BTC: ${:,.2f}'.format(btc_price))
print('Current ETH: ${:,.2f}'.format(eth_price))

# Simple analysis
btc_trades = [t['price'] for t in trades if 'BTC' in str(t.get('symbol', '')).upper() and t.get('price')]
eth_trades = [t['price'] for t in trades if 'ETH' in str(t.get('symbol', '')).upper() and t.get('price')]

if btc_trades:
    avg_btc = sum(btc_trades)/len(btc_trades)
    print('\nBTC: Entry ${:,.2f}, P&L: {:.2f}%'.format(avg_btc, (btc_price-avg_btc)/avg_btc*100))
    print('  5% Stop-loss: ${:,.2f}'.format(avg_btc*0.95))
    diff_btc = btc_price - avg_btc*0.95
    print('  Current vs stop-loss: ${:,.2f}'.format(diff_btc))
    if diff_btc < 0:
        print('  🚨 BTC BELOW STOP-LOSS!')

if eth_trades:
    avg_eth = sum(eth_trades)/len(eth_trades)
    print('\nETH: Entry ${:,.2f}, P&L: {:.2f}%'.format(avg_eth, (eth_price-avg_eth)/avg_eth*100))
    print('  5% Stop-loss: ${:,.2f}'.format(avg_eth*0.95))
    diff_eth = eth_price - avg_eth*0.95
    print('  Current vs stop-loss: ${:,.2f}'.format(diff_eth))
    if diff_eth < 0:
        print('  🚨 ETH BELOW STOP-LOSS!')

print('\n=== SUMMARY ===')
if btc_trades:
    status = '🚨 STOP-LOSS' if diff_btc < 0 else '✅ OK'
    print('BTC: {} (P&L: {:.2f}%)'.format(status, (btc_price-avg_btc)/avg_btc*100))
if eth_trades:
    status = '🚨 STOP-LOSS' if diff_eth < 0 else '✅ OK'
    print('ETH: {} (P&L: {:.2f}%)'.format(status, (eth_price-avg_eth)/avg_eth*100))