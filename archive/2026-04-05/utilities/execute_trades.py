#!/usr/bin/env python3
"""
Execute conservative crypto trades based on analysis
"""

import requests
import json
from datetime import datetime
import time

# Configuration
CAPITAL = 1000.0
STOP_LOSS = 0.05  # 5%
TAKE_PROFIT = 0.10  # 10%
MAX_TRADES_PER_DAY = 2
TRADE_SIZE_PERCENT = 0.20  # 20% of capital per trade

class ConservativeTrader:
    def __init__(self):
        self.trades_today = 0
        self.last_trade_date = None
        self.executed_trades = []
    
    def can_trade(self):
        """Check if we can execute more trades today"""
        today = datetime.now().date()
        
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
        
        return self.trades_today < MAX_TRADES_PER_DAY
    
    def get_current_price(self, symbol):
        """Get current price from Gemini"""
        try:
            url = f"https://api.gemini.com/v1/pubticker/{symbol}"
            response = requests.get(url, timeout=10)
            data = response.json()
            return float(data["last"])
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return None
    
    def calculate_position_size(self, price):
        """Calculate position size based on capital and risk"""
        trade_amount = CAPITAL * TRADE_SIZE_PERCENT
        position_size = trade_amount / price
        return position_size
    
    def simulate_trade(self, symbol, side, price, reason):
        """Simulate a trade execution (in real implementation, this would call Gemini API)"""
        
        if not self.can_trade():
            return {
                "status": "rejected",
                "reason": f"Maximum trades per day ({MAX_TRADES_PER_DAY}) reached"
            }
        
        position_size = self.calculate_position_size(price)
        
        # Calculate stop loss and take profit prices
        if side == "buy":
            stop_loss_price = price * (1 - STOP_LOSS)
            take_profit_price = price * (1 + TAKE_PROFIT)
        else:  # sell
            stop_loss_price = price * (1 + STOP_LOSS)
            take_profit_price = price * (1 - TAKE_PROFIT)
        
        trade = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "entry_price": price,
            "position_size": position_size,
            "notional_value": position_size * price,
            "stop_loss": stop_loss_price,
            "take_profit": take_profit_price,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "status": "simulated_executed",
            "trade_id": f"sim_{int(time.time())}_{symbol}"
        }
        
        self.executed_trades.append(trade)
        self.trades_today += 1
        
        return trade
    
    def analyze_and_trade(self):
        """Main trading logic"""
        print("=" * 70)
        print("CONSERVATIVE CRYPTO TRADING EXECUTION")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        symbols = ["btcusd", "ethusd"]
        
        # Get current market data
        market_data = {}
        for symbol in symbols:
            price = self.get_current_price(symbol)
            if price:
                market_data[symbol] = price
                print(f"\n{symbol.upper()}:")
                print(f"  Current Price: ${price:,.2f}")
        
        # Conservative trading logic
        trades_to_execute = []
        
        # Strategy: Only trade if price is stable (less than 2% change from recent average)
        # For simulation, we'll use a simple mean reversion strategy
        
        for symbol, price in market_data.items():
            # Get order book for support/resistance
            try:
                url = f"https://api.gemini.com/v1/book/{symbol}"
                response = requests.get(url, timeout=10)
                order_book = response.json()
                
                bids = order_book.get("bids", [])[:3]
                asks = order_book.get("asks", [])[:3]
                
                if bids and asks:
                    avg_bid = sum(float(bid["price"]) for bid in bids) / len(bids)
                    avg_ask = sum(float(ask["price"]) for ask in asks) / len(asks)
                    
                    print(f"  Support (avg bid): ${avg_bid:,.2f}")
                    print(f"  Resistance (avg ask): ${avg_ask:,.2f}")
                    
                    # Conservative entry conditions:
                    # 1. Price near support for BUY
                    # 2. Price near resistance for SELL
                    # 3. Small position size (20% of capital)
                    
                    buy_zone = avg_bid * 1.01  # Within 1% of support
                    sell_zone = avg_ask * 0.99  # Within 1% of resistance
                    
                    if price <= buy_zone:
                        reason = f"Price ${price:,.2f} near support ${avg_bid:,.2f}"
                        trades_to_execute.append({
                            "symbol": symbol,
                            "side": "buy",
                            "price": price,
                            "reason": reason
                        })
                        print(f"  ✅ BUY opportunity: {reason}")
                    
                    elif price >= sell_zone:
                        reason = f"Price ${price:,.2f} near resistance ${avg_ask:,.2f}"
                        trades_to_execute.append({
                            "symbol": symbol,
                            "side": "sell",
                            "price": price,
                            "reason": reason
                        })
                        print(f"  ✅ SELL opportunity: {reason}")
                    
                    else:
                        print(f"  ⏸️  No clear entry - price between support/resistance")
            
            except Exception as e:
                print(f"  Error analyzing {symbol}: {e}")
        
        # Execute trades (simulated)
        print("\n" + "=" * 70)
        print("TRADE EXECUTION")
        print("=" * 70)
        
        executed_trades = []
        
        for trade_op in trades_to_execute[:2]:  # Max 2 trades
            if self.can_trade():
                trade = self.simulate_trade(
                    symbol=trade_op["symbol"],
                    side=trade_op["side"],
                    price=trade_op["price"],
                    reason=trade_op["reason"]
                )
                
                if trade["status"] == "simulated_executed":
                    executed_trades.append(trade)
                    print(f"\n✓ Trade Executed:")
                    print(f"  Symbol: {trade['symbol']}")
                    print(f"  Side: {trade['side']}")
                    print(f"  Entry: ${trade['entry_price']:,.2f}")
                    print(f"  Size: {trade['position_size']:.6f}")
                    print(f"  Value: ${trade['notional_value']:,.2f}")
                    print(f"  Stop Loss: ${trade['stop_loss']:,.2f}")
                    print(f"  Take Profit: ${trade['take_profit']:,.2f}")
                    print(f"  Reason: {trade['reason']}")
                else:
                    print(f"\n✗ Trade Rejected: {trade['reason']}")
            else:
                print(f"\n✗ Cannot execute more trades today (max: {MAX_TRADES_PER_DAY})")
                break
        
        # Generate summary
        print("\n" + "=" * 70)
        print("TRADING SUMMARY")
        print("=" * 70)
        
        if executed_trades:
            print(f"\nTrades Executed Today: {len(executed_trades)}")
            total_invested = sum(trade['notional_value'] for trade in executed_trades)
            print(f"Total Capital Deployed: ${total_invested:,.2f}")
            print(f"Remaining Capital: ${CAPITAL - total_invested:,.2f}")
            
            print("\nTrade Details:")
            for i, trade in enumerate(executed_trades, 1):
                print(f"\n{i}. {trade['side']} {trade['symbol']}")
                print(f"   Entry: ${trade['entry_price']:,.2f}")
                print(f"   Size: {trade['position_size']:.6f}")
                print(f"   Stop Loss: ${trade['stop_loss']:,.2f} ({STOP_LOSS*100}% risk)")
                print(f"   Take Profit: ${trade['take_profit']:,.2f} ({TAKE_PROFIT*100}% target)")
                print(f"   Reason: {trade['reason']}")
        else:
            print("\nNo trades executed.")
            print("Reason: No high-confidence opportunities meeting conservative criteria.")
        
        print(f"\nRemaining Trades Available Today: {MAX_TRADES_PER_DAY - self.trades_today}")
        print(f"\nAnalysis completed at: {datetime.now().strftime('%H:%M:%S')}")
        
        return executed_trades

def main():
    trader = ConservativeTrader()
    trades = trader.analyze_and_trade()
    
    # Return plain text summary for cron delivery
    summary_lines = []
    summary_lines.append("=" * 60)
    summary_lines.append("CRYPTO TRADING SUMMARY - CONSERVATIVE STRATEGY")
    summary_lines.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append("=" * 60)
    
    if trades:
        summary_lines.append(f"\nTrades Executed: {len(trades)}")
        total_invested = sum(trade['notional_value'] for trade in trades)
        summary_lines.append(f"Capital Deployed: ${total_invested:,.2f}")
        summary_lines.append(f"Remaining Capital: ${CAPITAL - total_invested:,.2f}")
        
        for i, trade in enumerate(trades, 1):
            summary_lines.append(f"\n{i}. {trade['side']} {trade['symbol']}")
            summary_lines.append(f"   Entry Price: ${trade['entry_price']:,.2f}")
            summary_lines.append(f"   Position Size: {trade['position_size']:.6f}")
            summary_lines.append(f"   Stop Loss: ${trade['stop_loss']:,.2f} (5% risk)")
            summary_lines.append(f"   Take Profit: ${trade['take_profit']:,.2f} (10% target)")
            summary_lines.append(f"   Reason: {trade['reason']}")
    else:
        summary_lines.append("\nNo trades executed today.")
        summary_lines.append("Market conditions did not meet conservative entry criteria.")
        summary_lines.append("Recommendation: Wait for clearer signals near support/resistance levels.")
    
    summary_lines.append(f"\nRemaining Trades Available: {MAX_TRADES_PER_DAY - trader.trades_today}")
    summary_lines.append(f"\nNext analysis scheduled per cron job.")
    
    # Print summary for cron delivery
    print("\n" + "\n".join(summary_lines))
    
    # Also save to file for record keeping
    with open("trading_summary.txt", "w") as f:
        f.write("\n".join(summary_lines))

if __name__ == "__main__":
    main()