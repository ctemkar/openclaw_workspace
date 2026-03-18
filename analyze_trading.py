import json
from datetime import datetime

# Current time
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Sample data analysis
data = {'status': 'STOPPED', 'strategies': {}, 'timestamp': '13:24:46', 'trades': [{'amount': 0.00013472197560616131, 'model': 'Gemini-Pro', 'price': 74226.94, 'side': 'buy', 'status': 'filled', 'time': '11:43:17'}, {'amount': 0.0001346542375419246, 'model': 'Gemini-Pro', 'price': 74264.28, 'side': 'buy', 'status': 'filled', 'time': '11:40:15'}, {'amount': 0.0001346910913695875, 'model': 'Gemini-Pro', 'price': 74243.96, 'side': 'buy', 'status': 'filled', 'time': '11:34:59'}, {'amount': 0.0001346910913695875, 'model': 'Gemini-Pro', 'price': 74243.96, 'side': 'buy', 'status': 'filled', 'time': '11:34:59'}, {'amount': 0.0001346910913695875, 'model': 'Gemini-Pro', 'price': 74243.96, 'side': 'buy', 'status': 'filled', 'time': '11:34:59'}, {'amount': 0.0001346910913695875, 'model': 'Gemini-Pro', 'price': 74243.96, 'side': 'buy', 'status': 'filled', 'time': '11:34:58'}, {'amount': 0.00013465197110961168, 'model': 'Gemini-Pro', 'price': 74265.53, 'side': 'buy', 'status': 'filled', 'time': '11:31:37'}, {'amount': 0.0001346409120144529, 'model': 'Gemini-Pro', 'price': 74271.63, 'side': 'buy', 'status': 'filled', 'time': '11:31:36'}, {'amount': 0.0001346409120144529, 'model': 'Gemini-Pro', 'price': 74271.63, 'side': 'buy', 'status': 'filled', 'time': '11:31:36'}, {'amount': 0.00013468022537388915, 'model': 'Gemini-Pro', 'price': 74249.95, 'side': 'buy', 'status': 'filled', 'time': '11:31:01'}, {'amount': 0.00013464430206856735, 'model': 'Gemini-Pro', 'price': 74269.76, 'side': 'buy', 'status': 'filled', 'time': '11:30:55'}, {'amount': 0.00013443133260973428, 'model': 'Gemini-Pro', 'price': 74387.42, 'side': 'buy', 'status': 'filled', 'time': '11:24:15'}, {'amount': 0.00013443133260973428, 'model': 'Gemini-Pro', 'price': 74387.42, 'side': 'buy', 'status': 'filled', 'time': '11:24:13'}, {'amount': 0.00013443133260973428, 'model': 'Gemini-Pro', 'price': 74387.42, 'side': 'buy', 'status': 'filled', 'time': '11:24:12'}, {'amount': 0.00013429759002974692, 'model': 'Gemini-Pro', 'price': 74461.5, 'side': 'buy', 'status': 'filled', 'time': '11:20:49'}, {'amount': 0.00013443057359912588, 'model': 'Gemini-Pro', 'price': 74387.84, 'side': 'buy', 'status': 'filled', 'time': '11:19:07'}, {'amount': 0.00013440750015356056, 'model': 'Gemini-Pro', 'price': 74400.61, 'side': 'buy', 'status': 'filled', 'time': '11:19:03'}, {'amount': 0.00013429757199390666, 'model': 'Gemini-Pro', 'price': 74461.51, 'side': 'buy', 'status': 'filled', 'time': '11:13:18'}, {'amount': 0.00013423458433254202, 'model': 'Gemini-Pro', 'price': 74496.45, 'side': 'buy', 'status': 'filled', 'time': '10:55:40'}, {'amount': 0.00013423458433254202, 'model': 'Gemini-Pro', 'price': 74496.45, 'side': 'buy', 'status': 'filled', 'time': '10:55:40'}, {'amount': 0.00013409359035319984, 'model': 'Gemini-Pro', 'price': 74574.78, 'side': 'buy', 'status': 'filled', 'time': '10:32:34'}, {'amount': 0.00013409359035319984, 'model': 'Gemini-Pro', 'price': 74574.78, 'side': 'buy', 'status': 'filled', 'time': '10:32:34'}, {'amount': 0.0042721167484065, 'model': 'GPT-4o', 'price': 2340.76, 'side': 'sell', 'status': 'filled', 'time': '10:30:02'}, {'amount': 0.00013415255828928659, 'model': 'Gemini-Pro', 'price': 74542.0, 'side': 'buy', 'status': 'filled', 'time': '10:30:01'}, {'amount': 0.00013415255828928659, 'model': 'Gemini-Pro', 'price': 74542.0, 'side': 'buy', 'status': 'filled', 'time': '10:30:01'}, {'amount': 0.10477018659570232, 'model': 'LLM_Analysis_SOL_USD', 'price': 95.447, 'side': 'sell', 'status': 'filled', 'time': '10:29:40'}, {'amount': 0.004271751759961725, 'model': 'LLM_Analysis_ETH_USD', 'price': 2340.96, 'side': 'buy', 'status': 'filled', 'time': '10:29:39'}, {'amount': 0.00013410761707125595, 'model': 'LLM_Analysis_BTC_USD', 'price': 74566.98, 'side': 'buy', 'status': 'filled', 'time': '10:29:38'}, {'amount': 0.004271660522594948, 'model': 'GPT-4o', 'price': 2341.01, 'side': 'sell', 'status': 'filled', 'time': '10:29:18'}, {'amount': 0.00013410761707125595, 'model': 'Gemini-Pro', 'price': 74566.98, 'side': 'buy', 'status': 'filled', 'time': '10:29:17'}, {'amount': 0.004270383608559557, 'model': 'GPT-4o', 'price': 2341.71, 'side': 'sell', 'status': 'filled', 'time': '10:29:10'}, {'amount': 0.00013410268940261544, 'model': 'Gemini-Pro', 'price': 74569.72, 'side': 'buy', 'status': 'filled', 'time': '10:29:10'}, {'amount': 0.10487237032531409, 'model': 'LLM_Analysis_SOL_USD', 'price': 95.354, 'side': 'sell', 'status': 'filled', 'time': '10:24:24'}, {'amount': 0.004276062601556487, 'model': 'LLM_Analysis_ETH_USD', 'price': 2338.6, 'side': 'buy', 'status': 'filled', 'time': '10:24:23'}, {'amount': 0.00013422400805773564, 'model': 'LLM_Analysis_BTC_USD', 'price': 74502.32, 'side': 'buy', 'status': 'filled', 'time': '10:24:23'}, {'amount': 0.00013449899125756557, 'model': 'Gemini', 'price': 74350.0, 'side': 'buy', 'status': 'filled', 'time': '10:22:36'}, {'amount': 0.00013449906361751908, 'model': 'Gemini', 'price': 74349.96, 'side': 'buy', 'status': 'filled', 'time': '10:22:30'}, {'amount': 0.0001345158351368544, 'model': 'Gemini', 'price': 74340.69, 'side': 'buy', 'status': 'filled', 'time': '10:22:25'}, {'amount': 0.00013451550943646476, 'model': 'Gemini', 'price': 74340.87, 'side': 'buy', 'status': 'filled', 'time': '10:22:09'}, {'amount': 0.00013453282802803126, 'model': 'Gemini', 'price': 74331.3, 'side': 'buy', 'status': 'filled', 'time': '10:22:04'}, {'amount': 0.0001345308371584935, 'model': 'Gemini', 'price': 74332.4, 'side': 'buy', 'status': 'filled', 'time': '10:21:59'}, {'amount': 0.0001345424755304236, 'model': 'Gemini', 'price': 74325.97, 'side': 'buy', 'status': 'filled', 'time': '10:21:34'}, {'amount': 0.00013452624028485123, 'model': 'Gemini', 'price': 74334.94, 'side': 'buy', 'status': 'filled', 'time': '10:21:28'}, {'amount': 0.10531637037661135, 'model': 'LLM_Analysis_SOL_USD', 'price': 94.952, 'side': 'sell', 'status': 'filled', 'time': '10:21:23'}, {'amount': 0.00428856924752764, 'model': 'LLM_Analysis_ETH_USD', 'price': 2331.78, 'side': 'buy', 'status': 'filled', 'time': '10:21:22'}, {'amount': 0.0001345244667719186, 'model': 'LLM_Analysis_BTC_USD', 'price': 74335.92, 'side': 'buy', 'status': 'filled', 'time': '10:21:21'}, {'amount': 0.0001345750121117511, 'model': 'Gemini', 'price': 74308.0, 'side': 'buy', 'status': 'filled', 'time': '10:20:26'}, {'amount': 0.00013457358140268468, 'model': 'Gemini', 'price': 74308.79, 'side': 'buy', 'status': 'filled', 'time': '10:18:29'}, {'amount': 0.00013453038469636157, 'model': 'Gemini', 'price': 74332.65, 'side': 'buy', 'status': 'filled', 'time': '10:14:36'}, {'amount': 0.00013455424265000813, 'model': 'Gemini', 'price': 74319.47, 'side': 'buy', 'status': 'filled', 'time': '10:14:33'}]}

trades = data['trades']
total_trades = len(trades)
buy_trades = sum(1 for t in trades if t['side'] == 'buy')
sell_trades = sum(1 for t in trades if t['side'] == 'sell')
btc_trades = sum(1 for t in trades if 'BTC' in t.get('model', ''))
btc_buy_trades = sum(1 for t in trades if 'BTC' in t.get('model', '') and t['side'] == 'buy')
btc_sell_trades = sum(1 for t in trades if 'BTC' in t.get('model', '') and t['side'] == 'sell')

# Calculate buy/sell ratio
buy_sell_ratio = buy_trades / sell_trades if sell_trades > 0 else float('inf')

# Calculate BTC concentration
btc_concentration = btc_trades / total_trades * 100 if total_trades > 0 else 0

# Check for recent trades (last hour)
current_hour = datetime.now().hour
recent_trades = sum(1 for t in trades if int(t['time'].split(':')[0]) >= current_hour - 1)

# Calculate average BTC buy price
btc_buy_prices = [t['price'] for t in trades if 'BTC' in t.get('model', '') and t['side'] == 'buy']
avg_btc_buy_price = sum(btc_buy_prices) / len(btc_buy_prices) if btc_buy_prices else 0

# Model analysis
models = {}
for t in trades:
    model = t['model']
    if model not in models:
        models[model] = {'buys': 0, 'sells': 0, 'total': 0}
    models[model]['total'] += 1
    if t['side'] == 'buy':
        models[model]['buys'] += 1
    else:
        models[model]['sells'] += 1

# Find models with extreme bias
extreme_bias_models = []
for model, stats in models.items():
    total = stats['total']
    if total > 0:
        buy_percent = stats['buys'] / total * 100
        if buy_percent == 100 or buy_percent == 0:
            extreme_bias_models.append((model, buy_percent))

# Generate output
output = []
output.append('=== TRADING DASHBOARD MONITORING ===')
output.append(f'Timestamp: {current_time}')
output.append(f'Dashboard Status: {data["status"]}')
output.append(f'Total Trades: {total_trades}')
output.append(f'Buy Trades: {buy_trades} ({buy_trades/total_trades*100:.1f}%)')
output.append(f'Sell Trades: {sell_trades} ({sell_trades/total_trades*100:.1f}%)')
output.append(f'Buy/Sell Ratio: {buy_sell_ratio:.1f}:1')
output.append(f'BTC Trades: {btc_trades} ({btc_concentration:.1f}% of total)')
output.append(f'BTC Buy Trades: {btc_buy_trades}')
output.append(f'BTC Sell Trades: {btc_sell_trades}')
output.append(f'Recent Trades (last hour): {recent_trades}')
output.append(f'Average BTC Buy Price: ${avg_btc_buy_price:,.2f}')
output.append(f'Models Used: {len(models)}')
for model, stats in models.items():
    output.append(f'  - {model}: {stats["total"]} trades ({stats["buys"]} buys, {stats["sells"]} sells)')
output.append('=== ANALYSIS COMPLETE ===')

print('\n'.join(output))

# Determine if there are critical alerts
critical_alerts = []

# Check for extreme buy bias
if buy_sell_ratio > 5:
    critical_alerts.append(f'EXTREME BUY BIAS: Buy/Sell ratio = {buy_sell_ratio:.1f}:1')

# Check for high BTC concentration
if btc_concentration > 80:
    critical_alerts.append(f'HIGH BTC CONCENTRATION: {btc_concentration:.1f}% of all trades')

# Check for no BTC sell trades
if btc_sell_trades == 0 and btc_buy_trades > 0:
    critical_alerts.append(f'NO BTC SELL TRADES: {btc_buy_trades} buys, 0 sells')

# Check for trading bot stopped
if data['status'] == 'STOPPED':
    critical_alerts.append(f'TRADING BOT STOPPED: No active trading operations')

# Check for extreme model bias
for model, buy_percent in extreme_bias_models:
    if buy_percent == 100:
        critical_alerts.append(f'{model}_EXTREME_BUY_BIAS: 100% buys')
    elif buy_percent == 0:
        critical_alerts.append(f'{model}_EXTREME_SELL_BIAS: 100% sells')

# Check for high trade frequency
if total_trades > 40:
    critical_alerts.append(f'HIGH_TRADE_FREQUENCY: {total_trades} total trades')

# Check for no recent trades (if bot is supposed to be running)
if data['status'] != 'STOPPED' and recent_trades == 0:
    critical_alerts.append(f'NO RECENT TRADES: No trades in the last hour')

print('\n=== CRITICAL ALERTS ===')
if critical_alerts:
    for alert in critical_alerts:
        print(f'ALERT: {alert}')
else:
    print('No critical alerts detected')
print('=== END OF REPORT ===')