#!/usr/bin/env python3
"""
Position Monitor - Tracks open positions and calculates real-time P&L
"""

import json
import os
import time
import ccxt
from datetime import datetime
import logging

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "position_monitor.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_open_positions():
    """Load all open positions from trade files"""
    open_positions = []
    
    # Check Binance futures trades
    binance_trades_file = os.path.join(BASE_DIR, "executed_futures_trades.json")
    if os.path.exists(binance_trades_file):
        with open(binance_trades_file, 'r') as f:
            trades = json.load(f)
        
        for trade in trades:
            if trade.get('status') in ['EXECUTED', 'OPEN']:
                open_positions.append({
                    'exchange': 'binance_futures',
                    'symbol': trade['symbol'],
                    'side': trade['side'],
                    'type': trade.get('type', 'SHORT'),
                    'entry_price': trade['entry_price'],
                    'amount': trade['amount'],
                    'position_value': trade.get('position_value', 0),
                    'leverage': trade.get('leverage', 1),
                    'stop_loss': trade.get('stop_loss', 0),
                    'take_profit': trade.get('take_profit', 0),
                    'timestamp': trade['timestamp'],
                    'trade_data': trade
                })
    
    # Check Gemini trades
    gemini_trades_file = os.path.join(BASE_DIR, "real_trades_history.json")
    if os.path.exists(gemini_trades_file):
        with open(gemini_trades_file, 'r') as f:
            trades = json.load(f)
        
        for trade in trades:
            if trade.get('status') in ['open', 'executed']:
                open_positions.append({
                    'exchange': 'gemini',
                    'symbol': trade['symbol'],
                    'side': trade['side'],
                    'type': 'SPOT',
                    'entry_price': trade['price'],
                    'amount': trade['quantity'],
                    'position_value': trade.get('value', 0),
                    'leverage': 1,
                    'timestamp': trade['timestamp'],
                    'trade_data': trade
                })
    
    return open_positions

def calculate_position_pnl(position, current_price):
    """Calculate P&L for a position"""
    entry = position['entry_price']
    amount = position['amount']
    side = position['side']
    leverage = position.get('leverage', 1)
    
    if side == 'buy' or side == 'BUY':
        # LONG position: profit when price goes up
        pnl = (current_price - entry) * amount
        pnl_percent = ((current_price - entry) / entry) * 100
    else:
        # SHORT position: profit when price goes down
        pnl = (entry - current_price) * amount
        pnl_percent = ((entry - current_price) / entry) * 100
    
    # Apply leverage for futures
    if position['exchange'] == 'binance_futures':
        pnl *= leverage
        pnl_percent *= leverage
    
    return {
        'pnl': pnl,
        'pnl_percent': pnl_percent,
        'current_price': current_price,
        'value_change': abs(current_price - entry) * amount
    }

def check_position_closure(position, pnl_data):
    """Check if position should be closed based on stop-loss/take-profit"""
    current_price = pnl_data['current_price']
    pnl_percent = pnl_data['pnl_percent']
    
    should_close = False
    close_reason = ""
    
    # Check stop-loss
    stop_loss = position.get('stop_loss', 0)
    if stop_loss > 0:
        if position['side'] in ['buy', 'BUY']:
            # LONG: stop-loss if price drops below stop_loss
            if current_price <= stop_loss:
                should_close = True
                close_reason = f"Stop-loss hit: ${current_price:.4f} <= ${stop_loss:.4f}"
        else:
            # SHORT: stop-loss if price rises above stop_loss
            if current_price >= stop_loss:
                should_close = True
                close_reason = f"Stop-loss hit: ${current_price:.4f} >= ${stop_loss:.4f}"
    
    # Check take-profit
    take_profit = position.get('take_profit', 0)
    if take_profit > 0:
        if position['side'] in ['buy', 'BUY']:
            # LONG: take-profit if price rises above take_profit
            if current_price >= take_profit:
                should_close = True
                close_reason = f"Take-profit hit: ${current_price:.4f} >= ${take_profit:.4f}"
        else:
            # SHORT: take-profit if price drops below take_profit
            if current_price <= take_profit:
                should_close = True
                close_reason = f"Take-profit hit: ${current_price:.4f} <= ${take_profit:.4f}"
    
    return should_close, close_reason

def update_trade_status(trade_data, status, exit_price=0, pnl=0):
    """Update trade status in the trade file"""
    exchange = trade_data.get('exchange', '')
    
    if exchange == 'binance_futures':
        trades_file = os.path.join(BASE_DIR, "executed_futures_trades.json")
    elif exchange == 'gemini':
        trades_file = os.path.join(BASE_DIR, "real_trades_history.json")
    else:
        return False
    
    try:
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                trades = json.load(f)
            
            # Find and update the trade
            for i, trade in enumerate(trades):
                if trade.get('timestamp') == trade_data.get('timestamp'):
                    trades[i]['status'] = status
                    if exit_price > 0:
                        trades[i]['exit_price'] = exit_price
                    if pnl != 0:
                        trades[i]['pnl'] = pnl
                        trades[i]['pnl_percent'] = (pnl / trade_data.get('position_value', 1)) * 100
                    trades[i]['closed_at'] = datetime.now().isoformat()
                    
                    # Save updated trades
                    with open(trades_file, 'w') as f:
                        json.dump(trades, f, indent=2)
                    
                    logger.info(f"✅ Updated {exchange} trade status to {status}")
                    return True
        
        return False
    except Exception as e:
        logger.error(f"Error updating trade status: {e}")
        return False

def monitor_positions():
    """Main monitoring loop"""
    logger.info("🚀 Starting Position Monitor")
    logger.info("=" * 60)
    
    # Initialize exchange connections
    binance = ccxt.binance()
    
    while True:
        try:
            open_positions = load_open_positions()
            
            if not open_positions:
                logger.info("No open positions to monitor")
                time.sleep(60)  # Check every minute
                continue
            
            logger.info(f"📊 Monitoring {len(open_positions)} open positions")
            
            total_unrealized_pnl = 0
            positions_to_close = []
            
            for position in open_positions:
                symbol = position['symbol']
                
                try:
                    # Get current price
                    ticker = binance.fetch_ticker(symbol)
                    current_price = ticker['last']
                    
                    # Calculate P&L
                    pnl_data = calculate_position_pnl(position, current_price)
                    
                    # Check if position should be closed
                    should_close, close_reason = check_position_closure(position, pnl_data)
                    
                    # Log position status
                    status_symbol = "📈" if pnl_data['pnl'] > 0 else "📉" if pnl_data['pnl'] < 0 else "➖"
                    logger.info(f"{status_symbol} {symbol} ({position['side']}): "
                               f"Entry: ${position['entry_price']:.4f}, "
                               f"Current: ${current_price:.4f}, "
                               f"P&L: ${pnl_data['pnl']:.2f} ({pnl_data['pnl_percent']:.1f}%)")
                    
                    if should_close:
                        logger.warning(f"⚠️  Should close {symbol}: {close_reason}")
                        positions_to_close.append({
                            'position': position,
                            'current_price': current_price,
                            'pnl': pnl_data['pnl'],
                            'reason': close_reason
                        })
                    
                    total_unrealized_pnl += pnl_data['pnl']
                    
                except Exception as e:
                    logger.error(f"Error monitoring {symbol}: {e}")
            
            # Log total P&L
            if total_unrealized_pnl > 0:
                logger.info(f"💰 Total Unrealized P&L: +${total_unrealized_pnl:.2f}")
            elif total_unrealized_pnl < 0:
                logger.info(f"💰 Total Unrealized P&L: -${abs(total_unrealized_pnl):.2f}")
            else:
                logger.info(f"💰 Total Unrealized P&L: ${total_unrealized_pnl:.2f}")
            
            # Close positions that hit stop-loss/take-profit
            for close_info in positions_to_close:
                position = close_info['position']
                logger.critical(f"🔒 Closing {position['symbol']}: {close_info['reason']}")
                
                # Update trade status (in real trading, would execute close order)
                success = update_trade_status(
                    position['trade_data'],
                    'CLOSED',
                    close_info['current_price'],
                    close_info['pnl']
                )
                
                if success:
                    logger.critical(f"✅ Position closed: P&L = ${close_info['pnl']:.2f}")
                else:
                    logger.error(f"❌ Failed to update trade status")
            
            logger.info(f"⏳ Next check in 30 seconds...")
            logger.info("=" * 60)
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Position monitor stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    monitor_positions()