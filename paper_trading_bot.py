#!/usr/bin/env python3
"""
SAFE PAPER TRADING BOT
Simulates trading without real money
For testing and strategy development only
"""

import time
import logging
import json
from datetime import datetime

print("="*70)
print("📝 PAPER TRADING BOT - SIMULATION ONLY")
print("="*70)
print("NO REAL MONEY WILL BE USED")
print("ALL TRADES ARE SIMULATED")
print("="*70)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - PAPER - %(message)s'
)
logger = logging.getLogger(__name__)

class PaperTradingBot:
    def __init__(self):
        self.paper_balance = 10000.00  # Virtual $10,000
        self.trade_history = []
        self.paper_mode = True
        
        print(f"\n💰 PAPER BALANCE: ${self.paper_balance:.2f}")
        print("🎯 MODE: SIMULATION ONLY - NO REAL MONEY")
        print("="*70)
    
    def simulate_trade(self, symbol, side, amount, price):
        """Simulate a trade without real money"""
        trade_value = amount * price
        fee = trade_value * 0.001  # 0.1% fee
        
        if side == 'buy':
            cost = trade_value + fee
            if cost > self.paper_balance:
                return False, "Insufficient paper balance"
            
            self.paper_balance -= cost
            result = f"PAPER BUY: {amount} {symbol} @ ${price:.2f} = ${trade_value:.2f} (fee: ${fee:.4f})"
            
        else:  # sell
            revenue = trade_value - fee
            self.paper_balance += revenue
            result = f"PAPER SELL: {amount} {symbol} @ ${price:.2f} = ${trade_value:.2f} (fee: ${fee:.4f})"
        
        trade_record = {
            'time': datetime.now().isoformat(),
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': price,
            'value': trade_value,
            'fee': fee,
            'paper_balance': self.paper_balance,
            'real_money': False
        }
        
        self.trade_history.append(trade_record)
        
        # Save to log
        with open('paper_trading_log.json', 'a') as f:
            f.write(json.dumps(trade_record) + '\n')
        
        return True, result
    
    def run(self):
        """Main paper trading loop"""
        print("\n📈 PAPER TRADING SIMULATION STARTING...")
        print("   Mode: 100% simulated")
        print("   Balance: Virtual $10,000")
        print("   Real money: $0.00")
        print("="*70)
        
        cycle = 0
        while True:
            cycle += 1
            print(f"\n📊 PAPER CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            print(f"   Virtual Balance: ${self.paper_balance:.2f}")
            print(f"   Real Money Used: $0.00")
            print(f"   Mode: SIMULATION ONLY")
            
            # Simulate checking market (no real API calls)
            print("   📡 Checking simulated market data...")
            
            # Simulate a trade decision
            if cycle % 3 == 0:
                success, result = self.simulate_trade(
                    symbol='BTC/USDT',
                    side='buy' if cycle % 6 == 0 else 'sell',
                    amount=0.001,
                    price=67000.00
                )
                
                if success:
                    print(f"   ✅ {result}")
                else:
                    print(f"   ⚠️ {result}")
            
            print(f"   ⏰ Next paper cycle in 30 seconds...")
            time.sleep(30)

def main():
    """Main function"""
    print("\n" + "="*70)
    print("🚀 SAFE PAPER TRADING SYSTEM")
    print("="*70)
    print("This system:")
    print("   1. Uses ZERO real money")
    print("   2. Trades with virtual balance only")
    print("   3. Logs all simulated trades")
    print("   4. Cannot access real exchange APIs")
    print("="*70)
    
    bot = PaperTradingBot()
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Paper trading stopped by user")
        print(f"💰 Final paper balance: ${bot.paper_balance:.2f}")
        print(f"📊 Total simulated trades: {len(bot.trade_history)}")
        print("="*70)

if __name__ == "__main__":
    main()
