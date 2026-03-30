#!/usr/bin/env python3
"""
IMPROVED 26-Crypto Trading Bot
Better logging, realistic thresholds, checks all pairs
"""

import os
import json
import time
import ccxt
from datetime import datetime
import logging

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

# Setup logging
log_file = os.path.join(BASE_DIR, "26_crypto_live_trading.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 26 Cryptocurrencies
CRYPTOS = [
    "BTC", "ETH", "SOL", "ADA", "XRP", "DOT", "DOGE",
    "AVAX", "MATIC", "LINK", "UNI", "LTC", "ATOM", "ETC",
    "XLM", "ALGO", "VET", "FIL", "ICP", "XTZ", "EOS",
    "AAVE", "MKR", "COMP", "SNX", "YFI"
]

# Gemini available pairs (from earlier check)
GEMINI_PAIRS = [
    "BTC/USD", "ETH/USD", "SOL/USD", "XRP/USD", "DOT/USD", "DOGE/USD",
    "AVAX/USD", "LINK/USD", "UNI/USD", "LTC/USD", "ATOM/USD", "FIL/USD",
    "XTZ/USD", "AAVE/USD", "COMP/USD", "YFI/USD"
]

# Trading parameters (MORE REALISTIC)
LONG_THRESHOLD = 0.5    # 0.5% for LONG (was 0.8%)
SHORT_THRESHOLD = 0.8   # 0.8% for SHORT (was 1.0%)
SCAN_INTERVAL = 60      # 60 seconds (was 120)

def load_api_keys():
    """Load API keys"""
    try:
        # Gemini
        with open(os.path.join(BASE_DIR, '.gemini_key'), 'r') as f:
            gemini_key = f.read().strip()
        with open(os.path.join(BASE_DIR, '.gemini_secret'), 'r') as f:
            gemini_secret = f.read().strip()
        
        # Binance
        with open(os.path.join(BASE_DIR, '.binance_key'), 'r') as f:
            binance_key = f.read().strip()
        with open(os.path.join(BASE_DIR, '.binance_secret'), 'r') as f:
            binance_secret = f.read().strip()
        
        return {
            'gemini': (gemini_key, gemini_secret),
            'binance': (binance_key, binance_secret)
        }
    except Exception as e:
        logger.error(f"Error loading API keys: {e}")
        return None

def initialize_exchanges(keys):
    """Initialize exchange connections"""
    exchanges = {}
    
    if keys and 'gemini' in keys:
        try:
            gemini_key, gemini_secret = keys['gemini']
            exchanges['gemini'] = ccxt.gemini({
                'apiKey': gemini_key,
                'secret': gemini_secret,
                'enableRateLimit': True
            })
            logger.info("✅ Gemini exchange connected")
        except Exception as e:
            logger.error(f"❌ Gemini connection failed: {e}")
    
    if keys and 'binance' in keys:
        try:
            binance_key, binance_secret = keys['binance']
            exchanges['binance'] = ccxt.binance({
                'apiKey': binance_key,
                'secret': binance_secret,
                'options': {'defaultType': 'spot'},
                'enableRateLimit': True
            })
            logger.info("✅ Binance exchange connected")
        except Exception as e:
            logger.error(f"❌ Binance connection failed: {e}")
    
    return exchanges

def check_balances(exchanges):
    """Check exchange balances"""
    balances = {}
    
    for name, exchange in exchanges.items():
        try:
            balance = exchange.fetch_balance()
            if name == 'gemini':
                usd = balance.get('USD', {}).get('free', 0)
                balances['gemini'] = usd
                logger.info(f"💰 Gemini USD balance: ${usd:.2f}")
            elif name == 'binance':
                usdt = balance.get('USDT', {}).get('free', 0)
                balances['binance'] = usdt
                logger.info(f"💰 Binance USDT balance: ${usdt:.2f}")
        except Exception as e:
            logger.error(f"Error checking {name} balance: {e}")
    
    return balances

def analyze_pair(exchange, pair, is_gemini=True):
    """Analyze a trading pair"""
    try:
        ticker = exchange.fetch_ticker(pair)
        
        price = ticker['last']
        change = ticker.get('percentage', 0)
        volume = ticker.get('quoteVolume', ticker.get('baseVolume', 0))
        
        # Determine signal
        if is_gemini:
            # LONG signal for Gemini
            if change > LONG_THRESHOLD:
                signal = "LONG"
                strength = change
            else:
                signal = "HOLD"
                strength = 0
        else:
            # SHORT signal for Binance
            if change < -SHORT_THRESHOLD:
                signal = "SHORT"
                strength = abs(change)
            else:
                signal = "HOLD"
                strength = 0
        
        return {
            'pair': pair,
            'price': price,
            'change': change,
            'volume': volume,
            'signal': signal,
            'strength': strength,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing {pair}: {e}")
        return None

def log_opportunity(analysis, exchange_name):
    """Log trading opportunity"""
    if analysis['signal'] != 'HOLD':
        logger.info(f"⚡ {exchange_name.upper()} {analysis['signal']} SIGNAL: {analysis['pair']}")
        logger.info(f"   Price: ${analysis['price']:.2f}, Change: {analysis['change']:.2f}%")
        logger.info(f"   Strength: {analysis['strength']:.2f}%")
        
        # Save to opportunities file
        opp_file = os.path.join(BASE_DIR, "trading_opportunities.json")
        try:
            if os.path.exists(opp_file):
                with open(opp_file, 'r') as f:
                    opportunities = json.load(f)
            else:
                opportunities = []
            
            opportunities.append({
                'timestamp': analysis['timestamp'],
                'exchange': exchange_name,
                'pair': analysis['pair'],
                'signal': analysis['signal'],
                'price': analysis['price'],
                'change': analysis['change'],
                'strength': analysis['strength']
            })
            
            # Keep only last 100 opportunities
            if len(opportunities) > 100:
                opportunities = opportunities[-100:]
            
            with open(opp_file, 'w') as f:
                json.dump(opportunities, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving opportunity: {e}")

def main():
    """Main trading loop"""
    logger.info("=" * 70)
    logger.info("🚀 IMPROVED 26-CRYPTO TRADING BOT STARTING")
    logger.info("=" * 70)
    logger.info(f"LONG threshold: {LONG_THRESHOLD}% (Gemini)")
    logger.info(f"SHORT threshold: {SHORT_THRESHOLD}% (Binance)")
    logger.info(f"Scan interval: {SCAN_INTERVAL} seconds")
    logger.info(f"Gemini pairs: {len(GEMINI_PAIRS)}")
    logger.info(f"Binance pairs: {len(CRYPTOS)}")
    logger.info("=" * 70)
    
    # Load API keys
    keys = load_api_keys()
    if not keys:
        logger.error("❌ Failed to load API keys")
        return
    
    # Initialize exchanges
    exchanges = initialize_exchanges(keys)
    if not exchanges:
        logger.error("❌ No exchanges connected")
        return
    
    # Check balances
    balances = check_balances(exchanges)
    
    cycle = 0
    total_opportunities = 0
    
    try:
        while True:
            cycle += 1
            cycle_start = datetime.now()
            
            logger.info(f"\n📊 CYCLE {cycle} - {cycle_start.strftime('%H:%M:%S')}")
            logger.info("-" * 50)
            
            opportunities_this_cycle = 0
            
            # Analyze Gemini pairs (LONG)
            if 'gemini' in exchanges:
                logger.info(f"🔍 Analyzing {len(GEMINI_PAIRS)} Gemini pairs...")
                for pair in GEMINI_PAIRS:
                    analysis = analyze_pair(exchanges['gemini'], pair, is_gemini=True)
                    if analysis:
                        if analysis['signal'] == 'LONG':
                            log_opportunity(analysis, 'gemini')
                            opportunities_this_cycle += 1
                        # Log all pairs for transparency
                        logger.debug(f"   {pair:12} ${analysis['price']:8.2f} {analysis['change']:6.2f}%")
            
            # Analyze Binance pairs (SHORT)
            if 'binance' in exchanges:
                logger.info(f"🔍 Analyzing {len(CRYPTOS)} Binance pairs...")
                # Check all pairs every cycle
                for crypto in CRYPTOS:
                    pair = f"{crypto}/USDT"
                    analysis = analyze_pair(exchanges['binance'], pair, is_gemini=False)
                    if analysis:
                        if analysis['signal'] == 'SHORT':
                            log_opportunity(analysis, 'binance')
                            opportunities_this_cycle += 1
                        # Log all pairs for transparency
                        logger.debug(f"   {pair:12} ${analysis['price']:8.2f} {analysis['change']:6.2f}%")
            
            total_opportunities += opportunities_this_cycle
            
            cycle_end = datetime.now()
            cycle_duration = (cycle_end - cycle_start).total_seconds()
            
            logger.info(f"\n📈 CYCLE {cycle} SUMMARY:")
            logger.info(f"   Opportunities found: {opportunities_this_cycle}")
            logger.info(f"   Total opportunities: {total_opportunities}")
            logger.info(f"   Cycle duration: {cycle_duration:.1f} seconds")
            
            if opportunities_this_cycle > 0:
                logger.info(f"   ⚡ TRADING OPPORTUNITIES DETECTED!")
            else:
                logger.info(f"   ⏳ No strong signals this cycle")
            
            logger.info(f"\n⏰ Next cycle in {SCAN_INTERVAL} seconds...")
            logger.info("=" * 70)
            
            # Wait for next cycle
            time.sleep(SCAN_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Trading bot stopped by user")
    except Exception as e:
        logger.error(f"\n❌ Error in trading bot: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()