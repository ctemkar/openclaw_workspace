#!/usr/bin/env python3
"""
SIMPLE FOREX TRADING BOT - Ready to Test
- Uses free Forex API for prices
- Simulated trading (paper trading)
- Technical analysis signals
- Risk management
- Ready for real API integration
"""

import time
import logging
import json
import requests
from datetime import datetime
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('forex_trading.log'),
        logging.StreamHandler()
    ]
)

class SimpleForexBot:
    def __init__(self):
        logging.info("🚀 SIMPLE FOREX TRADING BOT INITIALIZING")
        logging.info("💰 Paper trading mode - Ready for real accounts")
        
        # Major Forex pairs (most liquid)
        self.forex_pairs = [
            'EUR/USD',  # Most traded pair
            'GBP/USD',  # Cable
            'USD/JPY',  # Gopher
            'USD/CHF',  # Swissy
            'AUD/USD',  # Aussie
        ]
        
        # Trading parameters (conservative)
        self.paper_balance = 10000.00  # $10,000 paper trading
        self.trade_size = 0.01  # 0.01 lots (micro)
        self.max_trades = 2
        self.stop_loss_pips = 15
        self.take_profit_pips = 30
        self.risk_per_trade = 0.01  # 1% risk
        
        # Track performance
        self.trades = []
        self.total_profit = 0.0
        self.win_rate = 0.0
        
        # Free Forex API
        self.api_url = "https://api.exchangerate-api.com/v4/latest/USD"
        
        logging.info(f"📊 Trading {len(self.forex_pairs)} major Forex pairs")
        logging.info(f"💰 Paper balance: ${self.paper_balance:.2f}")
        logging.info(f"🎯 Risk: {self.risk_per_trade*100}% per trade")
        logging.info(f"📈 Strategy: Trend following + Mean reversion")
    
    def get_forex_rates(self) -> Dict[str, float]:
        """Get real-time Forex rates from free API"""
        try:
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                rates = data.get('rates', {})
                
                # Get our pairs
                forex_prices = {}
                for pair in self.forex_pairs:
                    base, quote = pair.split('/')
                    
                    if base == 'USD':
                        # USD is quote, invert
                        if quote in rates:
                            forex_prices[pair] = 1 / rates[quote]
                    elif quote == 'USD':
                        # USD is base
                        if base in rates:
                            forex_prices[pair] = rates[base]
                
                logging.debug(f"Fetched {len(forex_prices)} Forex rates")
                return forex_prices
                
        except Exception as e:
            logging.error(f"❌ Error fetching Forex rates: {e}")
        
        # Fallback rates (approximate)
        return {
            'EUR/USD': 1.0850,
            'GBP/USD': 1.2650,
            'USD/JPY': 151.50,
            'USD/CHF': 0.9050,
            'AUD/USD': 0.6550,
        }
    
    def analyze_pair(self, pair: str, current_price: float, history: List[float]) -> Dict:
        """Analyze Forex pair for trading signals"""
        if len(history) < 10:
            return {'signal': 'HOLD', 'confidence': 0}
        
        # Simple moving averages
        sma_5 = sum(history[-5:]) / 5
        sma_10 = sum(history[-10:]) / 10
        
        # Price position relative to SMA
        price_vs_sma5 = (current_price - sma_5) / sma_5 * 100
        price_vs_sma10 = (current_price - sma_10) / sma_10 * 100
        
        # Simple trend detection
        trend = 'UP' if sma_5 > sma_10 else 'DOWN'
        
        # Mean reversion signal
        if abs(price_vs_sma5) > 0.3:  # 0.3% deviation
            if price_vs_sma5 > 0:
                signal = 'SELL'  # Overbought
                confidence = min(abs(price_vs_sma5) / 1.0, 1.0)
            else:
                signal = 'BUY'   # Oversold
                confidence = min(abs(price_vs_sma5) / 1.0, 1.0)
        else:
            # Trend following
            if trend == 'UP':
                signal = 'BUY'
                confidence = 0.3
            else:
                signal = 'SELL'
                confidence = 0.3
        
        return {
            'signal': signal,
            'confidence': confidence,
            'price': current_price,
            'sma_5': sma_5,
            'sma_10': sma_10,
            'trend': trend,
            'deviation': price_vs_sma5
        }
    
    def execute_paper_trade(self, pair: str, analysis: Dict):
        """Execute paper trade (simulated)"""
        signal = analysis['signal']
        confidence = analysis['confidence']
        current_price = analysis['price']
        
        # Only trade with sufficient confidence
        if confidence < 0.4:
            return False
        
        # Check max open trades
        open_trades = [t for t in self.trades if t.get('status') == 'OPEN']
        if len(open_trades) >= self.max_trades:
            logging.info(f"   ⏳ Max trades reached ({self.max_trades})")
            return False
        
        # Check if already have position in this pair
        for trade in open_trades:
            if trade.get('pair') == pair:
                logging.info(f"   ⏳ Already have open position in {pair}")
                return False
        
        # Calculate position size based on risk
        risk_amount = self.paper_balance * self.risk_per_trade
        pip_value = 10  # $10 per pip for 0.01 lot
        position_size = risk_amount / (self.stop_loss_pips * pip_value)
        position_size = max(0.01, min(position_size, 0.1))  # 0.01 to 0.1 lots
        
        # Calculate stop loss and take profit
        if signal == 'BUY':
            stop_loss = current_price - (self.stop_loss_pips * 0.0001)
            take_profit = current_price + (self.take_profit_pips * 0.0001)
            trade_type = "LONG"
        else:  # SELL
            stop_loss = current_price + (self.stop_loss_pips * 0.0001)
            take_profit = current_price - (self.take_profit_pips * 0.0001)
            trade_type = "SHORT"
        
        # Create trade record
        trade_id = f"FOREX_{pair.replace('/', '')}_{int(time.time())}"
        
        trade = {
            'id': trade_id,
            'pair': pair,
            'type': trade_type,
            'signal': signal,
            'entry_price': current_price,
            'position_size': position_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'timestamp': datetime.now().isoformat(),
            'status': 'OPEN',
            'paper_trade': True
        }
        
        self.trades.append(trade)
        
        logging.info(f"🎯 PAPER TRADE EXECUTED: {trade_type} {pair}")
        logging.info(f"   Entry: {current_price:.5f}")
        logging.info(f"   Size: {position_size:.2f} lots")
        logging.info(f"   Stop Loss: {stop_loss:.5f}")
        logging.info(f"   Take Profit: {take_profit:.5f}")
        logging.info(f"   Confidence: {confidence:.1%}")
        
        # Save trade
        self.save_trade(trade)
        
        return True
    
    def monitor_trades(self, current_prices: Dict[str, float]):
        """Monitor and update open trades"""
        for trade in self.trades:
            if trade.get('status') != 'OPEN':
                continue
            
            pair = trade['pair']
            current_price = current_prices.get(pair)
            
            if not current_price:
                continue
            
            entry = trade['entry_price']
            stop_loss = trade['stop_loss']
            take_profit = trade['take_profit']
            position_size = trade['position_size']
            
            # Check for exit conditions
            if trade['type'] == 'LONG':
                if current_price <= stop_loss:
                    profit = (current_price - entry) * position_size * 100000
                    result = 'LOSS'
                elif current_price >= take_profit:
                    profit = (current_price - entry) * position_size * 100000
                    result = 'PROFIT'
                else:
                    continue
            else:  # SHORT
                if current_price >= stop_loss:
                    profit = (entry - current_price) * position_size * 100000
                    result = 'LOSS'
                elif current_price <= take_profit:
                    profit = (entry - current_price) * position_size * 100000
                    result = 'PROFIT'
                else:
                    continue
            
            # Close trade
            trade['status'] = 'CLOSED'
            trade['exit_price'] = current_price
            trade['profit'] = profit
            trade['result'] = result
            trade['exit_time'] = datetime.now().isoformat()
            
            # Update paper balance
            self.paper_balance += profit
            self.total_profit += profit
            
            logging.info(f"📊 TRADE CLOSED: {pair} - {result}")
            logging.info(f"   Entry: {entry:.5f}, Exit: {current_price:.5f}")
            logging.info(f"   P&L: ${profit:.2f}")
            logging.info(f"   Paper Balance: ${self.paper_balance:.2f}")
            logging.info(f"   Total Profit: ${self.total_profit:.2f}")
            
            # Update win rate
            closed_trades = [t for t in self.trades if t.get('status') == 'CLOSED']
            winning_trades = [t for t in closed_trades if t.get('result') == 'PROFIT']
            if closed_trades:
                self.win_rate = len(winning_trades) / len(closed_trades)
    
    def save_trade(self, trade: Dict):
        """Save trade to JSON file"""
        try:
            # Load existing trades
            try:
                with open('paper_forex_trades.json', 'r') as f:
                    trades = json.load(f)
            except:
                trades = []
            
            trades.append(trade)
            
            with open('paper_forex_trades.json', 'w') as f:
                json.dump(trades, f, indent=2)
                
        except Exception as e:
            logging.error(f"❌ Error saving trade: {e}")
    
    def run(self):
        """Main trading loop"""
        logging.info("=" * 60)
        logging.info("🚀 SIMPLE FOREX BOT STARTING - PAPER TRADING")
        logging.info("💰 Ready for real account integration")
        logging.info("=" * 60)
        
        # Price history storage
        price_history = {pair: [] for pair in self.forex_pairs}
        
        scan_count = 0
        while True:
            try:
                scan_count += 1
                logging.info(f"🔍 Forex Scan #{scan_count}")
                
                # Get current Forex rates
                current_prices = self.get_forex_rates()
                
                # Update price history
                for pair, price in current_prices.items():
                    if pair in price_history:
                        price_history[pair].append(price)
                        # Keep last 50 prices
                        if len(price_history[pair]) > 50:
                            price_history[pair] = price_history[pair][-50:]
                
                # Analyze each pair
                for pair in self.forex_pairs:
                    current_price = current_prices.get(pair)
                    history = price_history.get(pair, [])
                    
                    if not current_price or len(history) < 10:
                        continue
                    
                    # Analyze for trading signal
                    analysis = self.analyze_pair(pair, current_price, history)
                    
                    if analysis['signal'] != 'HOLD':
                        logging.info(f"📊 {pair}: {analysis['signal']} signal")
                        logging.info(f"   Price: {current_price:.5f}")
                        logging.info(f"   Trend: {analysis['trend']}")
                        logging.info(f"   Confidence: {analysis['confidence']:.1%}")
                        
                        # Execute paper trade
                        self.execute_paper_trade(pair, analysis)
                
                # Monitor and update open trades
                self.monitor_trades(current_prices)
                
                # Performance summary
                open_trades = [t for t in self.trades if t.get('status') == 'OPEN']
                closed_trades = [t for t in self.trades if t.get('status') == 'CLOSED']
                
                logging.info(f"📈 PERFORMANCE SUMMARY:")
                logging.info(f"   Paper Balance: ${self.paper_balance:.2f}")
                logging.info(f"   Total Profit: ${self.total_profit:.2f}")
                logging.info(f"   Open Trades: {len(open_trades)}")
                logging.info(f"   Closed Trades: {len(closed_trades)}")
                logging.info(f"   Win Rate: {self.win_rate*100:.1f}%")
                
                # Wait for next scan (Forex markets move slower than crypto)
                logging.info(f"⏳ Waiting 10 minutes for next scan...")
                time.sleep(600)  # 10 minutes
                
            except KeyboardInterrupt:
                logging.info("🛑 Forex bot stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Error in Forex bot: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = SimpleForexBot()
    bot.run()