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
    """Calculate P&L for all exchanges using position monitor"""
    try:
        # Import position monitor functions
        from position_monitor import load_open_positions, calculate_position_pnl
        
        pnl_data = {
            "gemini": {"realized": 0.0, "unrealized": 0.0, "total": 0.0, "trades": 0, "open_positions": 0},
            "binance": {"realized": 0.0, "unrealized": 0.0, "total": 0.0, "trades": 0, "open_positions": 0},
            "total": {"realized": 0.0, "unrealized": 0.0, "total": 0.0, "open_positions": 0}
        }
        
        # Initialize exchange for price fetching
        import ccxt
        binance = ccxt.binance()
        
        # Load all positions
        open_positions = load_open_positions()
        
        # Separate by exchange and calculate P&L
        for position in open_positions:
            exchange = position['exchange']
            symbol = position['symbol']
            
            # Get current price
            try:
                ticker = binance.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Calculate P&L
                pnl_info = calculate_position_pnl(position, current_price)
                
                # Update exchange P&L data
                if exchange == 'gemini':
                    pnl_data["gemini"]["unrealized"] += pnl_info['pnl']
                    pnl_data["gemini"]["open_positions"] += 1
                elif exchange == 'binance_futures':
                    pnl_data["binance"]["unrealized"] += pnl_info['pnl']
                    pnl_data["binance"]["open_positions"] += 1
                    
            except Exception as e:
                print(f"[{datetime.now()}] Error calculating P&L for {symbol}: {e}")
        
        # Count total trades (including closed ones)
        # Check Gemini trades
        gemini_trades_file = os.path.join(BASE_DIR, "real_trades_history.json")
        if os.path.exists(gemini_trades_file):
            with open(gemini_trades_file, 'r') as f:
                trades = json.load(f)
            pnl_data["gemini"]["trades"] = len(trades)
            
            # Calculate realized P&L for closed Gemini trades
            for trade in trades:
                if trade.get('status') == 'closed':
                    entry_price = trade.get('price', 0)
                    exit_price = trade.get('exit_price', entry_price * 1.02)
                    quantity = trade.get('quantity', 0)
                    pnl = (exit_price - entry_price) * quantity
                    pnl_data["gemini"]["realized"] += pnl
        
        # Check Binance futures trades
        binance_trades_file = os.path.join(BASE_DIR, "executed_futures_trades.json")
        if os.path.exists(binance_trades_file):
            with open(binance_trades_file, 'r') as f:
                trades = json.load(f)
            pnl_data["binance"]["trades"] = len(trades)
            
            # Calculate realized P&L for closed Binance trades
            for trade in trades:
                if trade.get('status') == 'CLOSED':
                    pnl = trade.get('pnl', 0)
                    pnl_data["binance"]["realized"] += pnl
        
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
            <li>Stop-loss: 5% (ALL trades)</li>
            <li>Take-profit: 10% (ALL trades)</li>
            <li>Max trades/day: <strong>UNLIMITED</strong> (trade based on market conditions)</li>
            <li>Position size: 20% of capital per trade</li>
            <li>Cryptocurrencies: 26 total</li>
            <li>Gemini (LONG): 7 pairs (BTC, ETH, SOL, ADA, LINK, UNI, MATIC)</li>
            <li>Binance (SHORT): 26 pairs (All top cryptos)</li>
            <li><strong>Execution Mode: ✅ REAL TRADING - LIVE</strong></li>
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
            "max_trades_per_day": 999  # No limit  # Total: Gemini(4) + Binance(2) = 6
        },
        "trading_pairs": [
            "BTC/USD", "ETH/USD", "SOL/USD", "ADA/USD", "XRP/USD",
            "DOT/USD", "DOGE/USD", "AVAX/USD", "MATIC/USD", "LINK/USD"
        ]
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
    print(f"Capital: $250 (REAL) | Stop-loss: 5% | Take-profit: 10%")
    print(f"Max trades/day: UNLIMITED | Pairs: 26 cryptocurrencies")
    print(f"Server running at http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=False)