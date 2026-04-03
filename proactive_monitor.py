#!/usr/bin/env python3
"""
PROACTIVE MONITORING SYSTEM
Continuously checks ALL trading systems and automatically fixes issues
"""
import os
import time
import subprocess
import requests
import json
import logging
from datetime import datetime
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('proactive_monitor.log'),
        logging.StreamHandler()
    ]
)

class ProactiveMonitor:
    def __init__(self):
        self.check_interval = 60  # Check every 60 seconds
        self.fix_attempts = {}
        self.max_fix_attempts = 3
        
    def check_all_systems(self):
        """Check ALL trading systems"""
        logging.info("🔍 CHECKING ALL TRADING SYSTEMS")
        
        systems = [
            self.check_forex_bot,
            self.check_26_crypto_bot,
            self.check_practical_profit_bot,
            self.check_dashboard,
            self.check_exchange_apis,
            self.check_arbitrage_opportunities
        ]
        
        all_ok = True
        for system_check in systems:
            try:
                if not system_check():
                    all_ok = False
            except Exception as e:
                logging.error(f"❌ Error checking system: {e}")
                all_ok = False
        
        return all_ok
    
    def check_forex_bot(self):
        """Check Forex bot"""
        logging.info("💰 Checking Forex bot...")
        
        # Check if process is running
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        forex_running = 'forex_bot_with_schwab.py' in result.stdout
        
        if not forex_running:
            logging.error("❌ Forex bot NOT RUNNING!")
            self.fix_forex_bot()
            return False
        
        # Check if it's actually working (not just process)
        try:
            # Check recent logs
            if os.path.exists('real_forex_trading.log'):
                with open('real_forex_trading.log', 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        if 'ERROR' in last_line or 'failed' in last_line.lower():
                            logging.error(f"❌ Forex bot has errors: {last_line[:100]}")
                            return False
            
            logging.info("✅ Forex bot running")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error checking Forex bot: {e}")
            return False
    
    def fix_forex_bot(self):
        """Fix Forex bot"""
        logging.info("🔧 Fixing Forex bot...")
        
        # Kill any stuck processes
        subprocess.run(['pkill', '-f', 'forex_bot_with_schwab.py'], capture_output=True)
        time.sleep(2)
        
        # Restart
        try:
            subprocess.Popen([
                'python3', 'forex_bot_with_schwab.py', '--real-trading'
            ], stdout=open('real_forex_trading.log', 'a'), stderr=subprocess.STDOUT)
            logging.info("✅ Forex bot RESTARTED")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to restart Forex bot: {e}")
            return False
    
    def check_26_crypto_bot(self):
        """Check 26-crypto bot"""
        logging.info("⚡ Checking 26-crypto bot...")
        
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        crypto_running = 'real_26_crypto_trader.py' in result.stdout
        
        if not crypto_running:
            logging.error("❌ 26-crypto bot NOT RUNNING!")
            self.fix_26_crypto_bot()
            return False
        
        # Check logs for errors
        if os.path.exists('26_crypto_output.log'):
            with open('26_crypto_output.log', 'r') as f:
                content = f.read()
                if 'ERROR' in content or 'Traceback' in content:
                    logging.error("❌ 26-crypto bot has errors in log")
                    self.fix_26_crypto_bot()
                    return False
        
        logging.info("✅ 26-crypto bot running")
        return True
    
    def fix_26_crypto_bot(self):
        """Fix 26-crypto bot"""
        logging.info("🔧 Fixing 26-crypto bot...")
        
        subprocess.run(['pkill', '-f', 'real_26_crypto_trader.py'], capture_output=True)
        time.sleep(2)
        
        try:
            subprocess.Popen([
                'python3', 'real_26_crypto_trader.py'
            ], stdout=open('26_crypto_output.log', 'a'), stderr=subprocess.STDOUT)
            logging.info("✅ 26-crypto bot RESTARTED")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to restart 26-crypto bot: {e}")
            return False
    
    def check_practical_profit_bot(self):
        """Check practical profit bot"""
        logging.info("📈 Checking practical profit bot...")
        
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        profit_running = 'practical_profit_bot.py' in result.stdout
        
        if not profit_running:
            logging.error("❌ Practical profit bot NOT RUNNING!")
            self.fix_practical_profit_bot()
            return False
        
        # Check for Binance NOTIONAL errors
        if os.path.exists('practical_profit_output.log'):
            with open('practical_profit_output.log', 'r') as f:
                lines = f.readlines()[-20:]  # Last 20 lines
                for line in lines:
                    if 'NOTIONAL' in line or 'Filter failure' in line:
                        logging.error("❌ Practical profit bot has NOTIONAL error!")
                        # Fix trade size
                        self.fix_trade_size()
                        return False
        
        logging.info("✅ Practical profit bot running")
        return True
    
    def fix_practical_profit_bot(self):
        """Fix practical profit bot"""
        logging.info("🔧 Fixing practical profit bot...")
        
        subprocess.run(['pkill', '-f', 'practical_profit_bot.py'], capture_output=True)
        time.sleep(2)
        
        try:
            subprocess.Popen([
                'python3', 'practical_profit_bot.py'
            ], stdout=open('practical_profit_output.log', 'a'), stderr=subprocess.STDOUT)
            logging.info("✅ Practical profit bot RESTARTED")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to restart practical profit bot: {e}")
            return False
    
    def fix_trade_size(self):
        """Fix trade size for Binance NOTIONAL error"""
        logging.info("🔧 Fixing trade size (NOTIONAL error)...")
        
        try:
            # Read file
            with open('practical_profit_bot.py', 'r') as f:
                content = f.read()
            
            # Update min_trade_mana to 200
            if 'self.min_trade_mana = 50' in content:
                content = content.replace('self.min_trade_mana = 50', 'self.min_trade_mana = 200')
                with open('practical_profit_bot.py', 'w') as f:
                    f.write(content)
                logging.info("✅ Updated min_trade_mana from 50 to 200")
                
                # Restart bot
                self.fix_practical_profit_bot()
                return True
            else:
                logging.info("✅ Trade size already fixed (200 MANA)")
                return True
                
        except Exception as e:
            logging.error(f"❌ Failed to fix trade size: {e}")
            return False
    
    def check_dashboard(self):
        """Check dashboard"""
        logging.info("📊 Checking dashboard...")
        
        try:
            response = requests.get('http://localhost:5020', timeout=10)
            if response.status_code == 200:
                logging.info("✅ Dashboard running (HTTP 200)")
                return True
            else:
                logging.error(f"❌ Dashboard error: HTTP {response.status_code}")
                self.fix_dashboard()
                return False
        except Exception as e:
            logging.error(f"❌ Dashboard not responding: {e}")
            self.fix_dashboard()
            return False
    
    def fix_dashboard(self):
        """Fix dashboard"""
        logging.info("🔧 Fixing dashboard...")
        
        # Kill old dashboard
        subprocess.run(['pkill', '-f', 'arbitration_trading_dashboard.py'], capture_output=True)
        time.sleep(2)
        
        # Start new one
        try:
            subprocess.Popen([
                'python3', 'arbitration_trading_dashboard.py'
            ], stdout=open('dashboard.log', 'a'), stderr=subprocess.STDOUT)
            logging.info("✅ Dashboard RESTARTED")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to restart dashboard: {e}")
            return False
    
    def check_exchange_apis(self):
        """Check exchange APIs"""
        logging.info("🌐 Checking exchange APIs...")
        
        exchanges = [
            ('Binance', 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'),
            ('Gemini', 'https://api.gemini.com/v1/pubticker/btcusd')
        ]
        
        all_ok = True
        for name, url in exchanges:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logging.info(f"✅ {name} API accessible")
                else:
                    logging.error(f"❌ {name} API error: HTTP {response.status_code}")
                    all_ok = False
            except Exception as e:
                logging.error(f"❌ {name} API failed: {e}")
                all_ok = False
        
        return all_ok
    
    def check_arbitrage_opportunities(self):
        """Check if arbitrage is profitable"""
        logging.info("💰 Checking arbitrage opportunities...")
        
        try:
            # Get MANA prices
            b_resp = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=MANAUSDT', timeout=10)
            g_resp = requests.get('https://api.gemini.com/v1/pubticker/manausd', timeout=10)
            
            if b_resp.status_code == 200 and g_resp.status_code == 200:
                b_price = float(b_resp.json()['price'])
                g_price = float(g_resp.json()['last'])
                spread = ((g_price - b_price) / b_price) * 100
                
                if spread > 0.5:
                    logging.info(f"✅ ARBITRAGE PROFITABLE: {spread:.2f}% spread")
                    logging.info(f"   Binance: ${b_price:.4f}, Gemini: ${g_price:.4f}")
                    logging.info(f"   Profit: ${g_price-b_price:.4f} per MANA")
                else:
                    logging.info(f"⚠️  Arbitrage not profitable: {spread:.2f}% (need >0.5%)")
                
                return True
            else:
                logging.error("❌ Can't fetch prices for arbitrage check")
                return False
                
        except Exception as e:
            logging.error(f"❌ Error checking arbitrage: {e}")
            return False
    
    def run(self):
        """Main monitoring loop"""
        logging.info("🚀 STARTING PROACTIVE MONITORING SYSTEM")
        logging.info(f"⏰ Check interval: {self.check_interval} seconds")
        logging.info("=" * 60)
        
        cycle = 0
        while True:
            cycle += 1
            logging.info(f"\n🔄 MONITORING CYCLE #{cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logging.info("=" * 60)
            
            all_ok = self.check_all_systems()
            
            if all_ok:
                logging.info("🎉 ALL SYSTEMS OPERATIONAL!")
            else:
                logging.warning("⚠️  Some systems need attention (fixes attempted)")
            
            # Wait for next check
            logging.info(f"⏳ Next check in {self.check_interval} seconds...")
            time.sleep(self.check_interval)

if __name__ == '__main__':
    monitor = ProactiveMonitor()
    
    try:
        monitor.run()
    except KeyboardInterrupt:
        logging.info("\n👋 Monitoring stopped by user")
    except Exception as e:
        logging.error(f"❌ Monitor crashed: {e}")
        sys.exit(1)