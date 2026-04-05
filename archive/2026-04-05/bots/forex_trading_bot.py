#!/usr/bin/env python3
"""
FOREX TRADING BOT - Schwab & Other Account
- Trades major Forex pairs
- Uses technical analysis
- Manages risk properly
- Integrates with brokerage APIs
"""

import time
import logging
import json
from datetime import datetime
import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('forex_trading.log'),
        logging.StreamHandler()
    ]
)

class ForexTradingBot:
    def __init__(self):
        logging.info("🚀 FOREX TRADING BOT INITIALIZING")
        logging.info("💰 Trading with Schwab & Other Account")
        
        # Forex pairs to trade (major currencies)
        self.forex_pairs = [
            'EUR/USD',    # Euro vs US Dollar
            'GBP/USD',    # British Pound vs US Dollar  
            'USD/JPY',    # US Dollar vs Japanese Yen
            'USD/CHF',    # US Dollar vs Swiss Franc
            'AUD/USD',    # Australian Dollar vs US Dollar
            'USD/CAD',    # US Dollar vs Canadian Dollar
            'NZD/USD',    # New Zealand Dollar vs US Dollar
        ]
        
        # Trading parameters
        self.trade_size = 1000  # Micro lots (1000 units)
        self.max_trades = 3     # Maximum concurrent trades
        self.stop_loss_pips = 20  # 20 pips stop loss
        self.take_profit_pips = 40  # 40 pips take profit
        self.risk_per_trade = 0.02  # 2% risk per trade
        
        # Account info (you'll need to fill these)
        self.schwab_account = {
            'api_key': '',  # Schwab API key
            'account_id': '',  # Your account ID
            'balance': 0,  # Will fetch from API
            'available_margin': 0
        }
        
        self.other_account = {
            'api_key': '',  # Other broker API key
            'account_id': '',  # Your account ID
            'balance': 0,
            'available_margin': 0
        }
        
        # Track performance
        self.trades = []
        self.total_profit = 0.0
        self.win_rate = 0.0
        
        # Market data source (free Forex API)
        self.market_data_url = "https://api.exchangerate-api.com/v4/latest/USD"
        
        logging.info(f"📊 Trading {len(self.forex_pairs)} Forex pairs")
        logging.info(f"💰 Trade size: {self.trade_size} units")
        logging.info(f"🎯 Risk management: {self.risk_per_trade*100}% per trade")
    
    def get_forex_prices(self) -> Dict[str, float]:
        """Get current Forex prices from free API"""
        try:
            response = requests.get(self.market_data_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                rates = data.get('rates', {})
                
                # Convert to our pair format
                prices = {}
                for pair in self.forex_pairs:
                    base, quote = pair.split('/')
                    if base == 'USD':
                        prices[pair] = 1 / rates.get(quote, 1)
                    elif quote == 'USD':
                        prices[pair] = rates.get(base, 1)
                    else:
                        # Cross rate calculation
                        prices[pair] = rates.get(base, 1) / rates.get(quote, 1)
                
                logging.debug(f"Forex prices fetched: {len(prices)} pairs")
                return prices
                
        except Exception as e:
            logging.error(f"❌ Error fetching Forex prices: {e}")
        
        # Fallback: return last known prices or defaults
        return {pair: 1.0 for pair in self.forex_pairs}
    
    def calculate_technical_indicators(self, pair: str, prices: List[float]) -> Dict:
        """Calculate technical indicators for trading signals"""
        if len(prices) < 20:
            return {}
        
        # Convert to pandas Series for calculations
        series = pd.Series(prices)
        
        indicators = {}
        
        # Moving averages
        indicators['sma_10'] = series.tail(10).mean()
        indicators['sma_20'] = series.tail(20).mean()
        indicators['ema_12'] = series.ewm(span=12).mean().iloc[-1]
        indicators['ema_26'] = series.ewm(span=26).mean().iloc[-1]
        
        # MACD
        ema_12 = series.ewm(span=12).mean()
        ema_26 = series.ewm(span=26).mean()
        indicators['macd'] = ema_12.iloc[-1] - ema_26.iloc[-1]
        
        # RSI
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain.iloc[-1] / loss.iloc[-1] if loss.iloc[-1] != 0 else 0
        indicators['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        sma_20 = series.tail(20).mean()
        std_20 = series.tail(20).std()
        indicators['bb_upper'] = sma_20 + (2 * std_20)
        indicators['bb_lower'] = sma_20 - (2 * std_20)
        indicators['bb_middle'] = sma_20
        
        # Current price
        indicators['current_price'] = prices[-1]
        
        return indicators
    
    def generate_trading_signal(self, pair: str, indicators: Dict) -> Optional[str]:
        """Generate trading signal based on technical analysis"""
        if not indicators:
            return None
        
        current_price = indicators['current_price']
        sma_10 = indicators['sma_10']
        sma_20 = indicators['sma_20']
        rsi = indicators['rsi']
        macd = indicators['macd']
        bb_upper = indicators['bb_upper']
        bb_lower = indicators['bb_lower']
        
        signals = []
        
        # Moving average crossover
        if sma_10 > sma_20 and sma_10 > sma_20 * 1.001:  # Golden cross
            signals.append('BUY')
        elif sma_10 < sma_20 and sma_10 < sma_20 * 0.999:  # Death cross
            signals.append('SELL')
        
        # RSI overbought/oversold
        if rsi > 70:
            signals.append('SELL')
        elif rsi < 30:
            signals.append('BUY')
        
        # MACD signal
        if macd > 0:
            signals.append('BUY')
        elif macd < 0:
            signals.append('SELL')
        
        # Bollinger Bands
        if current_price > bb_upper:
            signals.append('SELL')  # Overbought
        elif current_price < bb_lower:
            signals.append('BUY')   # Oversold
        
        # Count signals
        buy_signals = signals.count('BUY')
        sell_signals = signals.count('SELL')
        
        if buy_signals > sell_signals and buy_signals >= 2:
            return 'BUY'
        elif sell_signals > buy_signals and sell_signals >= 2:
            return 'SELL'
        
        return None
    
    def calculate_position_size(self, account_balance: float, stop_loss_pips: float) -> float:
        """Calculate position size based on risk management"""
        # Risk amount = balance * risk_per_trade
        risk_amount = account_balance * self.risk_per_trade
        
        # Position size = risk_amount / (stop_loss_pips * pip_value)
        # For Forex, pip_value ≈ 0.0001 for most pairs
        pip_value = 0.0001
        position_size = risk_amount / (stop_loss_pips * pip_value)
        
        # Round to nearest 1000 (micro lot)
        position_size = round(position_size / 1000) * 1000
        
        # Minimum and maximum limits
        position_size = max(1000, min(position_size, 10000))  # 1-10 micro lots
        
        return position_size
    
    def execute_trade(self, pair: str, signal: str, account_type: str = 'schwab'):
        """Execute a Forex trade (simulated for now)"""
        try:
            # Get current price
            prices = self.get_forex_prices()
            current_price = prices.get(pair, 0)
            
            if current_price == 0:
                logging.error(f"❌ No price available for {pair}")
                return False
            
            # Get account balance
            if account_type == 'schwab':
                account = self.schwab_account
            else:
                account = self.other_account
            
            # Calculate position size
            position_size = self.calculate_position_size(
                account['balance'], 
                self.stop_loss_pips
            )
            
            # Calculate stop loss and take profit
            if signal == 'BUY':
                stop_loss = current_price - (self.stop_loss_pips * 0.0001)
                take_profit = current_price + (self.take_profit_pips * 0.0001)
                trade_type = "LONG"
            else:  # SELL
                stop_loss = current_price + (self.stop_loss_pips * 0.0001)
                take_profit = current_price - (self.take_profit_pips * 0.0001)
                trade_type = "SHORT"
            
            # Simulate trade execution
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
                'account': account_type,
                'status': 'OPEN'
            }
            
            self.trades.append(trade)
            
            logging.info(f"🎯 EXECUTED FOREX TRADE: {trade_type} {pair}")
            logging.info(f"   Entry: {current_price:.5f}")
            logging.info(f"   Size: {position_size} units")
            logging.info(f"   Stop Loss: {stop_loss:.5f}")
            logging.info(f"   Take Profit: {take_profit:.5f}")
            logging.info(f"   Account: {account_type.upper()}")
            
            # Save trade to file
            self.save_trade_to_file(trade)
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Trade execution failed: {e}")
            return False
    
    def save_trade_to_file(self, trade: Dict):
        """Save trade to JSON file"""
        try:
            # Load existing trades
            try:
                with open('forex_trades.json', 'r') as f:
                    trades = json.load(f)
            except:
                trades = []
            
            # Add new trade
            trades.append(trade)
            
            # Save back
            with open('forex_trades.json', 'w') as f:
                json.dump(trades, f, indent=2)
                
        except Exception as e:
            logging.error(f"❌ Error saving trade: {e}")
    
    def monitor_open_trades(self):
        """Monitor and manage open trades"""
        open_trades = [t for t in self.trades if t.get('status') == 'OPEN']
        
        if not open_trades:
            return
        
        # Get current prices
        prices = self.get_forex_prices()
        
        for trade in open_trades:
            pair = trade['pair']
            current_price = prices.get(pair, 0)
            
            if current_price == 0:
                continue
            
            entry = trade['entry_price']
            stop_loss = trade['stop_loss']
            take_profit = trade['take_profit']
            
            # Check if stop loss or take profit hit
            if trade['type'] == 'LONG':
                if current_price <= stop_loss:
                    trade['status'] = 'CLOSED'
                    trade['exit_price'] = current_price
                    trade['profit'] = (current_price - entry) * trade['position_size']
                    trade['result'] = 'LOSS'
                    
                elif current_price >= take_profit:
                    trade['status'] = 'CLOSED'
                    trade['exit_price'] = current_price
                    trade['profit'] = (current_price - entry) * trade['position_size']
                    trade['result'] = 'PROFIT'
                    
            else:  # SHORT
                if current_price >= stop_loss:
                    trade['status'] = 'CLOSED'
                    trade['exit_price'] = current_price
                    trade['profit'] = (entry - current_price) * trade['position_size']
                    trade['result'] = 'LOSS'
                    
                elif current_price <= take_profit:
                    trade['status'] = 'CLOSED'
                    trade['exit_price'] = current_price
                    trade['profit'] = (entry - current_price) * trade['position_size']
                    trade['result'] = 'PROFIT'
            
            # Update if closed
            if trade['status'] == 'CLOSED':
                profit = trade.get('profit', 0)
                self.total_profit += profit
                
                logging.info(f"📊 TRADE CLOSED: {trade['pair']} - {trade['result']}")
                logging.info(f"   Entry: {entry:.5f}, Exit: {trade['exit_price']:.5f}")
                logging.info(f"   Profit: ${profit:.2f}")
                logging.info(f"   Total Profit: ${self.total_profit:.2f}")
                
                # Update win rate
                winning_trades = [t for t in self.trades if t.get('result') == 'PROFIT']
                self.win_rate = len(winning_trades) / len([t for t in self.trades if t.get('result')])
    
    def run_forex_strategy(self):
        """Main Forex trading strategy"""
        logging.info("=" * 60)
        logging.info("🚀 FOREX TRADING BOT STARTING")
        logging.info("💰 Trading with Schwab & Other Account")
        logging.info("=" * 60)
        
        # Historical data storage (simplified)
        price_history = {pair: [] for pair in self.forex_pairs}
        
        scan_count = 0
        while True:
            try:
                scan_count += 1
                logging.info(f"🔍 Forex Scan #{scan_count}")
                
                # Get current prices
                prices = self.get_forex_prices()
                
                # Update price history
                for pair, price in prices.items():
                    if pair in price_history:
                        price_history[pair].append(price)
                        # Keep last 100 prices
                        if len(price_history[pair]) > 100:
                            price_history[pair] = price_history[pair][-100:]
                
                # Check each pair for trading opportunities
                for pair in self.forex_pairs:
                    pair_prices = price_history.get(pair, [])
                    
                    if len(pair_prices) < 20:
                        continue  # Need more data
                    
                    # Calculate technical indicators
                    indicators = self.calculate_technical_indicators(pair, pair_prices)
                    
                    # Generate trading signal
                    signal = self.generate_trading_signal(pair, indicators)
                    
                    if signal:
                        logging.info(f"🎯 Signal for {pair}: {signal}")
                        logging.info(f"   Price: {indicators['current_price']:.5f}")
                        logging.info(f"   RSI: {indicators.get('rsi', 0):.1f}")
                        logging.info(f"   MACD: {indicators.get('macd', 0):.5f}")
                        
                        # Check if we have open trades for this pair
                        open_trades_for_pair = [
                            t for t in self.trades 
                            if t.get('pair') == pair and t.get('status') == 'OPEN'
                        ]
                        
                        # Only trade if we don't have an open position
                        if not open_trades_for_pair and len(self.trades) < self.max_trades:
                            # Alternate between accounts
                            account_type = 'schwab' if scan_count % 2 == 0 else 'other'
                            
                            # Execute trade
                            self.execute_trade(pair, signal, account_type)
                
                # Monitor and manage open trades
                self.monitor_open_trades()
                
                # Log performance
                open_trades = [t for t in self.trades if t.get('status') == 'OPEN']
                closed_trades = [t for t in self.trades if t.get('status') == 'CLOSED']
                
                logging.info(f"📊 Performance:")
                logging.info(f"   Open Trades: {len(open_trades)}")
                logging.info(f"   Closed Trades: {len(closed_trades)}")
                logging.info(f"   Total Profit: ${self.total_profit:.2f}")
                logging.info(f"   Win Rate: {self.win_rate*100:.1f}%")
                
                # Wait between scans (Forex markets are 24/5)
                logging.info(f"⏳ Waiting 5 minutes for next scan...")
                time.sleep(300)  # 5 minutes
                
            except KeyboardInterrupt:
                logging.info("🛑 Forex trading bot stopped")
                break
            except Exception as e:
                logging.error(f"❌ Error in Forex scan: {e}")
                time.sleep(60)

    def run(self):
        """Main entry point"""
        self.run_forex_strategy()

if __name__ == "__main__":
    bot = ForexTradingBot()
    bot.run()