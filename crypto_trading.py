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
import datetime
from typing import Dict, List, Optional, Tuple
import math

# Configuration
CAPITAL = 1000.0  # $1,000 capital
STOP_LOSS = 0.05  # 5% stop-loss
TAKE_PROFIT = 0.10  # 10% take-profit
MAX_TRADES_PER_DAY = 2
SYMBOLS = ['BTCUSD', 'ETHUSD']

# Gemini API endpoints (sandbox for testing)
GEMINI_API_BASE = "https://api.gemini.com"
GEMINI_SANDBOX_BASE = "https://api.sandbox.gemini.com"

class ConservativeCryptoTrader:
    def __init__(self, api_key: str = None, api_secret: str = None, use_sandbox: bool = True):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.api_secret = api_secret or os.getenv('GEMINI_API_SECRET')
        self.use_sandbox = use_sandbox
        self.base_url = GEMINI_SANDBOX_BASE if use_sandbox else GEMINI_API_BASE
        self.trades_today = 0
        self.today_date = datetime.date.today().isoformat()
        self.load_trade_history()
        
    def load_trade_history(self):
        """Load today's trade history from file"""
        try:
            with open('trade_history.json', 'r') as f:
                history = json.load(f)
                today = datetime.date.today().isoformat()
                if history.get('date') == today:
                    self.trades_today = history.get('trades_today', 0)
        except FileNotFoundError:
            self.trades_today = 0
            
    def save_trade_history(self):
        """Save today's trade history to file"""
        history = {
            'date': datetime.date.today().isoformat(),
            'trades_today': self.trades_today
        }
        with open('trade_history.json', 'w') as f:
            json.dump(history, f)
    
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Get current market data for a symbol"""
        try:
            url = f"{self.base_url}/v1/pubticker/{symbol.lower()}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching market data for {symbol}: {e}")
        return None
    
    def analyze_market_sentiment(self, btc_data: Dict, eth_data: Dict) -> Dict:
        """Analyze market sentiment based on price action"""
        sentiment = {
            'btc_trend': 'neutral',
            'eth_trend': 'neutral',
            'overall_sentiment': 'neutral',
            'recommendation': 'hold'
        }
        
        if btc_data and eth_data:
            btc_price = float(btc_data.get('last', 0))
            btc_volume = float(btc_data.get('volume', {}).get('USD', 0))
            eth_price = float(eth_data.get('last', 0))
            eth_volume = float(eth_data.get('volume', {}).get('USD', 0))
            
            # Simple trend analysis based on 24h change
            btc_change = float(btc_data.get('percentChange24h', 0))
            eth_change = float(eth_data.get('percentChange24h', 0))
            
            if btc_change > 2.0:
                sentiment['btc_trend'] = 'bullish'
            elif btc_change < -2.0:
                sentiment['btc_trend'] = 'bearish'
                
            if eth_change > 2.0:
                sentiment['eth_trend'] = 'bullish'
            elif eth_change < -2.0:
                sentiment['eth_trend'] = 'bearish'
            
            # Overall sentiment
            bullish_count = sum([1 for trend in [sentiment['btc_trend'], sentiment['eth_trend']] if trend == 'bullish'])
            bearish_count = sum([1 for trend in [sentiment['btc_trend'], sentiment['eth_trend']] if trend == 'bearish'])
            
            if bullish_count >= 2:
                sentiment['overall_sentiment'] = 'bullish'
                sentiment['recommendation'] = 'consider_buy'
            elif bearish_count >= 2:
                sentiment['overall_sentiment'] = 'bearish'
                sentiment['recommendation'] = 'consider_sell'
            else:
                sentiment['overall_sentiment'] = 'neutral'
                sentiment['recommendation'] = 'hold'
        
        return sentiment
    
    def calculate_support_resistance(self, symbol: str, market_data: Dict) -> Dict:
        """Calculate support and resistance levels"""
        if not market_data:
            return {'support': 0, 'resistance': 0, 'current_position': 'middle'}
        
        high = float(market_data.get('high', 0))
        low = float(market_data.get('low', 0))
        current = float(market_data.get('last', 0))
        
        if high == low:
            return {'support': low, 'resistance': high, 'current_position': 'middle'}
        
        # Simple support/resistance calculation
        range_size = high - low
        support = low + (range_size * 0.3)  # 30% from bottom
        resistance = high - (range_size * 0.3)  # 30% from top
        
        position = 'middle'
        if current < support:
            position = 'near_support'
        elif current > resistance:
            position = 'near_resistance'
        
        return {
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'current_position': position
        }
    
    def should_trade(self, symbol: str, sentiment: Dict, levels: Dict) -> Tuple[bool, str, float]:
        """Determine if we should trade based on conservative strategy"""
        if self.trades_today >= MAX_TRADES_PER_DAY:
            return False, "max_trades_reached", 0.0
        
        # Conservative trading logic
        position_size = CAPITAL * 0.1  # 10% of capital per trade = $100
        
        if sentiment['overall_sentiment'] == 'bullish' and levels['current_position'] == 'near_support':
            # Good buying opportunity: bullish sentiment near support
            return True, "buy", position_size
        elif sentiment['overall_sentiment'] == 'bearish' and levels['current_position'] == 'near_resistance':
            # Good selling opportunity: bearish sentiment near resistance
            return True, "sell", position_size
        
        return False, "no_opportunity", 0.0
    
    def execute_trade(self, symbol: str, side: str, amount: float, price: float) -> Dict:
        """Execute a trade (simulated for now)"""
        if self.trades_today >= MAX_TRADES_PER_DAY:
            return {'error': 'Maximum trades per day reached'}
        
        trade_id = f"{symbol}_{side}_{int(time.time())}"
        trade_value = amount * price
        
        # Calculate stop-loss and take-profit prices
        if side == "buy":
            stop_price = price * (1 - STOP_LOSS)
            take_profit_price = price * (1 + TAKE_PROFIT)
        else:  # sell
            stop_price = price * (1 + STOP_LOSS)
            take_profit_price = price * (1 - TAKE_PROFIT)
        
        trade = {
            'trade_id': trade_id,
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': price,
            'value': trade_value,
            'stop_loss': round(stop_price, 2),
            'take_profit': round(take_profit_price, 2),
            'timestamp': datetime.datetime.now().isoformat(),
            'status': 'executed'
        }
        
        self.trades_today += 1
        self.save_trade_history()
        
        return trade
    
    def run_analysis(self) -> Dict:
        """Run complete trading analysis"""
        print(f"=== Conservative Crypto Trading Analysis ===")
        print(f"Time: {datetime.datetime.now().isoformat()}")
        print(f"Capital: ${CAPITAL}")
        print(f"Risk Parameters: {STOP_LOSS*100}% stop-loss, {TAKE_PROFIT*100}% take-profit")
        print(f"Trades today: {self.trades_today}/{MAX_TRADES_PER_DAY}")
        print()
        
        # Get market data
        btc_data = self.get_market_data('btcusd')
        eth_data = self.get_market_data('ethusd')
        
        analysis_results = {
            'timestamp': datetime.datetime.now().isoformat(),
            'capital': CAPITAL,
            'trades_today': self.trades_today,
            'max_trades_per_day': MAX_TRADES_PER_DAY,
            'market_data': {},
            'analysis': {},
            'trades_executed': []
        }
        
        symbols_data = {}
        for symbol in ['BTCUSD', 'ETHUSD']:
            data = btc_data if symbol == 'BTCUSD' else eth_data
            if data:
                symbols_data[symbol] = {
                    'price': float(data.get('last', 0)),
                    '24h_change': float(data.get('percentChange24h', 0)),
                    'volume': float(data.get('volume', {}).get('USD', 0)),
                    'high': float(data.get('high', 0)),
                    'low': float(data.get('low', 0))
                }
                print(f"{symbol}:")
                print(f"  Price: ${symbols_data[symbol]['price']:,.2f}")
                print(f"  24h Change: {symbols_data[symbol]['24h_change']:.2f}%")
                print(f"  Volume: ${symbols_data[symbol]['volume']:,.0f}")
                print(f"  High: ${symbols_data[symbol]['high']:,.2f}")
                print(f"  Low: ${symbols_data[symbol]['low']:,.2f}")
        
        analysis_results['market_data'] = symbols_data
        
        # Analyze sentiment
        sentiment = self.analyze_market_sentiment(btc_data, eth_data)
        analysis_results['analysis']['sentiment'] = sentiment
        
        print(f"\nMarket Sentiment:")
        print(f"  BTC Trend: {sentiment['btc_trend']}")
        print(f"  ETH Trend: {sentiment['eth_trend']}")
        print(f"  Overall: {sentiment['overall_sentiment']}")
        print(f"  Recommendation: {sentiment['recommendation']}")
        
        # Calculate support/resistance and check for trading opportunities
        for symbol in ['BTCUSD', 'ETHUSD']:
            data = btc_data if symbol == 'BTCUSD' else eth_data
            if data:
                levels = self.calculate_support_resistance(symbol, data)
                analysis_results['analysis'][symbol] = levels
                
                print(f"\n{symbol} Levels:")
                print(f"  Support: ${levels['support']:,.2f}")
                print(f"  Resistance: ${levels['resistance']:,.2f}")
                print(f"  Current Position: {levels['current_position']}")
                
                # Check if we should trade
                should_trade, reason, amount = self.should_trade(symbol, sentiment, levels)
                
                if should_trade and amount > 0:
                    price = symbols_data[symbol]['price']
                    side = "buy" if reason == "buy" else "sell"
                    
                    # Execute trade
                    trade = self.execute_trade(symbol, side, amount/price, price)
                    analysis_results['trades_executed'].append(trade)
                    
                    print(f"\n✅ EXECUTED TRADE:")
                    print(f"  Symbol: {symbol}")
                    print(f"  Side: {side}")
                    print(f"  Amount: ${amount:,.2f}")
                    print(f"  Price: ${price:,.2f}")
                    print(f"  Stop Loss: ${trade['stop_loss']:,.2f}")
                    print(f"  Take Profit: ${trade['take_profit']:,.2f}")
                else:
                    print(f"\n{symbol}: No trade - {reason}")
        
        print(f"\n=== Analysis Complete ===")
        print(f"Total trades executed today: {self.trades_today}/{MAX_TRADES_PER_DAY}")
        
        return analysis_results

def main():
    """Main function to run the trading analysis"""
    trader = ConservativeCryptoTrader(use_sandbox=True)
    
    try:
        results = trader.run_analysis()
        
        # Save results to file
        with open('trading_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        # Generate plain text summary
        summary = generate_summary(results)
        print("\n" + "="*50)
        print("TRADING SUMMARY")
        print("="*50)
        print(summary)
        
        return summary
        
    except Exception as e:
        error_msg = f"Error in trading analysis: {str(e)}"
        print(error_msg)
        return error_msg

def generate_summary(results: Dict) -> str:
    """Generate plain text summary of trading results"""
    summary_lines = []
    summary_lines.append("CONSERVATIVE CRYPTO TRADING SUMMARY")
    summary_lines.append("=" * 40)
    summary_lines.append(f"Time: {results.get('timestamp', 'N/A')}")
    summary_lines.append(f"Capital: ${results.get('capital', 0):,.2f}")
    summary_lines.append(f"Trades Today: {results.get('trades_today', 0)}/{results.get('max_trades_per_day', 2)}")
    summary_lines.append("")
    
    # Market data
    summary_lines.append("MARKET DATA:")
    for symbol, data in results.get('market_data', {}).items():
        summary_lines.append(f"  {symbol}:")
        summary_lines.append(f"    Price: ${data.get('price', 0):,.2f}")
        summary_lines.append(f"    24h Change: {data.get('24h_change', 0):+.2f}%")
    
    # Sentiment
    sentiment = results.get('analysis', {}).get('sentiment', {})
    summary_lines.append("")
    summary_lines.append("MARKET SENTIMENT:")
    summary_lines.append(f"  BTC Trend: {sentiment.get('btc_trend', 'N/A')}")
    summary_lines.append(f"  ETH Trend: {sentiment.get('eth_trend', 'N/A')}")
    summary_lines.append(f"  Overall: {sentiment.get('overall_sentiment', 'N/A')}")
    summary_lines.append(f"  Recommendation: {sentiment.get('recommendation', 'N/A')}")
    
    # Trades executed
    trades = results.get('trades_executed', [])
    summary_lines.append("")
    summary_lines.append("TRADES EXECUTED:")
    if trades:
        for i, trade in enumerate(trades, 1):
            summary_lines.append(f"  Trade {i}:")
            summary_lines.append(f"    Symbol: {trade.get('symbol', 'N/A')}")
            summary_lines.append(f"    Side: {trade.get('side', 'N/A')}")
            summary_lines.append(f"    Amount: ${trade.get('value', 0):,.2f}")
            summary_lines.append(f"    Price: ${trade.get('price', 0):,.2f}")
            summary_lines.append(f"    Stop Loss: ${trade.get('stop_loss', 0):,.2f}")
            summary_lines.append(f"    Take Profit: ${trade.get('take_profit', 0):,.2f}")
    else:
        summary_lines.append("  No trades executed (conservative conditions not met)")
    
    summary_lines.append("")
    summary_lines.append("RISK PARAMETERS:")
    summary_lines.append(f"  Stop Loss: {STOP_LOSS*100}%")
    summary_lines.append(f"  Take Profit: {TAKE_PROFIT*100}%")
    summary_lines.append(f"  Max Trades/Day: {MAX_TRADES_PER_DAY}")
    
    summary_lines.append("")
    summary_lines.append("END OF SUMMARY")
    summary_lines.append("=" * 40)
    
    return "\n".join(summary_lines)

if __name__ == "__main__":
    main()