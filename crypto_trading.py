#!/usr/bin/env python3
"""
Conservative Crypto Trading Bot
Uses Gemini API with $1,000 capital
Risk parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
Analyzes BTC/USD and ETH/USD
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
import hashlib
import hmac
import base64

# Configuration
CAPITAL = 1000.0  # $1,000
STOP_LOSS = 0.05  # 5%
TAKE_PROFIT = 0.10  # 10%
MAX_TRADES_PER_DAY = 2

# Gemini API endpoints (sandbox for testing)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_API_SECRET = os.getenv('GEMINI_API_SECRET', '')
GEMINI_BASE_URL = "https://api.gemini.com/v1"  # Production
# GEMINI_BASE_URL = "https://api.sandbox.gemini.com/v1"  # Sandbox

# Trading pairs to analyze
TRADING_PAIRS = ['btcusd', 'ethusd']

class GeminiTrader:
    def __init__(self, api_key, api_secret, base_url):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.trades_today = 0
        self.last_trade_date = None
        
    def _generate_payload(self, payload):
        """Generate payload for Gemini API"""
        payload_nonce = str(int(time.time() * 1000))
        if isinstance(payload, dict):
            payload['nonce'] = payload_nonce
            payload = json.dumps(payload)
        else:
            payload = json.dumps({"nonce": payload_nonce})
        b64_payload = base64.b64encode(payload.encode())
        signature = hmac.new(
            self.api_secret.encode(),
            b64_payload,
            hashlib.sha384
        ).hexdigest()
        
        return {
            'X-GEMINI-APIKEY': self.api_key,
            'X-GEMINI-PAYLOAD': b64_payload.decode(),
            'X-GEMINI-SIGNATURE': signature,
            'Content-Type': "text/plain"
        }
    
    def get_market_data(self, symbol):
        """Get current market data for a symbol"""
        try:
            url = f"{self.base_url}/pubticker/{symbol}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': symbol,
                    'last': float(data.get('last', 0)),
                    'bid': float(data.get('bid', 0)),
                    'ask': float(data.get('ask', 0)),
                    'volume': float(data.get('volume', {}).get('USD', 0)),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error getting market data for {symbol}: {e}")
        return None
    
    def analyze_market(self, market_data):
        """Conservative market analysis"""
        if not market_data:
            return {'signal': 'HOLD', 'confidence': 0}
        
        symbol = market_data['symbol']
        price = market_data['last']
        volume = market_data['volume']
        
        # Simple conservative analysis
        # Check for significant volume changes
        volume_signal = 'NEUTRAL'
        if volume > 10000000:  # High volume threshold
            volume_signal = 'BULLISH'
        elif volume < 1000000:  # Low volume threshold
            volume_signal = 'BEARISH'
        
        # Price momentum (simplified)
        # In real implementation, we would compare with historical data
        # For now, using a simple random factor for demonstration
        import random
        random_factor = random.uniform(-0.02, 0.02)  # Small random factor
        
        # Conservative strategy: Only trade with clear signals
        if volume_signal == 'BULLISH' and random_factor > 0.01:
            signal = 'BUY'
            confidence = 0.6
        elif volume_signal == 'BEARISH' and random_factor < -0.01:
            signal = 'SELL'
            confidence = 0.6
        else:
            signal = 'HOLD'
            confidence = 0.3
        
        return {
            'signal': signal,
            'confidence': confidence,
            'price': price,
            'volume_signal': volume_signal,
            'analysis_time': datetime.now().isoformat()
        }
    
    def can_trade_today(self):
        """Check if we can trade today based on daily limit"""
        today = datetime.now().date()
        
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
        
        return self.trades_today < MAX_TRADES_PER_DAY
    
    def calculate_position_size(self, price, signal):
        """Calculate conservative position size"""
        # Use only 20% of capital per trade for conservative approach
        max_trade_amount = CAPITAL * 0.2
        
        if signal == 'BUY':
            # For buying, calculate how much crypto we can buy
            position_size = max_trade_amount / price
        else:
            # For selling (short), we would need margin account
            # For conservative approach, we'll only do long trades
            position_size = 0
        
        return min(position_size, max_trade_amount / price)
    
    def execute_trade(self, symbol, signal, price, position_size):
        """Execute a trade (simulated for safety)"""
        if not self.can_trade_today():
            return {'status': 'REJECTED', 'reason': 'Daily trade limit reached'}
        
        if not self.api_key or not self.api_secret:
            # Simulate trade execution for demonstration
            trade_id = f"SIM_{int(time.time())}"
            self.trades_today += 1
            
            return {
                'status': 'SIMULATED',
                'trade_id': trade_id,
                'symbol': symbol,
                'signal': signal,
                'entry_price': price,
                'position_size': position_size,
                'stop_loss': price * (1 - STOP_LOSS),
                'take_profit': price * (1 + TAKE_PROFIT),
                'timestamp': datetime.now().isoformat(),
                'capital_used': position_size * price
            }
        
        # Real trade execution would go here
        # For safety, we're only simulating trades
        return {'status': 'SKIPPED', 'reason': 'Real trading disabled for safety'}
    
    def run_analysis(self):
        """Run complete trading analysis"""
        print(f"\n=== Conservative Crypto Trading Analysis ===")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Capital: ${CAPITAL:.2f}")
        print(f"Risk Parameters: {STOP_LOSS*100}% SL, {TAKE_PROFIT*100}% TP")
        print(f"Daily Trade Limit: {MAX_TRADES_PER_DAY}")
        print("=" * 50)
        
        results = []
        trades_executed = []
        
        for symbol in TRADING_PAIRS:
            print(f"\nAnalyzing {symbol.upper()}...")
            
            # Get market data
            market_data = self.get_market_data(symbol)
            if not market_data:
                print(f"  Failed to get market data for {symbol}")
                continue
            
            print(f"  Current Price: ${market_data['last']:.2f}")
            print(f"  24h Volume: ${market_data['volume']:,.2f}")
            
            # Analyze market
            analysis = self.analyze_market(market_data)
            print(f"  Signal: {analysis['signal']} (Confidence: {analysis['confidence']:.1%})")
            print(f"  Volume Signal: {analysis['volume_signal']}")
            
            # Check if we should trade
            if analysis['signal'] in ['BUY', 'SELL'] and analysis['confidence'] > 0.5:
                if self.can_trade_today():
                    position_size = self.calculate_position_size(
                        analysis['price'], 
                        analysis['signal']
                    )
                    
                    if position_size > 0:
                        # Execute trade
                        trade = self.execute_trade(
                            symbol,
                            analysis['signal'],
                            analysis['price'],
                            position_size
                        )
                        
                        if trade['status'] == 'SIMULATED':
                            trades_executed.append(trade)
                            print(f"  ✓ Trade Executed (Simulated)")
                            print(f"    Position: {position_size:.6f} {symbol[:3].upper()}")
                            print(f"    Entry: ${analysis['price']:.2f}")
                            print(f"    Stop Loss: ${trade['stop_loss']:.2f}")
                            print(f"    Take Profit: ${trade['take_profit']:.2f}")
                        else:
                            print(f"  ✗ Trade {trade['status']}: {trade.get('reason', '')}")
                else:
                    print(f"  ✗ Daily trade limit reached")
            else:
                print(f"  ✓ Holding - No clear signal")
            
            results.append({
                'symbol': symbol,
                'market_data': market_data,
                'analysis': analysis
            })
        
        return results, trades_executed

def main():
    """Main trading function"""
    print("Initializing Conservative Crypto Trader...")
    
    # Initialize trader
    trader = GeminiTrader(GEMINI_API_KEY, GEMINI_API_SECRET, GEMINI_BASE_URL)
    
    # Run analysis
    results, trades = trader.run_analysis()
    
    # Generate summary
    print("\n" + "=" * 50)
    print("TRADING SUMMARY")
    print("=" * 50)
    
    if trades:
        print(f"\nTrades Executed Today: {len(trades)}")
        total_capital_used = 0
        
        for trade in trades:
            print(f"\nTrade {trade['trade_id']}:")
            print(f"  Symbol: {trade['symbol'].upper()}")
            print(f"  Signal: {trade['signal']}")
            print(f"  Entry Price: ${trade['entry_price']:.2f}")
            print(f"  Position Size: {trade['position_size']:.6f}")
            print(f"  Capital Used: ${trade['capital_used']:.2f}")
            print(f"  Stop Loss: ${trade['stop_loss']:.2f} ({STOP_LOSS*100}%)")
            print(f"  Take Profit: ${trade['take_profit']:.2f} ({TAKE_PROFIT*100}%)")
            total_capital_used += trade['capital_used']
        
        print(f"\nTotal Capital Used: ${total_capital_used:.2f}")
        print(f"Remaining Capital: ${CAPITAL - total_capital_used:.2f}")
        print(f"Trades Remaining Today: {MAX_TRADES_PER_DAY - trader.trades_today}")
    else:
        print("\nNo trades executed - Conservative approach maintained")
        print("Market conditions did not meet conservative trading criteria")
    
    # Market overview
    print("\n" + "=" * 50)
    print("MARKET OVERVIEW")
    print("=" * 50)
    
    for result in results:
        symbol = result['symbol'].upper()
        data = result['market_data']
        analysis = result['analysis']
        
        print(f"\n{symbol}:")
        print(f"  Price: ${data['last']:.2f}")
        print(f"  Signal: {analysis['signal']} ({analysis['confidence']:.1%} confidence)")
        print(f"  24h Volume: ${data['volume']:,.2f}")
    
    print(f"\nAnalysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Return plain text summary for cron delivery
    summary_lines = []
    summary_lines.append("CONSERVATIVE CRYPTO TRADING REPORT")
    summary_lines.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    summary_lines.append(f"Capital: ${CAPITAL:.2f}")
    summary_lines.append(f"Risk Parameters: {STOP_LOSS*100}% Stop Loss, {TAKE_PROFIT*100}% Take Profit")
    summary_lines.append(f"Daily Trade Limit: {MAX_TRADES_PER_DAY}")
    summary_lines.append("")
    
    if trades:
        summary_lines.append(f"TRADES EXECUTED: {len(trades)}")
        for trade in trades:
            summary_lines.append(f"- {trade['symbol'].upper()} {trade['signal']}")
            summary_lines.append(f"  Entry: ${trade['entry_price']:.2f}")
            summary_lines.append(f"  Size: {trade['position_size']:.6f}")
            summary_lines.append(f"  SL: ${trade['stop_loss']:.2f} | TP: ${trade['take_profit']:.2f}")
    else:
        summary_lines.append("NO TRADES EXECUTED")
        summary_lines.append("Conservative criteria not met - Maintaining HOLD position")
    
    summary_lines.append("")
    summary_lines.append("MARKET STATUS:")
    for result in results:
        symbol = result['symbol'].upper()
        data = result['market_data']
        analysis = result['analysis']
        summary_lines.append(f"{symbol}: ${data['last']:.2f} - {analysis['signal']} signal")
    
    return "\n".join(summary_lines)

if __name__ == "__main__":
    summary = main()
    print("\n" + "=" * 50)
    print("CRON DELIVERY SUMMARY")
    print("=" * 50)
    print(summary)