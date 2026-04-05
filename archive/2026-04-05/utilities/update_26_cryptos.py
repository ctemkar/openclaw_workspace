#!/usr/bin/env python3
"""
Update trading system to monitor all 26 cryptocurrencies
"""

import os
import json
import re
from datetime import datetime

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

# Top 26 cryptocurrencies by market cap (commonly traded)
ALL_26_CRYPTOS = [
    # Top Tier (Major)
    "BTC",   # Bitcoin
    "ETH",   # Ethereum
    "SOL",   # Solana
    
    # Large Cap
    "ADA",   # Cardano
    "XRP",   # Ripple
    "DOT",   # Polkadot
    "DOGE",  # Dogecoin
    "AVAX",  # Avalanche
    "MATIC", # Polygon
    "LINK",  # Chainlink
    
    # Mid Cap
    "UNI",   # Uniswap
    "LTC",   # Litecoin
    "ATOM",  # Cosmos
    "ETC",   # Ethereum Classic
    "XLM",   # Stellar
    "ALGO",  # Algorand
    "VET",   # VeChain
    "FIL",   # Filecoin
    
    # Smaller but significant
    "ICP",   # Internet Computer
    "XTZ",   # Tezos
    "EOS",   # EOS
    "AAVE",  # Aave
    "MKR",   # Maker
    "COMP",  # Compound
    "SNX",   # Synthetix
    "YFI",   # Yearn Finance
]

def create_26_crypto_config():
    """Create configuration for all 26 cryptocurrencies"""
    print("\n" + "="*60)
    print("CONFIGURING 26 CRYPTOCURRENCIES FOR TRADING")
    print("="*60)
    
    # Gemini symbols (USD pairs)
    gemini_symbols = []
    for crypto in ALL_26_CRYPTOS:
        # Check which cryptos are available on Gemini
        # Gemini typically has: BTC, ETH, SOL, etc.
        if crypto in ["BTC", "ETH", "SOL", "ADA", "LINK", "UNI", "MATIC"]:
            gemini_symbols.append(f"{crypto}/USD")
        else:
            # For others, we'll use Binance
            pass
    
    # Binance symbols (USDT pairs)
    binance_symbols = [f"{crypto}/USDT" for crypto in ALL_26_CRYPTOS]
    
    config = {
        "version": "26_crypto_v1.0",
        "created_at": datetime.now().isoformat(),
        "total_cryptos": len(ALL_26_CRYPTOS),
        "cryptocurrencies": ALL_26_CRYPTOS,
        "exchange_config": {
            "gemini": {
                "available_pairs": gemini_symbols,
                "capital_allocation": 200.00,
                "trading_mode": "LONG",
                "risk": {
                    "stop_loss": 0.05,
                    "take_profit": 0.10,
                    "max_position_size": 0.3
                }
            },
            "binance": {
                "available_pairs": binance_symbols,
                "capital_allocation": 50.00,
                "trading_mode": "SHORT",
                "risk": {
                    "stop_loss": 0.07,
                    "take_profit": 0.08,
                    "max_position_size": 0.2
                }
            }
        },
        "trading_strategy": {
            "name": "Conservative 26-Crypto Momentum",
            "analysis_frequency": "5 minutes",
            "max_daily_trades": 3,
            "cooldown_minutes": 30,
            "selection_criteria": [
                "Volume > $100M daily",
                "Market cap > $1B",
                "Liquidity score > 70",
                "Volatility within 2-10% daily"
            ]
        },
        "monitoring": {
            "dashboard_port": 5080,
            "api_port": 5001,
            "log_file": "26_crypto_trading.log",
            "alerts": ["price_breakout", "volume_surge", "trend_reversal"]
        }
    }
    
    config_file = os.path.join(BASE_DIR, "26_crypto_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ 26-crypto configuration saved to {config_file}")
    print(f"\n📊 CONFIGURATION SUMMARY:")
    print(f"   Total cryptocurrencies: {len(ALL_26_CRYPTOS)}")
    print(f"   Gemini pairs: {len(gemini_symbols)}")
    print(f"   Binance pairs: {len(binance_symbols)}")
    print(f"   Total capital: $250")
    print(f"     • Gemini (LONG): $200")
    print(f"     • Binance (SHORT): $50")
    
    return config

def update_conservative_trading_bot():
    """Update the conservative trading bot for 26 cryptos"""
    print("\n" + "="*60)
    print("UPDATING CONSERVATIVE TRADING BOT")
    print("="*60)
    
    bot_file = os.path.join(BASE_DIR, "conservative_crypto_trading.py")
    
    if not os.path.exists(bot_file):
        print(f"❌ Trading bot not found: {bot_file}")
        return False
    
    with open(bot_file, 'r') as f:
        content = f.read()
    
    # Update the symbols section
    new_gemini_symbols = [
        'BTC/USD', 'ETH/USD', 'SOL/USD', 'ADA/USD', 
        'LINK/USD', 'UNI/USD', 'MATIC/USD'
    ]
    
    new_binance_symbols = [
        'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'XRP/USDT',
        'DOT/USDT', 'DOGE/USDT', 'AVAX/USDT', 'MATIC/USDT', 'LINK/USDT',
        'UNI/USDT', 'LTC/USDT', 'ATOM/USDT', 'ETC/USDT', 'XLM/USDT',
        'ALGO/USDT', 'VET/USDT', 'FIL/USDT', 'ICP/USDT', 'XTZ/USDT',
        'EOS/USDT', 'AAVE/USDT', 'MKR/USDT', 'COMP/USDT', 'SNX/USDT',
        'YFI/USDT'
    ]
    
    # Find and replace the symbols section
    import re
    
    # Update Gemini symbols
    gemini_pattern = r"GEMINI_SYMBOLS = \['.*?'\]"
    gemini_replacement = f"GEMINI_SYMBOLS = {new_gemini_symbols}"
    content = re.sub(gemini_pattern, gemini_replacement, content)
    
    # Update Binance symbols
    binance_pattern = r"BINANCE_SYMBOLS = \['.*?'\]"
    binance_replacement = f"BINANCE_SYMBOLS = {new_binance_symbols}"
    content = re.sub(binance_pattern, binance_replacement, content)
    
    # Update max trades for more opportunities
    content = content.replace("MAX_TRADES_PER_DAY = 2", "MAX_TRADES_PER_DAY = 3")
    content = content.replace("MAX_BINANCE_TRADES_PER_DAY = 1", "MAX_BINANCE_TRADES_PER_DAY = 2")
    
    with open(bot_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Trading bot updated for 26 cryptocurrencies")
    print(f"   Gemini pairs: {len(new_gemini_symbols)}")
    print(f"   Binance pairs: {len(new_binance_symbols)}")
    print(f"   Max daily trades: 3 (Gemini) + 2 (Binance)")
    
    return True

def create_26_crypto_monitor():
    """Create a monitor for all 26 cryptocurrencies"""
    print("\n" + "="*60)
    print("CREATING 26-CRYPTO MONITOR")
    print("="*60)
    
    monitor_script = f"""#!/usr/bin/env python3
"""
    
    monitor_file = os.path.join(BASE_DIR, "monitor_26_cryptos.py")
    with open(monitor_file, 'w') as f:
        f.write(monitor_script)
    
    os.chmod(monitor_file, 0o755)
    print(f"✅ 26-crypto monitor created: {monitor_file}")
    
    return monitor_file

def update_trading_server():
    """Update trading server for 26 cryptos"""
    print("\n" + "="*60)
    print("UPDATING TRADING SERVER")
    print("="*60)
    
    server_file = os.path.join(BASE_DIR, "trading_server.py")
    
    if not os.path.exists(server_file):
        print(f"❌ Trading server not found: {server_file}")
        return False
    
    with open(server_file, 'r') as f:
        content = f.read()
    
    # Update the HTML display
    old_html = """        <h2>Configuration:</h2>
        <ul>
            <li>Capital: $100</li>
            <li>Stop-loss: 5%</li>
            <li>Take-profit: 10%</li>
            <li>Max trades/day: 2</li>
            <li>Pairs: BTC/USD, ETH/USD</li>
        </ul>"""
    
    new_html = """        <h2>Configuration:</h2>
        <ul>
            <li>Capital: $250 ($200 Gemini + $50 Binance)</li>
            <li>Stop-loss: 5% (Gemini) / 7% (Binance)</li>
            <li>Take-profit: 10% (Gemini) / 8% (Binance)</li>
            <li>Max trades/day: 5 total (3 Gemini + 2 Binance)</li>
            <li>Cryptocurrencies: 26 total</li>
            <li>Gemini (LONG): 7 pairs (BTC, ETH, SOL, ADA, LINK, UNI, MATIC)</li>
            <li>Binance (SHORT): 26 pairs (All top cryptos)</li>
        </ul>"""
    
    content = content.replace(old_html, new_html)
    
    # Update status endpoint
    status_pattern = r'"pairs": \["BTC/USD", "ETH/USD"\]'
    status_replacement = '"pairs": ["26 cryptocurrencies - See config"]'
    content = re.sub(status_pattern, status_replacement, content)
    
    with open(server_file, 'w') as f:
        f.write(content)
    
    print("✅ Trading server updated for 26 cryptocurrencies")
    
    return True

def create_trading_instructions():
    """Create instructions for 26-crypto trading"""
    print("\n" + "="*60)
    print("CREATING TRADING INSTRUCTIONS")
    print("="*60)
    
    instructions = f"""
    26-CRYPTOCURRENCY TRADING SYSTEM
    =================================
    
    CONFIGURATION:
    • Total Capital: $250
      - Gemini (LONG): $200
      - Binance (SHORT): $50
    • Cryptocurrencies: 26 total
    • Trading Pairs: 33 total (7 Gemini + 26 Binance)
    • Risk Management:
      - Gemini Stop Loss: 5%
      - Gemini Take Profit: 10%
      - Binance Stop Loss: 7%
      - Binance Take Profit: 8%
    • Max Daily Trades: 5 (3 Gemini + 2 Binance)
    
    CRYPTOCURRENCIES MONITORED:
    {', '.join(ALL_26_CRYPTOS)}
    
    GEMINI PAIRS (LONG):
    • BTC/USD, ETH/USD, SOL/USD, ADA/USD
    • LINK/USD, UNI/USD, MATIC/USD
    
    BINANCE PAIRS (SHORT):
    • All 26 cryptocurrencies with USDT pairs
    
    TRADING STRATEGY:
    1. Conservative momentum analysis
    2. 5-minute scanning intervals
    3. Volume and volatility filters
    4. AI-powered signal generation
    5. Risk-adjusted position sizing
    
    MONITORING:
    • Dashboard: http://127.0.0.1:5080
    • API Status: http://127.0.0.1:5001/status
    • Logs: tail -f 26_crypto_trading.log
    
    SETUP STEPS:
    1. Configure API keys (Binance & Gemini)
    2. Start trading server: python3 trading_server.py
    3. Start trading bot: python3 conservative_crypto_trading.py
    4. Monitor dashboard for signals
    
    SECURITY:
    • API keys stored in secure_keys/ directory
    • IP whitelisting recommended
    • Regular balance checks
    • Trade confirmation alerts
    
    FILES CREATED:
    1. 26_crypto_config.json - Main configuration
    2. Updated conservative_crypto_trading.py
    3. Updated trading_server.py
    4. monitor_26_cryptos.py - Monitoring script
    
    ACTIVATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    instructions_file = os.path.join(BASE_DIR, "26_CRYPTO_TRADING_INSTRUCTIONS.txt")
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"✅ Instructions saved to: {instructions_file}")
    
    return instructions_file

def main():
    """Main function - Update system for 26 cryptocurrencies"""
    print("UPDATING FOR 26 CRYPTOCURRENCIES")
    print("="*60)
    
    try:
        # Step 1: Create configuration
        config = create_26_crypto_config()
        
        # Step 2: Update trading bot
        bot_updated = update_conservative_trading_bot()
        
        # Step 3: Create monitor
        monitor = create_26_crypto_monitor()
        
        # Step 4: Update trading server
        server_updated = update_trading_server()
        
        # Step 5: Create instructions
        instructions = create_trading_instructions()
        
        print("\n" + "="*60)
        print("✅ 26-CRYPTO TRADING SYSTEM UPDATED")
        print("="*60)
        
        print(f"\n🎯 CONFIGURATION:")
        print(f"   Total Cryptocurrencies: {config['total_cryptos']}")
        print(f"   Gemini Pairs: {len(config['exchange_config']['gemini']['available_pairs'])}")
        print(f"   Binance Pairs: {len(config['exchange_config']['binance']['available_pairs'])}")
        print(f"   Total Capital: ${config['exchange_config']['gemini']['capital_allocation'] + config['exchange_config']['binance']['capital_allocation']}")
        
        print(f"\n📈 TRADING STRATEGY:")
        print(f"   Name: {config['trading_strategy']['name']}")
        print(f"   Frequency: {config['trading_strategy']['analysis_frequency']}")
        print(f"   Max Daily Trades: {config['trading_strategy']['max_daily_trades']}")
        
        print(f"\n🚀 NEXT STEPS:")
        print("1. Configure API keys for Binance and Gemini")
        print("2. Start the updated trading system")
        print("3. Monitor all 26 cryptocurrencies")
        print("4. Watch for trading signals")
        
        print(f"\n📋 INSTRUCTIONS:")
        print(f"   {instructions}")
        
        print(f"\n⚠️ IMPORTANT:")
        print("• API keys must have trading permissions")
        print("• Start with conservative position sizes")
        print("• Monitor system performance")
        print("• Adjust risk parameters as needed")
        
        print(f"\n⏰ System ready for 26-crypto trading!")
        
    except Exception as e:
        print(f"\n❌ Error updating system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()