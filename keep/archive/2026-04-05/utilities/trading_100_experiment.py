#!/usr/bin/env python3
"""
$100 Trading Experiment Bot
AI-powered trading with $100 capital
"""

import json
import time
import random
from datetime import datetime, timedelta
import os

class TradingExperiment:
    def __init__(self, capital=100.0):
        self.capital = capital
        self.balance = capital
        self.positions = []
        self.trade_history = []
        self.start_time = datetime.now()
        
        # Trading parameters
        self.trade_size = 20.0  # $20 per trade
        self.max_positions = 2  # Max 2 open positions
        self.stop_loss = 0.015  # 1.5%
        self.take_profit = 0.03  # 3%
        
        # Assets to trade
        self.assets = [
            {"symbol": "BTC/USD", "price": 71234.50, "volatility": 0.02},
            {"symbol": "ETH/USD", "price": 2210.73, "volatility": 0.025},
            {"symbol": "SOL/USD", "price": 90.54, "volatility": 0.035}
        ]
        
        # Create data directory
        os.makedirs('experiment_data', exist_ok=True)
        
    def analyze_market(self):
        """AI market analysis (simulated)"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "signals": [],
            "recommendations": []
        }
        
        for asset in self.assets:
            # Simulate AI analysis
            signal_score = random.uniform(-1, 1)
            
            if signal_score > 0.3:
                signal = "STRONG_BUY"
            elif signal_score > 0.1:
                signal = "BUY"
            elif signal_score < -0.3:
                signal = "STRONG_SELL"
            elif signal_score < -0.1:
                signal = "SELL"
            else:
                signal = "HOLD"
            
            analysis["signals"].append({
                "symbol": asset["symbol"],
                "signal": signal,
                "score": round(signal_score, 3),
                "price": asset["price"]
            })
            
            # Generate price movement
            movement = random.uniform(-asset["volatility"], asset["volatility"])
            asset["price"] *= (1 + movement)
            asset["price"] = round(asset["price"], 2)
        
        return analysis
    
    def check_trade_opportunities(self, analysis):
        """Check if we should enter new trades"""
        opportunities = []
        
        for signal in analysis["signals"]:
            if signal["signal"] in ["STRONG_BUY", "BUY"]:
                # Check if we have capacity
                if len(self.positions) < self.max_positions and self.balance >= self.trade_size:
                    opportunities.append({
                        "symbol": signal["symbol"],
                        "price": signal["price"],
                        "signal": signal["signal"],
                        "size_usd": self.trade_size
                    })
        
        return opportunities
    
    def execute_trade(self, opportunity):
        """Execute a trade"""
        trade_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Calculate position size
        symbol = opportunity["symbol"]
        entry_price = opportunity["price"]
        size_usd = opportunity["size_usd"]
        
        # For simulation, we'll use units
        if "BTC" in symbol:
            units = size_usd / entry_price
        elif "ETH" in symbol:
            units = size_usd / entry_price
        else:  # SOL
            units = size_usd / entry_price
        
        position = {
            "id": trade_id,
            "symbol": symbol,
            "entry_price": entry_price,
            "units": round(units, 6),
            "size_usd": size_usd,
            "entry_time": datetime.now().isoformat(),
            "stop_loss": entry_price * (1 - self.stop_loss),
            "take_profit": entry_price * (1 + self.take_profit),
            "status": "open"
        }
        
        # Update balance
        self.balance -= size_usd
        self.positions.append(position)
        
        # Log trade
        trade_log = {
            **position,
            "type": "BUY",
            "reason": opportunity["signal"]
        }
        self.trade_history.append(trade_log)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📈 OPEN: {symbol} @ ${entry_price:,.2f} (${size_usd})")
        
        return position
    
    def monitor_positions(self):
        """Monitor open positions for exit signals"""
        closed_positions = []
        
        for position in self.positions[:]:  # Copy for iteration
            symbol = position["symbol"]
            current_price = next((a["price"] for a in self.assets if a["symbol"] == symbol), position["entry_price"])
            
            # Check stop loss
            if current_price <= position["stop_loss"]:
                pnl = (current_price - position["entry_price"]) * position["units"]
                pnl_pct = (current_price / position["entry_price"] - 1) * 100
                
                # Close position
                self.close_position(position, current_price, "STOP_LOSS", pnl, pnl_pct)
                closed_positions.append(position)
            
            # Check take profit
            elif current_price >= position["take_profit"]:
                pnl = (current_price - position["entry_price"]) * position["units"]
                pnl_pct = (current_price / position["entry_price"] - 1) * 100
                
                # Close position
                self.close_position(position, current_price, "TAKE_PROFIT", pnl, pnl_pct)
                closed_positions.append(position)
        
        return closed_positions
    
    def close_position(self, position, exit_price, reason, pnl, pnl_pct):
        """Close a position"""
        position["exit_price"] = exit_price
        position["exit_time"] = datetime.now().isoformat()
        position["status"] = "closed"
        position["pnl"] = round(pnl, 2)
        position["pnl_pct"] = round(pnl_pct, 2)
        position["exit_reason"] = reason
        
        # Update balance
        self.balance += position["size_usd"] + pnl
        
        # Remove from open positions
        self.positions.remove(position)
        
        # Log closure
        closure_log = {
            "id": position["id"],
            "symbol": position["symbol"],
            "entry_price": position["entry_price"],
            "exit_price": exit_price,
            "pnl": position["pnl"],
            "pnl_pct": position["pnl_pct"],
            "reason": reason,
            "duration": str(datetime.now() - datetime.fromisoformat(position["entry_time"]))
        }
        self.trade_history.append(closure_log)
        
        emoji = "🔴" if pnl < 0 else "🟢"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {emoji} CLOSE: {position['symbol']} | P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%) | Reason: {reason}")
    
    def generate_report(self):
        """Generate trading report"""
        total_trades = len([t for t in self.trade_history if "exit_price" in t])
        winning_trades = len([t for t in self.trade_history if "pnl" in t and t["pnl"] > 0])
        losing_trades = len([t for t in self.trade_history if "pnl" in t and t["pnl"] < 0])
        
        total_pnl = sum(t.get("pnl", 0) for t in self.trade_history)
        total_pnl_pct = (total_pnl / self.capital) * 100
        
        open_positions_value = sum(p["size_usd"] for p in self.positions)
        total_value = self.balance + open_positions_value
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "experiment_duration": str(datetime.now() - self.start_time),
            "initial_capital": self.capital,
            "current_balance": round(self.balance, 2),
            "open_positions_value": round(open_positions_value, 2),
            "total_value": round(total_value, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round(total_pnl_pct, 2),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round(winning_trades / total_trades * 100, 2) if total_trades > 0 else 0,
            "open_positions": len(self.positions),
            "positions": self.positions,
            "recent_trades": self.trade_history[-5:] if self.trade_history else []
        }
        
        return report
    
    def save_data(self):
        """Save trading data to files"""
        # Save current state
        state = {
            "balance": self.balance,
            "positions": self.positions,
            "trade_history": self.trade_history[-50:],  # Last 50 trades
            "last_update": datetime.now().isoformat()
        }
        
        with open('experiment_data/current_state.json', 'w') as f:
            json.dump(state, f, indent=2)
        
        # Save report
        report = self.generate_report()
        with open('experiment_data/latest_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Append to log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "balance": self.balance,
            "open_positions": len(self.positions),
            "total_pnl": report["total_pnl"]
        }
        
        log_file = 'experiment_data/trading_log.json'
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = []
        
        log_data.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(log_data[-100:], f, indent=2)  # Keep last 100 entries
    
    def run(self):
        """Main trading loop"""
        print(f"\n🚀 Starting $100 Trading Experiment")
        print(f"💰 Initial Capital: ${self.capital}")
        print(f"📈 Trade Size: ${self.trade_size}")
        print(f"⏱️  Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        cycle = 0
        while True:
            cycle += 1
            print(f"\n📊 Cycle {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            # 1. Analyze market
            analysis = self.analyze_market()
            
            # 2. Monitor existing positions
            closed = self.monitor_positions()
            
            # 3. Check for new opportunities (if we have capacity)
            if len(self.positions) < self.max_positions and self.balance >= self.trade_size:
                opportunities = self.check_trade_opportunities(analysis)
                for opp in opportunities[:2]:  # Max 2 new trades per cycle
                    self.execute_trade(opp)
            
            # 4. Generate and display report
            report = self.generate_report()
            print(f"   Balance: ${report['current_balance']:.2f} | Open Positions: {report['open_positions']}")
            print(f"   Total P&L: ${report['total_pnl']:+.2f} ({report['total_pnl_pct']:+.2f}%)")
            print(f"   Trades: {report['total_trades']} (Win Rate: {report['win_rate']}%)")
            
            # 5. Save data
            self.save_data()
            
            # 6. Wait for next cycle (5 minutes in simulation, would be longer in real trading)
            time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    # Start trading experiment
    experiment = TradingExperiment(capital=100.0)
    
    try:
        experiment.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Trading experiment stopped by user")
        final_report = experiment.generate_report()
        print(f"\n📋 Final Report:")
        print(f"   Initial Capital: ${final_report['initial_capital']}")
        print(f"   Final Value: ${final_report['total_value']:.2f}")
        print(f"   Total P&L: ${final_report['total_pnl']:+.2f} ({final_report['total_pnl_pct']:+.2f}%)")
        print(f"   Total Trades: {final_report['total_trades']}")
        print(f"   Win Rate: {final_report['win_rate']}%")
        print(f"\n📊 Data saved to experiment_data/")
        experiment.save_data()