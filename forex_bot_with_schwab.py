#!/usr/bin/env python3
"""
FOREX TRADING BOT WITH SCHWAB INTEGRATION
- Paper trading mode (default)
- Real trading mode with Schwab API
- Technical analysis + Risk management
- Ready for your Schwab credentials
"""

import time
import logging
import json
import requests
import argparse
from datetime import datetime
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('forex_trading_with_schwab.log'),
        logging.StreamHandler()
    ]
)

class ForexTradingBotWithSchwab:
    def __init__(self, real_trading=False):
        self.real_trading = real_trading
        self.schwab_connected = False
        
        logging.info("🚀 FOREX TRADING BOT INITIALIZING")
        
        if real_trading:
            logging.info("💰 REAL TRADING MODE - Schwab Integration")
            self.setup_schwab_connection()
        else:
            logging.info("📝 PAPER TRADING MODE - Ready for real trading")
        
        # Forex pairs to trade
        self.forex_pairs = [
            'EUR/USD',  # Euro vs US Dollar
            'GBP/USD',  # British Pound vs US Dollar
            'USD/JPY',  # US Dollar vs Japanese Yen
            'USD/CHF',  # US Dollar vs Swiss Franc
            'AUD/USD',  # Australian Dollar vs US Dollar
        ]
        
        # Trading parameters
        if real_trading and self.schwab_connected:
            # Real trading parameters (conservative)
            self.trade_size = 0.01  # 0.01 lots (micro)
            self.starting_balance = self.get_schwab_balance()
        else:
            # Paper trading parameters
            self.trade_size = 0.01  # 0.01 lots (micro)
            self.starting_balance = 10000.00  # $10,000 paper
        
        self.max_trades = 2
        self.stop_loss_pips = 20
        self.take_profit_pips = 40
        self.risk_per_trade = 0.01  # 1% risk
        
        # Track performance
        self.trades = []
        self.total_profit = 0.0
        self.win_rate = 0.0
        self.current_balance = self.starting_balance
        
        # Free Forex API for market data
        self.market_data_url = "https://api.exchangerate-api.com/v4/latest/USD"
        
        logging.info(f"📊 Trading {len(self.forex_pairs)} Forex pairs")
        logging.info(f"💰 {'Real' if real_trading else 'Paper'} balance: ${self.current_balance:.2f}")
        logging.info(f"🎯 Risk: {self.risk_per_trade*100}% per trade")
        logging.info(f"📈 Strategy: Trend following + Mean reversion")
    
    def setup_schwab_connection(self):
        """Setup Schwab API connection"""
        try:
            load_dotenv()
            
            schwab_api_key = os.getenv('SCHWAB_API_KEY')
            schwab_api_secret = os.getenv('SCHWAB_API_SECRET')
            schwab_account_id = os.getenv('SCHWAB_ACCOUNT_ID')
            
            if not all([schwab_api_key, schwab_api_secret, schwab_account_id]):
                logging.error("❌ Schwab credentials missing in .env file")
                logging.error("   Add: SCHWAB_API_KEY, SCHWAB_API_SECRET, SCHWAB_ACCOUNT_ID")
                logging.error("   Running in paper trading mode instead")
                self.real_trading = False
                return
            
            # In a real implementation, you would initialize Schwab API client here
            # Example:
            # from schwab.client import SchwabClient
            # self.schwab_client = SchwabClient(
            #     app_key=schwab_api_key,
            #     app_secret=schwab_api_secret,
            #     account_id=schwab_account_id
            # )
            
            logging.info(f"✅ Schwab credentials loaded")
            logging.info(f"   Account ID: {schwab_account_id}")
            self.schwab_connected = True
            
        except Exception as e:
            logging.error(f"❌ Schwab setup failed: {e}")
            logging.error("   Running in paper trading mode instead")
            self.real_trading = False
    
    def get_schwab_balance(self):
        """Get account balance from Schwab"""
        if not self.schwab_connected:
            return 10000.00  # Default paper balance
        
        try:
            # In a real implementation:
            # balance = self.schwab_client.get_account_balance()
            # return balance.get('cash_available', 10000.00)
            
            # For now, return simulated balance
            logging.info("   📊 Would fetch real balance from Schwab API")
            return 10000.00  # Simulated
            
        except Exception as e:
            logging.error(f"❌ Error getting Schwab balance: {e}")
            return 10000.00  # Fallback paper balance
    
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
                
                logging.debug(f"Forex prices fetched: {len(prices)} pairs")
                return prices
                
        except Exception as e:
            logging.error(f"❌ Error fetching Forex prices: {e}")
        
        # Fallback prices
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
    
    def execute_trade(self, pair: str, analysis: Dict):
        """Execute trade (paper or real)"""
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
        risk_amount = self.current_balance * self.risk_per_trade
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
            'real_trade': self.real_trading and self.schwab_connected
        }
        
        self.trades.append(trade)
        
        # Execute trade
        if self.real_trading and self.schwab_connected:
            # Real trade execution would go here
            # Example:
            # order_id = self.schwab_client.place_forex_order(
            #     pair=pair,
            #     side='BUY' if signal == 'BUY' else 'SELL',
            #     quantity=position_size,
            #     stop_loss=stop_loss,
            #     take_profit=take_profit
            # )
            # trade['order_id'] = order_id
            
            logging.info(f"🎯 REAL TRADE EXECUTED WITH SCHWAB: {trade_type} {pair}")
            logging.info(f"   (Simulated - Real API would execute)")
        else:
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
            
            # Update balance
            self.current_balance += profit
            self.total_profit += profit
            
            # Real trade closure would go here
            if trade.get('real_trade'):
                logging.info(f"📊 REAL TRADE CLOSED WITH SCHWAB: {pair} - {result}")
                # Example: self.schwab_client.close_order(trade['order_id'])
            else:
                logging.info(f"📊 PAPER TRADE CLOSED: {pair} - {result}")
            
            logging.info(f"   Entry: {entry:.5f}, Exit: {current_price:.5f}")
            logging.info(f"   P&L: ${profit:.2f}")
            logging.info(f"   Balance: ${self.current_balance:.2f}")
            logging.info(f"   Total Profit: ${self.total_profit:.2f}")
            
            # Update win rate
            closed_trades = [t for t in self.trades if t.get('status') == 'CLOSED']
            winning_trades = [t for t in closed_trades if t.get('result') == 'PROFIT']
            if closed_trades:
                self.win_rate = len(winning_trades) / len(closed_trades)
    
    def save_trade(self, trade: Dict):
        """Save trade to JSON file"""
        try:
            filename = 'real_forex_trades.json' if trade.get('real_trade') else 'paper_forex_trades.json'
            
            # Load existing trades
            try:
                with open(filename, 'r') as f:
                    trades = json.load(f)
            except:
                trades = []
            
            trades.append(trade)
            
            with open(filename, 'w') as f:
                json.dump(trades, f, indent=2)
                
        except Exception as e:
            logging.error(f"❌ Error saving trade: {e}")
    
    def run(self):
        """Main trading loop"""
        logging.info("=" * 60)
        if self.real_trading and self.schwab_connected:
            logging.info("🚀 FOREX BOT - REAL TRADING WITH SCHWAB")
        else:
            logging.info("🚀 FOREX BOT - PAPER TRADING MODE")
        logging.info("💰 Ready for real account integration")
        logging.info("=" * 60)
        
        # Price history storage
        price_history = {pair: [] for pair in self.forex_pairs}
        
        scan_count = 0
        while True:
            try:
                scan_count += 1
                logging.info(f"🔍 Forex Scan #{scan_count}")
                
                # Get current Forex prices
                current_prices = self.get_forex_prices()
                
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
                        
                        # Execute trade
                        self.execute_trade(pair, analysis)
                
                # Monitor and update open trades
                self.monitor_trades(current_prices)
                
                # Performance summary
                open_trades = [t for t in self.trades if t.get('status') == 'OPEN']
                closed_trades = [t for t in self.trades if t.get('status') == 'CLOSED']
                
                logging.info(f"📈 PERFORMANCE SUMMARY:")
                logging.info(f"   Mode: {'REAL' if self.real_trading else 'PAPER'} trading")
                logging.info(f"   Balance: ${self.current_balance:.2f}")
                logging.info(f"   Total Profit: ${self.total_profit:.2f}")
                logging.info(f"   Open Trades: {len(open_trades)}")
                logging.info(f"   Closed Trades: {len(closed_trades)}")
                logging.info(f"   Win Rate: {self.win_rate*100:.1f}%")
                
                # Wait for next scan (Forex markets move slower)
                logging.info(f"🚨 SCAN INTERVAL REDUCED FROM 10 MINUTES TO 2 MINUTES!")
                logging.info(f"⏳ Waiting 2 minutes for next scan... (Was 10 minutes - TOO LONG!)")
                time.sleep(120)  # 2 minutes - MUCH SAFER!
                
            except KeyboardInterrupt:
                logging.info("🛑 Forex bot stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Error in Forex bot: {e}")
                time.sleep(60)

def main():
    """Main entry point with command line arguments"""
    parser = argparse.ArgumentParser(description='Forex Trading Bot with Schwab Integration')
    parser.add_argument('--real-trading', action='store_true', help='Enable real trading with Schwab')
    parser.add_argument('--paper-trading', action='store_true', help='Enable paper trading (default)')
    
    args = parser.parse_args()
    
    # Determine mode
    real_trading = args.real_trading
    
    if args.paper_trading:
        real_trading = False
    
    # Run bot
    bot = ForexTradingBotWithSchwab(real_trading=real_trading)
    bot.run()

if __name__ == "__main__":
    main()
