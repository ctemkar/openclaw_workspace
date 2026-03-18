#!/usr/bin/env python3

btc_price = 74213
btc_holdings = 0.00053507
avg_entry = 74756.91

current_value = btc_holdings * btc_price
investment = btc_holdings * avg_entry
pnl = current_value - investment
pnl_percent = (pnl / investment) * 100

stop_loss_price = avg_entry * 0.95
take_profit_price = avg_entry * 1.10

distance_to_stop = ((btc_price - stop_loss_price) / stop_loss_price) * 100
distance_to_take = ((take_profit_price - btc_price) / btc_price) * 100

print(f'Current BTC Price: ${btc_price:,}')
print(f'BTC Holdings: {btc_holdings:.8f} BTC')
print(f'Average Entry Price: ${avg_entry:,.2f}')
print(f'Current Value: ${current_value:.2f}')
print(f'Investment: ${investment:.2f}')
print(f'Current P&L: ${pnl:.2f} ({pnl_percent:.2f}%)')
print(f'Stop-Loss Price (5%): ${stop_loss_price:.2f}')
print(f'Take-Profit Price (10%): ${take_profit_price:.2f}')
print(f'Distance to Stop-Loss: {distance_to_stop:.2f}% buffer')
print(f'Distance to Take-Profit: {distance_to_take:.2f}% needed')