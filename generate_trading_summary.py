#!/usr/bin/env python3
"""
Generate trading summary from the trading server API
"""

import json
import requests
from datetime import datetime
import sys

def fetch_trading_data():
    """Fetch trading data from the server API"""
    try:
        response = requests.get("http://localhost:5001/api/data", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def generate_summary(data):
    """Generate a comprehensive trading summary"""
    if not data:
        return "Error: Could not fetch trading data"
    
    summary = []
    summary.append("=" * 60)
    summary.append("REAL CRYPTO TRADING SYSTEM - DAILY SUMMARY")
    summary.append("=" * 60)
    summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    summary.append("")
    
    # Cumulative P&L Section
    pnl = data.get('cumulative_pnl', {})
    summary.append("📊 CUMULATIVE PERFORMANCE (NEVER RESETS)")
    summary.append("-" * 40)
    summary.append(f"Initial Capital: ${pnl.get('initial', 0):.2f}")
    summary.append(f"Current Capital: ${pnl.get('current', 0):.2f}")
    summary.append(f"Cumulative P&L: ${pnl.get('pnl', 0):.2f} ({pnl.get('pnl_percent', 0):.2f}%)")
    summary.append(f"Recovery Needed: ${pnl.get('recovery_needed', 0):.2f} (+{pnl.get('recovery_percent_needed', 0):.1f}%)")
    summary.append(f"Recovery Target: ${pnl.get('recovery_target', 0):.2f}")
    summary.append("")
    
    # Capital Allocation
    capital = data.get('capital_allocation', {})
    summary.append("💰 CAPITAL ALLOCATION")
    summary.append("-" * 40)
    summary.append(f"Total Capital: ${capital.get('total_capital', 0):.2f}")
    summary.append(f"Gemini: ${capital.get('gemini_total', 0):.2f} ({capital.get('gemini_total', 0)/capital.get('total_capital', 1)*100:.1f}%)")
    summary.append(f"Binance: ${capital.get('binance_total', 0):.2f} ({capital.get('binance_total', 0)/capital.get('total_capital', 1)*100:.1f}%)")
    summary.append(f"Deployed: ${capital.get('deployed', 0):.2f} ({capital.get('deployed', 0)/capital.get('total_capital', 1)*100:.1f}%)")
    summary.append(f"Available: ${capital.get('available_gemini', 0) + capital.get('available_binance', 0):.2f}")
    summary.append("")
    
    # Current Positions
    positions = data.get('current_positions', [])
    summary.append("📈 CURRENT OPEN POSITIONS")
    summary.append("-" * 40)
    
    if positions:
        total_position_value = 0
        for i, pos in enumerate(positions, 1):
            exchange = pos.get('exchange', 'unknown').upper()
            symbol = pos.get('symbol', 'N/A')
            amount = pos.get('amount', 0)
            price = pos.get('price', 0)
            value = pos.get('value', 0)
            side = pos.get('side', '').upper()
            timestamp = pos.get('timestamp', '')
            
            summary.append(f"{i}. {exchange} {side} {symbol}")
            summary.append(f"   Amount: {amount:.6f}")
            summary.append(f"   Entry Price: ${price:.2f}")
            summary.append(f"   Position Value: ${value:.2f}")
            summary.append(f"   Opened: {timestamp}")
            if pos.get('notes'):
                summary.append(f"   Notes: {pos.get('notes')}")
            summary.append("")
            total_position_value += value
        
        summary.append(f"Total Open Positions: {len(positions)}")
        summary.append(f"Total Position Value: ${total_position_value:.2f}")
        summary.append(f"Average Position Size: ${capital.get('avg_position_value', 0):.2f}")
    else:
        summary.append("No open positions")
    
    summary.append("")
    
    # Exchange Breakdown
    summary.append("🏦 EXCHANGE BREAKDOWN")
    summary.append("-" * 40)
    summary.append(f"Gemini P&L: ${pnl.get('current', 0) - capital.get('gemini_total', 0):.2f}")
    summary.append(f"Binance Futures Equity: ${pnl.get('binance_futures_equity', 0):.2f}")
    summary.append(f"Binance Futures Unrealized P&L: ${pnl.get('binance_futures_unrealized_pnl', 0):.2f}")
    summary.append("")
    
    # Risk Metrics
    summary.append("⚠️ RISK METRICS")
    summary.append("-" * 40)
    summary.append(f"Max Drawdown: ${abs(pnl.get('pnl', 0)):.2f} ({abs(pnl.get('pnl_percent', 0)):.2f}%)")
    summary.append(f"Capital at Risk: ${capital.get('deployed', 0):.2f}")
    summary.append(f"Cash Reserve: ${capital.get('available_gemini', 0) + capital.get('available_binance', 0):.2f}")
    summary.append("")
    
    # Notes and Status
    summary.append("📝 SYSTEM STATUS & NOTES")
    summary.append("-" * 40)
    if pnl.get('notes'):
        summary.append(pnl.get('notes'))
    summary.append(f"Data Source: {data.get('data_source', 'N/A')}")
    summary.append(f"System Status: {data.get('status', 'unknown').upper()}")
    summary.append(f"Last Updated: {data.get('timestamp', 'N/A')}")
    summary.append("")
    
    summary.append("=" * 60)
    summary.append("END OF DAILY TRADING SUMMARY")
    summary.append("=" * 60)
    
    return "\n".join(summary)

def main():
    """Main function"""
    print("Fetching trading data...")
    data = fetch_trading_data()
    
    if data:
        summary = generate_summary(data)
        print(summary)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trading_summary_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(summary)
        
        print(f"\nSummary saved to: {filename}")
        
        # Also update the latest summary file
        with open("trading_summary_latest.txt", 'w') as f:
            f.write(summary)
        
        print("Latest summary updated: trading_summary_latest.txt")
    else:
        print("Failed to generate trading summary")

if __name__ == "__main__":
    main()