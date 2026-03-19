#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime
import time

def check_trading_server():
    """Check if trading server is running and get status"""
    try:
        # Check status endpoint
        status_response = requests.get("http://localhost:5001/status", timeout=5)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"✅ Trading server is running on port 5001")
            print(f"   Status: {status_data.get('status', 'unknown')}")
            print(f"   Last analysis: {status_data.get('last_analysis', 'unknown')}")
            print(f"   Capital: ${status_data.get('capital', 0):.2f}")
            print(f"   Next analysis: {status_data.get('analysis_scheduled', 'unknown')}")
            return True
        else:
            print(f"❌ Status endpoint returned {status_response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to trading server on port 5001")
        return False
    except Exception as e:
        print(f"❌ Error checking trading server: {e}")
        return False

def check_recent_trades():
    """Check recent trades"""
    try:
        trades_response = requests.get("http://localhost:5001/trades", timeout=5)
        if trades_response.status_code == 200:
            trades_data = trades_response.json()
            trade_count = trades_data.get('count', 0)
            trades = trades_data.get('trades', [])
            
            print(f"\n📊 Recent trades: {trade_count}")
            
            # Show last 3 trades
            for i, trade in enumerate(trades[:3]):
                symbol = trade.get('symbol', 'Unknown')
                side = trade.get('side', 'Unknown')
                price = trade.get('price', 0)
                time_str = trade.get('time', 'Unknown')
                print(f"   {i+1}. {symbol} {side} @ ${price:.2f} ({time_str})")
            
            return True
        else:
            print(f"\n❌ Trades endpoint returned {trades_response.status_code}")
            return False
    except Exception as e:
        print(f"\n❌ Error checking trades: {e}")
        return False

def check_trading_summary():
    """Check trading summary"""
    try:
        summary_response = requests.get("http://localhost:5001/summary", timeout=5)
        if summary_response.status_code == 200:
            summary_text = summary_response.text
            
            # Extract key information
            lines = summary_text.split('\n')
            print("\n📈 Trading Summary:")
            
            for line in lines:
                line = line.strip()
                if "Today's trades:" in line:
                    print(f"   {line}")
                elif "Total trades:" in line:
                    print(f"   {line}")
                elif "Total P&L:" in line:
                    print(f"   {line}")
                elif "Available capital:" in line:
                    print(f"   {line}")
                elif "Analysis complete" in line:
                    print(f"   {line}")
            
            return True
        else:
            print(f"\n❌ Summary endpoint returned {summary_response.status_code}")
            return False
    except Exception as e:
        print(f"\n❌ Error checking summary: {e}")
        return False

def main():
    print(f"=== Trading Dashboard Monitor ===\n")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Server: http://localhost:5001/\n")
    
    # Check if server is running
    if not check_trading_server():
        print("\n⚠️ Trading server may not be running or is unreachable")
        sys.exit(1)
    
    # Check recent trades
    check_recent_trades()
    
    # Check trading summary
    check_trading_summary()
    
    print(f"\n=== Monitor complete ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()