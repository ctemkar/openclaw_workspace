#!/usr/bin/env python3
# Current prices from latest analysis
btc_current = 71435.40
eth_current = 2194.74

# Latest buy prices from trades
btc_buy = 73990.75  # From 15:05:29 trade
eth_buy = 2331.78   # From 10:21:22 trade

# Calculate drawdowns
btc_drawdown = (btc_current - btc_buy) / btc_buy * 100
eth_drawdown = (eth_current - eth_buy) / eth_buy * 100

# Stop-loss thresholds (5%)
stop_loss_threshold = 5.0
btc_stop_price = btc_buy * (1 - stop_loss_threshold/100)
eth_stop_price = eth_buy * (1 - stop_loss_threshold/100)

# Distance to stop-loss
btc_distance = btc_current - btc_stop_price
eth_distance = eth_current - eth_stop_price

print('=== CURRENT MARKET ANALYSIS ===')
print('Time: 2026-03-18 21:57 (Asia/Bangkok)')
print()
print('BTC/USD:')
print(f'  Current price: ${btc_current:,.2f}')
print(f'  Recent buy price: ${btc_buy:,.2f} (15:05:29)')
print(f'  Current drawdown: {btc_drawdown:.2f}%')
print(f'  Stop-loss threshold: {stop_loss_threshold}%')
print(f'  Stop-loss trigger price: ${btc_stop_price:,.2f}')
print(f'  Distance to stop-loss: ${btc_distance:,.2f}')
btc_below_support = ((btc_current - 72009.20)/72009.20*100)
print(f'  Support level: $72,009.20 (current: ${btc_current:,.2f} - {btc_below_support:.2f}% below)')
print()
print('ETH/USD:')
print(f'  Current price: ${eth_current:,.2f}')
print(f'  Recent buy price: ${eth_buy:,.2f} (10:21:22)')
print(f'  Current drawdown: {eth_drawdown:.2f}%')
print(f'  Stop-loss threshold: {stop_loss_threshold}%')
print(f'  Stop-loss trigger price: ${eth_stop_price:,.2f}')
print(f'  Distance to stop-loss: ${eth_distance:,.2f}')
eth_below_support = ((eth_current - 2225.00)/2225.00*100)
print(f'  Support level: $2,225.00 (current: ${eth_current:,.2f} - {eth_below_support:.2f}% below)')
print()
print('=== RISK ASSESSMENT ===')
if eth_drawdown <= -4.9:
    print('🚨🚨🚨 CRITICAL: ETH/USD AT IMMINENT STOP-LOSS TRIGGER 🚨🚨🚨')
elif eth_drawdown <= -4.5:
    print('🚨 HIGH ALERT: ETH/USD APPROACHING STOP-LOSS')
elif eth_drawdown <= -4.0:
    print('⚠️ WARNING: ETH/USD SHOWING SIGNIFICANT DRAWDOWN')
    
if btc_drawdown <= -4.5:
    print('🚨 HIGH ALERT: BTC/USD APPROACHING STOP-LOSS')
elif btc_drawdown <= -3.5:
    print('⚠️ WARNING: BTC/USD SHOWING SIGNIFICANT DRAWDOWN')