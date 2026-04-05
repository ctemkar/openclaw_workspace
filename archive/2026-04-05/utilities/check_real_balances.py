#!/usr/bin/env python3
"""
Check REAL Gemini and Binance balances via API
"""

import os
import json
from datetime import datetime

def check_gemini_balance():
    """Check actual Gemini balance via API"""
    print("🔵 CHECKING GEMINI ACTUAL BALANCE")
    print("="*50)
    
    try:
        # Try to import Gemini API
        import ccxt
        gemini = ccxt.gemini({
            'apiKey': os.environ.get('GEMINI_API_KEY', ''),
            'secret': os.environ.get('GEMINI_API_SECRET', ''),
            'enableRateLimit': True,
        })
        
        # Fetch balance
        balance = gemini.fetch_balance()
        print(f"💰 Total Balance: ${balance.get('total', {}).get('USD', 0):.2f}")
        print(f"💵 Free USD: ${balance.get('free', {}).get('USD', 0):.2f}")
        print(f"📊 Used USD: ${balance.get('used', {}).get('USD', 0):.2f}")
        
        # Show crypto holdings
        print("\n📈 Crypto Holdings:")
        for currency, amount in balance.get('total', {}).items():
            if currency != 'USD' and amount > 0:
                print(f"  {currency}: {amount:.8f}")
        
        return balance
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        print("⚠️  Using fallback data from logs")
        
        # Try to get data from trading bot logs
        try:
            with open('real_26_crypto_trading.log', 'r') as f:
                lines = f.readlines()[-100:]  # Last 100 lines
                for line in lines:
                    if 'Gemini cash balance' in line or 'GEMINI_CAPITAL' in line:
                        print(f"📝 From log: {line.strip()}")
        except:
            pass
        
        return None

def check_binance_balance():
    """Check actual Binance balance via API"""
    print("\n🟡 CHECKING BINANCE ACTUAL BALANCE")
    print("="*50)
    
    try:
        # Try to import Binance API
        import ccxt
        binance = ccxt.binance({
            'apiKey': os.environ.get('BINANCE_API_KEY', ''),
            'secret': os.environ.get('BINANCE_API_SECRET', ''),
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # For futures trading
            }
        })
        
        # Fetch balance
        balance = binance.fetch_balance()
        print(f"💰 Total Balance: ${balance.get('total', {}).get('USDT', 0):.2f}")
        print(f"💵 Free USDT: ${balance.get('free', {}).get('USDT', 0):.2f}")
        print(f"📊 Used USDT: ${balance.get('used', {}).get('USDT', 0):.2f}")
        
        # Show positions
        print("\n📈 Positions:")
        positions = binance.fetch_positions()
        for pos in positions:
            if float(pos.get('contracts', 0)) > 0:
                symbol = pos.get('symbol', '')
                side = pos.get('side', '')
                contracts = pos.get('contracts', 0)
                entry_price = pos.get('entryPrice', 0)
                mark_price = pos.get('markPrice', 0)
                pnl = pos.get('unrealizedPnl', 0)
                print(f"  {symbol} {side} x{contracts} @ ${entry_price:.4f} (Mark: ${mark_price:.4f}, P&L: ${pnl:.2f})")
        
        return balance
    except Exception as e:
        print(f"❌ Binance API Error: {e}")
        print("⚠️  Note: Binance may be geographically restricted in Thailand")
        
        # Try to get data from trading bot logs
        try:
            with open('real_26_crypto_trading.log', 'r') as f:
                lines = f.readlines()[-100:]  # Last 100 lines
                for line in lines:
                    if 'Binance' in line and ('capital' in line.lower() or 'balance' in line.lower()):
                        print(f"📝 From log: {line.strip()}")
        except:
            pass
        
        return None

def check_trade_history():
    """Check actual trade history"""
    print("\n📊 CHECKING ACTUAL TRADE HISTORY")
    print("="*50)
    
    trade_files = [
        '26_crypto_trade_history.json',
        '26_crypto_trade_history_CORRECTED.json',
        'daily_trades.json'
    ]
    
    for file in trade_files:
        if os.path.exists(file):
            try:
                with open(file, 'r') as f:
                    trades = json.load(f)
                
                if isinstance(trades, list):
                    print(f"\n📁 {file}: {len(trades)} trades")
                    # Show recent trades
                    for i, trade in enumerate(trades[-5:]):  # Last 5 trades
                        exchange = trade.get('exchange', 'unknown')
                        symbol = trade.get('symbol', 'unknown')
                        side = trade.get('side', 'unknown')
                        entry = trade.get('entry_price', 0)
                        current = trade.get('current_price', 0)
                        pnl = trade.get('pnl', 0)
                        status = trade.get('status', 'unknown')
                        print(f"  {i+1}. {exchange} {symbol} {side} @ ${entry:.4f} (Now: ${current:.4f}, P&L: ${pnl:.2f}) [{status}]")
                else:
                    print(f"📁 {file}: Not a list format")
            except Exception as e:
                print(f"❌ Error reading {file}: {e}")

def main():
    print("="*60)
    print("🔍 CHECKING REAL EXCHANGE DATA - PROACTIVE MONITORING")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check actual balances
    gemini_balance = check_gemini_balance()
    binance_balance = check_binance_balance()
    
    # Check trade history
    check_trade_history()
    
    print("\n" + "="*60)
    print("🎯 RECOMMENDATIONS:")
    print("1. Update dashboard with REAL API data, not estimates")
    print("2. Show actual trade rows from trade history")
    print("3. Fix P&L calculations with real current prices")
    print("4. Monitor proactively, not reactively")
    print("="*60)

if __name__ == "__main__":
    main()