#!/usr/bin/env python3
"""
Execute Conservative Crypto Trading Strategy
Using real market data with $1,000 capital
"""

import requests
import json
import datetime
import math
from typing import Dict, List, Optional

# Trading parameters
CAPITAL = 1000.0
STOP_LOSS_PCT = 0.05
TAKE_PROFIT_PCT = 0.10
MAX_TRADES_PER_DAY = 2
POSITION_SIZE_PCT = 0.10  # 10% of capital per trade

class RealMarketTrader:
    def __init__(self):
        self.capital = CAPITAL
        self.trades_today = 0
        self.trade_history = []
        self.last_trade_date = None
        
    def get_real_market_data(self) -> Dict:
        """Get real market data from Binance API"""
        try:
            symbols = ['BTCUSDT', 'ETHUSDT']
            results = {}
            
            for symbol in symbols:
                url = "https://api.binance.com/api/v3/ticker/24hr"
                params = {'symbol': symbol}
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    symbol_key = symbol.replace('USDT', 'USD')
                    results[symbol_key] = {
                        'price': float(data['lastPrice']),
                        'change': float(data['priceChangePercent']),
                        'high': float(data['highPrice']),
                        'low': float(data['lowPrice']),
                        'volume': float(data['volume']),
                        'bid': float(data['bidPrice']),
                        'ask': float(data['askPrice'])
                    }
            
            return results
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return {}
    
    def calculate_conservative_signals(self, market_data: Dict) -> List[Dict]:
        """Calculate conservative trading signals based on real market data"""
        signals = []
        
        for symbol, data in market_data.items():
            current_price = data['price']
            daily_high = data['high']
            daily_low = data['low']
            daily_change = data['change']
            volume = data['volume']
            
            # Calculate distance from daily high/low
            dist_from_high = (daily_high - current_price) / daily_high
            dist_from_low = (current_price - daily_low) / current_price
            
            # Conservative trading rules:
            # 1. Only consider if volume > threshold
            # 2. Buy signal: Price near daily low, small negative/neutral change
            # 3. Sell signal: Price near daily high, small positive change
            # 4. Avoid extreme volatility (>5% daily change)
            
            volume_ok = volume > 10000  # Reasonable volume threshold
            
            if not volume_ok:
                continue
            
            if abs(daily_change) > 5:  # Too volatile for conservative trading
                signal = {
                    'symbol': symbol,
                    'action': 'HOLD',
                    'reason': f'High volatility ({daily_change:.2f}%)',
                    'price': current_price
                }
                signals.append(signal)
                continue
            
            # Buy signal conditions
            if dist_from_low < 0.02 and -2 < daily_change < 1:  # Within 2% of low, not too bearish
                signal = {
                    'symbol': symbol,
                    'action': 'BUY',
                    'reason': f'Near daily low ({dist_from_low*100:.1f}% from low), change: {daily_change:.2f}%',
                    'price': current_price,
                    'confidence': 'MEDIUM'
                }
                signals.append(signal)
            
            # Sell signal conditions  
            elif dist_from_high < 0.02 and 0 < daily_change < 3:  # Within 2% of high, modest gains
                signal = {
                    'symbol': symbol,
                    'action': 'SELL',
                    'reason': f'Near daily high ({dist_from_high*100:.1f}% from high), change: {daily_change:.2f}%',
                    'price': current_price,
                    'confidence': 'MEDIUM'
                }
                signals.append(signal)
            else:
                signal = {
                    'symbol': symbol,
                    'action': 'HOLD',
                    'reason': f'Middle range ({dist_from_low*100:.1f}% from low, {dist_from_high*100:.1f}% from high)',
                    'price': current_price
                }
                signals.append(signal)
        
        return signals
    
    def check_trade_limits(self) -> bool:
        """Check daily trade limits"""
        today = datetime.date.today()
        
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
        
        return self.trades_today < MAX_TRADES_PER_DAY
    
    def calculate_position(self, price: float) -> Dict:
        """Calculate position size and risk parameters"""
        position_value = self.capital * POSITION_SIZE_PCT
        position_size = position_value / price
        
        return {
            'size': round(position_size, 6),
            'value': round(position_value, 2),
            'capital_used_pct': POSITION_SIZE_PCT * 100
        }
    
    def execute_simulated_trade(self, signal: Dict) -> Optional[Dict]:
        """Execute a simulated trade based on signal"""
        if not self.check_trade_limits():
            print(f"Daily trade limit reached ({self.trades_today}/{MAX_TRADES_PER_DAY})")
            return None
        
        symbol = signal['symbol']
        action = signal['action']
        price = signal['price']
        
        if action not in ['BUY', 'SELL']:
            return None
        
        position = self.calculate_position(price)
        
        # Calculate stop loss and take profit
        if action == 'BUY':
            stop_loss = price * (1 - STOP_LOSS_PCT)
            take_profit = price * (1 + TAKE_PROFIT_PCT)
            risk_amount = position['value'] * STOP_LOSS_PCT
            reward_amount = position['value'] * TAKE_PROFIT_PCT
        else:  # SELL
            stop_loss = price * (1 + STOP_LOSS_PCT)
            take_profit = price * (1 - TAKE_PROFIT_PCT)
            risk_amount = position['value'] * STOP_LOSS_PCT
            reward_amount = position['value'] * TAKE_PROFIT_PCT
        
        trade = {
            'id': f"TRADE_{len(self.trade_history)+1:03d}",
            'timestamp': datetime.datetime.now().isoformat(),
            'symbol': symbol,
            'action': action,
            'price': round(price, 2),
            'size': position['size'],
            'value': position['value'],
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'risk_amount': round(risk_amount, 2),
            'reward_amount': round(reward_amount, 2),
            'risk_reward_ratio': round(TAKE_PROFIT_PCT / STOP_LOSS_PCT, 2),
            'reason': signal['reason'],
            'confidence': signal.get('confidence', 'LOW'),
            'status': 'SIMULATED_EXECUTED'
        }
        
        self.trades_today += 1
        self.trade_history.append(trade)
        
        return trade
    
    def generate_trading_summary(self) -> str:
        """Generate comprehensive trading summary"""
        now = datetime.datetime.now()
        market_data = self.get_real_market_data()
        signals = self.calculate_conservative_signals(market_data)
        
        summary = []
        summary.append("CONSERVATIVE CRYPTO TRADING EXECUTION SUMMARY")
        summary.append("=" * 60)
        summary.append(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        summary.append(f"Timezone: Asia/Bangkok (GMT+7)")
        summary.append("")
        
        # Market Overview
        summary.append("MARKET OVERVIEW:")
        summary.append("-" * 40)
        for symbol, data in market_data.items():
            summary.append(f"{symbol}:")
            summary.append(f"  Price: ${data['price']:,.2f}")
            summary.append(f"  24h Change: {data['change']:+.2f}%")
            summary.append(f"  24h Range: ${data['low']:,.2f} - ${data['high']:,.2f}")
            summary.append(f"  Volume: {data['volume']:,.0f}")
        summary.append("")
        
        # Trading Parameters
        summary.append("TRADING PARAMETERS:")
        summary.append("-" * 40)
        summary.append(f"Capital: ${self.capital:,.2f}")
        summary.append(f"Position Size: {POSITION_SIZE_PCT*100}% of capital per trade")
        summary.append(f"Stop Loss: {STOP_LOSS_PCT*100}%")
        summary.append(f"Take Profit: {TAKE_PROFIT_PCT*100}%")
        summary.append(f"Max Trades/Day: {MAX_TRADES_PER_DAY}")
        summary.append(f"Risk/Reward Ratio: {TAKE_PROFIT_PCT/STOP_LOSS_PCT:.1f}:1")
        summary.append(f"Trades Today: {self.trades_today}/{MAX_TRADES_PER_DAY}")
        summary.append("")
        
        # Trading Signals
        summary.append("TRADING SIGNALS ANALYSIS:")
        summary.append("-" * 40)
        for signal in signals:
            summary.append(f"{signal['symbol']}: {signal['action']}")
            summary.append(f"  Price: ${signal['price']:,.2f}")
            summary.append(f"  Reason: {signal['reason']}")
            if 'confidence' in signal:
                summary.append(f"  Confidence: {signal['confidence']}")
            summary.append("")
        
        # Trade Execution
        summary.append("TRADE EXECUTION:")
        summary.append("-" * 40)
        if self.trade_history:
            for trade in self.trade_history[-MAX_TRADES_PER_DAY:]:  # Show recent trades
                summary.append(f"Trade {trade['id']}:")
                summary.append(f"  {trade['action']} {trade['symbol']} @ ${trade['price']:,.2f}")
                summary.append(f"  Size: {trade['size']} (Value: ${trade['value']:,.2f})")
                summary.append(f"  Stop Loss: ${trade['stop_loss']:,.2f}")
                summary.append(f"  Take Profit: ${trade['take_profit']:,.2f}")
                summary.append(f"  Risk: ${trade['risk_amount']:,.2f} | Reward: ${trade['reward_amount']:,.2f}")
                summary.append(f"  Risk/Reward: {trade['risk_reward_ratio']}:1")
                summary.append(f"  Reason: {trade['reason']}")
                summary.append(f"  Status: {trade['status']}")
                summary.append("")
        else:
            summary.append("No trades executed yet today.")
            summary.append("")
        
        # Recommendations
        summary.append("RECOMMENDATIONS:")
        summary.append("-" * 40)
        
        # Check if we should execute any trades
        executable_signals = [s for s in signals if s['action'] in ['BUY', 'SELL']]
        
        if not self.check_trade_limits():
            summary.append("✓ Daily trade limit reached - wait for next trading day")
        elif executable_signals:
            available_trades = MAX_TRADES_PER_DAY - self.trades_today
            summary.append(f"✓ {available_trades} trade(s) available today")
            
            for signal in executable_signals[:available_trades]:  # Only show up to available slots
                action = "BUY" if signal['action'] == 'BUY' else "SELL (short)"
                summary.append(f"✓ Consider {action} {signal['symbol']} at ${signal['price']:,.2f}")
                summary.append(f"  Reason: {signal['reason']}")
        else:
            summary.append("✓ No clear conservative signals - maintain HOLD position")
            summary.append("✓ Wait for prices to approach support/resistance levels")
        
        summary.append("")
        summary.append("RISK MANAGEMENT:")
        summary.append("-" * 40)
        summary.append("✓ Always use stop-loss orders (5% maximum)")
        summary.append("✓ Take profit at 10% or adjust based on market conditions")
        summary.append("✓ Maximum 2 trades per day to avoid overtrading")
        summary.append("✓ 10% position sizing preserves capital for opportunities")
        summary.append("✓ Monitor market sentiment and volume changes")
        
        return "\n".join(summary)
    
    def execute_daily_trading(self):
        """Execute daily trading routine"""
        print("Executing Conservative Crypto Trading Strategy...")
        print("=" * 60)
        
        # Get market data
        market_data = self.get_real_market_data()
        if not market_data:
            print("Failed to fetch market data. Exiting.")
            return
        
        # Calculate signals
        signals = self.calculate_conservative_signals(market_data)
        
        # Execute trades based on signals
        executed_trades = []
        for signal in signals:
            if signal['action'] in ['BUY', 'SELL'] and self.check_trade_limits():
                trade = self.execute_simulated_trade(signal)
                if trade:
                    executed_trades.append(trade)
                    print(f"Executed {trade['action']} {trade['symbol']} @ ${trade['price']:,.2f}")
        
        # Generate summary
        summary = self.generate_trading_summary()
        
        # Save to file
        with open("daily_trading_summary.txt", "w") as f:
            f.write(summary)
        
        print("\n" + summary)
        
        return summary

def main():
    trader = RealMarketTrader()
    summary = trader.execute_daily_trading()
    
    # Return plain text summary for cron delivery
    return summary

if __name__ == "__main__":
    main()