#!/usr/bin/env python3
"""
GEMINI NUCLEAR FIX - Complete nonce reset
- Starts with FRESH nonce (current time * 1000)
- NO stored nonce file (fresh start)
- 60-second delays between calls
- If this doesn't work, Gemini API is fundamentally broken for us
"""

import ccxt
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gemini_nuclear_fix.log'),
        logging.StreamHandler()
    ]
)

class GeminiNuclearFix:
    def __init__(self):
        logging.info("🚀 GEMINI NUCLEAR FIX INITIALIZED")
        logging.info("💰 COMPLETE nonce reset - Fresh start!")
        
        # Load API keys
        self.keys = self.load_keys()
        
        # Track last call
        self.last_call = 0
        self.min_delay = 60  # 60 seconds to be EXTRA safe
        
        # Initialize Binance
        self.binance = ccxt.binance({
            'apiKey': self.keys.get('BINANCE_API_KEY', ''),
            'secret': self.keys.get('BINANCE_API_SECRET', ''),
            'enableRateLimit': True
        })
        
        # Gemini with NUCLEAR nonce reset
        self.gemini_call_count = 0
        
        self.gemini = ccxt.gemini({
            'apiKey': self.keys.get('GEMINI_API_KEY', ''),
            'secret': self.keys.get('GEMINI_API_SECRET', ''),
            'enableRateLimit': True,
            'nonce': self.get_nuclear_nonce  # FRESH nonce every time
        })
        
        # Simple trading
        self.cryptos = ['MANA']
        
        logging.info("📊 Nuclear Trading: 60s delays, fresh nonce")
    
    def load_keys(self):
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
        return keys
    
    def get_nuclear_nonce(self):
        """NUCLEAR nonce - Fresh start every time"""
        self.gemini_call_count += 1
        current_time = int(time.time() * 1000)
        # Start fresh from current time, add call count
        nuclear_nonce = current_time + (self.gemini_call_count * 1000000)
        logging.debug(f"Nuclear nonce #{self.gemini_call_count}: {nuclear_nonce}")
        return nuclear_nonce
    
    def enforce_nuclear_delay(self):
        """Enforce 60-second delay"""
        current_time = time.time()
        time_since = current_time - self.last_call
        
        if time_since < self.min_delay:
            wait_time = self.min_delay - time_since
            logging.info(f"⏳ Nuclear delay: {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        self.last_call = time.time()
    
    def gemini_nuclear_call(self, func, *args, **kwargs):
        """NUCLEAR Gemini call"""
        try:
            # Enforce 60-second delay
            self.enforce_nuclear_delay()
            
            logging.info(f"🔍 Gemini Nuclear call #{self.gemini_call_count + 1}")
            
            # Execute
            result = func(*args, **kwargs)
            
            return result
            
        except Exception as e:
            logging.error(f"❌ Nuclear call failed: {e}")
            return None
    
    def test_gemini_connection(self):
        """Test if Gemini API works at all"""
        logging.info("🔍 Testing Gemini API connection...")
        
        try:
            # Try simple public call first
            logging.info("   Testing public endpoint...")
            ticker = self.gemini.fetch_ticker('BTC/USD')
            logging.info(f"   ✅ Public API works: BTC = ${ticker['last']:.2f}")
            
            # Try private call with nuclear delay
            logging.info("   Testing private endpoint (60s delay)...")
            time.sleep(60)
            
            balance = self.gemini_nuclear_call(self.gemini.fetch_balance)
            if balance:
                usd = balance.get('USD', {}).get('free', 0)
                logging.info(f"   ✅ Private API works: ${usd:.2f} USD")
                return True
            else:
                logging.error("   ❌ Private API failed")
                return False
                
        except Exception as e:
            logging.error(f"   ❌ API test failed: {e}")
            return False
    
    def check_simple_arbitrage(self):
        """Check simple arbitrage opportunity"""
        try:
            # Get Binance price
            binance_price = self.binance.fetch_ticker('MANA/USDT')['last']
            
            # Get Gemini price with nuclear delay
            gemini_ticker = self.gemini_nuclear_call(self.gemini.fetch_ticker, 'MANA/USD')
            
            if not gemini_ticker:
                return None
            
            gemini_price = gemini_ticker['last']
            
            spread = ((gemini_price - binance_price) / binance_price) * 100
            
            logging.info(f"📊 MANA Spread: {abs(spread):.2f}%")
            logging.info(f"   Gemini: ${gemini_price:.4f}")
            logging.info(f"   Binance: ${binance_price:.4f}")
            
            if abs(spread) > 0.5:
                profit = 30 * (abs(spread)/100) - 0.06
                logging.info(f"   💰 Profit with $30: ${profit:.2f}")
                
                return {
                    'spread': abs(spread),
                    'profit': profit,
                    'gemini_price': gemini_price,
                    'binance_price': binance_price
                }
            
            return None
            
        except Exception as e:
            logging.error(f"❌ Arbitrage check failed: {e}")
            return None
    
    def run(self):
        """Main loop - NUCLEAR FIX"""
        logging.info("=" * 60)
        logging.info("🚀 GEMINI NUCLEAR FIX - COMPLETE RESET")
        logging.info("=" * 60)
        
        # Test connection first
        if not self.test_gemini_connection():
            logging.error("❌❌❌ GEMINI API FUNDAMENTALLY BROKEN ❌❌❌")
            logging.error("   Even Nuclear fix doesn't work")
            logging.error("   Gemini API key might be invalid/expired")
            logging.error("   Or Gemini blocking our IP/region")
            return
        
        logging.info("✅ Gemini API connection established!")
        
        scan_count = 0
        while True:
            try:
                scan_count += 1
                logging.info(f"🔍 Nuclear Scan #{scan_count}")
                
                # Check arbitrage
                opportunity = self.check_simple_arbitrage()
                
                if opportunity:
                    logging.info(f"   🎯 Opportunity: {opportunity['spread']:.2f}% spread")
                    logging.info(f"      Profit: ${opportunity['profit']:.2f}")
                    
                    # For now, just log - actual trading would need balance checks
                    logging.info("   📝 Would execute trade if we had balances")
                else:
                    logging.info("   ⏳ No arbitrage opportunity")
                
                # Long wait between scans
                logging.info(f"   ⏳ Waiting 120 seconds...")
                time.sleep(120)
                
            except KeyboardInterrupt:
                logging.info("🛑 Nuclear bot stopped")
                break
            except Exception as e:
                logging.error(f"❌ Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = GeminiNuclearFix()
    bot.run()