#!/usr/bin/env python3
"""
Conservative Crypto Trading Analysis and Execution
Real trading with $1,000 capital using Gemini API
Risk parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
"""

import ccxt
import os
import json
import time
import subprocess
from datetime import datetime, timedelta
import requests
import statistics
from typing import Dict, List, Optional, Tuple

# Configuration
CAPITAL = 1000.0  # $1,000 investment
MAX_TRADES_PER_DAY = 2
STOP_LOSS_PCT = 0.05  # 5%
TAKE_PROFIT_PCT = 0.10  # 10%
MAX_POSITION_SIZE = 0.2  # Max 20% of capital per trade

# Trading pairs
PAIRS = ["BTC/USD", "ETH/USD"]

# Files
TRADES_LOG = "completed_trades.json"
TRADING_LOG = "conservative_trading.log"
CONFIG_FILE = "trading_config.json"

def get_gemini_credentials() -> Tuple[str, str]:
    """Get Gemini API credentials from secure storage"""
    try:
        key = subprocess.check_output(
            ["security", "find-generic-password", "-s", "GEMINI_API_KEY", "-w"],
            timeout=2
        ).decode().strip()
        secret = subprocess.check_output(
            ["security", "find-generic-password", "-s", "GEMINI_SECRET", "-w"],
            timeout=2
        ).decode().strip()
        return key, secret
    except Exception as e:
        print(f"Error getting credentials: {e}")
        # Fallback to file-based credentials
        try:
            with open(".gemini_key", "r") as f:
                key = f.read().strip()
            with open(".gemini_secret", "r") as f:
                secret = f.read().strip()
            return key, secret
        except:
            return None, None

def log_message(message: str):
    """Log trading activity"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(TRADING_LOG, "a") as f:
        f.write(log_entry)

def load_trades() -> List[Dict]:
    """Load completed trades from log"""
    if os.path.exists(TRADES_LOG):
        try:
            with open(TRADES_LOG, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_trade(trade_data: Dict):
    """Save a completed trade"""
    trades = load_trades()
    
    # Ensure timestamp is in ISO format
    if "timestamp" not in trade_data:
        trade_data["timestamp"] = datetime.now().isoformat()
    
    trades.append(trade_data)
    with open(TRADES_LOG, "w") as f:
        json.dump(trades[-100:], f, indent=2)  # Keep last 100 trades

def get_market_data() -> Dict:
    """Get current market prices and analysis"""
    market_data = {}
    
    try:
        # Get BTC and ETH prices from CoinGecko
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum", "vs_currencies": "usd"}
        )
        if response.status_code == 200:
            data = response.json()
            market_data["BTC/USD"] = data.get("bitcoin", {}).get("usd")
            market_data["ETH/USD"] = data.get("ethereum", {}).get("usd")
    except Exception as e:
        log_message(f"Error fetching market data: {e}")
    
    return market_data

def analyze_market_sentiment(pair: str, price: float) -> Dict:
    """Analyze market sentiment for a trading pair"""
    sentiment = {
        "pair": pair,
        "price": price,
        "sentiment": "neutral",
        "confidence": 0.5,
        "support_levels": [],
        "resistance_levels": [],
        "recommendation": "hold"
    }
    
    # Simple sentiment analysis based on price movement
    # In a real implementation, this would use technical indicators
    try:
        # Get historical data for basic analysis
        exchange = ccxt.gemini({
            'apiKey': 'dummy',
            'secret': 'dummy',
            'enableRateLimit': True
        })
        
        # Calculate simple moving averages
        ohlcv = exchange.fetch_ohlcv(pair, '1h', limit=24)
        if len(ohlcv) >= 20:
            closes = [c[4] for c in ohlcv]
            sma_20 = statistics.mean(closes[-20:])
            sma_10 = statistics.mean(closes[-10:])
            
            # Determine sentiment
            if price > sma_20 and sma_10 > sma_20:
                sentiment["sentiment"] = "bullish"
                sentiment["confidence"] = 0.7
            elif price < sma_20 and sma_10 < sma_20:
                sentiment["sentiment"] = "bearish"
                sentiment["confidence"] = 0.7
            
            # Calculate support/resistance levels
            high = max([h[2] for h in ohlcv])
            low = min([l[3] for l in ohlcv])
            
            sentiment["support_levels"] = [
                low,
                low * 0.98,  # 2% below low
                low * 0.95   # 5% below low
            ]
            
            sentiment["resistance_levels"] = [
                high,
                high * 1.02,  # 2% above high
                high * 1.05   # 5% above high
            ]
            
            # Trading recommendation
            if sentiment["sentiment"] == "bullish" and price < sma_20 * 0.98:
                sentiment["recommendation"] = "buy"
            elif sentiment["sentiment"] == "bearish" and price > sma_20 * 1.02:
                sentiment["recommendation"] = "sell"
            else:
                sentiment["recommendation"] = "hold"
                
    except Exception as e:
        log_message(f"Error in sentiment analysis for {pair}: {e}")
    
    return sentiment

def can_trade_today() -> bool:
    """Check if we can execute more trades today"""
    trades = load_trades()
    today = datetime.now().date()
    
    today_trades = []
    for t in trades:
        # Handle both timestamp formats
        if "timestamp" in t:
            try:
                trade_date = datetime.fromisoformat(t["timestamp"]).date()
                if trade_date == today:
                    today_trades.append(t)
            except:
                pass
        elif "time" in t:
            # For existing trades with just time, assume today
            # This is conservative - we'll count them as today's trades
            today_trades.append(t)
    
    return len(today_trades) < MAX_TRADES_PER_DAY

def calculate_position_size(capital: float, price: float, risk_pct: float = 0.02) -> float:
    """Calculate position size based on risk management"""
    max_risk_amount = capital * risk_pct
    position_value = min(capital * MAX_POSITION_SIZE, max_risk_amount / STOP_LOSS_PCT)
    amount = position_value / price
    return amount

def execute_trade(exchange, pair: str, side: str, amount: float, price: float) -> Optional[Dict]:
    """Execute a trade on Gemini"""
    try:
        # Gemini uses limit orders with immediate-or-cancel for market-like execution
        limit_price = price * 1.01 if side == "buy" else price * 0.99
        
        params = {'options': ['immediate-or-cancel']}
        order = exchange.create_order(
            pair, 
            'limit', 
            side, 
            amount, 
            limit_price, 
            params
        )
        
        # Wait for order to fill
        time.sleep(2)
        
        # Check order status
        order_id = order['id']
        filled_order = exchange.fetch_order(order_id, pair)
        
        if filled_order['status'] == 'closed':
            trade_data = {
                "timestamp": datetime.now().isoformat(),
                "pair": pair,
                "side": side,
                "amount": amount,
                "price": price,
                "filled_price": filled_order['average'],
                "filled_amount": filled_order['filled'],
                "cost": filled_order['cost'],
                "fee": filled_order['fee']['cost'] if filled_order['fee'] else 0,
                "order_id": order_id,
                "status": "filled"
            }
            
            log_message(f"Trade executed: {side.upper()} {amount:.6f} {pair} at ${filled_order['average']:.2f}")
            return trade_data
        else:
            log_message(f"Order not filled: {order['status']}")
            exchange.cancel_order(order_id, pair)
            return None
            
    except Exception as e:
        log_message(f"Error executing trade: {e}")
        return None

def manage_positions(exchange, positions: List[Dict], current_prices: Dict):
    """Manage existing positions with stop-loss and take-profit"""
    for position in positions:
        pair = position["pair"]
        current_price = current_prices.get(pair)
        
        if not current_price:
            continue
            
        entry_price = position["price"]
        side = position["side"]
        
        if side == "buy":
            # Calculate P&L
            pnl_pct = (current_price - entry_price) / entry_price
            
            # Check stop-loss
            if pnl_pct <= -STOP_LOSS_PCT:
                log_message(f"Stop-loss triggered for {pair}: {pnl_pct:.2%}")
                # Execute sell to close position
                execute_trade(exchange, pair, "sell", position["amount"], current_price)
                
            # Check take-profit
            elif pnl_pct >= TAKE_PROFIT_PCT:
                log_message(f"Take-profit triggered for {pair}: {pnl_pct:.2%}")
                # Execute sell to close position
                execute_trade(exchange, pair, "sell", position["amount"], current_price)

def get_account_balance(exchange) -> Dict:
    """Get account balance"""
    try:
        balance = exchange.fetch_balance()
        return {
            "total": balance["total"],
            "free": balance["free"],
            "used": balance["used"]
        }
    except Exception as e:
        log_message(f"Error fetching balance: {e}")
        return {}

def conservative_trading_strategy():
    """Main conservative trading strategy"""
    log_message("=" * 60)
    log_message("CONSERVATIVE CRYPTO TRADING ANALYSIS & EXECUTION")
    log_message("=" * 60)
    
    # Get credentials
    api_key, api_secret = get_gemini_credentials()
    if not api_key or not api_secret:
        log_message("ERROR: Gemini API credentials not found")
        return
    
    # Initialize exchange
    exchange = ccxt.gemini({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',
        }
    })
    
    # Get market data
    log_message("Fetching market data...")
    market_data = get_market_data()
    
    if not market_data:
        log_message("ERROR: Could not fetch market data")
        return
    
    # Display current prices
    log_message("\nCURRENT MARKET PRICES:")
    for pair in PAIRS:
        price = market_data.get(pair)
        if price:
            log_message(f"  {pair}: ${price:,.2f}")
    
    # Analyze market sentiment
    log_message("\nMARKET SENTIMENT ANALYSIS:")
    sentiments = []
    for pair in PAIRS:
        price = market_data.get(pair)
        if price:
            sentiment = analyze_market_sentiment(pair, price)
            sentiments.append(sentiment)
            
            log_message(f"\n  {pair}:")
            log_message(f"    Price: ${price:,.2f}")
            log_message(f"    Sentiment: {sentiment['sentiment'].upper()} (confidence: {sentiment['confidence']:.1%})")
            log_message(f"    Recommendation: {sentiment['recommendation'].upper()}")
            log_message(f"    Support Levels: ${', '.join(f'{l:,.2f}' for l in sentiment['support_levels'])}")
            log_message(f"    Resistance Levels: ${', '.join(f'{l:,.2f}' for l in sentiment['resistance_levels'])}")
    
    # Check if we can trade today
    if not can_trade_today():
        log_message("\nTRADING LIMIT REACHED: Maximum 2 trades per day already executed")
        return
    
    # Get account balance
    log_message("\nACCOUNT STATUS:")
    balance = get_account_balance(exchange)
    if balance:
        usd_balance = balance.get("total", {}).get("USD", 0)
        btc_balance = balance.get("total", {}).get("BTC", 0)
        eth_balance = balance.get("total", {}).get("ETH", 0)
        
        log_message(f"  USD Balance: ${usd_balance:,.2f}")
        log_message(f"  BTC Balance: {btc_balance:.6f} (${btc_balance * market_data.get('BTC/USD', 0):,.2f})")
        log_message(f"  ETH Balance: {eth_balance:.6f} (${eth_balance * market_data.get('ETH/USD', 0):,.2f})")
        
        total_value = usd_balance + (btc_balance * market_data.get('BTC/USD', 0)) + (eth_balance * market_data.get('ETH/USD', 0))
        log_message(f"  Total Portfolio Value: ${total_value:,.2f}")
    
    # Execute trades based on conservative strategy
    log_message("\nTRADING DECISIONS:")
    
    trades_executed = 0
    for sentiment in sentiments:
        if trades_executed >= MAX_TRADES_PER_DAY:
            break
            
        pair = sentiment["pair"]
        price = sentiment["price"]
        recommendation = sentiment["recommendation"]
        
        if recommendation == "buy" and sentiment["confidence"] > 0.6:
            # Calculate position size
            amount = calculate_position_size(CAPITAL, price)
            
            if amount * price < 10:  # Minimum trade size
                log_message(f"  {pair}: Position too small (${amount * price:.2f}), skipping")
                continue
            
            log_message(f"  {pair}: EXECUTING BUY - {amount:.6f} at ~${price:,.2f}")
            
            # Execute trade
            trade = execute_trade(exchange, pair, "buy", amount, price)
            if trade:
                save_trade(trade)
                trades_executed += 1
                log_message(f"    ✓ Trade executed successfully")
            else:
                log_message(f"    ✗ Trade failed to execute")
                
        elif recommendation == "sell" and sentiment["confidence"] > 0.6:
            # Check if we have position to sell
            # This would require tracking open positions
            log_message(f"  {pair}: SELL signal detected (requires position tracking)")
    
    if trades_executed == 0:
        log_message("  No trades executed - conservative conditions not met")
    
    # Manage existing positions
    log_message("\nPOSITION MANAGEMENT:")
    positions = load_trades()
    open_positions = [p for p in positions if p.get("status") == "filled" and not p.get("closed")]
    
    if open_positions:
        log_message(f"  Managing {len(open_positions)} open positions")
        manage_positions(exchange, open_positions, market_data)
    else:
        log_message("  No open positions to manage")
    
    # Risk summary
    log_message("\nRISK MANAGEMENT SUMMARY:")
    log_message(f"  Capital: ${CAPITAL:,.2f}")
    log_message(f"  Stop-Loss: {STOP_LOSS_PCT:.1%}")
    log_message(f"  Take-Profit: {TAKE_PROFIT_PCT:.1%}")
    log_message(f"  Max Trades/Day: {MAX_TRADES_PER_DAY}")
    log_message(f"  Max Position Size: {MAX_POSITION_SIZE:.0%} of capital")
    
    log_message("\n" + "=" * 60)
    log_message("ANALYSIS COMPLETE")
    log_message("=" * 60)

if __name__ == "__main__":
    try:
        conservative_trading_strategy()
    except KeyboardInterrupt:
        log_message("\nTrading interrupted by user")
    except Exception as e:
        log_message(f"\nERROR in trading strategy: {e}")
        import traceback
        traceback.print_exc()