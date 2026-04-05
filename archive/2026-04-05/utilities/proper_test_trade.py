#!/usr/bin/env python3
"""
PROPER TEST TRADE - Small test to verify everything works
"""

import ccxt
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_binance_trade():
    """Test a small Binance trade"""
    logging.info("🔍 TESTING BINANCE TRADE...")
    
    # Load keys
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
        logging.error(f"Error: {e}")
        return
    
    # Initialize Binance
    binance = ccxt.binance({
        'apiKey': keys.get('BINANCE_API_KEY', ''),
        'secret': keys.get('BINANCE_API_SECRET', ''),
        'enableRateLimit': True
    })
    
    try:
        # 1. Check balance PROPERLY
        logging.info("1. Checking balance...")
        balance = binance.fetch_balance()
        
        # Show ALL balances
        logging.info("📊 ALL Balances > 0:")
        for currency, data in balance.items():
            if isinstance(data, dict) and data.get('free', 0) > 0:
                logging.info(f"   {currency}: Free={data['free']}, Total={data['total']}")
        
        usdt = balance.get('USDT', {}).get('free', 0)
        logging.info(f"💰 USDT Balance: ${usdt:.2f}")
        
        # 2. Check MANA price
        logging.info("2. Checking MANA price...")
        ticker = binance.fetch_ticker('MANA/USDT')
        price = ticker['last']
        logging.info(f"   MANA price: ${price:.4f}")
        
        # 3. Calculate SMALL trade amount
        trade_usd = 5.0  # Only $5 for test
        trade_amount = trade_usd / price
        
        logging.info(f"3. Testing with ${trade_usd} trade...")
        logging.info(f"   Amount: {trade_amount:.2f} MANA")
        
        # 4. Check minimum order
        logging.info("4. Checking market info...")
        market = binance.market('MANA/USDT')
        logging.info(f"   Min amount: {market['limits']['amount']['min']}")
        logging.info(f"   Min cost: {market['limits']['cost']['min']}")
        
        if trade_amount < market['limits']['amount']['min']:
            logging.warning(f"   ⚠️ Amount too small! Need at least {market['limits']['amount']['min']}")
            # Adjust to minimum
            trade_amount = market['limits']['amount']['min']
            trade_usd = trade_amount * price
            logging.info(f"   Adjusted to: {trade_amount:.2f} MANA (${trade_usd:.2f})")
        
        # 5. Try test trade if we have enough
        if usdt >= trade_usd:
            logging.info(f"5. Attempting test trade of ${trade_usd:.2f}...")
            
            # Try to create order
            try:
                order = binance.create_market_buy_order('MANA/USDT', trade_amount)
                logging.info(f"   ✅ TEST ORDER CREATED!")
                logging.info(f"   Order ID: {order['id']}")
                logging.info(f"   Amount: {order['amount']}")
                logging.info(f"   Cost: ${order['cost']:.2f}")
                
                # Wait and sell
                time.sleep(2)
                sell_order = binance.create_market_sell_order('MANA/USDT', trade_amount)
                logging.info(f"   ✅ SOLD!")
                logging.info(f"   Profit/Loss: ${float(sell_order['cost']) - float(order['cost']):.2f}")
                
            except Exception as e:
                logging.error(f"   ❌ Order failed: {e}")
        else:
            logging.warning(f"   ⚠️ Insufficient balance for ${trade_usd:.2f} trade")
            
    except Exception as e:
        logging.error(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_binance_trade()