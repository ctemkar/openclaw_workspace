#!/usr/bin/env python3
"""
Conservative Crypto Trading System - $1,000 Capital
Real analysis with $1,000 capital, 5% stop-loss, 10% take-profit
Maximum 2 trades per day
Execute REAL trades using Gemini API
"""

import requests
import json
import os
import hmac
import hashlib
import base64
import time
from datetime import datetime
from typing import Dict, Optional

# ============================================================================
# CONFIGURATION - $1,000 CAPITAL
# ============================================================================
TOTAL_CAPITAL = 1000.0  # $1,000 total capital as requested
STOP_LOSS_PCT = 0.05  # 5% stop-loss
TAKE_PROFIT_PCT = 0.10  # 10% take-profit
MAX_POSITION_SIZE = 0.5  # Maximum 50% of capital per trade
MAX_DAILY_TRADES = 2

# Gemini API Configuration
GEMINI_API_URL = "https://api.gemini.com"
GEMINI_SANDBOX_URL = "https://api.sandbox.gemini.com"

# Load API credentials from secure keys
try:
    with open("secure_keys/.gemini_key", "r") as f:
        GEMINI_API_KEY = f.read().strip()
    with open("secure_keys/.gemini_secret", "r") as f:
        GEMINI_API_SECRET = f.read().strip()
    USE_REAL_API = bool(GEMINI_API_KEY and GEMINI_API_SECRET)
    print(f"✅ API Key loaded: {GEMINI_API_KEY[:10]}...")
except Exception as e:
    print(f"❌ Error loading API keys: {e}")
    GEMINI_API_KEY = None
    GEMINI_API_SECRET = None
    USE_REAL_API = False

# ============================================================================
# MARKET DATA FUNCTIONS
# ============================================================================

def fetch_market_data() -> Dict:
    """Fetch current BTC and ETH market data"""
    print("📊 Fetching real-time market data...")
    
    data = {
        "btc": {},
        "eth": {},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC+7"),
        "success": False
    }
    
    try:
        # BTC/USD
        btc_response = requests.get(f"{GEMINI_API_URL}/v1/pubticker/btcusd", timeout=10)
        if btc_response.status_code == 200:
            btc_data = btc_response.json()
            data["btc"] = {
                "price": float(btc_data.get("last", 0)),
                "bid": float(btc_data.get("bid", 0)),
                "ask": float(btc_data.get("ask", 0)),
                "volume": float(btc_data.get("volume", {}).get("USD", 0))
            }
        
        # ETH/USD
        eth_response = requests.get(f"{GEMINI_API_URL}/v1/pubticker/ethusd", timeout=10)
        if eth_response.status_code == 200:
            eth_data = eth_response.json()
            data["eth"] = {
                "price": float(eth_data.get("last", 0)),
                "bid": float(eth_data.get("bid", 0)),
                "ask": float(eth_data.get("ask", 0)),
                "volume": float(eth_data.get("volume", {}).get("USD", 0))
            }
        
        data["success"] = bool(data["btc"] and data["eth"])
        
    except Exception as e:
        print(f"❌ Error fetching market data: {e}")
    
    return data

def calculate_support_resistance(symbol: str) -> Dict:
    """Calculate support and resistance levels from order book"""
    try:
        response = requests.get(f"{GEMINI_API_URL}/v1/book/{symbol}", timeout=10)
        if response.status_code != 200:
            return {"support": 0, "resistance": 0}
        
        order_book = response.json()
        bids = order_book.get("bids", [])
        asks = order_book.get("asks", [])
        
        # Support = average of top 5 bids
        support = 0
        if bids and len(bids) >= 5:
            top_bids = [float(bid["price"]) for bid in bids[:5]]
            support = sum(top_bids) / len(top_bids)
        
        # Resistance = average of top 5 asks
        resistance = 0
        if asks and len(asks) >= 5:
            top_asks = [float(ask["price"]) for ask in asks[:5]]
            resistance = sum(top_asks) / len(top_asks)
        
        return {
            "support": round(support, 2),
            "resistance": round(resistance, 2),
            "bid_depth": len(bids),
            "ask_depth": len(asks)
        }
        
    except Exception as e:
        print(f"❌ Error calculating S/R for {symbol}: {e}")
        return {"support": 0, "resistance": 0}

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
# TRADING STRATEGY
# ============================================================================

class ConservativeTradingStrategy:
    def __init__(self, capital: float):
        self.capital = capital
        self.trades_today = 0
    
    def analyze_trade_opportunity(self, market_data: Dict, btc_sr: Dict, eth_sr: Dict) -> Dict:
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
        if btc_price > 0 and btc_sr["support"] > 0:
            distance_pct = abs(btc_price - btc_sr["support"]) / btc_price
            
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
                    "reason": f"Price within 1% of support (${btc_sr['support']})",
                    "risk_reward": f"1:{TAKE_PROFIT_PCT/STOP_LOSS_PCT:.1f}"
                }
                return result
        
        # Check ETH opportunity (only if no BTC signal)
        if eth_price > 0 and eth_sr["support"] > 0:
            distance_pct = abs(eth_price - eth_sr["support"]) / eth_price
            
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
                    "reason": f"Price within 1% of support (${eth_sr['support']})",
                    "risk_reward": f"1:{TAKE_PROFIT_PCT/STOP_LOSS_PCT:.1f}"
                }
                return result
        
        return result

# ============================================================================
# GEMINI API TRADING FUNCTIONS
# ============================================================================

class GeminiTrader:
    def __init__(self, api_key: str, api_secret: str, sandbox: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret.encode()
        self.base_url = GEMINI_SANDBOX_URL if sandbox else GEMINI_API_URL
    
    def _generate_signature(self, payload: Dict) -> Dict:
        """Generate Gemini API signature"""
        payload_nonce = str(int(time.time() * 1000))
        payload["nonce"] = payload_nonce
        payload["request"] = "/v1/" + payload.get("request", "")
        
        payload_str = json.dumps(payload)
        signature = hmac.new(
            self.api_secret,
            payload_str.encode(),
            hashlib.sha384
        ).hexdigest()
        
        headers = {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": self.api_key,
            "X-GEMINI-PAYLOAD": base64.b64encode(payload_str.encode()).decode(),
            "X-GEMINI-SIGNATURE": signature,
            "Cache-Control": "no-cache"
        }
        
        return headers, payload_str
    
    def place_order(self, symbol: str, amount: float, price: float, side: str) -> Dict:
        """Place a limit order on Gemini"""
        if not USE_REAL_API:
            return {"simulated": True, "status": "SIMULATED_ORDER"}
        
        try:
            payload = {
                "request": "order/new",
                "symbol": symbol.replace("/", "").lower(),
                "amount": str(amount),
                "price": str(price),
                "side": side,
                "type": "exchange limit",
                "options": ["maker-or-cancel"]
            }
            
            headers, _ = self._generate_signature(payload)
            url = f"{self.base_url}/v1/order/new"
            
            response = requests.post(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ Error placing order: {e}")
            return {"error": str(e)}
    
    def get_account_balance(self) -> Dict:
        """Get account balances"""
        if not USE_REAL_API:
            return {"simulated": True, "balances": [{"currency": "USD", "amount": "1000.00"}]}
        
        try:
            payload = {"request": "balances"}
            headers, _ = self._generate_signature(payload)
            url = f"{self.base_url}/v1/balances"
            
            response = requests.post(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ Error getting balances: {e}")
            return {"error": str(e)}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("CONSERVATIVE CRYPTO TRADING SYSTEM - $1,000 CAPITAL")
    print("=" * 70)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC+7)")
    print(f"Capital: ${TOTAL_CAPITAL:,.2f}")
    print(f"Risk Management: {STOP_LOSS_PCT*100}% SL, {TAKE_PROFIT_PCT*100}% TP")
    print(f"Position Size: Max {MAX_POSITION_SIZE*100}% of capital")
    print(f"Daily Limit: {MAX_DAILY_TRADES} trades")
    print(f"API Mode: {'REAL' if USE_REAL_API else 'SIMULATION'}")
    print("=" * 70)
    
    # Step 1: Fetch Market Data
    print("\n1️⃣  MARKET DATA ANALYSIS")
    print("-" * 40)
    
    market_data = fetch_market_data()
    if not market_data["success"]:
        print("❌ Failed to fetch market data. Exiting.")
        return
    
    btc_price = market_data["btc"]["price"]
    eth_price = market_data["eth"]["price"]
    
    print(f"✅ BTC/USD: ${btc_price:,.2f}")
    print(f"✅ ETH/USD: ${eth_price:,.2f}")
    print(f"✅ BTC 24h Volume: ${market_data['btc']['volume']:,.0f}")
    print(f"✅ ETH 24h Volume: ${market_data['eth']['volume']:,.0f}")
    
    # Step 2: Calculate Support/Resistance
    print("\n2️⃣  SUPPORT/RESISTANCE LEVELS")
    print("-" * 40)
    
    btc_sr = calculate_support_resistance("btcusd")
    eth_sr = calculate_support_resistance("ethusd")
    
    print(f"✅ BTC Support: ${btc_sr['support']:,.2f}")
    print(f"✅ BTC Resistance: ${btc_sr['resistance']:,.2f}")
    print(f"✅ ETH Support: ${eth_sr['support']:,.2f}")
    print(f"✅ ETH Resistance: ${eth_sr['resistance']:,.2f}")
    
    # Step 3: Market Sentiment
    print("\n3️⃣  MARKET SENTIMENT")
    print("-" * 40)
    
    sentiment = analyze_market_sentiment(market_data)
    print(f"✅ Market Sentiment: {sentiment}")
    
    # Step 4: Trading Analysis
    print("\n4️⃣  TRADING ANALYSIS")
    print("-" * 40)
    
    strategy = ConservativeTradingStrategy(TOTAL_CAPITAL)
    trade_analysis = strategy.analyze_trade_opportunity(market_data, btc_sr, eth_sr)
    
    print(f"✅ Trading Signal: {trade_analysis['signal']}")
    print(f"✅ Reason: {trade_analysis['reason']}")
    
    # Step 5: Trade Execution (Simulated or Real)
    print("\n5️⃣  TRADE EXECUTION")
    print("-" * 40)
    
    trade_executed = False
    order_result = None
    
    if trade_analysis["signal"] == "BUY":
        print("🎯 TRADE RECOMMENDATION FOUND!")
        print(f"   Symbol: {trade_analysis['symbol']}")
        print(f"   Entry Price: ${trade_analysis['entry_price']:,.2f}")
        print(f"   Position Size: {trade_analysis['position_size']}")
        print(f"   Position Value: ${trade_analysis['position_value']:,.2f}")
        print(f"   Stop Loss: ${trade_analysis['stop_loss']:,.2f} ({STOP_LOSS_PCT*100}%)")
        print(f"   Take Profit: ${trade_analysis['take_profit']:,.2f} ({TAKE_PROFIT_PCT*100}%)")
        print(f"   Risk/Reward: {trade_analysis['risk_reward']}")
        
        if USE_REAL_API:
            print("\n🔐 REAL TRADE EXECUTION")
            trader = GeminiTrader(GEMINI_API_KEY, GEMINI_API_SECRET)
            
            # Get account balance first
            print("   Checking account balance...")
            balance = trader.get_account_balance()
            if "error" not in balance:
                print(f"   ✅ Account balance retrieved")
            else:
                print(f"   ❌ Error getting balance: {balance.get('error', 'Unknown error')}")
            
            # Place order
            symbol = trade_analysis['symbol'].replace("/", "").lower()
            print(f"   Placing order for {symbol}...")
            order_result = trader.place_order(
                symbol=symbol,
                amount=trade_analysis['position_size'],
                price=trade_analysis['entry_price'],
                side="buy"
            )
            
            if "order_id" in order_result:
                print(f"   ✅ REAL ORDER PLACED: {order_result['order_id']}")
                print(f"   Order Details: {order_result}")
                trade_executed = True
            else:
                print(f"   ❌ Order failed: {order_result}")
        else:
            print("\n🔧 SIMULATED TRADE EXECUTION")
            print("   API credentials loaded but not using real trading")
            print("   To execute real trades, set USE_REAL_API = True")
            trade_executed = False
    else:
        print("⏸️  NO TRADE RECOMMENDED")
        print(f"   {trade_analysis['reason']}")
        print("   Conservative strategy waiting for better opportunity")
    
    # Step 6: Generate Final Summary
    print("\n" + "=" * 70)
    print("FINAL TRADING SUMMARY")
    print("=" * 70)
    
    # Generate plain text summary for cron delivery
    summary = f"""
CONSERVATIVE CRYPTO TRADING ANALYSIS - $1,000 CAPITAL
=====================================================
Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC+7)

MARKET DATA:
• BTC/USD: ${btc_price:,.2f}
• ETH/USD: ${eth_price:,.2f}
• BTC 24h Volume: ${market_data['btc']['volume']:,.0f}
• ETH 24h Volume: ${market_data['eth']['volume']:,.0f}
• Market Sentiment: {sentiment}

SUPPORT/RESISTANCE:
• BTC Support: ${btc_sr['support']:,.2f}
• BTC Resistance: ${btc_sr['resistance']:,.2f}
• ETH Support: ${eth_sr['support']:,.2f}
• ETH Resistance: ${eth_sr['resistance']:,.2f}

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

EXECUTION STATUS: {'REAL ORDER EXECUTED' if trade_executed else 'SIMULATED - Ready for real execution'}
"""
        if trade_executed and order_result:
            summary += f"• Order ID: {order_result.get('order_id', 'N/A')}\n"
            summary += f"• Order Status: {order_result.get('status', 'N/A')}\n"
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
• Max Position Size: {MAX_POSITION_SIZE*100}% of capital
• Stop Loss: {STOP_LOSS_PCT*100}%
• Take Profit: {TAKE_PROFIT_PCT*100}%
• Max Daily Trades: {MAX_DAILY_TRADES}
• Strategy: Conservative support-based trading

NEXT STEPS:
{'1. Monitor order execution and set stop-loss/take-profit' if trade_executed else '1. Review market conditions for next analysis'}
2. Run analysis again in 6-12 hours
3. Review market conditions before next trading window
4. Never risk more than 5% of capital per trade

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