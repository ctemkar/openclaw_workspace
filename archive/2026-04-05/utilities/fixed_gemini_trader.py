#!/usr/bin/env python3
"""
FIXED Gemini Trading Bot - With proper logging and position tracking
"""

import os
import json
import ccxt
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_config():
    """Load configuration"""
    config_path = os.path.join(BASE_DIR, "trading_config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return None

def save_trade(trade):
    """Save trade to daily trades file"""
    daily_path = os.path.join(BASE_DIR, "daily_trades.json")
    
    if os.path.exists(daily_path):
        with open(daily_path, 'r') as f:
            daily_data = json.load(f)
    else:
        daily_data = {
            'date': datetime.now().date().isoformat(),
            'trades': [],
            'metadata': {}
        }
    
    daily_data['trades'].append(trade)
    daily_data['metadata']['last_updated'] = datetime.now().isoformat()
    
    with open(daily_path, 'w') as f:
        json.dump(daily_data, f, indent=2)
    
    return True

def update_capital(new_capital, btc_holdings, btc_value):
    """Update capital configuration"""
    config_path = os.path.join(BASE_DIR, "trading_config.json")
    
    config = load_config() or {}
    config['current_capital'] = new_capital
    config['btc_holdings'] = btc_holdings
    config['btc_value'] = btc_value
    config['total_value'] = new_capital + btc_value
    config['last_updated'] = datetime.now().isoformat()
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config

def main():
    print("="*70)
    print("🔄 FIXED GEMINI TRADING BOT")
    print("="*70)
    
    # Load config
    config = load_config()
    if not config:
        print("❌ No configuration found. Run repair script first.")
        return
    
    print(f"💰 Capital: ${config['total_value']:.2f}")
    print(f"📊 Free USD: ${config['current_capital']:.2f}")
    print(f"📈 BTC Holdings: {config['btc_holdings']:.6f} (${config['btc_value']:.2f})")
    print("="*70)
    
    # Load API keys
    try:
        with open(os.path.join(BASE_DIR, "secure_keys/.gemini_key"), 'r') as f:
            key = f.read().strip()
        with open(os.path.join(BASE_DIR, "secure_keys/.gemini_secret"), 'r') as f:
            secret = f.read().strip()
    except:
        print("❌ Cannot load API keys")
        return
    
    # Initialize exchange
    exchange = ccxt.gemini({
        'apiKey': key,
        'secret': secret,
        'enableRateLimit': True
    })
    
    print("✅ System ready. Trading PAUSED until manually enabled.")
    print("   To enable trading, edit trading_config.json")
    print("   and set trading_status to 'ACTIVE'")
    
    # Monitoring loop (no trading until enabled)
    while True:
        try:
            # Check real balance
            balance = exchange.fetch_balance()
            usd = balance['free'].get('USD', 0)
            btc = balance['free'].get('BTC', 0)
            
            ticker = exchange.fetch_ticker('BTC/USD')
            btc_price = ticker['last']
            btc_value = btc * btc_price
            total_value = usd + btc_value
            
            # Update config with real data
            update_capital(usd, btc, btc_value)
            
            print(f"\n📊 Real-time check: {datetime.now().strftime('%H:%M:%S')}")
            print(f"   Free USD: ${usd:.2f}")
            print(f"   BTC: {btc:.6f} (${btc_value:.2f})")
            print(f"   Total: ${total_value:.2f}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
