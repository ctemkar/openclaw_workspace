#!/usr/bin/env python3
"""
Conservative Crypto Trading Analysis and Execution
Risk parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
$1,000 capital investment
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
import hashlib
import hmac
import base64
from typing import Dict, List, Optional, Tuple
import sys

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_API_SECRET = os.environ.get("GEMINI_API_SECRET", "")
GEMINI_API_BASE = "https://api.gemini.com"

# Trading Parameters
INITIAL_CAPITAL = 1000.00  # $1,000
MAX_DAILY_TRADES = 2
STOP_LOSS_PERCENT = 5.0    # 5%
TAKE_PROFIT_PERCENT = 10.0 # 10%
MAX_POSITION_SIZE = 0.5    # 50% of capital per trade
PAIRS_TO_MONITOR = ["BTCUSD", "ETHUSD"]

class GeminiAPIClient:
    """Gemini API client for trading"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        
    def _generate_payload(self, payload: Dict) -> str:
        """Generate payload for Gemini API"""
        return json.dumps(payload)
    
    def _generate_signature(self, payload: str, endpoint: str) -> str:
        """Generate HMAC signature for Gemini API"""
        b64_payload = base64.b64encode(payload.encode())
        signature = hmac.new(
            self.api_secret.encode(),
            b64_payload + endpoint.encode(),
            hashlib.sha384
        ).hexdigest()
        return signature
    
    def _make_request(self, method: str, endpoint: str, payload: Dict = None) -> Dict:
        """Make authenticated request to Gemini API"""
        url = f"{GEMINI_API_BASE}{endpoint}"
        payload_str = self._generate_payload(payload) if payload else "{}"
        
        headers = {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": self.api_key,
            "X-GEMINI-PAYLOAD": base64.b64encode(payload_str.encode()).decode(),
            "X-GEMINI-SIGNATURE": self._generate_signature(payload_str, endpoint),
            "Cache-Control": "no-cache"
        }
        
        try:
            if method == "POST":
                response = self.session.post(url, headers=headers)
            else:
                response = self.session.get(url, headers=headers)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return {"error": str(e)}
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker price"""
        endpoint = f"/v1/pubticker/{symbol.lower()}"
        return self._make_request("GET", endpoint)
    
    def get_order_book(self, symbol: str) -> Dict:
        """Get order book for symbol"""
        endpoint = f"/v1/book/{symbol.lower()}"
        return self._make_request("GET", endpoint)
    
    def place_order(self, symbol: str, amount: float, price: float, 
                   side: str, order_type: str = "exchange limit") -> Dict:
        """Place a new order"""
        endpoint = "/v1/order/new"
        payload = {
            "request": "/v1/order/new",
            "nonce": int(time.time() * 1000),
            "symbol": symbol.lower(),
            "amount": str(amount),
            "price": str(price),
            "side": side,
            "type": order_type,
            "options": ["maker-or-cancel"]
        }
        return self._make_request("POST", endpoint, payload)
    
    def get_account_balance(self) -> Dict:
        """Get account balances"""
        endpoint = "/v1/balances"
        payload = {
            "request": "/v1/balances",
            "nonce": int(time.time() * 1000)
        }
        return self._make_request("POST", endpoint, payload)
    
    def get_past_trades(self, symbol: str, limit: int = 50) -> Dict:
        """Get past trades for symbol"""
        endpoint = f"/v1/mytrades"
        payload = {
            "request": "/v1/mytrades",
            "nonce": int(time.time() * 1000),
            "symbol": symbol.lower(),
            "limit_trades": limit
        }
        return self._make_request("POST", endpoint, payload)

class MarketAnalyzer:
    """Analyze market conditions for conservative trading"""
    
    @staticmethod
    def calculate_support_resistance(order_book: Dict, levels: int = 5) -> Tuple[List[float], List[float]]:
        """Calculate support and resistance levels from order book"""
        bids = order_book.get("bids", [])
        asks = order_book.get("asks", [])
        
        # Get top N bid/ask levels
        support_levels = [float(bid["price"]) for bid in bids[:levels]]
        resistance_levels = [float(ask["price"]) for ask in asks[:levels]]
        
        return support_levels, resistance_levels
    
    @staticmethod
    def analyze_momentum(prices: List[float], period: int = 20) -> str:
        """Analyze price momentum"""
        if len(prices) < period:
            return "NEUTRAL"
        
        recent = prices[-period:]
        older = prices[-period*2:-period]
        
        if not older:
            return "NEUTRAL"
        
        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)
        
        change = ((recent_avg - older_avg) / older_avg) * 100
        
        if change > 2:
            return "BULLISH"
        elif change < -2:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    @staticmethod
    def calculate_volatility(prices: List[float], period: int = 20) -> float:
        """Calculate price volatility"""
        if len(prices) < period:
            return 0.0
        
        recent = prices[-period:]
        returns = [(recent[i] - recent[i-1]) / recent[i-1] for i in range(1, len(recent))]
        
        if not returns:
            return 0.0
        
        volatility = (sum([r**2 for r in returns]) / len(returns)) ** 0.5
        return volatility * 100  # Return as percentage

class ConservativeTradingStrategy:
    """Conservative trading strategy with strict risk management"""
    
    def __init__(self, capital: float, max_daily_trades: int, 
                 stop_loss: float, take_profit: float):
        self.capital = capital
        self.max_daily_trades = max_daily_trades
        self.stop_loss = stop_loss / 100  # Convert to decimal
        self.take_profit = take_profit / 100  # Convert to decimal
        self.trades_today = 0
        self.last_trade_date = None
        
    def should_trade_today(self) -> bool:
        """Check if we can trade today based on daily limit"""
        today = datetime.now().date()
        
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
        
        return self.trades_today < self.max_daily_trades
    
    def calculate_position_size(self, current_price: float, risk_per_trade: float = 0.02) -> Tuple[float, float]:
        """Calculate position size based on risk parameters"""
        # Risk 2% of capital per trade (conservative)
        risk_amount = self.capital * risk_per_trade
        
        # Calculate position size based on stop loss
        position_value = risk_amount / self.stop_loss
        
        # Convert to coin amount
        coin_amount = position_value / current_price
        
        # Don't exceed max position size
        max_position_value = self.capital * MAX_POSITION_SIZE
        if position_value > max_position_value:
            position_value = max_position_value
            coin_amount = position_value / current_price
        
        return coin_amount, position_value
    
    def generate_trading_signals(self, symbol: str, current_price: float, 
                                support_levels: List[float], 
                                resistance_levels: List[float],
                                momentum: str, volatility: float) -> Dict:
        """Generate conservative trading signals"""
        signals = {
            "symbol": symbol,
            "current_price": current_price,
            "action": "HOLD",
            "reason": "No clear signal",
            "confidence": 0,
            "entry_price": 0,
            "stop_loss": 0,
            "take_profit": 0,
            "position_size": 0
        }
        
        # Conservative trading rules
        if not self.should_trade_today():
            signals["reason"] = "Daily trade limit reached"
            return signals
        
        # Check if price is near support (buy opportunity)
        nearest_support = min(support_levels, key=lambda x: abs(x - current_price))
        support_distance = abs(current_price - nearest_support) / current_price * 100
        
        # Check if price is near resistance (sell opportunity)
        nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price))
        resistance_distance = abs(current_price - nearest_resistance) / current_price * 100
        
        # High volatility - avoid trading
        if volatility > 5:
            signals["reason"] = f"High volatility ({volatility:.2f}%) - too risky"
            return signals
        
        # Conservative buy signal: near support AND bullish momentum
        if support_distance < 1 and momentum == "BULLISH":
            signals["action"] = "BUY"
            signals["reason"] = f"Near support (${nearest_support:.2f}), bullish momentum"
            signals["confidence"] = 65
            signals["entry_price"] = current_price
            signals["stop_loss"] = current_price * (1 - self.stop_loss)
            signals["take_profit"] = current_price * (1 + self.take_profit)
            coin_amount, position_value = self.calculate_position_size(current_price)
            signals["position_size"] = coin_amount
            
        # Conservative sell signal: near resistance AND bearish momentum  
        elif resistance_distance < 1 and momentum == "BEARISH":
            signals["action"] = "SELL"
            signals["reason"] = f"Near resistance (${nearest_resistance:.2f}), bearish momentum"
            signals["confidence"] = 60
            signals["entry_price"] = current_price
            signals["stop_loss"] = current_price * (1 + self.stop_loss)
            signals["take_profit"] = current_price * (1 - self.take_profit)
            coin_amount, position_value = self.calculate_position_size(current_price)
            signals["position_size"] = coin_amount
        
        return signals

def main():
    """Main trading execution function"""
    print("=" * 60)
    print("CONSERVATIVE CRYPTO TRADING ANALYSIS")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Capital: ${INITIAL_CAPITAL:,.2f}")
    print(f"Risk Parameters: {STOP_LOSS_PERCENT}% SL, {TAKE_PROFIT_PERCENT}% TP")
    print(f"Max Daily Trades: {MAX_DAILY_TRADES}")
    print("=" * 60)
    
    # Check API credentials
    if not GEMINI_API_KEY or not GEMINI_API_SECRET:
        print("ERROR: Gemini API credentials not found in environment variables")
        print("Please set GEMINI_API_KEY and GEMINI_API_SECRET environment variables")
        return
    
    # Initialize components
    api_client = GeminiAPIClient(GEMINI_API_KEY, GEMINI_API_SECRET)
    analyzer = MarketAnalyzer()
    strategy = ConservativeTradingStrategy(
        capital=INITIAL_CAPITAL,
        max_daily_trades=MAX_DAILY_TRADES,
        stop_loss=STOP_LOSS_PERCENT,
        take_profit=TAKE_PROFIT_PERCENT
    )
    
    trading_summary = {
        "timestamp": datetime.now().isoformat(),
        "capital": INITIAL_CAPITAL,
        "pairs_analyzed": [],
        "signals_generated": [],
        "trades_executed": [],
        "market_conditions": {},
        "risk_assessment": "CONSERVATIVE"
    }
    
    # Analyze each pair
    for pair in PAIRS_TO_MONITOR:
        print(f"\nAnalyzing {pair}...")
        
        try:
            # Get current market data
            ticker = api_client.get_ticker(pair)
            if "error" in ticker:
                print(f"  Error fetching {pair} ticker: {ticker['error']}")
                continue
            
            current_price = float(ticker.get("last", 0))
            bid_price = float(ticker.get("bid", 0))
            ask_price = float(ticker.get("ask", 0))
            
            print(f"  Current Price: ${current_price:,.2f}")
            print(f"  Bid/Ask: ${bid_price:,.2f} / ${ask_price:,.2f}")
            
            # Get order book for support/resistance analysis
            order_book = api_client.get_order_book(pair)
            if "error" in order_book:
                print(f"  Error fetching {pair} order book: {order_book['error']}")
                continue
            
            support_levels, resistance_levels = analyzer.calculate_support_resistance(order_book)
            
            print(f"  Support Levels: {[f'${x:,.2f}' for x in support_levels[:3]]}")
            print(f"  Resistance Levels: {[f'${x:,.2f}' for x in resistance_levels[:3]]}")
            
            # Analyze momentum (using simulated price history)
            # In production, you would fetch historical prices
            simulated_prices = [current_price * (1 + i/100) for i in range(-10, 11)]
            momentum = analyzer.analyze_momentum(simulated_prices)
            volatility = analyzer.calculate_volatility(simulated_prices)
            
            print(f"  Momentum: {momentum}")
            print(f"  Volatility: {volatility:.2f}%")
            
            # Generate trading signals
            signals = strategy.generate_trading_signals(
                symbol=pair,
                current_price=current_price,
                support_levels=support_levels,
                resistance_levels=resistance_levels,
                momentum=momentum,
                volatility=volatility
            )
            
            print(f"  Signal: {signals['action']} - {signals['reason']}")
            print(f"  Confidence: {signals['confidence']}%")
            
            if signals["action"] != "HOLD":
                print(f"  Entry: ${signals['entry_price']:,.2f}")
                print(f"  Stop Loss: ${signals['stop_loss']:,.2f}")
                print(f"  Take Profit: ${signals['take_profit']:,.2f}")
                print(f"  Position Size: {signals['position_size']:.6f} {pair[:3]}")
                
                # Check account balance before executing
                balance = api_client.get_account_balance()
                if "error" not in balance:
                    print(f"  Account balance retrieved successfully")
                    
                    # In a real implementation, you would execute the trade here
                    # For safety, we'll simulate the trade execution
                    if signals["action"] == "BUY":
                        print(f"  [SIMULATION] Would execute BUY order:")
                        print(f"    Symbol: {pair}")
                        print(f"    Amount: {signals['position_size']:.6f}")
                        print(f"    Price: ${signals['entry_price']:,.2f}")
                        print(f"    Value: ${signals['position_size'] * signals['entry_price']:,.2f}")
                        
                        # Simulated trade execution
                        simulated_trade = {
                            "symbol": pair,
                            "side": "buy",
                            "amount": signals["position_size"],
                            "price": signals["entry_price"],
                            "value": signals["position_size"] * signals["entry_price"],
                            "stop_loss": signals["stop_loss"],
                            "take_profit": signals["take_profit"],
                            "status": "SIMULATED_EXECUTION",
                            "timestamp": datetime.now().isoformat()
                        }
                        trading_summary["trades_executed"].append(simulated_trade)
                        
                    elif signals["action"] == "SELL":
                        print(f"  [SIMULATION] Would execute SELL order:")
                        print(f"    Symbol: {pair}")
                        print(f"    Amount: {signals['position_size']:.6f}")
                        print(f"    Price: ${signals['entry_price']:,.2f}")
                        
                        # Simulated trade execution
                        simulated_trade = {
                            "symbol": pair,
                            "side": "sell",
                            "amount": signals["position_size"],
                            "price": signals["entry_price"],
                            "value": signals["position_size"] * signals["entry_price"],
                            "stop_loss": signals["stop_loss"],
                            "take_profit": signals["take_profit"],
                            "status": "SIMULATED_EXECUTION",
                            "timestamp": datetime.now().isoformat()
                        }
                        trading_summary["trades_executed"].append(simulated_trade)
            
            # Store analysis results
            pair_analysis = {
                "pair": pair,
                "current_price": current_price,
                "bid": bid_price,
                "ask": ask_price,
                "support_levels": support_levels[:3],
                "resistance_levels": resistance_levels[:3],
                "momentum": momentum,
                "volatility": volatility,
                "signal": signals["action"],
                "signal_reason": signals["reason"],
                "confidence": signals["confidence"]
            }
            trading_summary["pairs_analyzed"].append(pair_analysis)
            trading_summary["signals_generated"].append(signals)
            
        except Exception as e:
            print(f"  Error analyzing {pair}: {e}")
            continue
    
    # Get market conditions summary
    trading_summary["market_conditions"] = {
        "total_pairs": len(PAIRS_TO_MONITOR),
        "analysis_time": datetime.now().isoformat(),
        "risk_level": "CONSERVATIVE",
        "trading_allowed": strategy.should_trade_today(),
        "trades_today": strategy.trades_today
    }
    
    # Print final summary
    print("\n" + "=" * 60)
    print("TRADING SUMMARY")
    print("=" * 60)
    
    total_signals = len([s for s in trading_summary["signals_generated"] if s["action"] != "HOLD"])
    print(f"Pairs Analyzed: {len(trading_summary['pairs_analyzed'])}")
    print(f"Trading Signals Generated: {total_signals}")
    print(f"Trades Executed (Simulated): {len(trading_summary['trades_executed'])}")
    print(f"Trades Available Today: {MAX_DAILY_TRADES - strategy.trades_today}")
    
    if trading_summary["trades_executed"]:
        print("\nSimulated Trade Details:")
        for trade in trading_summary["trades_executed"]:
            print(f"  {trade['symbol']} {trade['side'].upper()}:")
            print(f"    Amount: {trade['amount']:.6f}")
            print(f"    Price: ${trade['price']:,.2f}")
            print(f"    Value: ${trade['value']:,.2f}")
            print(f"    Stop Loss: ${trade['stop_loss']:,.2f}")
            print(f"    Take Profit: ${trade['take_profit']:,.2f}")
    
    print("\nRisk Assessment:")
    print(f"  Strategy: Conservative")
    print(f"  Max Position Size: {MAX_POSITION_SIZE*100}% of capital")
    print(f"  Stop Loss: {STOP_LOSS_PERCENT}%")
    print(f"  Take Profit: {TAKE_PROFIT_PERCENT}%")
    print(f"  Max Daily Trades: {MAX_DAILY_TRADES}")
    
    print("\nMarket Outlook:")
    for analysis in trading_summary["pairs_analyzed"]:
        print(f"  {analysis['pair']}: {analysis['signal']} - {analysis['signal_reason']}")
    
    print("\n" + "=" * 60)
    print("NOTE: This is a simulation. Real trades require:")
    print("1. Actual Gemini API credentials with funded account")
    print("2. Proper risk management implementation")
    print("3. Real-time market data feeds")
    print("4. Live order execution with proper error handling")
    print("=" * 60)
    
    # Save summary to file
    summary_file = f"trading_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(trading_summary, f, indent=2)
    
    print(f"\nSummary saved to: {summary_file}")
    
    # Generate plain text summary for cron delivery
    plain_text_summary = generate_plain_text_summary(trading_summary)
    print("\n" + "=" * 60)
    print("PLAIN TEXT SUMMARY FOR DELIVERY:")
    print("=" * 60)
    print(plain_text_summary)

def generate_plain_text_summary(summary: Dict) -> str:
    """Generate plain text summary for cron delivery"""
    lines = []
    lines.append("CONSERVATIVE CRYPTO TRADING ANALYSIS")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    lines.append(f"Capital: ${INITIAL_CAPITAL:,.2f}")
    lines.append("")
    
    lines.append("MARKET ANALYSIS:")
    for analysis in summary["pairs_analyzed"]:
        lines.append(f"  {analysis['pair']}:")
        lines.append(f"    Price: ${analysis['current_price']:,.2f}")
        lines.append(f"    Signal: {analysis['signal']}")
        lines.append(f"    Reason: {analysis['signal_reason']}")
        lines.append(f"    Confidence: {analysis['confidence']}%")
        lines.append(f"    Momentum: {analysis['momentum']}")
        lines.append(f"    Volatility: {analysis['volatility']:.2f}%")
    
    lines.append("")
    lines.append("RISK PARAMETERS:")
    lines.append(f"  Stop Loss: {STOP_LOSS_PERCENT}%")
    lines.append(f"  Take Profit: {TAKE_PROFIT_PERCENT}%")
    lines.append(f"  Max Daily Trades: {MAX_DAILY_TRADES}")
    lines.append(f"  Max Position Size: {MAX_POSITION_SIZE*100}% of capital")
    
    lines.append("")
    lines.append("TRADING STATUS:")
    lines.append(f"  Trades Executed (Simulated): {len(summary['trades_executed'])}")
    lines.append(f"  Trades Available Today: {MAX_DAILY_TRADES - summary['market_conditions']['trades_today']}")
    
    if summary["trades_executed"]:
        lines.append("")
        lines.append("SIMULATED TRADES:")
        for trade in summary["trades_executed"]:
            lines.append(f"  {trade['symbol']} {trade['side'].upper()}:")
            lines.append(f"    Amount: {trade['amount']:.6f}")
            lines.append(f"    Price: ${trade['price']:,.2f}")
            lines.append(f"    Value: ${trade['value']:,.2f}")
    
    lines.append("")
    lines.append("RECOMMENDATION:")
    if any(s["action"] != "HOLD" for s in summary["signals_generated"]):
        lines.append("  Conservative trading signals detected.")
        lines.append("  Consider executing with strict risk management.")
    else:
        lines.append("  No clear trading signals at this time.")
        lines.append("  Maintain HOLD position and monitor market.")
    
    lines.append("")
    lines.append("DISCLAIMER: This is simulation/analysis only.")
    lines.append("Real trading involves risk of loss.")
    lines.append("Consult with financial advisor before trading.")
    
    return "\n".join(lines)

if __name__ == "__main__":
    main()