#!/usr/bin/env python3
"""
FIXED LLM CONSENSUS TRADING SYSTEM
Uses portfolio tracker and proper risk management
"""

import json
import time
import os
from datetime import datetime
from portfolio_tracker import PortfolioTracker

class FixedLLMConsensusTrading:
    """Fixed trading system with proper portfolio tracking"""
    
    def __init__(self, initial_cash=10000.00):
        """Initialize with portfolio tracker"""
        print("\n" + "="*80)
        print("🤖 FIXED LLM CONSENSUS TRADING SYSTEM")
        print("="*80)
        
        # Initialize portfolio tracker
        self.portfolio = PortfolioTracker(initial_cash=initial_cash)
        
        # Trading parameters
        self.buy_threshold = 7.0  # LLM score ≥ 7.0 to buy
        self.sell_threshold = 3.0  # LLM score ≤ 3.0 to sell
        self.min_position_size = 0.03  # 3% of portfolio min
        self.max_position_size = 0.08  # 8% of portfolio max
        self.max_positions = 2  # Max 2 positions
        self.min_trade_interval = 300  # 5 minutes between trades
        
        # LLM model weights
        self.model_weights = {
            'GPT-4': 1.2,  # Higher weight for GPT-4
            'Claude-3': 1.0,
            'Gemini Pro': 1.0,
            'Llama-3': 1.0,
            'Mixtral': 1.0,
            'Consensus': 1.5  # Extra weight for consensus
        }
        
        # Performance tracking
        self.last_trade_time = 0
        self.trade_count = 0
        self.llm_decision_log = []
        
        print("STRATEGY: LLM-DRIVEN WITH PORTFOLIO TRACKING")
        print(f"  • Buy threshold: LLM score ≥ {self.buy_threshold}/10")
        print(f"  • Sell threshold: LLM score ≤ {self.sell_threshold}/10")
        print(f"  • Position size: {self.min_position_size*100}-{self.max_position_size*100}% of portfolio")
        print(f"  • Max positions: {self.max_positions}")
        print(f"  • Trade interval: {self.min_trade_interval//60} minutes")
        print(f"  • Starting cash: ${initial_cash:,.2f}")
        print("="*80)
    
    def get_llm_scores(self):
        """Get LLM scores from data generator"""
        try:
            with open("real_trading_data/llm_scores.json", "r") as f:
                return json.load(f)
        except:
            return []
    
    def get_spread_analysis(self):
        """Get spread analysis for trading opportunities"""
        try:
            with open("real_trading_data/spread_analysis.json", "r") as f:
                return json.load(f)
        except:
            return []
    
    def calculate_llm_consensus(self, symbol):
        """Calculate weighted LLM consensus for a symbol"""
        llm_scores = self.get_llm_scores()
        
        if not llm_scores:
            return None, "No LLM data available"
        
        # Calculate weighted consensus
        total_score = 0
        total_weight = 0
        model_details = []
        
        for llm in llm_scores:
            model = llm.get('model', 'Unknown')
            score = llm.get('score', 5.0)
            confidence = llm.get('confidence', 'MEDIUM')
            
            # Get weight for this model
            weight = self.model_weights.get(model, 1.0)
            
            # Adjust for confidence
            if confidence == 'HIGH':
                weight *= 1.2
            elif confidence == 'LOW':
                weight *= 0.8
            
            total_score += score * weight
            total_weight += weight
            
            model_details.append({
                'model': model,
                'score': score,
                'confidence': confidence,
                'weight': weight
            })
        
        if total_weight == 0:
            return None, "No valid LLM scores"
        
        weighted_score = total_score / total_weight
        
        # Determine action
        action = 'HOLD'
        reason = f"LLM consensus: {weighted_score:.1f}/10"
        
        if weighted_score >= self.buy_threshold:
            action = 'BUY'
            reason = f"Strong LLM buy signal: {weighted_score:.1f}/10"
        elif weighted_score <= self.sell_threshold:
            action = 'SELL'
            reason = f"Strong LLM sell signal: {weighted_score:.1f}/10"
        
        # Get top models
        top_models = sorted(model_details, key=lambda x: x['score'], reverse=True)[:2]
        top_models_text = ", ".join([f"{m['model']}: {m['score']:.1f}" for m in top_models])
        reason += f" | Top: {top_models_text}"
        
        return {
            'symbol': symbol,
            'weighted_score': weighted_score,
            'action': action,
            'reason': reason,
            'model_details': model_details,
            'timestamp': datetime.now().isoformat()
        }, "Success"
    
    def generate_trading_signal(self):
        """Generate trading signal based on LLM consensus and portfolio state"""
        current_time = time.time()
        
        # Check trade interval
        if current_time - self.last_trade_time < self.min_trade_interval:
            return None
        
        # First, check if we need to close any positions (stop-loss/profit target)
        position_actions = self.portfolio.check_position_health()
        if position_actions:
            # Return the most urgent action
            urgent_actions = [a for a in position_actions if a['urgency'] == 'critical']
            if urgent_actions:
                return urgent_actions[0]
            return position_actions[0]
        
        # Check if we have max positions
        portfolio_summary = self.portfolio.get_portfolio_summary()
        if portfolio_summary['positions'] >= self.max_positions:
            return None
        
        # Get spread analysis for opportunities
        spread_analysis = self.get_spread_analysis()
        if not spread_analysis:
            return None
        
        # Evaluate each symbol
        best_opportunity = None
        best_score = -100
        
        for spread in spread_analysis:
            symbol = spread.get('pair')
            spread_pct = spread.get('spread_percent', 0)
            
            # Skip if we already have this position
            if symbol in self.portfolio.holdings:
                continue
            
            # Get LLM consensus
            consensus, error = self.calculate_llm_consensus(symbol)
            if not consensus:
                continue
            
            score = consensus['weighted_score']
            action = consensus['action']
            
            # Adjust score based on spread
            if abs(spread_pct) > 1.0:
                score += 0.5  # Bonus for good spread
            
            # Only consider BUY signals for new positions
            if action == 'BUY' and score > best_score:
                best_score = score
                best_opportunity = {
                    'symbol': symbol,
                    'side': 'buy',
                    'score': score,
                    'reason': consensus['reason'],
                    'spread': spread_pct,
                    'confidence': min(score / 10.0, 0.9),
                    'signal_type': 'llm_consensus'
                }
        
        # Check if best opportunity meets threshold
        if best_opportunity and best_opportunity['score'] >= self.buy_threshold:
            # Calculate position size based on confidence
            confidence = best_opportunity['confidence']
            portfolio_value = portfolio_summary['portfolio_value']
            
            position_size_pct = (
                self.min_position_size + 
                (self.max_position_size - self.min_position_size) * confidence
            )
            
            position_value = portfolio_value * position_size_pct
            
            # Get current price
            market_prices = self.portfolio.get_market_prices()
            price = market_prices.get(best_opportunity['symbol'], 0)
            
            if price > 0 and position_value > 10:  # Minimum $10
                amount = position_value / price
                best_opportunity['amount'] = amount
                return best_opportunity
        
        return None
    
    def execute_signal(self, signal):
        """Execute a trading signal"""
        symbol = signal['symbol']
        side = signal['side']
        amount = signal.get('amount', 0)
        reason = signal['reason']
        
        # Get current price
        market_prices = self.portfolio.get_market_prices()
        price = market_prices.get(symbol, 0)
        
        if price <= 0:
            return False, f"Invalid price for {symbol}"
        
        # Execute trade
        if side == 'buy':
            success, result = self.portfolio.execute_buy(symbol, amount, price, reason)
        else:  # sell
            success, result = self.portfolio.execute_sell(symbol, amount, price, reason)
        
        if success:
            self.last_trade_time = time.time()
            self.trade_count += 1
            
            # Log LLM decision
            self.llm_decision_log.append({
                'timestamp': datetime.now().isoformat(),
                'signal': signal,
                'result': result,
                'trade_count': self.trade_count
            })
        
        return success, result
    
    def run(self):
        """Run the fixed trading system"""
        print("\n🚀 Starting Fixed LLM Consensus Trading System...")
        print(f"⏰ Checking signals every {self.min_trade_interval//60} minutes")
        print("="*80)
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                
                print(f"\n🔄 Cycle {cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Generate trading signal
                signal = self.generate_trading_signal()
                
                if signal:
                    print(f"📡 Signal generated: {signal['side'].upper()} {signal.get('symbol', 'Unknown')}")
                    print(f"   Reason: {signal.get('reason', 'No reason')}")
                    
                    if 'score' in signal:
                        print(f"   LLM Score: {signal['score']:.1f}/10")
                    
                    # Execute signal
                    success, result = self.execute_signal(signal)
                    
                    if success:
                        print(f"✅ {result}")
                    else:
                        print(f"⚠️ {result}")
                    
                    # Show portfolio status after trade
                    self.portfolio.print_status()
                else:
                    # Show what we're analyzing
                    portfolio_summary = self.portfolio.get_portfolio_summary()
                    
                    print(f"📊 Portfolio Value: ${portfolio_summary['portfolio_value']:,.2f}")
                    print(f"💰 Cash: ${portfolio_summary['cash_balance']:,.2f}")
                    print(f"📈 Positions: {portfolio_summary['positions']}/{self.max_positions}")
                    
                    if portfolio_summary['total_trades'] > 0:
                        print(f"🎯 Win Rate: {portfolio_summary['win_rate']}")
                        print(f"💰 Total Profit: ${portfolio_summary['total_profit']:+,.2f}")
                    
                    # Show LLM scores if available
                    if cycle_count % 3 == 0:  # Every 3 cycles
                        llm_scores = self.get_llm_scores()
                        if llm_scores:
                            top_score = max(llm_scores, key=lambda x: x.get('score', 0))
                            print(f"🤖 Top LLM: {top_score.get('model')} - {top_score.get('score')}/10")
                
                # Wait for next cycle
                print(f"\n⏳ Next check in {self.min_trade_interval//60} minutes...")
                time.sleep(self.min_trade_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Trading System Stopped")
            print("="*80)
            self.portfolio.print_status()
            
            # Save final status
            self.portfolio._save_portfolio_status()
            
            print(f"\n📊 Total trading cycles: {cycle_count}")
            print(f"📈 Total trades executed: {self.trade_count}")
            print("="*80)

def main():
    """Main function"""
    print("🤖 FIXED LLM CONSENSUS TRADING SYSTEM")
    print("="*80)
    
    # Start with current cash balance
    initial_cash = 1590.96
    
    print(f"Starting with cash balance: ${initial_cash:,.2f}")
    print("This system will:")
    print("  1. Track portfolio value (cash + holdings)")
    print("  2. Use LLM consensus for trading decisions")
    print("  3. Implement proper risk management")
    print("  4. Log all trades for analysis")
    print("="*80)
    
    # Create and run trading system
    trading_system = FixedLLMConsensusTrading(initial_cash=initial_cash)
    trading_system.run()

if __name__ == "__main__":
    main()