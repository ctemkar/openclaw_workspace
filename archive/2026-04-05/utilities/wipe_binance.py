import ccxt
import os
from dotenv import load_dotenv
load_dotenv(override=True)
exchange = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET'),
    'enableRateLimit': True
})
assets = ['USDT', 'USDC']
def run_wipe():
    try:
        balance = exchange.fetch_balance({'type': 'future'})
        for asset in assets:
            amount = balance.get(asset, {}).get('free', 0)
            if amount > 0:
                print(f"Transferring {amount} {asset} from Futures to Spot...")
                exchange.transfer(asset, amount, 'future', 'spot')
            else:
                print(f"No {asset} balance found in Futures.")
    except Exception as e:
        print(f"Error: {e}")
if __name__ == "__main__":
    run_wipe()
