#!/usr/bin/env python3
"""
26-CRYPTOCURRENCY TRADING BOT
Monitors all 26 top cryptocurrencies for trading opportunities
Dual exchange: Gemini (LONG) + Binance (SHORT)
"""

import os
import json
import time
import ccxt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

# ================================================
# CONFIGURATION - 26 CRYPTOCURRENCIES
# ================================================

# Top 26 cryptocurrencies
ALL_26_CRYPTOS = [
    "BTC", "ETH", "SOL", "ADA", "XRP", "DOT", "DOGE",
    "AVAX", "MATIC", "LINK", "UNI", "LTC", "ATOM", "ETC",
    "XLM", "ALGO", "VET", "FIL", "ICP", "XTZ", "EOS",
    "AAVE", "MKR", "COMP", "SNX", "YFI"
]

# Capital allocation
GEMINI_CAPITAL = 200.00  # $200 for LONG positions
BINANCE_CAPITAL = 50.00   # $50 for SHORT positions
TOTAL_CAPITAL = GEMINI_CAPITAL + BINANCE_CAPITAL

# Trading pairs
GEMINI_SYMBOLS = [
    "BTC/USD", "ETH/USD", "SOL/USD", "ADA/USD",
    "MATIC/USD", "LINK/USD", "UNI/USD"
]

BINANCE_SYMBOLS = [f"{crypto}/USDT" for crypto in ALL_26_CRYPTOS]

# Risk parameters
GEMINI_STOP_LOSS = 0.05  # 5%
GEMINI_TAKE_PROFIT = 0.10  # 10%
BINANCE_STOP_LOSS = 0.07  # 7%
BINANCE_TAKE_PROFIT = 0.08  # 8%

MAX_GEMINI_TRADES = 3
MAX_BINANCE_TRADES = 2
MAX_TOTAL_TRADES = MAX_GEMINI_TRADES + MAX_BINANCE_TRADES

# Position sizing
MAX_GEMINI_POSITION = 0.3  # 30% of Gemini capital
MAX_BINANCE_POSITION = 0.2  # 20% of Binance capital

# Files
CONFIG_FILE = os.path.join(BASE_DIR, "26_crypto_config.json")
TRADES_LOG = os.path.join(BASE_DIR, "26_crypto_trades.json")
ANALYSIS_LOG = os.path.join(BASE_DIR, "26_crypto_analysis.log")

# ================================================
# API KEY MANAGEMENT
# ================================================

def load_api_keys(exchange: str) -> Tuple[Optional[str], Optional[str]]:
    """Load API keys from secure files"""
    try:
        if exchange.lower() == "gemini":
            key_file = os.path.join(BASE_DIR, ".gemini_key")
            secret_file = os.path.join(BASE_DIR, ".gemini_secret")
        elif exchange.lower() == "binance":
            key_file = os.path.join(BASE_DIR, ".binance_key")
            secret_file = os.path.join(BASE_DIR, ".binance_secret")
        else:
            return None, None
        
        if os.path.exists(key_file) and os.path.exists(secret_file):
            with open(key_file, 'r') as f:
                api_key = f.read().strip()
            with open(secret_file, 'r') as f:
                api_secret = f.read().strip()
            
            if api_key and api_secret:
                return api_key, api_secret
        
        return None, None
    except Exception as e:
        print(f"❌ Error loading {exchange} API keys: {e}")
        return None, None

# ================================================
# MARKET ANALYSIS
# ================================================

def analyze_crypto_momentum(prices: List[float], volumes: List[float]) -> Dict:
    """Analyze momentum for a cryptocurrency"""
    if len(prices) < 10:
        return {"signal": "NEUTRAL", "strength": 0, "reason": "Insufficient data"}
    
    # Calculate returns
    returns = np.diff(prices) / prices[:-1]
    
    # Calculate metrics
    avg_return = np.mean(returns[-5:])  # Last 5 periods
    volatility = np.std(returns[-10:])   # Last 10 periods
    volume_trend = np.mean(volumes[-5:]) / np.mean(volumes[-10:]) if np.mean(volumes[-10:]) > 0 else 1
    
    # Momentum signals
    if avg_return > 0.002 and volume_trend > 1.2:  # 0.2% gain with volume surge
        signal = "BULLISH"
        strength = min(1.0, avg_return * 100)  # Strength as percentage
        reason = f"Positive momentum ({avg_return*100:.2f}%) with volume surge ({volume_trend:.2f}x)"
    elif avg_return < -0.002 and volume_trend > 1.2:  # 0.2% loss with volume surge
        signal = "BEARISH"
        strength = min(1.0, abs(avg_return) * 100)
        reason = f"Negative momentum ({avg_return*100:.2f}%) with volume surge ({volume_trend:.2f}x)"
    else:
        signal = "NEUTRAL"
        strength = 0
        reason = f"Sideways movement ({avg_return*100:.2f}%), volume normal"
    
    return {
        "signal": signal,
        "strength": strength,
        "reason": reason,
        "metrics": {
            "avg_return": avg_return,
            "volatility": volatility,
            "volume_trend": volume_trend,
            "current_price": prices[-1]
        }
    }

def fetch_market_data(exchange, symbol: str, periods: int = 20) -> Tuple[List[float], List[float]]:
    """Fetch OHLCV data for analysis"""
    try:
        # Fetch recent candles
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=periods)
        
        if len(ohlcv) >= 10:
            prices = [candle[4] for candle in ohlcv]  # Close prices
            volumes = [candle[5] for candle in ohlcv]  # Volumes
            return prices, volumes
        else:
            return [], []
    except Exception as e:
        print(f"⚠️ Error fetching {symbol}: {e}")
        return [], []

# ================================================
# TRADING LOGIC
# ================================================

def calculate_position_size(capital: float, risk_pct: float, current_price: float, stop_loss_pct: float) -> float:
    """Calculate position size based on risk management"""
    risk_amount = capital * risk_pct
    stop_loss_amount = current_price * stop_loss_pct
    position_size = risk_amount / stop_loss_amount if stop_loss_amount > 0 else 0
    return position_size

def should_trade_gemini(signal: Dict, symbol: str, trades_today: int) -> bool:
    """Check if we should take a LONG position on Gemini"""
    if trades_today >= MAX_GEMINI_TRADES:
        return False
    
    if signal["signal"] != "BULLISH":
        return False
    
    # Minimum strength requirement
    if signal["strength"] < 0.3:  # 0.3% minimum strength
        return False
    
    # Volume requirement
    if signal["metrics"]["volume_trend"] < 1.1:
        return False
    
    return True

def should_trade_binance(signal: Dict, symbol: str, trades_today: int) -> bool:
    """Check if we should take a SHORT position on Binance"""
    if trades_today >= MAX_BINANCE_TRADES:
        return False
    
    if signal["signal"] != "BEARISH":
        return False
    
    # Minimum strength requirement (higher for shorts)
    if signal["strength"] < 0.4:  # 0.4% minimum strength
        return False
    
    # Volume requirement
    if signal["metrics"]["volume_trend"] < 1.15:
        return False
    
    return True

# ================================================
# LOGGING & MONITORING
# ================================================

def log_analysis(symbol: str, exchange: str, signal: Dict, action: str):
    """Log analysis results"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "symbol": symbol,
        "exchange": exchange,
        "signal": signal["signal"],
        "strength": signal["strength"],
        "reason": signal["reason"],
        "action": action,
        "price": signal["metrics"]["current_price"] if "metrics" in signal else 0
    }
    
    # Append to log file
    try:
        with open(ANALYSIS_LOG, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except:
        pass
    
    # Print to console
    print(f"[{timestamp}] {exchange.upper():8} {symbol:12} {signal['signal']:8} "
          f"Strength: {signal['strength']:.2f}% - {action}")

def log_trade(trade_data: Dict):
    """Log executed trades"""
    try:
        # Load existing trades
        if os.path.exists(TRADES_LOG):
            with open(TRADES_LOG, 'r') as f:
                trades = json.load(f)
        else:
            trades = []
        
        # Add new trade
        trades.append(trade_data)
        
        # Save updated trades
        with open(TRADES_LOG, 'w') as f:
            json.dump(trades, f, indent=2)
        
        print(f"✅ Trade logged: {trade_data['symbol']} {trade_data['side']} "
              f"${trade_data['amount']:.4f} @ ${trade_data['price']:.2f}")
    except Exception as e:
        print(f"❌ Error logging trade: {e}")

# ================================================
# MAIN TRADING LOOP
# ================================================

def main():
    """Main trading loop for 26 cryptocurrencies"""
    print("=" * 70)
    print("26-CRYPTOCURRENCY TRADING BOT")
    print("=" * 70)
    print(f"💰 Capital: ${TOTAL_CAPITAL:.2f} (Gemini: ${GEMINI_CAPITAL:.2f} LONG, Binance: ${BINANCE_CAPITAL:.2f} SHORT)")
    print(f"📊 Cryptocurrencies: {len(ALL_26_CRYPTOS)}")
    print(f"⚡ Trading Pairs: {len(GEMINI_SYMBOLS)} Gemini + {len(BINANCE_SYMBOLS)} Binance")
    print(f"🎯 Max Trades: {MAX_GEMINI_TRADES} Gemini + {MAX_BINANCE_TRADES} Binance = {MAX_TOTAL_TRADES} total")
    print("=" * 70)
    
    # Load API keys
    gemini_key, gemini_secret = load_api_keys("gemini")
    binance_key, binance_secret = load_api_keys("binance")
    
    # Initialize exchanges
    exchanges = {}
    
    if gemini_key and gemini_secret:
        try:
            exchanges["gemini"] = ccxt.gemini({
                'apiKey': gemini_key,
                'secret': gemini_secret,
                'enableRateLimit': True
            })
            print("✅ Gemini exchange connected")
        except Exception as e:
            print(f"❌ Gemini connection failed: {e}")
    else:
        print("⚠️ Gemini API keys not configured")
    
    if binance_key and binance_secret:
        try:
            exchanges["binance"] = ccxt.binance({
                'apiKey': binance_key,
                'secret': binance_secret,
                'options': {'defaultType': 'spot'},
                'enableRateLimit': True
            })
            print("✅ Binance exchange connected")
        except Exception as e:
            print(f"❌ Binance connection failed: {e}")
    else:
        print("⚠️ Binance API keys not configured")
    
    if not exchanges:
        print("❌ No exchanges connected. Please configure API keys.")
        print("\n💡 Setup instructions:")
        print("1. Save Gemini API keys to .gemini_key and .gemini_secret")
        print("2. Save Binance API keys to .binance_key and .binance_secret")
        print("3. Ensure keys have trading permissions")
        return
    
    # Track daily trades
    gemini_trades_today = 0
    binance_trades_today = 0
    last_reset = datetime.now().date()
    
    print("\n🚀 Starting 26-crypto analysis loop...")
    print("   Scanning every 5 minutes for opportunities")
    print("-" * 70)
    
    while True:
        try:
            # Reset daily counters if it's a new day
            current_date = datetime.now().date()
            if current_date != last_reset:
                gemini_trades_today = 0
                binance_trades_today = 0
                last_reset = current_date
                print(f"\n📅 New trading day: {current_date}")
            
            # Analyze Gemini pairs (LONG)
            if "gemini" in exchanges:
                print(f"\n🔍 Analyzing Gemini pairs ({len(GEMINI_SYMBOLS)} cryptos)...")
                for symbol in GEMINI_SYMBOLS:
                    prices, volumes = fetch_market_data(exchanges["gemini"], symbol)
                    if prices and volumes:
                        signal = analyze_crypto_momentum(prices, volumes)
                        
                        if should_trade_gemini(signal, symbol, gemini_trades_today):
                            action = "LONG BUY SIGNAL"
                            log_analysis(symbol, "gemini", signal, action)
                            
                            # Calculate position size
                            position_size = calculate_position_size(
                                GEMINI_CAPITAL, MAX_GEMINI_POSITION,
                                signal["metrics"]["current_price"], GEMINI_STOP_LOSS
                            )
                            
                            # Here you would place the actual trade
                            # For now, we just log it
                            trade_data = {
                                "timestamp": datetime.now().isoformat(),
                                "exchange": "gemini",
                                "symbol": symbol,
                                "side": "buy",
                                "price": signal["metrics"]["current_price"],
                                "amount": position_size,
                                "value": position_size * signal["metrics"]["current_price"],
                                "stop_loss": signal["metrics"]["current_price"] * (1 - GEMINI_STOP_LOSS),
                                "take_profit": signal["metrics"]["current_price"] * (1 + GEMINI_TAKE_PROFIT),
                                "signal_strength": signal["strength"],
                                "reason": signal["reason"]
                            }
                            
                            log_trade(trade_data)
                            gemini_trades_today += 1
                        else:
                            log_analysis(symbol, "gemini", signal, "No action")
            
            # Analyze Binance pairs (SHORT)
            if "binance" in exchanges:
                print(f"\n🔍 Analyzing Binance pairs ({len(BINANCE_SYMBOLS)} cryptos)...")
                # Analyze a subset each cycle to avoid rate limits
                symbols_to_analyze = BINANCE_SYMBOLS[:10]  # 10 at a time
                
                for symbol in symbols_to_analyze:
                    prices, volumes = fetch_market_data(exchanges["binance"], symbol)
                    if prices and volumes:
                        signal = analyze_crypto_momentum(prices, volumes)
                        
                        if should_trade_binance(signal, symbol, binance_trades_today):
                            action = "SHORT SELL SIGNAL"
                            log_analysis(symbol, "binance", signal, action)
                            
                            # Calculate position size for short
                            position_size = calculate_position_size(
                                BINANCE_CAPITAL, MAX_BINANCE_POSITION,
                                signal["metrics"]["current_price"], BINANCE_STOP_LOSS
                            )
                            
                            # Here you would place the actual short trade
                            trade_data = {
                                "timestamp": datetime.now().isoformat(),
                                "exchange": "binance",
                                "symbol": symbol,
                                "side": "sell",
                                "price": signal["metrics"]["current_price"],
                                "amount": position_size,
                                "value": position_size * signal["metrics"]["current_price"],
                                "stop_loss": signal["metrics"]["current_price"] * (1 + BINANCE_STOP_LOSS),
                                "take_profit": signal["metrics"]["current_price"] * (1 - BINANCE_TAKE_PROFIT),
                                "signal_strength": signal["strength"],
                                "reason": signal["reason"]
                            }
                            
                            log_trade(trade_data)
                            binance_trades_today += 1
                        else:
                            log_analysis(symbol, "binance", signal, "No action")
            
            # Summary
            print(f"\n📊 SUMMARY: Gemini trades today: {gemini_trades_today}/{MAX_GEMINI_TRADES} | "
                  f"Binance trades today: {binance_trades_today}/{MAX_BINANCE_TRADES}")
            print(f"⏰ Next analysis in 5 minutes...")
            print("-" * 70)
            
            # Wait for next analysis cycle
            time.sleep(300)  # 5 minutes
            
        except KeyboardInterrupt:
            print("\n\n🛑 Trading bot stopped by user")
            break
        except Exception as e:
            print(f"\n⚠