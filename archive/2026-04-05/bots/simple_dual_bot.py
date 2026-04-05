#!/usr/bin/env python3
"""
SIMPLE Dual-Exchange Trading Bot
- Uses your $572 Gemini + $72 Binance
- Actually trades with real money
"""

import ccxt
import time
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_dual_trading.log'),
        logging.StreamHandler()
    ]
)

def load_api_keys():
    """Load API keys from .env"""
    keys = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        keys[key.strip()] = value.strip()
    except Exception as e:
        logging.error(f"Error reading .env: {e}")
    
    return keys

def main():
    logging.info("🚀 STARTING SIMPLE DUAL-EXCHANGE BOT")
    logging.info("💰 YOU HAVE: $572 Gemini + $72 Binance = $644 TOTAL")
    
    # Load API keys
    keys = load_api_keys()
    
    # Initialize exchanges
    gemini = ccxt.gemini({
        'apiKey': keys.get('GEMINI_API_KEY', ''),
        'secret': keys.get('GEMINI_API_SECRET', ''),
        'enableRateLimit': True
    })
    
    binance = ccxt.binance({
        'apiKey': keys.get('BINANCE_API_KEY', ''),
        'secret': keys.get('BINANCE_API_SECRET', ''),
        'enableRateLimit': True
    })
    
    # Check balances
    try:
        gemini_balance = gemini.fetch_balance()
        gemini_usd = gemini_balance.get('USD', {}).get('free', 0)
        logging.info(f"💰 Gemini Balance: ${gemini_usd:.2f} USD")
        
        binance_balance = binance.fetch_balance()
        binance_usdt = binance_balance.get('USDT', {}).get('free', 0)
        logging.info(f"💰 Binance Balance: ${binance_usdt:.2f} USDT")
    except Exception as e:
        logging.error(f"❌ Balance check error: {e}")
        return
    
    # Trading parameters
    min_spread = 0.4  # 0.4%
    gemini_trade = 50.0  # $50 from Gemini
    binance_trade = 20.0  # $20 from Binance
    min_profit = 0.15  # $0.15
    
    cryptos = ['MANA', 'ARB', 'GALA', 'BTC', 'ETH', 'SOL']
    
    trade_count = 0
    total_profit = 0.0
    
    logging.info(f"📊 Trading: {len(cryptos)} cryptos, min spread {min_spread}%")
    
    while True:
        try:
            trade_count += 1
            logging.info(f"🔍 Scan #{trade_count}")
            
            # Check each crypto
            for crypto in cryptos:
                try:
                    # Get prices
                    gemini_price = gemini.fetch_ticker(f"{crypto}/USD")['last']
                    binance_price = binance.fetch_ticker(f"{crypto}/USDT")['last']
                    
                    # Calculate spread
                    spread = ((gemini_price - binance_price) / binance_price) * 100
                    
                    # Determine direction
                    if gemini_price > binance_price:
                        # Buy Binance, Sell Gemini
                        direction = "BUY_BINANCE_SELL_GEMINI"
                        trade_size = binance_trade
                        buy_price = binance_price
                        sell_price = gemini_price
                        buy_exchange = binance
                        sell_exchange = gemini
                        buy_symbol = f"{crypto}/USDT"
                        sell_symbol = f"{crypto}/USD"
                        available = binance_usdt
                    else:
                        # Buy Gemini, Sell Binance
                        direction = "BUY_GEMINI_SELL_BINANCE"
                        trade_size = gemini_trade
                        buy_price = gemini_price
                        sell_price = binance_price
                        buy_exchange = gemini
                        sell_exchange = binance
                        buy_symbol = f"{crypto}/USD"
                        sell_symbol = f"{crypto}/USDT"
                        available = gemini_usd
                    
                    # Calculate profit
                    gross_profit = trade_size * (abs(spread) / 100)
                    fees = trade_size * 0.002
                    net_profit = gross_profit - fees
                    
                    if abs(spread) >= min_spread and net_profit >= min_profit and available >= trade_size:
                        logging.info(f"🎯 {crypto}: {abs(spread):.2f}% spread = ${net_profit:.2f} profit")
                        logging.info(f"   Strategy: {direction}")
                        
                        # Execute trade
                        try:
                            # Calculate amount
                            buy_amount = trade_size / buy_price
                            
                            logging.info(f"   📈 Buying {buy_amount:.6f} {crypto}...")
                            buy_order = buy_exchange.create_market_buy_order(buy_symbol, buy_amount)
                            
                            time.sleep(2)
                            
                            logging.info(f"   📉 Selling {buy_amount:.6f} {crypto}...")
                            sell_order = sell_exchange.create_market_sell_order(sell_symbol, buy_amount)
                            
                            # Calculate actual profit
                            actual_profit = sell_order['cost'] - buy_order['cost']
                            total_profit += actual_profit
                            
                            logging.info(f"   🎉 TRADE COMPLETE! Profit: ${actual_profit:.2f}")
                            logging.info(f"   📈 Total profit: ${total_profit:.2f}")
                            
                            # Update balance
                            if direction == "BUY_BINANCE_SELL_GEMINI":
                                binance_usdt -= trade_size
                                gemini_usd += trade_size + actual_profit
                            else:
                                gemini_usd -= trade_size
                                binance_usdt += trade_size + actual_profit
                            
                            # Wait before next trade
                            time.sleep(10)
                            
                        except Exception as e:
                            logging.error(f"   ❌ Trade failed: {e}")
                    
                except Exception as e:
                    logging.debug(f"   Can't check {crypto}: {e}")
            
            # Wait between scans
            time.sleep(30)
            
        except KeyboardInterrupt:
            logging.info("🛑 Bot stopped by user")
            break
        except Exception as e:
            logging.error(f"❌ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()