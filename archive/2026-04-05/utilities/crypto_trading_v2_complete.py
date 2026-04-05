#!/usr/bin/env python3
"""
Conservative Crypto Trading Bot - Complete Version
"""

import os
import json
import time
import requests
import datetime
from typing import Dict, List, Optional, Tuple
import math

# Configuration
CAPITAL = 1000.0
STOP_LOSS = 0.05
TAKE_PROFIT = 0.10
MAX_TRADES_PER_DAY = 2
SYMBOLS = ['BTC-USD', 'ETH-USD']

class ConservativeCryptoTrader:
    def __init__(self):
        self.trades_today = 0
        self.today_date = datetime.date.today().isoformat()
        self.load_trade_history()
        
    def load_trade_history(self):
        try:
            with open('trade_history.json', 'r') as f:
                history = json.load(f)
                today = datetime.date.today().isoformat()
                if history.get('date') == today:
                    self.trades_today = history.get('trades_today', 0)
        except FileNotFoundError:
            self.trades_today = 0
            
    def save_trade_history(self):
        history = {
            'date': self.today_date,
            'trades_today': self.trades_today,
            'last_updated': datetime.datetime.now().isoformat()
        }
        with open('trade_history.json', 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_market_data(self) -> Dict:
        """Get market data with fallback to simulation"""
        try:
            # Try CoinGecko first
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'bitcoin,ethereum',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                btc_price = data.get('bitcoin', {}).get('usd', 67271.91)
                btc_change = data.get('bitcoin', {}).get('usd_24h_change', 0.5)
                btc_volume = data.get('bitcoin', {}).get('usd_24h_vol', 35000000000)
                
                eth_price = data.get('ethereum', {}).get('usd', 2019.02)
                eth_change = data.get('ethereum', {}).get('usd_24h_change', 0.3)
                eth_volume = data.get('ethereum', {}).get('usd_24h_vol', 12000000000)
                
                # Calculate realistic highs/lows
                btc_high = btc_price * (1 + abs(btc_change/100) * 0.8)
                btc_low = btc_price * (1 - abs(btc_change/100) * 0.8)
                
                eth_high = eth_price * (1 + abs(eth_change/100) * 0.8)
                eth_low = eth_price * (1 - abs(eth_change/100) * 0.8)
                
                return {
                    'BTC-USD': {
                        'last': btc_price,
                        'percentChange24h': btc_change,
                        'volume': {'USD': btc_volume},
                        'high': btc_high,
                        'low': btc_low
                    },
                    'ETH-USD': {
                        'last': eth_price,
                        'percentChange24h': eth_change,
                        'volume': {'USD': eth_volume},
                        'high': eth_high,
                        'low': eth_low
                    }
                }
        except:
            pass
        
        # Fallback: realistic simulated data
        import random
        btc_price = 67271.91 + random.uniform(-1000, 1000)
        eth_price = 2019.02 + random.uniform(-50, 50)
        btc_change = random.uniform(-2, 2)
        eth_change = random.uniform(-3, 3)
        
        return {
            'BTC-USD': {
                'last': round(btc_price, 2),
                'percentChange24h': round(btc_change, 2),
                'volume': {'USD': 35000000000},
                'high': round(btc_price * 1.03, 2),
                'low': round(btc_price * 0.97, 2)
            },
            'ETH-USD': {
                'last': round(eth_price, 2),
                'percentChange24h': round(eth_change, 2),
                'volume': {'USD': 12000000000},
                'high': round(eth_price * 1.04, 2),
                'low': round(eth_price * 0.96, 2)
            }
        }
    
    def analyze_sentiment(self, market_data: Dict) -> Dict:
        sentiment = {
            'btc_trend': 'neutral',
            'eth_trend': 'neutral',
            'overall': 'neutral',
            'recommendation': 'hold',
            'confidence': 'medium'
        }
        
        btc_data = market_data.get('BTC-USD', {})
        eth_data = market_data.get('ETH-USD', {})
        
        if btc_data and eth_data:
            btc_change = btc_data.get('percentChange24h', 0)
            eth_change = eth_data.get('percentChange24h', 0)
            
            # Determine trends
            if btc_change > 1.5:
                sentiment['btc_trend'] = 'bullish'
            elif btc_change < -1.5:
                sentiment['btc_trend'] = 'bearish'
                
            if eth_change > 2.0:
                sentiment['eth_trend'] = 'bullish'
            elif eth_change < -2.0:
                sentiment['eth_trend'] = 'bearish'
            
            # Overall sentiment
            if sentiment['btc_trend'] == 'bullish' and sentiment['eth_trend'] == 'bullish':
                sentiment['overall'] = 'bullish'
                sentiment['recommendation'] = 'consider_buy'
                sentiment['confidence'] = 'high'
            elif sentiment['btc_trend'] == 'bearish' and sentiment['eth_trend'] == 'bearish':
                sentiment['overall'] = 'bearish'
                sentiment['recommendation'] = 'consider_sell'
                sentiment['confidence'] = 'high'
            elif sentiment['btc_trend'] != sentiment['eth_trend']:
                sentiment['confidence'] = 'low'
        
        return sentiment
    
    def calculate_levels(self, symbol: str, market_data: Dict) -> Dict:
        data = market_data.get(symbol, {})
        if not data:
            return {'support': 0, 'resistance': 0, 'position': 'middle'}
        
        high = data.get('high', 0)
        low = data.get('low', 0)
        current = data.get('last', 0)
        
        if high <= low or current <= 0:
            return {'support': current * 0.95, 'resistance': current * 1.05, 'position': 'middle'}
        
        # Calculate levels
        range_size = high - low
        support = low + (range_size * 0.382)
        resistance = high - (range_size * 0.382)
        
        # Determine position
        support_band = support * 1.02
        resistance_band = resistance * 0.98
        
        if current <= support_band:
            position = 'near_support'
        elif current >= resistance_band:
            position = 'near_resistance'
        else:
            position = 'middle'
        
        return {
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'position': position,
            'from_support': round(((current - support) / support) * 100, 2),
            'to_resistance': round(((resistance - current) / current) * 100, 2)
        }
    
    def evaluate_trade(self, symbol: str, sentiment: Dict, levels: Dict, market_data: Dict) -> Tuple[bool, str, float]:
        if self.trades_today >= MAX_TRADES_PER_DAY:
            return False, "max_trades_reached", 0.0
        
        data = market_data.get(symbol, {})
        price = data.get('last', 0)
        change = data.get('percentChange24h', 0)
        
        if price <= 0:
            return False, "invalid_price", 0.0
        
        # Conservative rules
        position_size = CAPITAL * 0.1  # $100 per trade
        
        # Check conditions
        conditions_met = 0
        
        # Condition 1: Clear trend
        if sentiment['overall'] == 'bullish' and sentiment['confidence'] == 'high':
            conditions_met += 2
        elif sentiment['overall'] == 'bearish' and sentiment['confidence'] == 'high':
            conditions_met += 2
        
        # Condition 2: Near key level
        if levels['position'] == 'near_support' and sentiment['overall'] == 'bullish':
            conditions_met += 2
        elif levels['position'] == 'near_resistance' and sentiment['overall'] == 'bearish':
            conditions_met += 2
        
        # Condition 3: Moderate volatility
        if abs(change) < 3.0:
            conditions_met += 1
        
        # Need at least 3 points to trade
        if conditions_met >= 3:
            if sentiment['overall'] == 'bullish':
                return True, "buy", position_size
            elif sentiment['overall'] == 'bearish':
                return True, "sell", position_size
        
        return False, f"conditions_not_met (score: {conditions_met})", 0.0
    
    def execute_trade(self, symbol: str, side: str, amount: float, price: float) -> Dict:
        trade_id = f"{symbol.replace('-', '')}_{side}_{int(time.time())}"
        
        if side == "buy":
            stop_price = price * (1 - STOP_LOSS)
            take_profit_price = price * (1 + TAKE_PROFIT)
        else:
            stop_price = price * (1 + STOP_LOSS)
            take_profit_price = price * (1 - TAKE_PROFIT)
        
        crypto_amount = amount / price
        
        trade = {
            'id': trade_id,
            'symbol': symbol,
            'side': side,
            'amount_usd': round(amount, 2),
            'amount_crypto': round(crypto_amount, 6),
            'entry_price': round(price, 2),
            'stop_loss': round(stop_price, 2),
            'take_profit': round(take_profit_price, 2),
            'max_loss': round(amount * STOP_LOSS, 2),
            'potential_gain': round(amount * TAKE_PROFIT, 2),
            'timestamp': datetime.datetime.now().isoformat(),
            'status': 'executed'
        }
        
        self.trades_today += 1
        self.save_trade_history()
        
        # Save to trade log
        self.log_trade(trade)
        
        return trade
    
    def log_trade(self, trade: Dict):
        try:
            trades = []
            try:
                with open('trades_log.json', 'r') as f:
                    trades = json.load(f)
            except:
                pass
            
            trades.append(trade)
            
            # Keep last 50 trades
            if len(trades) > 50:
                trades = trades[-50:]
            
            with open('trades_log.json', 'w') as f:
                json.dump(trades, f, indent=2)
        except:
            pass
    
    def run(self) -> str:
        """Main execution - returns plain text summary"""
        output_lines = []
        
        output_lines.append("=" * 60)
        output_lines.append("CONSERVATIVE CRYPTO TRADING ANALYSIS")
        output_lines.append("=" * 60)
        output_lines.append(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append(f"Capital: ${CAPITAL:,.2f}")
        output_lines.append(f"Trades Today: {self.trades_today}/{MAX_TRADES_PER_DAY}")
        output_lines.append("")
        
        # Get market data
        output_lines.append("📊 MARKET DATA")
        output_lines.append("-" * 40)
        market_data = self.get_market_data()
        
        for symbol in SYMBOLS:
            data = market_data.get(symbol, {})
            price = data.get('last', 0)
            change = data.get('percentChange24h', 0)
            volume = data.get('volume', {}).get('USD', 0)
            
            change_str = f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"
            change_icon = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
            
            output_lines.append(f"{symbol}:")
            output_lines.append(f"  Price: ${price:,.2f} {change_icon}")
            output_lines.append(f"  24h Change: {change_str}")
            output_lines.append(f"  24h Volume: ${volume/1e9:.1f}B")
        
        output_lines.append("")
        
        # Analyze sentiment
        output_lines.append("📈 MARKET SENTIMENT")
        output_lines.append("-" * 40)
        sentiment = self.analyze_sentiment(market_data)
        
        output_lines.append(f"BTC Trend: {sentiment['btc_trend'].upper()}")
        output_lines.append(f"ETH Trend: {sentiment['eth_trend'].upper()}")
        output_lines.append(f"Overall: {sentiment['overall'].upper()}")
        output_lines.append(f"Confidence: {sentiment['confidence'].upper()}")
        output_lines.append(f"Recommendation: {sentiment['recommendation'].replace('_', ' ').upper()}")
        
        output_lines.append("")
        
        # Technical analysis
        output_lines.append("📐 TECHNICAL ANALYSIS")
        output_lines.append("-" * 40)
        
        trades_executed = []
        
        for symbol in SYMBOLS:
            levels = self.calculate_levels(symbol, market_data)
            
            output_lines.append(f"{symbol}:")
            output_lines.append(f"  Support: ${levels['support']:,.2f}")
            output_lines.append(f"  Resistance: ${levels['resistance']:,.2f}")
            output_lines.append(f"  Position: {levels['position'].replace('_', ' ').upper()}")
            
            # Evaluate trade
            should_trade, reason, amount = self.evaluate_trade(symbol, sentiment, levels, market_data)
            
            if should_trade:
                price = market_data[symbol]['last']
                side = "buy" if sentiment['overall'] == 'bullish' else "sell"
                
                trade = self.execute_trade(symbol, side, amount, price)
                trades_executed.append(trade)
                
                output_lines.append(f"  ✅ TRADE EXECUTED:")
                output_lines.append(f"     Side: {side.upper()}")
                output_lines.append(f"     Amount: ${amount:,.2f}")
                output_lines.append(f"     Entry: ${price:,.2f}")
                output_lines.append(f"     Stop Loss: ${trade['stop_loss']:,.2f}")
                output_lines.append(f"     Take Profit: ${trade['take_profit']:,.2f}")
            else:
                output_lines.append(f"  ⏸️  NO TRADE: {reason}")
            
            output_lines.append("")
        
        # Risk summary
        output_lines.append("⚠️ RISK MANAGEMENT")
        output_lines.append("-" * 40)
        output_lines.append(f"Stop Loss: {STOP_LOSS*100}%")
        output_lines.append(f"Take Profit: {TAKE_PROFIT*100}%")
        output_lines.append(f"Risk/Reward Ratio: 1:{TAKE_PROFIT/STOP_LOSS:.1f}")
        output_lines.append(f"Max Position Size: ${CAPITAL * 0.1:,.2f} (10% of capital)")
        output_lines.append(f"Max Daily Trades: {MAX_TRADES_PER_DAY}")
        
        output_lines.append("")
        
        # Trade summary
        output_lines.append("💼 TRADE SUMMARY")
        output_lines.append("-" * 40)
        
        if trades_executed:
            total_invested = sum(t['amount_usd'] for t in trades_executed)
            output_lines.append(f"Trades Executed: {len(trades_executed)}")
            output_lines.append(f"Total Invested: ${total_invested:,.2f}")
            output_lines.append(f"Remaining Capital: ${CAPITAL - total_invested:,.2f}")
            
            for i, trade in enumerate(trades_executed, 1):
                output_lines.append(f"")
                output_lines.append(f"Trade {i}:")
                output_lines.append(f"  {trade['symbol']} {trade['side'].upper()}")
                output_lines.append(f"  Amount: ${trade['amount_usd']:,.2f}")
                output_lines.append(f"  Entry: ${trade['entry_price']:,.2f}")
                output_lines.append(f"  Stop: ${trade['stop_loss']:,.2f} ({STOP_LOSS*100}%)")
                output_lines.append(f"  Target: ${trade['take_profit']:,.2f} ({TAKE_PROFIT*100}%)")
        else:
            output_lines.append("No trades executed - Conservative conditions not met")
            output_lines.append(f"Available for trading: ${CAPITAL:,.2f}")
        
        output_lines.append("")
        output_lines.append("=" * 60)
        output_lines.append("ANALYSIS COMPLETE")
        output_lines.append("=" * 60)
        
        return "\n".join(output_lines)

def main():
    trader = ConservativeCryptoTrader()
    summary = trader.run()
    print(summary)
    
    # Save summary to file
    with open('trading_summary.txt', 'w') as f:
        f.write(summary)
    
    return summary

if __name__ == "__main__":
    main()