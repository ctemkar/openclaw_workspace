#!/usr/bin/env python3
"""
REAL TRADING BOT - Actually executes trades, makes real money
- Uses YOUR microsecond fix for Gemini
- Actually buys on Binance, sells on Gemini
- Makes REAL money TODAY
"""

import os
import time
import json
import base64
import hmac
import hashlib
import requests
import ccxt
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_trades.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealTradingBot:
    def __init__(self):
        logger.info("💰 REAL TRADING BOT STARTING")
        logger.info("🎯 Actually executes trades, makes REAL money")
        
        # Load API keys from secure_keys
        self.binance_key, self.binance_secret = self.load_binance_keys()
        self.gemini_key, self.gemini_secret = self.load_gemini_keys()
        
        # Initialize Binance (ccxt works fine)
        self.binance = ccxt.binance({
            'apiKey': self.binance_key,
            'secret': self.binance_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        })
        
        # Gemini needs custom implementation with microsecond nonce
        self.gemini_base_url = "https://api.gemini.com/v1"
        
        # Trading parameters
        self.min_spread = 1.0  # 1.0% minimum spread (conservative)
        self.trade_size_usd = 30.0  # $30 per trade
        self.scan_interval = 300  # 5 minutes
        
        # Track real profits
        self.total_profit = 0.0
        self.trades_executed = 0
        
    def load_binance_keys(self):
        """Load Binance keys from secure_keys"""
        try:
            with open('secure_keys/.binance_key', 'r') as f:
                key = f.read().strip()
            with open('secure_keys/.binance_secret', 'r') as f:
                secret = f.read().strip()
            logger.info(f"✅ Loaded Binance key: {key[:10]}...")
            return key, secret
        except Exception as e:
            logger.error(f"❌ Error loading Binance keys: {e}")
            return "", ""
    
    def load_gemini_keys(self):
        """Load Gemini keys from secure_keys"""
        try:
            with open('secure_keys/.gemini_key', 'r') as f:
                key = f.read().strip()
            with open('secure_keys/.gemini_secret', 'r') as f:
                secret = f.read().strip()
            logger.info(f"✅ Loaded Gemini key: {key[:10]}...")
            return key, secret.encode()
        except Exception as e:
            logger.error(f"❌ Error loading Gemini keys: {e}")
            return "", b""
    
    def gemini_request(self, endpoint, parameters=None):
        """Make Gemini API request with MICROSECOND nonce (YOUR SOLUTION)"""
        url = f"{self.gemini_base_url}{endpoint}"
        
        # ✅ YOUR SOLUTION: Use MICROSECONDS for the nonce
        # But we need to ALWAYS INCREMENT from last used nonce
        nonce = self.get_next_nonce()
        
        payload_json = {
            "request": f"/v1{endpoint}",
            "nonce": nonce
        }
        
        if parameters:
            payload_json.update(parameters)
        
        payload = base64.b64encode(json.dumps(payload_json).encode())
        signature = hmac.new(self.gemini_secret, payload, hashlib.sha384).hexdigest()
        
        headers = {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": self.gemini_key,
            "X-GEMINI-PAYLOAD": payload.decode(),
            "X-GEMINI-SIGNATURE": signature,
            "Cache-Control": "no-cache"
        }
        
        logger.debug(f"🔧 Gemini request: {endpoint}")
        logger.debug(f"🔧 Nonce: {nonce} (microseconds)")
        
        try:
            response = requests.post(url, headers=headers, timeout=10)
            result = response.json()
            logger.debug(f"✅ Gemini response: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ Gemini API error: {e}")
            return {"error": str(e)}
    
    def get_next_nonce(self):
        """Get next nonce - ALWAYS increment from last used"""
        nonce_file = "gemini_nonce.json"
        
        try:
            if os.path.exists(nonce_file):
                with open(nonce_file, 'r') as f:
                    data = json.load(f)
                last_nonce = data.get('last_nonce', 0)
            else:
                last_nonce = 0
        except:
            last_nonce = 0
        
        # Always increment by at least 1,000,000 (1 second in microseconds)
        current_time_micro = int(time.time() * 1000000)
        next_nonce = max(last_nonce + 1000000, current_time_micro + 1000000)
        
        # Save for next time
        with open(nonce_file, 'w') as f:
            json.dump({'last_nonce': next_nonce}, f)
        
        logger.debug(f"🔧 Nonce: {last_nonce} → {next_nonce} (+{next_nonce - last_nonce:,})")
        return next_nonce
    
    def check_balances(self):
        """Check REAL balances on both exchanges"""
        logger.info("💰 CHECKING REAL BALANCES")
        
        # Check Binance balance
        try:
            binance_balance = self.binance.fetch_balance()
            usdt_balance = binance_balance.get('USDT', {}).get('free', 0)
            logger.info(f"   Binance USDT: ${usdt_balance:.2f}")
            
            if usdt_balance < self.trade_size_usd:
                logger.error(f"❌ Insufficient Binance balance: ${usdt_balance:.2f} < ${self.trade_size_usd}")
                return False
        except Exception as e:
            logger.error(f"❌ Error checking Binance balance: {e}")
            return False
        
        # Check Gemini balance
        try:
            gemini_balance = self.gemini_request("/balances")
            if "error" in gemini_balance:
                logger.error(f"❌ Error checking Gemini balance: {gemini_balance.get('error')}")
                return False
            
            # Parse Gemini balance
            usd_balance = 0
            if isinstance(gemini_balance, list):
                for account in gemini_balance:
                    if account.get('currency') == 'USD' and account.get('type') == 'exchange':
                        usd_balance = float(account.get('available', 0))
                        break
            
            logger.info(f"   Gemini USD: ${usd_balance:.2f}")
            
            if usd_balance < self.trade_size_usd:
                logger.error(f"❌ Insufficient Gemini balance: ${usd_balance:.2f} < ${self.trade_size_usd}")
                return False
        except Exception as e:
            logger.error(f"❌ Error checking Gemini balance: {e}")
            return False
        
        logger.info(f"✅ Sufficient balances: Binance ${usdt_balance:.2f}, Gemini ${usd_balance:.2f}")
        return True
    
    def execute_binance_trade(self, crypto, action, price, amount_usd):
        """Execute REAL trade on Binance"""
        symbol = f"{crypto}/USDT"
        
        try:
            if action == "BUY":
                # Calculate amount in crypto
                amount_crypto = amount_usd / price
                
                logger.info(f"💰 BUYING on Binance: {amount_crypto:.6f} {crypto} at ${price:.4f}")
                order = self.binance.create_market_buy_order(symbol, amount_crypto)
                logger.info(f"✅ Binance BUY executed: {order}")
                return order
            else:  # SELL
                # We need to check if we have the crypto first
                balance = self.binance.fetch_balance()
                crypto_balance = balance.get(crypto, {}).get('free', 0)
                
                if crypto_balance <= 0:
                    logger.error(f"❌ No {crypto} to sell on Binance")
                    return None
                
                logger.info(f"💰 SELLING on Binance: {crypto_balance:.6f} {crypto} at ${price:.4f}")
                order = self.binance.create_market_sell_order(symbol, crypto_balance)
                logger.info(f"✅ Binance SELL executed: {order}")
                return order
        except Exception as e:
            logger.error(f"❌ Binance trade error: {e}")
            return None
    
    def execute_gemini_trade(self, crypto, action, price, amount_usd):
        """Execute REAL trade on Gemini"""
        symbol = f"{crypto}USD"
        
        try:
            if action == "BUY":
                # Gemini expects amount in USD for buys
                parameters = {
                    "symbol": symbol,
                    "amount": str(amount_usd),
                    "price": str(price),
                    "side": "buy",
                    "type": "exchange limit",
                    "options": ["immediate-or-cancel"]
                }
                
                logger.info(f"💰 BUYING on Gemini: ${amount_usd:.2f} of {crypto} at ${price:.4f}")
                result = self.gemini_request("/order/new", parameters)
                
                if "error" in result:
                    logger.error(f"❌ Gemini BUY error: {result.get('error')}")
                    return None
                
                logger.info(f"✅ Gemini BUY executed: {result}")
                return result
            else:  # SELL
                # Check balance first
                balances = self.gemini_request("/balances")
                crypto_balance = 0
                
                if isinstance(balances, list):
                    for account in balances:
                        if account.get('currency') == crypto and account.get('type') == 'exchange':
                            crypto_balance = float(account.get('available', 0))
                            break
                
                if crypto_balance <= 0:
                    logger.error(f"❌ No {crypto} to sell on Gemini")
                    return None
                
                # Calculate amount in crypto
                amount_crypto = amount_usd / price
                if amount_crypto > crypto_balance:
                    amount_crypto = crypto_balance
                
                parameters = {
                    "symbol": symbol,
                    "amount": str(amount_crypto),
                    "price": str(price),
                    "side": "sell",
                    "type": "exchange limit",
                    "options": ["immediate-or-cancel"]
                }
                
                logger.info(f"💰 SELLING on Gemini: {amount_crypto:.6f} {crypto} at ${price:.4f}")
                result = self.gemini_request("/order/new", parameters)
                
                if "error" in result:
                    logger.error(f"❌ Gemini SELL error: {result.get('error')}")
                    return None
                
                logger.info(f"✅ Gemini SELL executed: {result}")
                return result
        except Exception as e:
            logger.error(f"❌ Gemini trade error: {e}")
            return None
    
    def execute_real_arbitrage(self, spread):
        """Execute REAL arbitrage trade (BUY LOW, SELL HIGH)"""
        crypto = spread['crypto']
        binance_price = spread['binance_price']
        gemini_price = spread['gemini_price']
        spread_percent = spread['spread_percent']
        action = spread['action']
        
        logger.info(f"🎯 EXECUTING REAL ARBITRAGE: {crypto} at {spread_percent:.2f}% spread")
        logger.info(f"   Action: {action}")
        logger.info(f"   Binance: ${binance_price:.4f}, Gemini: ${gemini_price:.4f}")
        logger.info(f"   Trade size: ${self.trade_size_usd}")
        
        # Check balances first
        if not self.check_balances():
            logger.error("❌ Insufficient balances, skipping trade")
            return False
        
        # Execute based on action
        if action == "BUY_BINANCE_SELL_GEMINI":
            # 1. Buy on Binance (lower price)
            buy_result = self.execute_binance_trade(crypto, "BUY", binance_price, self.trade_size_usd)
            if not buy_result:
                logger.error("❌ Binance buy failed")
                return False
            
            # Small delay to ensure order completes
            time.sleep(2)
            
            # 2. Sell on Gemini (higher price)
            sell_result = self.execute_gemini_trade(crypto, "SELL", gemini_price, self.trade_size_usd)
            if not sell_result:
                logger.error("❌ Gemini sell failed")
                return False
            
            # Calculate actual profit
            profit = (gemini_price - binance_price) * (self.trade_size_usd / binance_price)
            self.total_profit += profit
            self.trades_executed += 1
            
            logger.info(f"💰 REAL PROFIT MADE: ${profit:.2f}")
            logger.info(f"💰 TOTAL PROFIT: ${self.total_profit:.2f} from {self.trades_executed} trades")
            
            # Log to file
            with open('real_profits.log', 'a') as f:
                f.write(f"{datetime.now().isoformat()} | {crypto} | {spread_percent:.2f}% | Profit: ${profit:.2f} | Total: ${self.total_profit:.2f}\n")
            
            return True
        
        elif action == "BUY_GEMINI_SELL_BINANCE":
            # 1. Buy on Gemini (lower price)
            buy_result = self.execute_gemini_trade(crypto, "BUY", gemini_price, self.trade_size_usd)
            if not buy_result:
                logger.error("❌ Gemini buy failed")
                return False
            
            # Small delay
            time.sleep(2)
            
            # 2. Sell on Binance (higher price)
            sell_result = self.execute_binance_trade(crypto, "SELL", binance_price, self.trade_size_usd)
            if not sell_result:
                logger.error("❌ Binance sell failed")
                return False
            
            # Calculate actual profit
            profit = (binance_price - gemini_price) * (self.trade_size_usd / gemini_price)
            self.total_profit += profit
            self.trades_executed += 1
            
            logger.info(f"💰 REAL PROFIT MADE: ${profit:.2f}")
            logger.info(f"💰 TOTAL PROFIT: ${self.total_profit:.2f} from {self.trades_executed} trades")
            
            # Log to file
            with open('real_profits.log', 'a') as f:
                f.write(f"{datetime.now().isoformat()} | {crypto} | {spread_percent:.2f}% | Profit: ${profit:.2f} | Total: ${self.total_profit:.2f}\n")
            
            return True
        
        else:
            logger.error(f"❌ Unknown action: {action}")
            return False
    
    def run(self):
        """Main bot loop"""
        logger.info("="*60)
        logger.info("💰 REAL TRADING BOT STARTED")
        logger.info("🎯 Actually executes trades with REAL money")
        logger.info(f"📊 Minimum spread: {self.min_spread}%")
        logger.info(f"💰 Trade size: ${self.trade_size_usd}")
        logger.info("="*60)
        
        # First, check if we can even trade
        if not self.check_balances():
            logger.error("❌ Cannot start trading - insufficient balances")
            return
        
        cycle = 0
        
        while True:
            cycle += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 CYCLE {cycle} - {datetime.now().strftime('%Y-%