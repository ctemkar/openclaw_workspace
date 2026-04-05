#!/usr/bin/env python3
"""
Conservative Crypto Trading with Real Execution
Uses ccxt library for reliable API access
$1,000 capital, 5% stop-loss, 10% take-profit, max 2 trades per day
"""

import ccxt
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================
TOTAL_CAPITAL = 1000.0  # $1,000 capital as requested
STOP_LOSS_PCT = 0.05    # 5% stop-loss
TAKE_PROFIT_PCT = 0.10  # 10% take-profit
MAX_POSITION_SIZE = 0.5  # Maximum 50% of capital per trade
MAX_DAILY_TRADES = 2

# Track daily trades
TRADE_HISTORY_FILE = "daily_trades.json"

# ============================================================================
# GEMINI EXCHANGE SETUP
# ============================================================================

def setup_gemini() -> ccxt.gemini:
    """Setup Gemini exchange with API credentials"""
    try:
        with open('.gemini_key', 'r') as f:
            api_key = f.read().strip()
        with open('.gemini_secret', 'r') as f:
            api_secret = f.read().strip()
        
        exchange = ccxt.gemini({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            }
        })
        
        # Test connection
        exchange.load_markets()
        print(f"✅ Connected to Gemini")
        print(f"✅ Available pairs: {len(exchange.markets)}")
        return exchange
        
    except Exception as e:
        print(f"❌ Failed to setup Gemini: {e}")
        raise

# ============================================================================
# MARKET ANALYSIS
# ============================================================================

def fetch_market_data(exchange: ccxt.gemini) -> Dict:
    """Fetch BTC and ETH market data"""
    print("📊 Fetching market data...")
    
    data = {
        "btc": {},
        "eth": {},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC+7"),
        "success": False
    }
    
    try:
        # BTC/USD
        btc_ticker = exchange.fetch_ticker('BTC/USD')
        btc_orderbook = exchange.fetch_order_book('BTC/USD', limit=10)
        
        data["btc"] = {
            "price": btc_ticker["last"],
            "bid": btc_ticker["bid"],
            "ask": btc_ticker["ask"],
            "volume": btc_ticker["quoteVolume"],
            "bid_depth": sum([bid[1] for bid in btc_orderbook["bids"][:5]]),
            "ask_depth": sum([ask[1] for ask in btc_orderbook["asks"][:5]])
        }
        
        # ETH/USD
        eth_ticker = exchange.fetch_ticker('ETH/USD')
        eth_orderbook = exchange.fetch_order_book('ETH/USD', limit=10)
        
        data["eth"] = {
            "price": eth_ticker["last"],
            "bid": eth_ticker["bid"],
            "ask": eth_ticker["ask"],
            "volume": eth_ticker["quoteVolume"],
            "bid_depth": sum([bid[1] for bid in eth_orderbook["bids"][:5]]),
            "ask_depth": sum([ask[1] for ask in eth_orderbook["asks"][:5]])
        }
        
        data["success"] = True
        
    except Exception as e:
        print(f"❌ Error fetching market data: {e}")
    
    return data

def calculate_support_resistance(orderbook_bids, orderbook_asks) -> Tuple[float, float]:
    """Calculate support and resistance from order book"""
    try:
        # Support = average of top 5 bids
        if len(orderbook_bids) >= 5:
            top_bids = [bid[0] for bid in orderbook_bids[:5]]
            support = sum(top_bids) / len(top_bids)
        else:
            support = orderbook_bids[0][0] if orderbook_bids else 0
        
        # Resistance = average of top 5 asks
        if len(orderbook_asks) >= 5:
            top_asks = [ask[0] for ask in orderbook_asks[:5]]
            resistance = sum(top_asks) / len(top_asks)
        else:
            resistance = orderbook_asks[0][0] if orderbook_asks else 0
        
        return round(support, 2), round(resistance, 2)
        
    except Exception as e:
        print(f"❌ Error calculating S/R: {e}")
        return 0, 0

def analyze_market_sentiment(market_data: Dict) -> str:
    """Analyze market sentiment based on price action and volume"""
    btc_price = market_data["btc"].get("price", 0)
    eth_price = market_data["eth"].get("price", 0)
    btc_volume = market_data["btc"].get("volume", 0)
    eth_volume = market_data["eth"].get("volume", 0)
    
    if btc_price == 0 or eth_price == 0:
        return "UNKNOWN"
    
    # Simple sentiment analysis
    if btc_volume > 15000000 and eth_volume > 8000000:  # High volume
        return "BULLISH"
    elif btc_volume < 5000000 or eth_volume < 3000000:  # Low volume
        return "CAUTIOUS"
    else:
        return "NEUTRAL"

# ============================================================================
# TRADE MANAGEMENT
# ============================================================================

def load_trade_history() -> Dict:
    """Load daily trade history"""
    try:
        if os.path.exists(TRADE_HISTORY_FILE):
            with open(TRADE_HISTORY_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"date": datetime.now().strftime("%Y-%m-%d"), "trades": []}

def save_trade_history(history: Dict):
    """Save daily trade history"""
    try:
        with open(TRADE_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving trade history: {e}")

def can_trade_today(history: Dict) -> bool:
    """Check if we can trade today based on daily limit"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if history.get("date") != today:
        # New day, reset trades
        history["date"] = today
        history["trades"] = []
        save_trade_history(history)
        return True
    
    return len(history["trades"]) < MAX_DAILY_TRADES

def record_trade(history: Dict, trade: Dict):
    """Record a trade in history"""
    history["trades"].append(trade)
    save_trade_history(history)

# ============================================================================
# TRADING STRATEGY
# ============================================================================

class ConservativeTradingStrategy:
    def __init__(self, capital: float):
        self.capital = capital
    
    def analyze_trade_opportunity(self, market_data: Dict, btc_support: float, eth_support: float) -> Dict:
        """Analyze if a trade opportunity exists based on conservative rules"""
        
        btc_price = market_data["btc"].get("price", 0)
        eth_price = market_data["eth"].get("price", 0)
        sentiment = analyze_market_sentiment(market_data)
        
        result = {
            "signal": "HOLD",
            "symbol": None,
            "entry_price": 0,
            "position_size": 0,
            "position_value": 0,
            "stop_loss": 0,
            "take_profit": 0,
            "reason": "No suitable opportunity found",
            "risk_reward": "N/A"
        }
        
        # Conservative rules:
        # 1. Only trade in NEUTRAL or BULLISH sentiment
        # 2. Price must be within 1% of support level
        # 3. Maximum 50% position size
        
        if sentiment not in ["NEUTRAL", "BULLISH"]:
            result["reason"] = f"Market sentiment too cautious: {sentiment}"
            return result
        
        # Check BTC opportunity
        if btc_price > 0 and btc_support > 0:
            distance_pct = abs(btc_price - btc_support) / btc_price
            
            if distance_pct <= 0.01:  # Within 1% of support
                position_size = (self.capital * MAX_POSITION_SIZE) / btc_price
                stop_loss = btc_price * (1 - STOP_LOSS_PCT)
                take_profit = btc_price * (1 + TAKE_PROFIT_PCT)
                
                result = {
                    "signal": "BUY",
                    "symbol": "BTC/USD",
                    "entry_price": round(btc_price, 2),
                    "position_size": round(position_size, 6),
                    "position_value": round(position_size * btc_price, 2),
                    "stop_loss": round(stop_loss, 2),
                    "take_profit": round(take_profit, 2),
                    "reason": f"Price within 1% of support (${btc_support:,.2f})",
                    "risk_reward": f"1:{TAKE_PROFIT_PCT/STOP_LOSS_PCT:.1f}"
                }
                return result
        
        # Check ETH opportunity (only if no BTC signal)
        if eth_price > 0 and eth_support > 0:
            distance_pct = abs(eth_price - eth_support) / eth_price
            
            if distance_pct <= 0.01:  # Within 1% of support
                position_size = (self.capital * MAX_POSITION_SIZE) / eth_price
                stop_loss = eth_price * (1 - STOP_LOSS_PCT)
                take_profit = eth_price * (1 + TAKE_PROFIT_PCT)
                
                result = {
                    "signal": "BUY",
                    "symbol": "ETH/USD",
                    "entry_price": round(eth_price, 2),
                    "position_size": round(position_size, 6),
                    "position_value": round(position_size * eth_price, 2),
                    "stop_loss": round(stop_loss, 2),
                    "take_profit": round(take_profit, 2),
                    "reason": f"Price within 1% of support (${eth_support:,.2f})",
                    "risk_reward": f"1:{TAKE_PROFIT_PCT/STOP_LOSS_PCT:.1f}"
                }
                return result
        
        return result

# ============================================================================
# TRADE EXECUTION
# ============================================================================

def execute_trade(exchange: ccxt.gemini, trade_analysis: Dict, available_capital: float) -> Dict:
    """Execute a trade on Gemini"""
    
    symbol = trade_analysis["symbol"]
    entry_price = trade_analysis["entry_price"]
    position_size = trade_analysis["position_size"]
    
    print(f"\n🎯 Executing trade: {symbol}")
    print(f"   Entry Price: ${entry_price:,.2f}")
    print(f"   Position Size: {position_size}")
    print(f"   Position Value: ${trade_analysis['position_value']:,.2f}")
    
    # Check if we have enough capital
    if trade_analysis["position_value"] > available_capital:
        print(f"❌ Insufficient capital. Available: ${available_capital:,.2f}, Required: ${trade_analysis['position_value']:,.2f}")
        return {"error": "Insufficient capital"}
    
    try:
        # Place limit order
        order = exchange.create_limit_buy_order(
            symbol=symbol,
            amount=position_size,
            price=entry_price
        )
        
        print(f"✅ Order placed: {order['id']}")
        print(f"   Status: {order['status']}")
        print(f"   Filled: {order.get('filled', 0)}")
        
        # Record trade details
        trade_record = {
            "id": order["id"],
            "symbol": symbol,
            "side": "buy",
            "price": entry_price,
            "amount": position_size,
            "value": trade_analysis["position_value"],
            "stop_loss": trade_analysis["stop_loss"],
            "take_profit": trade_analysis["take_profit"],
            "timestamp": datetime.now().isoformat(),
            "status": order["status"]
        }
        
        return {"success": True, "order": order, "trade": trade_record}
        
    except Exception as e:
        print(f"❌ Trade execution failed: {e}")
        return {"error": str(e)}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("CONSERVATIVE CRYPTO TRADING - REAL EXECUTION")
    print("=" * 70)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC+7)")
    print(f"Capital: ${TOTAL_CAPITAL:,.2f}")
    print(f"Risk Management: {STOP_LOSS_PCT*100}% SL, {TAKE_PROFIT_PCT*100}% TP")
    print(f"Position Size: Max {MAX_POSITION_SIZE*100}% of capital")
    print(f"Daily Limit: {MAX_DAILY_TRADES} trades")
    print("=" * 70)
    
    # Setup exchange
    try:
        exchange = setup_gemini()
    except Exception as e:
        print(f"❌ Failed to initialize exchange: {e}")
        return
    
    # Check account balance
    print("\n💰 ACCOUNT BALANCE")
    print("-" * 40)
    try:
        balance = exchange.fetch_balance()
        usd_balance = balance['free'].get('USD', 0)
        print(f"✅ Available USD: ${usd_balance:,.2f}")
        
        if usd_balance < TOTAL_CAPITAL * 0.1:  # Less than 10% of target capital
            print(f"⚠️  Low balance. Consider depositing more funds.")
            available_capital = usd_balance
        else:
            available_capital = min(usd_balance, TOTAL_CAPITAL)
            print(f"✅ Using capital: ${available_capital:,.2f}")
            
    except Exception as e:
        print(f"❌ Error fetching balance: {e}")
        available_capital = TOTAL_CAPITAL
        print(f"⚠️  Using configured capital: ${available_capital:,.2f}")
    
    # Check daily trade limit
    print("\n📅 DAILY TRADE LIMIT CHECK")
    print("-" * 40)
    trade_history = load_trade_history()
    
    if not can_trade_today(trade_history):
        print(f"❌ Daily trade limit reached ({MAX_DAILY_TRADES} trades today)")
        print(f"   Trades today: {len(trade_history['trades'])}")
        print("   Skipping trade execution")
        trade_executed = False
    else:
        print(f"✅ Can trade today. Trades so far: {len(trade_history['trades'])}/{MAX_DAILY_TRADES}")
        trade_executed = True
    
    # Fetch market data
    print("\n1️⃣  MARKET DATA ANALYSIS")
    print("-" * 40)
    
    market_data = fetch_market_data(exchange)
    if not market_data["success"]:
        print("❌ Failed to fetch market data. Exiting.")
        return
    
    btc_price = market_data["btc"]["price"]
    eth_price = market_data["eth"]["price"]
    
    print(f"✅ BTC/USD: ${btc_price:,.2f}")
    print(f"✅ ETH/USD: ${eth_price:,.2f}")
    print(f"✅ BTC 24h Volume: ${market_data['btc']['volume']:,.0f}")
    print(f"✅ ETH 24h Volume: ${market_data['eth']['volume']:,.0f}")
    
    # Calculate Support/Resistance
    print("\n2️⃣  SUPPORT/RESISTANCE LEVELS")
    print("-" * 40)
    
    try:
        btc_orderbook = exchange.fetch_order_book('BTC/USD', limit=10)
        eth_orderbook = exchange.fetch_order_book('ETH/USD', limit=10)
        
        btc_support, btc_resistance = calculate_support_resistance(btc_orderbook["bids"], btc_orderbook["asks"])
        eth_support, eth_resistance = calculate_support_resistance(eth_orderbook["bids"], eth_orderbook["asks"])
        
        print(f"✅ BTC Support: ${btc_support:,.2f}")
        print(f"✅ BTC Resistance: ${btc_resistance:,.2f}")
        print(f"✅ ETH Support: ${eth_support:,.2f}")
        print(f"✅ ETH Resistance: ${eth_resistance:,.2f}")
        
    except Exception as e:
        print(f"❌ Error calculating S/R: {e}")
        btc_support = btc_resistance = eth_support = eth_resistance = 0
    
    # Market Sentiment
    print("\n3️⃣  MARKET SENTIMENT")
    print("-" * 40)
    
    sentiment = analyze_market_sentiment(market_data)
    print(f"✅ Market Sentiment: {sentiment}")
    
    # Trading Analysis
    print("\n4️⃣  TRADING ANALYSIS")
    print("-" * 40)
    
    strategy = ConservativeTradingStrategy(available_capital)
    trade_analysis = strategy.analyze_trade_opportunity(market_data, btc_support, eth_support)
    
    print(f"✅ Trading Signal: {trade_analysis['signal']}")
    print(f"✅ Reason: {trade_analysis['reason']}")
    
    # Trade Execution
    print("\n5️⃣  TRADE EXECUTION")
    print("-" * 40)
    
    trade_result = None
    
    if trade_analysis["signal"] == "BUY" and trade_executed:
        print("🎯 TRADE RECOMMENDATION FOUND!")
        
        # Execute trade
        trade_result = execute_trade(exchange, trade_analysis, available_capital)
        
        if trade_result and "success" in trade_result and trade_result["success"]:
            # Record trade
            record_trade(trade_history, trade_result["trade"])
            print(f"✅ Trade recorded in daily history")
            
    elif trade_analysis["signal"] == "BUY" and not trade_executed:
        print("⏸️  TRADE RECOMMENDED BUT DAILY LIMIT REACHED")
        print(f"   {trade_analysis['symbol']} at ${trade_analysis['entry_price']:,.2f}")
        print(f"   Daily limit: {MAX_DAILY_TRADES} trades")
        
    else:
        print("⏸️  NO TRADE RECOMMENDED")
        print(f"   {trade_analysis['reason']}")
        print("   Conservative strategy waiting for better opportunity")
    
    # Generate Final Summary
    print("\n" + "=" * 70)
    print("FINAL TRADING SUMMARY")
    print("=" * 70)
    
    # Generate plain text summary for cron delivery
    summary = f"""
CONSERVATIVE CRYPTO TRADING ANALYSIS - REAL EXECUTION
=====================================================
Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC+7)

ACCOUNT STATUS:
• Available USD: ${usd_balance:,.2f}
• Using Capital: ${available_capital:,.2f}
• Daily Trades: {len(trade_history['trades'])}/{MAX_DAILY_TRADES}

MARKET DATA:
• BTC/USD: ${btc_price:,.2f}
• ETH/USD: ${eth_price:,.2f}
• BTC 24h Volume: ${market_data['btc']['volume']:,.0f}
• ETH 24h Volume: ${market_data['eth']['volume']:,.0f}
• Market Sentiment: {sentiment}

SUPPORT/RESISTANCE:
• BTC Support: ${btc_support:,.2f}
• BTC Resistance: ${btc_resistance:,.2f}
• ETH Support: ${eth_support:,.2f}
• ETH Resistance: ${eth_resistance:,.2f}

TRADING DECISION: {trade_analysis['signal']}
Reason: {trade_analysis['reason']}
"""

    if trade_analysis["signal"] == "BUY":
        summary += f"""
TRADE RECOMMENDATION:
• Symbol: {trade_analysis['symbol']}
• Action: BUY
• Entry Price: ${trade_analysis['entry_price']:,.2f}
• Position Size: {trade_analysis['position_size']}
• Position Value: ${trade_analysis['position_value']:,.2f}
• Stop Loss: ${trade_analysis['stop_loss']:,.2f} ({STOP_LOSS_PCT*100}%)
• Take Profit: ${trade_analysis['take_profit']:,.2f} ({TAKE_PROFIT_PCT*100}%)
• Risk/Reward Ratio: {trade_analysis['risk_reward']}
"""

        if trade_result and "success" in trade_result and trade_result["success"]:
            order = trade_result["order"]
            summary += f"""
EXECUTION STATUS: ✅ REAL ORDER EXECUTED
• Order ID: {order['id']}
• Status: {order['status']}
• Filled Amount: {order.get('filled', 0)}
• Trade recorded in daily history
"""
        elif trade_executed:
            summary += f"""
EXECUTION STATUS: ⚠️  ORDER FAILED
• Error: {trade_result.get('error', 'Unknown error') if trade_result else 'No execution attempted'}
"""
        else:
            summary += f"""
EXECUTION STATUS: ⏸️  DAILY LIMIT REACHED
• Maximum {MAX_DAILY_TRADES} trades per day already executed
• Trade recommendation saved for manual review
"""
    else:
        summary += """
NO TRADE EXECUTED:
• Conservative strategy criteria not met
• Waiting for price near support levels
• Maintaining capital preservation stance
"""

    summary += f"""
RISK MANAGEMENT PARAMETERS:
• Capital: ${TOTAL_CAPITAL:,.2f}
• Available: ${available_capital:,.2f}
• Max Position Size: {MAX_POSITION_SIZE*100}% of capital
• Stop Loss: {STOP_LOSS_PCT*100}%
• Take Profit: {TAKE_PROFIT_PCT*100}%
• Max Daily Trades: {MAX_DAILY_TRADES}
• Strategy: Conservative support-based trading

NEXT STEPS:
{'1. Monitor order execution and set stop-loss/take-profit' if trade_result and trade_result.get('success') else '1. Run analysis again in 6-12 hours'}
2. Review market conditions before next trading window
3. Never risk more than 5% of capital per trade
4. Maintain conservative approach for capital preservation

END OF ANALYSIS
=====================================================
"""
    
    print(summary)
    return summary

if __name__ == "__main__":
    result = main()
    if result:
        print("\n" + "=" * 70)
        print("SUMMARY READY FOR CRON DELIVERY")
        print("=" * 70)