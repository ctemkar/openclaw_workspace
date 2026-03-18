import json
from datetime import datetime

# Sample data from API (truncated for analysis)
data = {
    'status': 'STOPPED',
    'strategies': {},
    'timestamp': '12:46:37',
    'trades': [
        {'amount': 0.00013472197560616131, 'model': 'Gemini-Pro', 'price': 74226.94, 'side': 'buy', 'status': 'filled', 'time': '11:43:17'},
        {'amount': 0.0001346542375419246, 'model': 'Gemini-Pro', 'price': 74264.28, 'side': 'buy', 'status': 'filled', 'time': '11:40:15'},
        {'amount': 0.0001346910913695875, 'model': 'Gemini-Pro', 'price': 74243.96, 'side': 'buy', 'status': 'filled', 'time': '11:34:59'},
        {'amount': 0.0001346910913695875, 'model': 'Gemini-Pro', 'price': 74243.96, 'side': 'buy', 'status': 'filled', 'time': '11:34:59'},
        {'amount': 0.0001346910913695875, 'model': 'Gemini-Pro', 'price': 74243.96, 'side': 'buy', 'status': 'filled', 'time': '11:34:59'},
        {'amount': 0.0001346910913695875, 'model': 'Gemini-Pro', 'price': 74243.96, 'side': 'buy', 'status': 'filled', 'time': '11:34:58'},
        {'amount': 0.00013465197110961168, 'model': 'Gemini-Pro', 'price': 74265.53, 'side': 'buy', 'status': 'filled', 'time': '11:31:37'},
        {'amount': 0.0001346409120144529, 'model': 'Gemini-Pro', 'price': 74271.63, 'side': 'buy', 'status': 'filled', 'time': '11:31:36'},
        {'amount': 0.0001346409120144529, 'model': 'Gemini-Pro', 'price': 74271.63, 'side': 'buy', 'status': 'filled', 'time': '11:31:36'},
        {'amount': 0.00013468022537388915, 'model': 'Gemini-Pro', 'price': 74249.95, 'side': 'buy', 'status': 'filled', 'time': '11:31:01'},
        {'amount': 0.00013464430206856735, 'model': 'Gemini-Pro', 'price': 74269.76, 'side': 'buy', 'status': 'filled', 'time': '11:30:55'},
        {'amount': 0.00013443133260973428, 'model': 'Gemini-Pro', 'price': 74387.42, 'side': 'buy', 'status': 'filled', 'time': '11:24:15'},
        {'amount': 0.00013443133260973428, 'model': 'Gemini-Pro', 'price': 74387.42, 'side': 'buy', 'status': 'filled', 'time': '11:24:13'},
        {'amount': 0.00013443133260973428, 'model': 'Gemini-Pro', 'price': 74387.42, 'side': 'buy', 'status': 'filled', 'time': '11:24:12'},
        {'amount': 0.00013429759002974692, 'model': 'Gemini-Pro', 'price': 74461.5, 'side': 'buy', 'status': 'filled', 'time': '11:20:49'},
        {'amount': 0.00013443057359912588, 'model': 'Gemini-Pro', 'price': 74387.84, 'side': 'buy', 'status': 'filled', 'time': '11:19:07'},
        {'amount': 0.00013440750015356056, 'model': 'Gemini-Pro', 'price': 74400.61, 'side': 'buy', 'status': 'filled', 'time': '11:19:03'},
        {'amount': 0.00013429757199390666, 'model': 'Gemini-Pro', 'price': 74461.51, 'side': 'buy', 'status': 'filled', 'time': '11:13:18'},
        {'amount': 0.00013423458433254202, 'model': 'Gemini-Pro', 'price': 74496.45, 'side': 'buy', 'status': 'filled', 'time': '10:55:40'},
        {'amount': 0.00013423458433254202, 'model': 'Gemini-Pro', 'price': 74496.45, 'side': 'buy', 'status': 'filled', 'time': '10:55:40'},
        {'amount': 0.00013409359035319984, 'model': 'Gemini-Pro', 'price': 74574.78, 'side': 'buy', 'status': 'filled', 'time': '10:32:34'},
        {'amount': 0.00013409359035319984, 'model': 'Gemini-Pro', 'price': 74574.78, 'side': 'buy', 'status': 'filled', 'time': '10:32:34'},
        {'amount': 0.0042721167484065, 'model': 'GPT-4o', 'price': 2340.76, 'side': 'sell', 'status': 'filled', 'time': '10:30:02'},
        {'amount': 0.00013415255828928659, 'model': 'Gemini-Pro', 'price': 74542.0, 'side': 'buy', 'status': 'filled', 'time': '10:30:01'},
        {'amount': 0.00013415255828928659, 'model': 'Gemini-Pro', 'price': 74542.0, 'side': 'buy', 'status': 'filled', 'time': '10:30:01'},
        {'amount': 0.10477018659570232, 'model': 'LLM_Analysis_SOL_USD', 'price': 95.447, 'side': 'sell', 'status': 'filled', 'time': '10:29:40'},
        {'amount': 0.004271751759961725, 'model': 'LLM_Analysis_ETH_USD', 'price': 2340.96, 'side': 'buy', 'status': 'filled', 'time': '10:29:39'},
        {'amount': 0.00013410761707125595, 'model': 'LLM_Analysis_BTC_USD', 'price': 74566.98, 'side': 'buy', 'status': 'filled', 'time': '10:29:38'},
        {'amount': 0.004271660522594948, 'model': 'GPT-4o', 'price': 2341.01, 'side': 'sell', 'status': 'filled', 'time': '10:29:18'},
        {'amount': 0.00013410761707125595, 'model': 'Gemini-Pro', 'price': 74566.98, 'side': 'buy', 'status': 'filled', 'time': '10:29:17'},
        {'amount': 0.004270383608559557, 'model': 'GPT-4o', 'price': 2341.71, 'side': 'sell', 'status': 'filled', 'time': '10:29:10'},
        {'amount': 0.00013410268940261544, 'model': 'Gemini-Pro', 'price': 74569.72, 'side': 'buy', 'status': 'filled', 'time': '10:29:10'},
        {'amount': 0.10487237032531409, 'model': 'LLM_Analysis_SOL_USD', 'price': 95.354, 'side': 'sell', 'status': 'filled', 'time': '10:24:24'},
        {'amount': 0.004276062601556487, 'model': 'LLM_Analysis_ETH_USD', 'price': 2338.6, 'side': 'buy', 'status': 'filled', 'time': '10:24:23'},
        {'amount': 0.00013422400805773564, 'model': 'LLM_Analysis_BTC_USD', 'price': 74502.32, 'side': 'buy', 'status': 'filled', 'time': '10:24:23'},
        {'amount': 0.00013449899125756557, 'model': 'Gemini', 'price': 74350.0, 'side': 'buy', 'status': 'filled', 'time': '10:22:36'},
        {'amount': 0.00013449906361751908, 'model': 'Gemini', 'price': 74349.96, 'side': 'buy', 'status': 'filled', 'time': '10:22:30'},
        {'amount': 0.0001345158351368544, 'model': 'Gemini', 'price': 74340.69, 'side': 'buy', 'status': 'filled', 'time': '10:22:25'},
        {'amount': 0.00013451550943646476, 'model': 'Gemini', 'price': 74340.87, 'side': 'buy', 'status': 'filled', 'time': '10:22:09'},
        {'amount': 0.00013453282802803126, 'model': 'Gemini', 'price': 74331.3, 'side': 'buy', 'status': 'filled', 'time': '10:22:04'},
        {'amount': 0.0001345308371584935, 'model': 'Gemini', 'price': 74332.4, 'side': 'buy', 'status': 'filled', 'time': '10:21:59'},
        {'amount': 0.0001345424755304236, 'model': 'Gemini', 'price': 74325.97, 'side': 'buy', 'status': 'filled', 'time': '10:21:34'},
        {'amount': 0.00013452624028485123, 'model': 'Gemini', 'price': 74334.94, 'side': 'buy', 'status': 'filled', 'time': '10:21:28'},
        {'amount': 0.10531637037661135, 'model': 'LLM_Analysis_SOL_USD', 'price': 94.952, 'side': 'sell', 'status': 'filled', 'time': '10:21:23'},
        {'amount': 0.00428856924752764, 'model': 'LLM_Analysis_ETH_USD', 'price': 2331.78, 'side': 'buy', 'status': 'filled', 'time': '10:21:22'},
        {'amount': 0.0001345244667719186, 'model': 'LLM_Analysis_BTC_USD', 'price': 74335.92, 'side': 'buy', 'status': 'filled', 'time': '10:21:21'},
        {'amount': 0.0001345750121117511, 'model': 'Gemini', 'price': 74308.0, 'side': 'buy', 'status': 'filled', 'time': '10:20:26'},
        {'amount': 0.00013457358140268468, 'model': 'Gemini', 'price': 74308.79, 'side': 'buy', 'status': 'filled', 'time': '10:18:29'},
        {'amount': 0.00013453038469636157, 'model': 'Gemini', 'price': 74332.65, 'side': 'buy', 'status': 'filled', 'time': '10:14:36'},
        {'amount': 0.00013455424265000813, 'model': 'Gemini', 'price': 74319.47, 'side': 'buy', 'status': 'filled', 'time': '10:14:33'}
    ]
}

trades = data['trades']
total_trades = len(trades)
buy_trades = sum(1 for t in trades if t['side'] == 'buy')
sell_trades = sum(1 for t in trades if t['side'] == 'sell')

# Calculate BTC-specific stats
btc_buys = [t for t in trades if t['side'] == 'buy' and ('BTC' in t.get('model', '') or 'Gemini' in t.get('model', ''))]
btc_sells = [t for t in trades if t['side'] == 'sell' and ('BTC' in t.get('model', '') or 'Gemini' in t.get('model', ''))]

if btc_buys:
    avg_btc_buy_price = sum(t['price'] for t in btc_buys) / len(btc_buys)
else:
    avg_btc_buy_price = 0

# Get latest trade time
latest_time = max(t['time'] for t in trades) if trades else 'N/A'

# Calculate time since last trade
current_time = datetime.now().strftime('%H:%M:%S')
if latest_time != 'N/A':
    # Simple time difference calculation
    latest_h, latest_m, latest_s = map(int, latest_time.split(':'))
    current_h, current_m, current_s = map(int, current_time.split(':'))
    
    latest_total = latest_h * 3600 + latest_m * 60 + latest_s
    current_total = current_h * 3600 + current_m * 60 + current_s
    
    if current_total >= latest_total:
        hours_since = (current_total - latest_total) / 3600
    else:
        # Handle cross-day
        hours_since = (24 * 3600 - latest_total + current_total) / 3600
else:
    hours_since = 0

print(f'Total Trades: {total_trades}')
print(f'Buy Trades: {buy_trades}')
print(f'Sell Trades: {sell_trades}')
print(f'Buy/Sell Ratio: {buy_trades}:{sell_trades}')
print(f'BTC Buy Trades: {len(btc_buys)}')
print(f'BTC Sell Trades: {len(btc_sells)}')
print(f'Average BTC Buy Price: ${avg_btc_buy_price:.2f}')
print(f'Latest Trade Time: {latest_time}')
print(f'Hours Since Last Trade: {hours_since:.1f}')
print(f'Current Time: {current_time}')
print(f'Trading Status: {data["status"]}')