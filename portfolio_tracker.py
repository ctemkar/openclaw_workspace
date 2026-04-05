#!/usr/bin/env python3
"""
PORTFOLIO TRACKER - FIXED SYSTEM
Tracks both cash AND holdings value to show actual portfolio value
"""

import json
import time
from datetime import datetime
import os

class PortfolioTracker:
    """Tracks complete portfolio value (cash + holdings)"""
    
    def __init__(self, initial_cash=10000.00):
        """Initialize with cash balance"""
        self.cash = initial_cash
        self.holdings = {}  # symbol: {'amount': X, 'entry_price': Y, 'entry_time': Z}
        self.trade_history = []
        self.audit_file = "portfolio_trades_audit.json"
        self.portfolio_file = "portfolio_status.json"
        
        # Performance tracking
        self.peak_portfolio_value = initial_cash
        self.max_drawdown = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0
        
        # Risk management
        self.max_position_size_pct = 0.08  # 8% max per position
        self.max_portfolio_risk_pct = 0.02  # 2% max risk per trade
        self.stop_loss_pct = 0.02  # 2% stop loss
        self.profit_target_pct = 0.025  # 2.5% profit target
        
        print("\n" + "="*80)
        print("💰 PORTFOLIO TRACKER INITIALIZED")
        print("="*80)
        print(f"Starting Cash: ${self.cash:,.2f}")
        print(f"Starting Portfolio Value: ${self.cash:,.2f}")
        print(f"Risk Management: Stop-loss {self.stop_loss_pct*100}%, Profit target {self.profit_target_pct*100}%")
        print("="*80)
    
    def get_market_prices(self):
        """Get current market prices from data generator"""
        try:
            with open("real_trading_data/dashboard_data.json", "r") as f:
                data = json.load(f)
                return data.get('market_prices', {})
        except:
            return {}
    
    def calculate_portfolio_value(self):
        """Calculate total portfolio value (cash + holdings)"""
        market_prices = self.get_market_prices()
        
        holdings_value = 0
        for symbol, position in self.holdings.items():
            current_price = market_prices.get(symbol, 0)
            if current_price > 0:
                holdings_value += position['amount'] * current_price
        
        portfolio_value = self.cash + holdings_value
        
        # Update peak and drawdown
        if portfolio_value > self.peak_portfolio_value:
            self.peak_portfolio_value = portfolio_value
        
        current_drawdown = (self.peak_portfolio_value - portfolio_value) / self.peak_portfolio_value * 100
        if current_drawdown > self.max_drawdown:
            self.max_drawdown = current_drawdown
        
        return portfolio_value, holdings_value
    
    def execute_buy(self, symbol, amount, price, reason=""):
        """Execute a BUY trade and update portfolio"""
        if amount <= 0 or price <= 0:
            return False, "Invalid amount or price"
        
        trade_value = amount * price
        fee = trade_value * 0.001  # 0.1% fee
        
        # Check if we have enough cash
        if trade_value + fee > self.cash:
            # Adjust amount to fit available cash
            max_value = self.cash * 0.99  # Leave 1% buffer
            amount = max_value / price
            trade_value = amount * price
            fee = trade_value * 0.001
            reason = f"{reason} (size_adjusted)"
        
        # Execute buy
        self.cash -= (trade_value + fee)
        
        if symbol in self.holdings:
            # Average down existing position
            old_amount = self.holdings[symbol]['amount']
            old_value = old_amount * self.holdings[symbol]['entry_price']
            new_value = trade_value
            total_amount = old_amount + amount
            avg_price = (old_value + trade_value) / total_amount
            
            self.holdings[symbol] = {
                'amount': total_amount,
                'entry_price': avg_price,
                'entry_time': time.time(),
                'total_cost': old_value + trade_value + fee
            }
        else:
            # New position
            self.holdings[symbol] = {
                'amount': amount,
                'entry_price': price,
                'entry_time': time.time(),
                'total_cost': trade_value + fee
            }
        
        # Record trade
        portfolio_value, holdings_value = self.calculate_portfolio_value()
        
        trade_record = {
            'time': datetime.now().isoformat(),
            'symbol': symbol,
            'side': 'buy',
            'amount': amount,
            'price': price,
            'value': trade_value,
            'fee': fee,
            'cash_balance': self.cash,
            'holdings_value': holdings_value,
            'portfolio_value': portfolio_value,
            'reason': reason,
            'trade_pnl': 0,  # No P&L on buy
            'position_count': len(self.holdings)
        }
        
        self._save_trade(trade_record)
        
        result = f"BUY {amount:.6f} {symbol} at ${price:,.2f}"
        result += f" | Cash: ${self.cash:,.2f}"
        result += f" | Portfolio: ${portfolio_value:,.2f}"
        result += f" | Reason: {reason}"
        
        return True, result
    
    def execute_sell(self, symbol, amount, price, reason=""):
        """Execute a SELL trade and update portfolio"""
        if symbol not in self.holdings:
            return False, f"No {symbol} position"
        
        position = self.holdings[symbol]
        if amount > position['amount']:
            amount = position['amount']  # Sell entire position
            reason = f"{reason} (full_position)"
        
        trade_value = amount * price
        fee = trade_value * 0.001  # 0.1% fee
        
        # Calculate P&L
        entry_price = position['entry_price']
        trade_pnl = (price - entry_price) * amount - fee
        
        # Execute sell
        self.cash += (trade_value - fee)
        
        # Update or remove position
        if amount == position['amount']:
            # Sold entire position
            del self.holdings[symbol]
        else:
            # Partial sell
            self.holdings[symbol]['amount'] -= amount
        
        # Update performance stats
        self.total_trades += 1
        self.total_profit += trade_pnl
        
        if trade_pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        # Record trade
        portfolio_value, holdings_value = self.calculate_portfolio_value()
        
        trade_record = {
            'time': datetime.now().isoformat(),
            'symbol': symbol,
            'side': 'sell',
            'amount': amount,
            'price': price,
            'value': trade_value,
            'fee': fee,
            'cash_balance': self.cash,
            'holdings_value': holdings_value,
            'portfolio_value': portfolio_value,
            'reason': reason,
            'trade_pnl': trade_pnl,
            'position_count': len(self.holdings),
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'total_profit': self.total_profit
        }
        
        self._save_trade(trade_record)
        
        result = f"SELL {amount:.6f} {symbol} at ${price:,.2f}"
        result += f" | P&L: ${trade_pnl:+,.2f}"
        result += f" | Cash: ${self.cash:,.2f}"
        result += f" | Portfolio: ${portfolio_value:,.2f}"
        result += f" | Reason: {reason}"
        
        return True, result
    
    def _save_trade(self, trade_record):
        """Save trade to audit log"""
        with open(self.audit_file, 'a') as f:
            f.write(json.dumps(trade_record) + '\n')
        
        self.trade_history.append(trade_record)
        self._save_portfolio_status()
    
    def _save_portfolio_status(self):
        """Save current portfolio status"""
        portfolio_value, holdings_value = self.calculate_portfolio_value()
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'cash_balance': self.cash,
            'holdings_value': holdings_value,
            'portfolio_value': portfolio_value,
            'peak_portfolio_value': self.peak_portfolio_value,
            'max_drawdown_pct': self.max_drawdown,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'total_profit': self.total_profit,
            'win_rate': self.winning_trades / self.total_trades if self.total_trades > 0 else 0,
            'positions': len(self.holdings),
            'holdings': self.holdings
        }
        
        with open(self.portfolio_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    def check_position_health(self):
        """Check all positions for stop-loss or profit target"""
        market_prices = self.get_market_prices()
        actions = []
        
        for symbol, position in list(self.holdings.items()):
            current_price = market_prices.get(symbol, 0)
            if current_price <= 0:
                continue
            
            entry_price = position['entry_price']
            pnl_pct = (current_price - entry_price) / entry_price
            
            # Check profit target
            if pnl_pct >= self.profit_target_pct:
                actions.append({
                    'symbol': symbol,
                    'side': 'sell',
                    'amount': position['amount'],
                    'reason': f'profit_target_reached (+{pnl_pct:.2%})',
                    'urgency': 'high'
                })
            
            # Check stop loss
            elif pnl_pct <= -self.stop_loss_pct:
                actions.append({
                    'symbol': symbol,
                    'side': 'sell',
                    'amount': position['amount'],
                    'reason': f'stop_loss_triggered ({pnl_pct:.2%})',
                    'urgency': 'critical'
                })
        
        return actions
    
    def get_portfolio_summary(self):
        """Get comprehensive portfolio summary"""
        portfolio_value, holdings_value = self.calculate_portfolio_value()
        
        summary = {
            'cash_balance': self.cash,
            'holdings_value': holdings_value,
            'portfolio_value': portfolio_value,
            'peak_value': self.peak_portfolio_value,
            'max_drawdown': f"{self.max_drawdown:.2f}%",
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'total_profit': self.total_profit,
            'win_rate': f"{(self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0:.1f}%",
            'positions': len(self.holdings),
            'positions_detail': self.holdings
        }
        
        return summary
    
    def print_status(self):
        """Print current portfolio status"""
        portfolio_value, holdings_value = self.calculate_portfolio_value()
        
        print("\n" + "="*80)
        print("💰 PORTFOLIO STATUS")
        print("="*80)
        print(f"Cash Balance:      ${self.cash:,.2f}")
        print(f"Holdings Value:    ${holdings_value:,.2f}")
        print(f"Portfolio Value:   ${portfolio_value:,.2f}")
        print(f"Peak Value:        ${self.peak_portfolio_value:,.2f}")
        print(f"Max Drawdown:      {self.max_drawdown:.2f}%")
        
        if self.total_trades > 0:
            win_rate = (self.winning_trades / self.total_trades) * 100
            print(f"\n📊 PERFORMANCE:")
            print(f"Total Trades:      {self.total_trades}")
            print(f"Winning Trades:    {self.winning_trades}")
            print(f"Losing Trades:     {self.losing_trades}")
            print(f"Win Rate:          {win_rate:.1f}%")
            print(f"Total Profit:      ${self.total_profit:+,.2f}")
        
        if self.holdings:
            print(f"\n📈 CURRENT POSITIONS ({len(self.holdings)}):")
            market_prices = self.get_market_prices()
            
            for symbol, position in self.holdings.items():
                current_price = market_prices.get(symbol, position['entry_price'])
                position_value = position['amount'] * current_price
                entry_value = position['amount'] * position['entry_price']
                pnl = position_value - entry_value
                pnl_pct = (pnl / entry_value) * 100 if entry_value > 0 else 0
                
                print(f"  • {symbol}:")
                print(f"    Amount:    {position['amount']:.6f}")
                print(f"    Entry:     ${position['entry_price']:,.2f}")
                print(f"    Current:   ${current_price:,.2f}")
                print(f"    Value:     ${position_value:,.2f}")
                print(f"    P&L:       ${pnl:+,.2f} ({pnl_pct:+.2f}%)")
        
        print("="*80)

def main():
    """Test the portfolio tracker"""
    print("Testing Portfolio Tracker...")
    
    # Start with current cash balance
    tracker = PortfolioTracker(initial_cash=1590.96)
    
    # Get market prices
    market_prices = tracker.get_market_prices()
    
    print("\nMarket Prices Available:")
    for symbol, price in list(market_prices.items())[:5]:
        print(f"  {symbol}: ${price:,.2f}")
    
    # Show initial status
    tracker.print_status()
    
    # Save initial status
    tracker._save_portfolio_status()
    
    print("\n✅ Portfolio Tracker initialized successfully!")
    print("   Portfolio value tracking: ACTIVE")
    print("   Risk management: ACTIVE")
    print("   Audit logging: ACTIVE")

if __name__ == "__main__":
    main()