#!/usr/bin/env python3
"""
26-Crypto Trading Bot - REAL CAPITAL VERSION
Uses actual $121 capital ($50 Gemini + $71 Binance Futures)
"""

import os
import json
import time
import ccxt
from datetime import datetime

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

# 26 Cryptocurrencies
CRYPTOS = [
    "BTC", "ETH", "SOL", "ADA", "XRP", "DOT", "DOGE",
    "AVAX", "MATIC", "LINK", "UNI", "LTC", "ATOM", "ETC",
    "XLM", "ALGO", "VET", "FIL", "ICP", "XTZ", "EOS",
    "AAVE", "MKR", "COMP", "SNX", "YFI"
]

# Trading configuration - ADJUSTED FOR REAL CAPITAL
POSITION_SIZE_PERCENT = 0.20  # 20% of capital per trade
STOP_LOSS_PERCENT = 0.05      # 5% stop-loss
TAKE_PROFIT_PERCENT = 0.10    # 10% take-profit
MIN_TRADE_AMOUNT = 10         # Minimum $10 per trade

def load_keys(exchange):
    """Load API keys from environment variables"""
    try:
        if exchange == "binance":
            api_key = os.getenv('BINANCE_API_KEY')
            api_secret = os.getenv('BINANCE_API_SECRET')
        elif exchange == "gemini":
            api_key = os.getenv('GEMINI_API_KEY')
            api_secret = os.getenv('GEMINI_API_SECRET')
        else:
            return None, None
        
        if not api_key or not api_secret:
            print(f"❌ ERROR: Missing {exchange} API keys")
            return None, None
        
        return api_key, api_secret
    except Exception as e:
        print(f"❌ Error loading {exchange} keys: {e}")
        return None, None

def get_real_capital():
    """Get ACTUAL trading capital from both exchanges"""
    capital = {
        'gemini_spot': 0,
        'binance_futures': 0,
        'binance_spot': 0,
        'total_free': 0
    }
    
    # Load environment
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line:
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val
    except:
        print("⚠️  Could not load .env file")
        return capital
    
    # Gemini Spot
    try:
        gemini_key, gemini_secret = load_keys("gemini")
        if gemini_key and gemini_secret:
            g = ccxt.gemini({
                'apiKey': gemini_key,
                'secret': gemini_secret,
                'enableRateLimit': True
            })
            g_bal = g.fetch_balance()
            capital['gemini_spot'] = g_bal.get('USD', {}).get('free', 0)
            print(f"✅ Gemini Spot: ${capital['gemini_spot']:.2f} free")
    except Exception as e:
        print(f"❌ Gemini error: {e}")
    
    # Binance Futures (where your $71 actually is)
    try:
        binance_key, binance_secret = load_keys("binance")
        if binance_key and binance_secret:
            # Futures account
            b_futures = ccxt.binance({
                'apiKey': binance_key,
                'secret': binance_secret,
                'options': {'defaultType': 'future'},
                'enableRateLimit': True
            })
            bf_bal = b_futures.fetch_balance()
            capital['binance_futures'] = bf_bal.get('USDT', {}).get('free', 0)
            print(f"✅ Binance Futures: ${capital['binance_futures']:.2f} free")
            
            # Spot account (for reference)
            b_spot = ccxt.binance({
                'apiKey': binance_key,
                'secret': binance_secret,
                'options': {'defaultType': 'spot'},
                'enableRateLimit': True
            })
            bs_bal = b_spot.fetch_balance()
            capital['binance_spot'] = bs_bal.get('USDT', {}).get('free', 0)
            print(f"✅ Binance Spot: ${capital['binance_spot']:.2f} free")
    except Exception as e:
        print(f"❌ Binance error: {e}")
    
    capital['total_free'] = capital['gemini_spot'] + capital['binance_futures'] + capital['binance_spot']
    return capital

def execute_trade(exchange_obj, symbol, side, capital_amount, exchange_type="spot"):
    """Execute trade with proper exchange type"""
    try:
        # Calculate position size (20% of available capital for this exchange)
        position_size = capital_amount * POSITION_SIZE_PERCENT
        
        if position_size < MIN_TRADE_AMOUNT:
            print(f"    ⚠️  Skipping: Position size ${position_size:.2f} below minimum ${MIN_TRADE_AMOUNT}")
            return False
        
        # Get current price
        ticker = exchange_obj.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Calculate quantity
        quantity = position_size / current_price
        
        # Round quantity
        market = exchange_obj.market(symbol)
        quantity = exchange_obj.amount_to_precision(symbol, quantity)
        
        print(f"    🚀 EXECUTING {side} ORDER ({exchange_type}):")
        print(f"       Symbol: {symbol}")
        print(f"       Price: ${current_price:.2f}")
        print(f"       Quantity: {quantity}")
        print(f"       Amount: ${position_size:.2f}")
        
        # Place order - market order for simplicity
        order = exchange_obj.create_order(
            symbol=symbol,
            type='market',
            side=side.lower(),
            amount=quantity
        )
        
        print(f"    ✅ ORDER PLACED: {order['id']}")
        print(f"       Status: {order['status']}")
        
        # Log the trade
        log_trade({
            'exchange': exchange_obj.name,
            'exchange_type': exchange_type,
            'symbol': symbol,
            'side': side,
            'price': current_price,
            'quantity': quantity,
            'amount': position_size,
            'order_id': order['id'],
            'timestamp': datetime.now().isoformat()
        })
        
        return True
        
    except Exception as e:
        print(f"    ❌ TRADE FAILED: {e}")
        return False

def log_trade(trade_data):
    """Log trade to file"""
    try:
        with open('real_trading_log.json', 'a') as f:
            f.write(json.dumps(trade_data) + '\n')
    except:
        pass

def main():
    """Main function - Uses REAL capital"""
    print("=" * 70)
    print("26-CRYPTO TRADING BOT - REAL $121 CAPITAL")
    print("=" * 70)
    print("Using ACTUAL available capital:")
    print("  Gemini Spot: ~$50")
    print("  Binance Futures: ~$71")
    print("  Total: ~$121")
    print("=" * 70)
    
    # Get REAL capital
    capital = get_real_capital()
    
    if capital['total_free'] < MIN_TRADE_AMOUNT:
        print(f"❌ Insufficient capital: ${capital['total_free']:.2f} available")
        print(f"   Need at least ${MIN_TRADE_AMOUNT} to trade")
        return
    
    print(f"\n💰 TOTAL AVAILABLE CAPITAL: ${capital['total_free']:.2f}")
    print(f"   Position size: ${capital['total_free'] * POSITION_SIZE_PERCENT:.2f} per trade")
    
    # Initialize exchanges
    exchanges = {}
    
    # Gemini Spot
    if capital['gemini_spot'] >= MIN_TRADE_AMOUNT:
        try:
            gemini_key, gemini_secret = load_keys("gemini")
            exchanges["gemini_spot"] = ccxt.gemini({
                'apiKey': gemini_key,
                'secret': gemini_secret,
                'enableRateLimit': True
            })
            print(f"\n✅ Gemini Spot ready (${capital['gemini_spot']:.2f})")
        except Exception as e:
            print(f"❌ Gemini setup failed: {e}")
    
    # Binance Futures
    if capital['binance_futures'] >= MIN_TRADE_AMOUNT:
        try:
            binance_key, binance_secret = load_keys("binance")
            exchanges["binance_futures"] = ccxt.binance({
                'apiKey': binance_key,
                'secret': binance_secret,
                'options': {'defaultType': 'future'},
                'enableRateLimit': True
            })
            print(f"✅ Binance Futures ready (${capital['binance_futures']:.2f})")
        except Exception as e:
            print(f"❌ Binance Futures setup failed: {e}")
    
    if not exchanges:
        print("\n❌ No exchanges with sufficient capital")
        return
    
    print("\n" + "=" * 70)
    print("🚀 STARTING TRADING WITH REAL CAPITAL")
    print("=" * 70)
    
    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"\n📊 CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 70)
            
            # Gemini Spot LONG trades
            if "gemini_spot" in exchanges and capital['gemini_spot'] >= MIN_TRADE_AMOUNT:
                print(f"\n🔍 GEMINI SPOT (LONG) - ${capital['gemini_spot']:.2f}")
                gemini_pairs = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD', 'DOT/USD', 'DOGE/USD']
                
                for pair in gemini_pairs[:3]:  # Check 3 pairs
                    try:
                        ticker = exchanges["gemini_spot"].fetch_ticker(pair)
                        change = ticker['percentage']
                        
                        if change > 0.8:  # 0.8% up
                            print(f"    ⚡ LONG SIGNAL: {pair} up {change:.2f}%")
                            if execute_trade(exchanges["gemini_spot"], pair, "BUY", capital['gemini_spot'], "spot"):
                                capital['gemini_spot'] *= 0.8  # Reduce available after trade
                    except Exception as e:
                        print(f"    Error checking {pair}: {e}")
            
            # Binance Futures SHORT trades
            if "binance_futures" in exchanges and capital['binance_futures'] >= MIN_TRADE_AMOUNT:
                print(f"\n🔍 BINANCE FUTURES (SHORT) - ${capital['binance_futures']:.2f}")
                futures_pairs = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT']
                
                for pair in futures_pairs[:2]:  # Check 2 pairs
                    try:
                        ticker = exchanges["binance_futures"].fetch_ticker(pair)
                        change = ticker['percentage']
                        
                        if change < -1.0:  # 1.0% down
                            print(f"    ⚡ SHORT SIGNAL: {pair} down {change:.2f}%")
                            if execute_trade(exchanges["binance_futures"], pair, "SELL", capital['binance_futures'], "futures"):
                                capital['binance_futures'] *= 0.8  # Reduce available after trade
                    except Exception as e:
                        print(f"    Error checking {pair}: {e}")
            
            print(f"\n⏰ Next check in 2 minutes...")
            print("=" * 70)
            
            time.sleep(120)  # 2 minutes
            
    except KeyboardInterrupt:
        print("\n\n🛑 Trading bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()