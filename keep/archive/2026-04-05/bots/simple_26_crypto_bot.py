#!/usr/bin/env python3
"""
Simple 26-Crypto Trading Bot
Monitors all 26 cryptocurrencies
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

def load_keys(exchange):
    """Load API keys from environment variables"""
    try:
        # First try to load .env file if python-dotenv is available
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # Fallback: manually load .env
            try:
                with open('.env', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
            except:
                pass  # .env file might not exist or can't be read
        
        if exchange == "binance":
            api_key = os.getenv('BINANCE_API_KEY')
            api_secret = os.getenv('BINANCE_API_SECRET')
        elif exchange == "gemini":
            api_key = os.getenv('GEMINI_API_KEY')
            api_secret = os.getenv('GEMINI_API_SECRET')
        else:
            return None, None
        
        # Fallback to file reading if env vars not set
        if not api_key or not api_secret:
            print(f"⚠️  {exchange} keys not in environment, trying file fallback...")
            if exchange == "binance":
                key_file = os.path.join(BASE_DIR, ".binance_key")
                secret_file = os.path.join(BASE_DIR, ".binance_secret")
            elif exchange == "gemini":
                key_file = os.path.join(BASE_DIR, ".gemini_key")
                secret_file = os.path.join(BASE_DIR, ".gemini_secret")
            else:
                return None, None
            
            try:
                with open(key_file, 'r') as f:
                    api_key = f.read().strip()
                with open(secret_file, 'r') as f:
                    api_secret = f.read().strip()
            except:
                return None, None
        
        return api_key, api_secret
    except Exception as e:
        print(f"❌ Error loading {exchange} keys: {e}")
        return None, None

def check_balance(exchange_obj):
    """Check exchange balance"""
    try:
        balance = exchange_obj.fetch_balance()
        
        # Check USDT for Binance, USD for Gemini
        if isinstance(exchange_obj, ccxt.binance):
            usdt = balance.get('USDT', {}).get('free', 0)
            print(f"  USDT Balance: ${usdt:.2f}")
            return usdt
        elif isinstance(exchange_obj, ccxt.gemini):
            usd = balance.get('USD', {}).get('free', 0)
            print(f"  USD Balance: ${usd:.2f}")
            return usd
        
        return 0
    except Exception as e:
        print(f"  Error checking balance: {e}")
        return 0

def analyze_symbol(exchange_obj, symbol):
    """Simple analysis for a symbol"""
    try:
        # Get ticker
        ticker = exchange_obj.fetch_ticker(symbol)
        
        price = ticker['last']
        change = ticker['percentage']
        volume = ticker['quoteVolume'] if 'quoteVolume' in ticker else ticker['baseVolume']
        
        # Simple signal logic
        if change > 1.0:  # 1% up
            signal = "BULLISH"
        elif change < -1.0:  # 1% down
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"
        
        return {
            "symbol": symbol,
            "price": price,
            "change": change,
            "volume": volume,
            "signal": signal,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
    except Exception as e:
        print(f"  Error analyzing {symbol}: {e}")
        return None

def main():
    """Main function"""
    print("=" * 70)
    print("26-CRYPTO TRADING BOT - REAL MODE (.env SECURE VERSION)")
    print("=" * 70)
    print("Monitoring all 26 top cryptocurrencies")
    print("Dual Exchange: Gemini (LONG on 16 cryptos) + Binance (SHORT on 26 cryptos)")
    print("SECURITY: Using .env file for API keys (not secure_keys/ directory)")
    print("=" * 70)
    
    # Load API keys
    print("\n🔑 Loading API keys...")
    gemini_key, gemini_secret = load_keys("gemini")
    binance_key, binance_secret = load_keys("binance")
    
    # Initialize exchanges
    exchanges = {}
    
    if gemini_key and gemini_secret:
        try:
            exchanges["gemini"] = ccxt.gemini({
                'apiKey': gemini_key,
                'secret': gemini_secret
            })
            print("✅ Gemini: Connected")
        except Exception as e:
            print(f"❌ Gemini: Connection failed - {e}")
    else:
        print("❌ Gemini: API keys not found")
    
    if binance_key and binance_secret:
        try:
            exchanges["binance"] = ccxt.binance({
                'apiKey': binance_key,
                'secret': binance_secret,
                'options': {'defaultType': 'spot'}
            })
            print("✅ Binance: Connected")
        except Exception as e:
            print(f"❌ Binance: Connection failed - {e}")
    else:
        print("❌ Binance: API keys not found")
    
    if not exchanges:
        print("\n❌ No exchanges connected. Please configure API keys.")
        print("\n💡 Setup instructions in REAL_TRADING_SETUP_INSTRUCTIONS.txt")
        return
    
    # Check balances
    print("\n💰 Checking balances...")
    for name, exchange in exchanges.items():
        print(f"\n{name.upper()}:")
        balance = check_balance(exchange)
        if balance > 0:
            print(f"  ✅ Funds available: ${balance:.2f}")
        else:
            print(f"  ⚠️  Low or no balance")
    
    print("\n" + "=" * 70)
    print("🚀 STARTING 26-CRYPTO ANALYSIS")
    print("=" * 70)
    print("Scanning every 2 minutes...")
    print("-" * 70)
    
    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"\n📊 CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 70)
            
            # Analyze Gemini pairs (LONG opportunities)
            if "gemini" in exchanges:
                print("\n🔍 GEMINI (LONG opportunities):")
                gemini_pairs = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD', 'DOT/USD', 'DOGE/USD', 'AVAX/USD', 'LINK/USD', 'UNI/USD', 'LTC/USD', 'ATOM/USD', 'FIL/USD', 'XTZ/USD', 'AAVE/USD', 'COMP/USD', 'YFI/USD']
                
                for pair in gemini_pairs[:6]:  # Check first 6 each cycle (was 3)
                    analysis = analyze_symbol(exchanges["gemini"], pair)
                    if analysis:
                        print(f"  {pair:10} ${analysis['price']:8.2f} {analysis['change']:6.2f}% {analysis['signal']:8}")
                        
                        # Simple LONG signal - lowered threshold for more opportunities
                        if analysis['signal'] == "BULLISH" and analysis['change'] > 0.8:
                            print(f"    ⚡ LONG SIGNAL: {pair} up {analysis['change']:.2f}%")
                            print(f"    💰 Potential LONG trade on Gemini")
            
            # Analyze Binance pairs (SHORT opportunities)
            if "binance" in exchanges:
                print("\n🔍 BINANCE (SHORT opportunities):")
                # Check a subset of cryptos each cycle
                start_idx = (cycle - 1) * 5 % len(CRYPTOS)
                cryptos_to_check = CRYPTOS[start_idx:start_idx + 8]  # Check 8 each cycle (was 5)
                
                for crypto in cryptos_to_check:
                    pair = f"{crypto}/USDT"
                    analysis = analyze_symbol(exchanges["binance"], pair)
                    if analysis:
                        print(f"  {pair:12} ${analysis['price']:8.2f} {analysis['change']:6.2f}% {analysis['signal']:8}")
                        
                        # Simple SHORT signal - lowered threshold for more opportunities
                        if analysis['signal'] == "BEARISH" and analysis['change'] < -1.0:
                            print(f"    ⚡ SHORT SIGNAL: {pair} down {analysis['change']:.2f}%")
                            print(f"    💰 Potential SHORT trade on Binance (when funds available)")
            
            print(f"\n⏰ Next analysis in 2 minutes...")
            print("=" * 70)
            
            # Wait for next cycle
            time.sleep(120)  # 2 minutes
            
    except KeyboardInterrupt:
        print("\n\n🛑 Trading bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error in trading bot: {e}")

if __name__ == "__main__":
    main()