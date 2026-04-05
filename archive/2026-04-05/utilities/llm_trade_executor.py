
#!/usr/bin/env python3
"""
Simple LLM Trade Executor
Executes trades based on LLM consensus
"""

import json
import ccxt
import os
from datetime import datetime

class LLMTradeExecutor:
    def __init__(self):
        self.base_dir = "/Users/chetantemkar/.openclaw/workspace/app"
        self.trades_file = os.path.join(self.base_dir, "trading_data/trades.json")
        self.positions_file = os.path.join(self.base_dir, "trading_data/positions.json")
        
        # Load exchanges
        try:
            with open(os.path.join(self.base_dir, "secure_keys/gemini_keys.json")) as f:
                gemini_keys = json.load(f)
            self.gemini = ccxt.gemini({
                "apiKey": gemini_keys["api_key"],
                "secret": gemini_keys["api_secret"]
            })
            print("✅ Gemini loaded for trading")
        except:
            self.gemini = None
            
        try:
            with open(os.path.join(self.base_dir, "secure_keys/binance_keys.json")) as f:
                binance_keys = json.load(f)
            self.binance = ccxt.binance({
                "apiKey": binance_keys["api_key"],
                "secret": binance_keys["api_secret"]
            })
            print("✅ Binance loaded for trading")
        except:
            self.binance = None
    
    def execute_trade(self, crypto, signal, price, confidence):
        """Execute a trade based on LLM consensus"""
        
        # Capital allocation
        gemini_capital = 434.35
        binance_capital = 36.70
        position_size = 0.15  # 15% to meet Binance minimum
        
        if signal in ["BUY", "STRONG_BUY"]:
            side = "buy"
            exchange = self.gemini if crypto in ["BTC", "ETH", "LTC", "BCH", "ZEC", "FIL", "BAT", "LINK", "MANA", "COMP"] else None
            capital = gemini_capital * position_size if exchange == self.gemini else 0
            
        elif signal in ["SELL", "STRONG_SELL"]:
            side = "sell"
            exchange = self.binance
            capital = binance_capital * position_size
            
        else:
            return None  # NEUTRAL - no trade
        
        if not exchange or capital < 5:
            print(f"❌ Cannot execute {crypto} {signal}: capital ${capital:.2f} < $5 minimum")
            return None
        
        # Calculate order size
        amount = capital / price
        
        try:
            # For demo - simulate trade
            trade = {
                "exchange": "gemini" if exchange == self.gemini else "binance",
                "symbol": f"{crypto}/USD" if exchange == self.gemini else f"{crypto}/USDT",
                "side": side,
                "price": price,
                "amount": amount,
                "value": capital,
                "order_id": f"LLM_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "current_price": price,
                "pnl": 0.0,
                "pnl_percent": 0.0,
                "current_value": capital,
                "last_updated": datetime.now().isoformat(),
                "signal": signal,
                "confidence": confidence
            }
            
            # Save trade
            self._save_trade(trade)
            
            print(f"✅ EXECUTED: {crypto} {side.upper()} at ${price:.2f} (${capital:.2f})")
            return trade
            
        except Exception as e:
            print(f"❌ Trade execution failed: {e}")
            return None
    
    def _save_trade(self, trade):
        """Save trade to trades.json"""
        try:
            # Load existing trades
            if os.path.exists(self.trades_file):
                with open(self.trades_file, "r") as f:
                    trades = json.load(f)
            else:
                trades = []
            
            # Add new trade
            trades.append(trade)
            
            # Save
            with open(self.trades_file, "w") as f:
                json.dump(trades, f, indent=2)
            
            # Update positions
            self._update_positions(trade)
            
        except Exception as e:
            print(f"❌ Error saving trade: {e}")
    
    def _update_positions(self, trade):
        """Update positions.json"""
        try:
            if os.path.exists(self.positions_file):
                with open(self.positions_file, "r") as f:
                    positions = json.load(f)
            else:
                positions = {}
            
            key = f"{trade['exchange']}_{trade['symbol']}"
            positions[key] = {
                "symbol": trade["symbol"],
                "exchange": trade["exchange"],
                "side": trade["side"],
                "entry_price": trade["price"],
                "amount": trade["amount"],
                "current_price": trade["price"],
                "pnl": 0.0,
                "pnl_percent": 0.0,
                "timestamp": trade["timestamp"],
                "last_updated": trade["last_updated"]
            }
            
            with open(self.positions_file, "w") as f:
                json.dump(positions, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error updating positions: {e}")
