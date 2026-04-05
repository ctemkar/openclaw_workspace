#!/usr/bin/env python3
"""
COMMON DATA LAYER for trading system
Single source of truth for all trading data
"""

import json
import os
import ccxt
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths - SINGLE SOURCE OF TRUTH
TRADES_FILE = os.path.join(BASE_DIR, "trading_data", "trades.json")
CAPITAL_FILE = os.path.join(BASE_DIR, "trading_data", "capital.json")
BOT_STATUS_FILE = os.path.join(BASE_DIR, "trading_data", "bot_status.json")

# Ensure directory exists
os.makedirs(os.path.join(BASE_DIR, "trading_data"), exist_ok=True)

class TradingData:
    """Common data layer for all trading components"""
    
    @staticmethod
    def get_current_price(symbol: str, exchange_name: str = 'binance') -> Optional[float]:
        """Get current price from exchange"""
        try:
            if exchange_name == 'binance':
                exchange = ccxt.binance({
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                })
                # Binance uses USDT, not USD
                symbol = symbol.replace('/USD', '/USDT').replace('USD', 'USDT')
            elif exchange_name == 'gemini':
                exchange = ccxt.gemini({
                    'enableRateLimit': True
                })
                # Gemini uses USD
                symbol = symbol.replace('/USDT', '/USD').replace('USDT', 'USD')
            else:
                return None
            
            ticker = exchange.fetch_ticker(symbol)
            return ticker.get('last')
            
        except Exception as e:
            # Try alternative symbol format
            try:
                if exchange_name == 'binance' and '/USD' in symbol:
                    alt_symbol = symbol.replace('/USD', '/USDT')
                    ticker = exchange.fetch_ticker(alt_symbol)
                    return ticker.get('last')
            except:
                pass
            
            print(f"❌ Error fetching price for {symbol} on {exchange_name}: {e}")
            return None
    
    @staticmethod
    def calculate_position_pnl(position: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate P&L for a position"""
        try:
            entry_price = position.get('price', 0)
            amount = position.get('amount', 0)
            side = position.get('side', 'buy')
            symbol = position.get('symbol', '')
            exchange = position.get('exchange', 'binance')
            
            if not entry_price or not amount or not symbol:
                return {'pnl': 0, 'pnl_percent': 0, 'current_price': entry_price}
            
            # Get current price
            current_price = TradingData.get_current_price(symbol, exchange)
            if not current_price:
                current_price = entry_price  # Fallback
            
            # Calculate P&L based on side
            if side == 'buy':  # LONG position
                pnl = (current_price - entry_price) * amount
                pnl_percent = ((current_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
            else:  # SHORT position
                pnl = (entry_price - current_price) * amount
                pnl_percent = ((entry_price - current_price) / entry_price) * 100 if entry_price > 0 else 0
            
            return {
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'current_price': current_price,
                'entry_price': entry_price,
                'value': amount * current_price
            }
            
        except Exception as e:
            print(f"❌ Error calculating P&L: {e}")
            return {'pnl': 0, 'pnl_percent': 0, 'current_price': position.get('price', 0)}
    
    @staticmethod
    def save_trade(trade_data: Dict[str, Any]) -> bool:
        """Save a trade - used by ALL bots"""
        try:
            # Load existing trades
            trades = TradingData.get_trades()
            
            # Add new trade
            trade_data['id'] = f"trade_{len(trades) + 1:06d}"
            trade_data['saved_at'] = datetime.now().isoformat()
            trades.append(trade_data)
            
            # Keep only last 1000 trades
            if len(trades) > 1000:
                trades = trades[-1000:]
            
            # Save to file
            with open(TRADES_FILE, 'w') as f:
                json.dump(trades, f, indent=2)
            
            # Update capital automatically
            TradingData.update_capital()
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving trade: {e}")
            return False
    
    @staticmethod
    def get_trades(limit: int = 100) -> List[Dict[str, Any]]:
        """Get trades - used by ALL dashboards/reports"""
        try:
            if os.path.exists(TRADES_FILE):
                with open(TRADES_FILE, 'r') as f:
                    trades = json.load(f)
                return trades[-limit:]  # Return most recent
            return []
        except:
            return []
    
    @staticmethod
    def get_open_positions() -> List[Dict[str, Any]]:
        """Get currently open positions"""
        trades = TradingData.get_trades()
        # For now, assume all trades are open (we'll add closing logic later)
        return [t for t in trades if t.get('status', 'open') == 'open']
    
    @staticmethod
    def update_capital() -> bool:
        """Update capital based on trades"""
        try:
            trades = TradingData.get_trades()
            open_positions = TradingData.get_open_positions()
            
            # Configuration - SINGLE SOURCE OF TRUTH
            gemini_total = 531.65
            binance_total = 154.02
            
            # Calculate deployed capital
            deployed = sum(t.get('value', 0) for t in open_positions)
            available_gemini = gemini_total - deployed
            
            capital_data = {
                'gemini_total': gemini_total,
                'binance_total': binance_total,
                'total_capital': gemini_total + binance_total,
                'deployed': deployed,
                'available_gemini': available_gemini,
                'available_binance': binance_total,  # Not used for now
                'position_count': len(open_positions),
                'avg_position_value': deployed / len(open_positions) if open_positions else 0,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(CAPITAL_FILE, 'w') as f:
                json.dump(capital_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating capital: {e}")
            return False
    
    @staticmethod
    def get_capital() -> Dict[str, Any]:
        """Get capital data"""
        try:
            if os.path.exists(CAPITAL_FILE):
                with open(CAPITAL_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        # Default if file doesn't exist
        return {
            'gemini_total': 531.65,
            'binance_total': 154.02,
            'total_capital': 685.67,
            'deployed': 0,
            'available_gemini': 531.65,
            'available_binance': 154.02,
            'position_count': 0,
            'avg_position_value': 0,
            'last_updated': datetime.now().isoformat()
        }
    
    @staticmethod
    def update_bot_status(status_data: Dict[str, Any]) -> bool:
        """Update bot status"""
        try:
            status_data['last_updated'] = datetime.now().isoformat()
            with open(BOT_STATUS_FILE, 'w') as f:
                json.dump(status_data, f, indent=2)
            return True
        except:
            return False
    
    @staticmethod
    def get_bot_status() -> Dict[str, Any]:
        """Get bot status"""
        try:
            if os.path.exists(BOT_STATUS_FILE):
                with open(BOT_STATUS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        # Default status
        return {
            'status': 'unknown',
            'strategy': 'Gemini LONG at 0.5% dips',
            'scan_interval': 60,
            'last_activity': 'No activity recorded',
            'last_updated': datetime.now().isoformat()
        }
    
    @staticmethod
    def get_dashboard_data() -> Dict[str, Any]:
        """Get all data needed for dashboard - SINGLE FUNCTION for ALL dashboards"""
        return {
            'timestamp': datetime.now().isoformat(),
            'positions': TradingData.get_open_positions(),
            'capital': TradingData.get_capital(),
            'bot_status': TradingData.get_bot_status(),
            'recent_trades': TradingData.get_trades(limit=10),
            'metadata': {
                'data_source': 'trading_data common layer',
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'version': '1.0'
            }
        }


# Test the data layer
if __name__ == "__main__":
    print("🧪 Testing Common Data Layer")
    print("=" * 60)
    
    # Test saving a trade
    test_trade = {
        'exchange': 'gemini',
        'symbol': 'TEST/USD',
        'side': 'buy',
        'price': 100.0,
        'amount': 1.0,
        'value': 100.0,
        'order_id': 'test_123',
        'timestamp': datetime.now().isoformat(),
        'notes': 'Test trade from common data layer'
    }
    
    if TradingData.save_trade(test_trade):
        print("✅ Trade saved successfully")
    
    # Get data
    trades = TradingData.get_trades()
    capital = TradingData.get_capital()
    
    print(f"📊 Trades in system: {len(trades)}")
    print(f"💰 Capital deployed: ${capital.get('deployed', 0):.2f}")
    print(f"📈 Open positions: {capital.get('position_count', 0)}")
    
    print("\n✅ Common data layer is working!")
    print(f"   Files created in: {os.path.join(BASE_DIR, 'trading_data')}")