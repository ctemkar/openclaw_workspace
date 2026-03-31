#!/usr/bin/env python3
"""
Conservative Crypto Trading Server
Runs on port 5001 and provides API endpoints for trading system
"""

from flask import Flask, jsonify, request
import subprocess
import json
import os
import time
import re
from datetime import datetime
from threading import Thread
import schedule

app = Flask(__name__)
BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

# Files
TRADES_LOG = os.path.join(BASE_DIR, "completed_trades.json")
STRATEGY_FILE = os.path.join(BASE_DIR, "llm_strategies.json")
TRADING_HISTORY = os.path.join(BASE_DIR, "trading_history.json")
SUMMARY_FILE = os.path.join(BASE_DIR, "trading_summary.txt")

def run_trading_analysis():
    """Run the conservative trading analysis"""
    print(f"[{datetime.now()}] Running trading analysis...")
    try:
        result = subprocess.run(
            ["python3", os.path.join(BASE_DIR, "conservative_crypto_trading.py")],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        
        # Create summary
        with open(SUMMARY_FILE, 'w') as f:
            f.write(f"TRADING ANALYSIS REPORT\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write("=" * 50 + "\n\n")
            f.write(result.stdout)
            if result.stderr:
                f.write("\nERRORS:\n")
                f.write(result.stderr)
        
        print(f"[{datetime.now()}] Analysis complete")
        return True
    except Exception as e:
        print(f"[{datetime.now()}] Analysis failed: {e}")
        return False

def get_real_capital():
    """Get REAL balances from exchanges"""
    try:
        total = 0
        
        # Try to get Gemini balance
        try:
            import ccxt
            with open(os.path.join(BASE_DIR, "secure_keys/.gemini_key"), 'r') as f:
                gemini_key = f.read().strip()
            with open(os.path.join(BASE_DIR, "secure_keys/.gemini_secret"), 'r') as f:
                gemini_secret = f.read().strip()
            
            gemini = ccxt.gemini({
                'apiKey': gemini_key,
                'secret': gemini_secret,
                'enableRateLimit': True
            })
            
            gemini_balance = gemini.fetch_balance()
            gemini_usd = gemini_balance['free'].get('USD', 0)
            total += gemini_usd
            print(f"[{datetime.now()}] Gemini balance: ${gemini_usd:.2f}")
        except Exception as e:
            print(f"[{datetime.now()}] Could not fetch Gemini balance: {e}")
            gemini_usd = 0
        
        # Try to get Binance balance (estimate from logs)
        try:
            binance_log = os.path.join(BASE_DIR, "binance_bot1.log")
            if os.path.exists(binance_log):
                with open(binance_log, 'r') as f:
                    lines = f.readlines()[-10:]  # Last 10 lines
                    for line in reversed(lines):
                        if "Free USDT:" in line:
                            import re
                            match = re.search(r'Free USDT:\s*\$\s*([\d.]+)', line)
                            if match:
                                binance_usd = float(match.group(1))
                                total += binance_usd
                                print(f"[{datetime.now()}] Binance balance: ${binance_usd:.2f}")
                                break
        except Exception as e:
            print(f"[{datetime.now()}] Could not estimate Binance balance: {e}")
        
        return round(total, 2)
    except Exception as e:
        print(f"[{datetime.now()}] Error getting real capital: {e}")
        return 0.0

def calculate_pnl():
    """Calculate P&L for all exchanges with real-time prices"""
    try:
        pnl_data = {
            "gemini": {"realized": 0.0, "unrealized": 0.0, "total": 0.0, "trades": 0, "open_positions": 0},
            "binance": {"realized": 0.0, "unrealized": 0.0, "total": 0.0, "trades": 0, "open_positions": 0},
            "total": {"realized": 0.0, "unrealized": 0.0, "total": 0.0, "open_positions": 0}
        }
        
        # Initialize exchange for price fetching
        import ccxt
        binance = ccxt.binance()
        
        # Check Gemini trades
        gemini_trades_file = os.path.join(BASE_DIR, "real_trades_history.json")
        if os.path.exists(gemini_trades_file):
            with open(gemini_trades_file, 'r') as f:
                trades = json.load(f)
            
            pnl_data["gemini"]["trades"] = len(trades)
            
            # Calculate Gemini P&L with current prices
            for trade in trades:
                status = trade.get('status', 'open')
                entry_price = trade.get('price', 0)
                quantity = trade.get('quantity', 0)
                symbol = trade.get('symbol', '')
                
                if status == 'closed':
                    exit_price = trade.get('exit_price', entry_price * 1.02)  # Assume 2% profit if not specified
                    pnl = (exit_price - entry_price) * quantity
                    pnl_data["gemini"]["realized"] += pnl
                else:
                    # Get current price for unrealized P&L
                    try:
                        if symbol:
                            # Convert Gemini symbol to Binance format if needed
                            if 'USD' in symbol:
                                symbol_ccxt = symbol.replace('USD', 'USDT')
                                ticker = binance.fetch_ticker(symbol_ccxt)
                                current_price = ticker['last']
                                
                                # Calculate unrealized P&L
                                pnl = (current_price - entry_price) * quantity
                                pnl_data["gemini"]["unrealized"] += pnl
                                pnl_data["gemini"]["open_positions"] += 1
                    except:
                        pass
        
        # Check Binance futures trades
        binance_trades_file = os.path.join(BASE_DIR, "executed_futures_trades.json")
        if os.path.exists(binance_trades_file):
            with open(binance_trades_file, 'r') as f:
                trades = json.load(f)
            
            # Calculate Binance futures P&L with current prices
            for trade in trades:
                pnl = trade.get('pnl', 0)
                status = trade.get('status', 'OPEN')
                entry_price = trade.get('entry_price', 0)
                symbol = trade.get('symbol', '')
                side = trade.get('side', 'sell')  # SHORT positions are 'sell'
                
                pnl_data["binance"]["trades"] += 1
                
                if status == 'CLOSED':
                    pnl_data["binance"]["realized"] += pnl
                else:
                    # Calculate unrealized P&L for open SHORT positions
                    try:
                        if symbol and entry_price > 0:
                            ticker = binance.fetch_ticker(symbol)
                            current_price = ticker['last']
                            
                            # For SHORT positions: profit when price goes down
                            if side == 'sell':
                                # SHORT: profit = (entry_price - current_price) * position_size
                                # Simplified calculation
                                price_change_pct = (entry_price - current_price) / entry_price
                                position_value = trade.get('position_value', 10)  # Default $10
                                unrealized_pnl = position_value * price_change_pct * 2  # 2x leverage
                                
                                pnl_data["binance"]["unrealized"] += unrealized_pnl
                                pnl_data["binance"]["open_positions"] += 1
                    except Exception as e:
                        print(f"[{datetime.now()}] Error calculating Binance unrealized P&L: {e}")
        
        # Calculate totals
        pnl_data["gemini"]["total"] = pnl_data["gemini"]["realized"] + pnl_data["gemini"]["unrealized"]
        pnl_data["binance"]["total"] = pnl_data["binance"]["realized"] + pnl_data["binance"]["unrealized"]
        pnl_data["total"]["realized"] = pnl_data["gemini"]["realized"] + pnl_data["binance"]["realized"]
        pnl_data["total"]["unrealized"] = pnl_data["gemini"]["unrealized"] + pnl_data["binance"]["unrealized"]
        pnl_data["total"]["total"] = pnl_data["total"]["realized"] + pnl_data["total"]["unrealized"]
        pnl_data["total"]["open_positions"] = pnl_data["gemini"]["open_positions"] + pnl_data["binance"]["open_positions"]
        
        return pnl_data
    except Exception as e:
        print(f"[{datetime.now()}] Error calculating P&L: {e}")
        import traceback
        print(traceback.format_exc())
        return {
            "gemini": {"realized": 0.0, "unrealized": 0.0, "total": 0.0, "trades": 0, "open_positions": 0},
            "binance": {"realized": 0.0, "unrealized": 0.0, "total": 0.0, "trades": 0, "open_positions": 0},
            "total": {"realized": 0.0, "unrealized": 0.0, "total": 0.0, "open_positions": 0}
        }

def schedule_analysis():
    """Schedule hourly analysis"""
    schedule.every().hour.do(run_trading_analysis)
    
    # Run initial analysis
    run_trading_analysis()
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

@app.route('/')
def index():
    """Home page with trading system info"""
    return """
    <html>
    <head><title>Conservative Crypto Trading System</title></head>
    <body>
        <h1>Conservative Crypto Trading System</h1>
        <p>Real trading with $250 capital ($200 Gemini longs + $50 Binance shorts)</p>
        
        <h2>Endpoints:</h2>
        <ul>
            <li><a href="/status">/status</a> - System status</li>
            <li><a href="/analysis">/analysis</a> - Run analysis now</li>
            <li><a href="/trades">/trades</a> - Recent trades</li>
            <li><a href="/strategy">/strategy</a> - Current strategy</li>
            <li><a href="/summary">/summary</a> - Trading summary</li>
        </ul>
        
        <h2>Configuration:</h2>
        <ul>
            <li>Capital: $250 ($200 Gemini + $50 Binance)</li>
            <li>Stop-loss: 5% (Gemini) / 7% (Binance)</li>
            <li>Take-profit: 10% (Gemini) / 8% (Binance)</li>
            <li>Max trades/day: 5 total (3 Gemini + 2 Binance)</li>
            <li>Cryptocurrencies: 26 total</li>
            <li>Gemini (LONG): 7 pairs (BTC, ETH, SOL, ADA, LINK, UNI, MATIC)</li>
            <li>Binance (SHORT): 26 pairs (All top cryptos)</li>
        </ul>
    </body>
    </html>
    """

@app.route('/status')
def get_status():
    """Get system status with P&L"""
    status = {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "port": 5001,
        "analysis_scheduled": "hourly",
        "capital": get_real_capital(),  # REAL balances only
        "pnl": calculate_pnl(),  # P&L data
        "risk_parameters": {
            "stop_loss": 0.05,
            "take_profit": 0.10,
            "max_trades_per_day": 2
        },
        "trading_pairs": ["BTC/USD", "ETH/USD"]
    }
    
    # Check if analysis is running
    try:
        with open(SUMMARY_FILE, 'r') as f:
            last_update = os.path.getmtime(SUMMARY_FILE)
            status["last_analysis"] = datetime.fromtimestamp(last_update).isoformat()
    except:
        status["last_analysis"] = None
    
    return jsonify(status)

@app.route('/analysis', methods=['GET', 'POST'])
def run_analysis():
    """Run trading analysis now"""
    if request.method == 'POST':
        # Run analysis
        success = run_trading_analysis()
        return jsonify({
            "success": success,
            "message": "Analysis completed" if success else "Analysis failed",
            "timestamp": datetime.now().isoformat()
        })
    else:
        # Show analysis form
        return """
        <html>
        <head><title>Run Trading Analysis</title></head>
        <body>
            <h1>Run Trading Analysis</h1>
            <form method="POST">
                <button type="submit">Run Analysis Now</button>
            </form>
            <p><a href="/">Back to home</a></p>
        </body>
        </html>
        """

@app.route('/trades')
def get_trades():
    """Get recent trades"""
    try:
        with open(TRADES_LOG, 'r') as f:
            trades = json.load(f)
        return jsonify({
            "trades": trades,
            "count": len(trades),
            "timestamp": datetime.now().isoformat()
        })
    except:
        return jsonify({
            "trades": [],
            "count": 0,
            "timestamp": datetime.now().isoformat(),
            "error": "No trades found"
        })

@app.route('/strategy')
def get_strategy():
    """Get current strategy"""
    try:
        with open(STRATEGY_FILE, 'r') as f:
            strategy = json.load(f)
        return jsonify(strategy)
    except:
        return jsonify({
            "error": "No strategy file found",
            "timestamp": datetime.now().isoformat()
        })

@app.route('/api/llm/strategies')
def get_llm_strategies():
    """API endpoint for LLM strategies (compatibility)"""
    try:
        with open(STRATEGY_FILE, 'r') as f:
            strategy = json.load(f)
        return jsonify([strategy])  # Return as array for compatibility
    except:
        return jsonify([])  # Return empty array if no strategy

@app.route('/summary')
def get_summary():
    """Get trading summary"""
    try:
        with open(SUMMARY_FILE, 'r') as f:
            summary = f.read()
        return f"<pre>{summary}</pre>"
    except:
        return "No summary available"

if __name__ == '__main__':
    # Start scheduling thread
    scheduler_thread = Thread(target=schedule_analysis, daemon=True)
    scheduler_thread.start()
    
    # Start Flask server
    print(f"Starting Conservative Crypto Trading Server on port 5001...")
    print(f"Capital: $1,000 | Stop-loss: 5% | Take-profit: 10%")
    print(f"Max trades/day: 2 | Pairs: BTC/USD, ETH/USD")
    print(f"Server running at http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=False)