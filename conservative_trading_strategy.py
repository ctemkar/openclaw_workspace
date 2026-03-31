#!/usr/bin/env python3
"""
Conservative Crypto Trading Strategy
Risk parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
$1,000 investment target (working with actual $533.63 available)
"""

import os
import json
import time
import hmac
import hashlib
import base64
import requests
from datetime import datetime
import math

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Risk Parameters
STOP_LOSS_PERCENT = 0.05      # 5%
TAKE_PROFIT_PERCENT = 0.10    # 10%
MAX_TRADES_PER_DAY = 2
MAX_POSITION_SIZE = 0.20      # 20% of available capital per trade
TARGET_INVESTMENT = 1000.00   # $1,000 target

class ConservativeTrader:
    def __init__(self):
        self.api_key = None
        self.api_secret = None
        self.available_usd = 0
        self.btc_holdings = 0
        self.eth_holdings = 0
        self.total_value = 0
        self.today_trades = 0
        self.load_credentials()
        
    def load_credentials(self):
        """Load Gemini API credentials"""
        try:
            with open(os.path.join(BASE_DIR, 'secure_keys/.gemini_key'), 'r') as f:
                self.api_key = f.read().strip()
            with open(os.path.join(BASE_DIR, 'secure_keys/.gemini_secret'), 'r') as f:
                self.api_secret = f.read().strip().encode()
            return True
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return False
    
    def get_market_data(self):
        """Get current market prices"""
        try:
            btc_data = requests.get('https://api.gemini.com/v1/pubticker/btcusd', timeout=10).json()
            eth_data = requests.get('https://api.gemini.com/v1/pubticker/ethusd', timeout=10).json()
            
            btc_price = float(btc_data['last'])
            eth_price = float(eth_data['last'])
            
            return {
                'btc_price': btc_price,
                'eth_price': eth_price,
                'btc_bid': float(btc_data['bid']),
                'btc_ask': float(btc_data['ask']),
                'eth_bid': float(eth_data['bid']),
                'eth_ask': float(eth_data['ask'])
            }
        except Exception as e:
            print(f"Error getting market data: {e}")
            return None
    
    def get_account_balance(self):
        """Get real account balance"""
        try:
            payload_nonce = str(int(time.time() * 1000))
            payload = {
                "request": "/v1/balances",
                "nonce": payload_nonce
            }
            
            payload_json = json.dumps(payload)
            payload_b64 = base64.b64encode(payload_json.encode()).decode()
            
            signature = hmac.new(
                self.api_secret,
                payload_b64.encode(),
                hashlib.sha384
            ).hexdigest()
            
            headers = {
                'Content-Type': 'text/plain',
                'Content-Length': '0',
                'X-GEMINI-APIKEY': self.api_key,
                'X-GEMINI-PAYLOAD': payload_b64,
                'X-GEMINI-SIGNATURE': signature
            }
            
            response = requests.post(
                'https://api.gemini.com/v1/balances',
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Balance API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting balance: {e}")
            return None
    
    def analyze_market_conditions(self, market_data):
        """Analyze market conditions for conservative trading"""
        analysis = {
            'btc_trend': 'NEUTRAL',
            'eth_trend': 'NEUTRAL',
            'market_volatility': 'LOW',
            'trading_recommendation': 'HOLD',
            'reason': ''
        }
        
        btc_price = market_data['btc_price']
        btc_spread = market_data['btc_ask'] - market_data['btc_bid']
        btc_spread_pct = (btc_spread / btc_price) * 100
        
        eth_price = market_data['eth_price']
        eth_spread = market_data['eth_ask'] - market_data['eth_bid']
        eth_spread_pct = (eth_spread / eth_price) * 100
        
        # Check spreads for volatility
        if btc_spread_pct > 0.05 or eth_spread_pct > 0.1:
            analysis['market_volatility'] = 'HIGH'
            analysis['trading_recommendation'] = 'AVOID'
            analysis['reason'] = 'Wide spreads indicate high volatility'
        elif btc_spread_pct < 0.01 and eth_spread_pct < 0.02:
            analysis['market_volatility'] = 'VERY LOW'
            analysis['trading_recommendation'] = 'CONSIDER'
            analysis['reason'] = 'Tight spreads, good liquidity'
        else:
            analysis['market_volendment'] = 'MODERATE'
            analysis['trading_recommendation'] = 'CAUTIOUS'
            analysis['reason'] = 'Normal market conditions'
        
        # Check if we should buy (conservative: only in stable conditions)
        if analysis['market_volatility'] == 'VERY LOW' and self.available_usd > 50:
            # Conservative buy signal: small position in stable market
            analysis['trading_recommendation'] = 'SMALL_BUY'
            analysis['reason'] = 'Stable market with good liquidity'
        
        return analysis
    
    def calculate_position_size(self, available_capital, asset_price):
        """Calculate conservative position size"""
        max_trade_value = available_capital * MAX_POSITION_SIZE
        max_trade_value = min(max_trade_value, 100)  # Max $100 per trade for safety
        
        # Round down to avoid fractional issues
        coin_amount = math.floor((max_trade_value / asset_price) * 100000000) / 100000000
        
        if coin_amount * asset_price < 10:  # Minimum $10 trade
            return 0
        
        return coin_amount
    
    def execute_conservative_trade(self, market_data, analysis):
        """Execute a conservative trade if conditions are right"""
        if self.today_trades >= MAX_TRADES_PER_DAY:
            print("⚠️ Daily trade limit reached")
            return None
        
        if analysis['trading_recommendation'] != 'SMALL_BUY':
            print(f"⚠️ Market conditions not favorable: {analysis['reason']}")
            return None
        
        if self.available_usd < 50:
            print("⚠️ Insufficient USD for trading")
            return None
        
        # Choose asset (prefer BTC for conservative trading)
        asset = 'BTC'
        asset_price = market_data['btc_price']
        
        # Calculate position size
        position_size = self.calculate_position_size(self.available_usd, asset_price)
        
        if position_size == 0:
            print("⚠️ Position size too small")
            return None
        
        trade_value = position_size * asset_price
        
        # Calculate stop loss and take profit
        stop_loss_price = asset_price * (1 - STOP_LOSS_PERCENT)
        take_profit_price = asset_price * (1 + TAKE_PROFIT_PERCENT)
        
        trade = {
            'asset': asset,
            'side': 'BUY',
            'amount': position_size,
            'entry_price': asset_price,
            'trade_value': trade_value,
            'stop_loss': stop_loss_price,
            'take_profit': take_profit_price,
            'timestamp': datetime.now().isoformat(),
            'risk_parameters': {
                'stop_loss_percent': STOP_LOSS_PERCENT,
                'take_profit_percent': TAKE_PROFIT_PERCENT
            }
        }
        
        print(f"✅ Conservative trade calculated:")
        print(f"   Asset: {asset}")
        print(f"   Amount: {position_size:.8f}")
        print(f"   Entry: ${asset_price:,.2f}")
        print(f"   Value: ${trade_value:,.2f}")
        print(f"   Stop Loss: ${stop_loss_price:,.2f} (-5%)")
        print(f"   Take Profit: ${take_profit_price:,.2f} (+10%)")
        
        # Note: In a real implementation, we would execute the trade here
        # For safety, we'll just simulate and log it
        
        return trade
    
    def run_analysis(self):
        """Run complete conservative trading analysis"""
        print("="*70)
        print("🛡️ CONSERVATIVE CRYPTO TRADING ANALYSIS")
        print("="*70)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC+7)")
        print()
        
        # Check credentials
        if not self.api_key or not self.api_secret:
            print("❌ API credentials not loaded")
            return
        
        # Get account balance
        balance_data = self.get_account_balance()
        if not balance_data:
            print("❌ Failed to get account balance")
            return
        
        # Parse balances
        for balance in balance_data:
            currency = balance['currency']
            amount = float(balance['amount'])
            
            if currency == 'USD':
                self.available_usd = amount
            elif currency == 'BTC':
                self.btc_holdings = amount
            elif currency == 'ETH':
                self.eth_holdings = amount
        
        # Get market data
        market_data = self.get_market_data()
        if not market_data:
            print("❌ Failed to get market data")
            return
        
        # Calculate total value
        btc_value = self.btc_holdings * market_data['btc_price']
        eth_value = self.eth_holdings * market_data['eth_price']
        self.total_value = self.available_usd + btc_value + eth_value
        
        # Display current status
        print("📊 CURRENT PORTFOLIO:")
        print(f"   Available USD: ${self.available_usd:,.2f}")
        print(f"   BTC Holdings: {self.btc_holdings:.8f} (${btc_value:,.2f})")
        print(f"   ETH Holdings: {self.eth_holdings:.8f} (${eth_value:,.2f})")
        print(f"   Total Value: ${self.total_value:,.2f}")
        print(f"   Target Investment: ${TARGET_INVESTMENT:,.2f}")
        print()
        
        print("📈 MARKET CONDITIONS:")
        print(f"   BTC Price: ${market_data['btc_price']:,.2f}")
        print(f"   ETH Price: ${market_data['eth_price']:,.2f}")
        print(f"   BTC Spread: ${market_data['btc_ask'] - market_data['btc_bid']:.2f}")
        print(f"   ETH Spread: ${market_data['eth_ask'] - market_data['eth_bid']:.2f}")
        print()
        
        # Analyze market
        analysis = self.analyze_market_conditions(market_data)
        
        print("🔍 TRADING ANALYSIS:")
        print(f"   Market Volatility: {analysis['market_volatility']}")
        print(f"   Recommendation: {analysis['trading_recommendation']}")
        print(f"   Reason: {analysis['reason']}")
        print()
        
        print("⚙️ RISK PARAMETERS:")
        print(f"   Stop Loss: {STOP_LOSS_PERCENT*100}%")
        print(f"   Take Profit: {TAKE_PROFIT_PERCENT*100}%")
        print(f"   Max Trades/Day: {MAX_TRADES_PER_DAY}")
        print(f"   Max Position Size: {MAX_POSITION_SIZE*100}% of capital")
        print()
        
        # Check if we should trade
        if analysis['trading_recommendation'] == 'SMALL_BUY' and self.available_usd > 50:
            print("✅ CONDITIONS MET FOR CONSERVATIVE TRADE")
            print("   Executing conservative buy strategy...")
            print()
            
            trade = self.execute_conservative_trade(market_data, analysis)
            if trade:
                self.today_trades += 1
                
                # Save trade to log
                self.save_trade_log(trade)
                
                print("📝 TRADE EXECUTED (SIMULATED):")
                print(f"   Asset: {trade['asset']}")
                print(f"   Amount: {trade['amount']:.8f}")
                print(f"   Entry Price: ${trade['entry_price']:,.2f}")
                print(f"   Trade Value: ${trade['trade_value']:,.2f}")
                print(f"   Stop Loss: ${trade['stop_loss']:,.2f}")
                print(f"   Take Profit: ${trade['take_profit']:,.2f}")
                print()
                print("⚠️ NOTE: This is a simulated trade for analysis.")
                print("   To execute real trades, enable trading in config.")
        else:
            print("⏸️ NO TRADE RECOMMENDED AT THIS TIME")
            print(f"   Reason: {analysis['reason']}")
        
        print("="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
        
        return analysis
    
    def save_trade_log(self, trade):
        """Save trade to log file"""
        log_path = os.path.join(BASE_DIR, 'conservative_trades_log.json')
        
        try:
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {'trades': [], 'metadata': {'strategy': 'conservative'}}
            
            log_data['trades'].append(trade)
            log_data['metadata']['last_updated'] = datetime.now().isoformat()
            
            with open(log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving trade log: {e}")

def main():
    trader = ConservativeTrader()
    trader.run_analysis()

if __name__ == "__main__":
    main()