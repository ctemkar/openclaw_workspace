#!/usr/bin/env python3
"""
Improved trading logic for 26-crypto bot
Adds: position tracking, market filters, better risk management
"""

import json
import time
from datetime import datetime

class ImprovedTradingLogic:
    def __init__(self):
        self.open_positions = []
        self.max_positions = 3
        self.daily_pnl = 0
        self.daily_loss_limit = -0.05  # -5% daily loss limit
        self.position_count = 0
        
    def can_open_new_position(self, capital):
        """Check if we can open a new position"""
        if len(self.open_positions) >= self.max_positions:
            return False, "Max positions reached"
        
        # Check daily loss limit
        if self.daily_pnl <= self.daily_loss_limit * capital:
            return False, "Daily loss limit reached"
        
        return True, "OK"
    
    def add_position(self, trade_data):
        """Add a new position to tracking"""
        position = {
            'symbol': trade_data['symbol'],
            'entry_price': trade_data.get('entry_price', trade_data.get('current_price')),
            'entry_time': datetime.now().isoformat(),
            'position_size': trade_data.get('position_size', 0),
            'side': trade_data.get('side', 'sell'),
            'stop_loss': trade_data.get('stop_loss'),
            'take_profit': trade_data.get('take_profit'),
            'status': 'OPEN'
        }
        self.open_positions.append(position)
        self.position_count += 1
        return position
    
    def remove_position(self, symbol):
        """Remove a position (when closed)"""
        self.open_positions = [p for p in self.open_positions if p['symbol'] != symbol]
    
    def check_market_filters(self, crypto_data, btc_trend):
        """Apply market context filters"""
        filters = []
        
        # 1. BTC trend filter
        if btc_trend > 1.0:  # BTC up >1% in last hour
            filters.append(("BTC up >1%, avoid shorting", False))
        
        # 2. Volume filter
        if crypto_data.get('volume_24h', 0) < 1000000:  # < $1M volume
            filters.append(("Low volume (<$1M)", False))
        
        # 3. RSI filter
        rsi = crypto_data.get('rsi', 50)
        if rsi < 30:  # Oversold - might bounce
            filters.append(("Oversold (RSI<30), avoid shorting", False))
        
        # 4. Time filter (avoid first hour of US trading)
        hour = datetime.now().hour
        if 13 <= hour <= 14:  # 1-2 PM UTC = 8-9 AM EST
            filters.append(("US market open hour, high volatility", True))
        
        # If any filter returns False, don't trade
        for filter_name, allowed in filters:
            if not allowed:
                return False, f"Filter failed: {filter_name}"
        
        return True, "All filters passed"
    
    def calculate_position_size(self, capital, risk_per_trade=0.02):
        """Calculate position size based on risk"""
        # Risk 2% of capital per trade
        risk_amount = capital * risk_per_trade
        return risk_amount
    
    def should_short(self, change_percent, confirmation_data):
        """Improved short decision logic"""
        # 1. Minimum drop threshold
        if change_percent > -3.0:
            return False, f"Drop too small: {change_percent:.2f}% (need >3%)"
        
        # 2. Confirmation: price stayed down for 15+ minutes
        if not confirmation_data.get('confirmed', False):
            return False, "No confirmation (need 15+ min downtrend)"
        
        # 3. Check if below moving average
        if not confirmation_data.get('below_ma', False):
            return False, "Not below moving average"
        
        # 4. Check volume spike
        if not confirmation_data.get('volume_spike', False):
            return False, "No volume spike (weak move)"
        
        return True, "Good short opportunity"
    
    def update_pnl(self, pnl_amount):
        """Update daily P&L"""
        self.daily_pnl += pnl_amount
    
    def get_status(self):
        """Get current trading status"""
        return {
            'open_positions': len(self.open_positions),
            'max_positions': self.max_positions,
            'daily_pnl': self.daily_pnl,
            'position_count': self.position_count,
            'can_trade': len(self.open_positions) < self.max_positions and self.daily_pnl > self.daily_loss_limit
        }

# Example usage
if __name__ == "__main__":
    logic = ImprovedTradingLogic()
    
    # Test scenarios
    print("🧪 TESTING IMPROVED TRADING LOGIC")
    print("=" * 60)
    
    # Test 1: Can open position?
    can_trade, reason = logic.can_open_new_position(1000)
    print(f"Test 1 - Can open position: {can_trade} ({reason})")
    
    # Test 2: Market filters
    crypto_data = {'volume_24h': 500000, 'rsi': 25}
    btc_trend = 1.5  # BTC up 1.5%
    filter_ok, filter_reason = logic.check_market_filters(crypto_data, btc_trend)
    print(f"Test 2 - Market filters: {filter_ok} ({filter_reason})")
    
    # Test 3: Should short?
    change_percent = -3.5
    confirmation_data = {'confirmed': True, 'below_ma': True, 'volume_spike': True}
    should_short, short_reason = logic.should_short(change_percent, confirmation_data)
    print(f"Test 3 - Should short: {should_short} ({short_reason})")
    
    # Test 4: Position size
    position_size = logic.calculate_position_size(1000)
    print(f"Test 4 - Position size for $1000 capital: ${position_size:.2f}")
    
    # Test 5: Add position
    trade_data = {
        'symbol': 'ETH/USDT',
        'current_price': 2000,
        'position_size': position_size
    }
    position = logic.add_position(trade_data)
    print(f"Test 5 - Added position: {position['symbol']} at ${position['entry_price']}")
    
    # Test 6: Status
    status = logic.get_status()
    print(f"Test 6 - Status: {status}")
    
    print("\n✅ Improved logic ready for integration into main bot")