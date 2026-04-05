import requests
import json

try:
    # Get SOL price from CoinGecko
    sol_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd', timeout=5)
    sol_price = sol_response.json()['solana']['usd']
    print(f'Current SOL Price: ${sol_price:.2f}')
    
    # Calculate stop-loss and take-profit levels
    stop_loss = sol_price * 0.961  # 3.9% below
    take_profit = sol_price * 1.04  # 4.0% above
    print(f'Stop-Loss Trigger: ${stop_loss:.2f} ({((sol_price-stop_loss)/sol_price*100):.1f}% below current)')
    print(f'Take-Profit Trigger: ${take_profit:.2f} ({((take_profit-sol_price)/sol_price*100):.1f}% above current)')
    
    # Check status
    if sol_price < stop_loss:
        print('Status: 🔴 STOP-LOSS TRIGGERED')
    elif sol_price > take_profit:
        print('Status: 🟢 TAKE-PROFIT TRIGGERED')
    else:
        print(f'Status: ✅ SAFE (Price between ${stop_loss:.2f} and ${take_profit:.2f})')
        print(f'Distance to Stop-Loss: +${sol_price-stop_loss:.2f} (+{((sol_price-stop_loss)/sol_price*100):.1f}%)')
        print(f'Distance to Take-Profit: -${take_profit-sol_price:.2f} (-{((take_profit-sol_price)/sol_price*100):.1f}%)')
except Exception as e:
    print(f'Error fetching market data: {e}')