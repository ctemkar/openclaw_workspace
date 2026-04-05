#!/usr/bin/env python3
"""
CURRENT POSITIONS REPORT
Shows all positions with individual P&L for Binance and Gemini
"""

import json
import os
from datetime import datetime
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_positions():
    """Load all positions from tracker"""
    tracker_path = os.path.join(BASE_DIR, 'cumulative_pnl_tracker.json')
    if not os.path.exists(tracker_path):
        return None
    
    with open(tracker_path, 'r') as f:
        return json.load(f)

def generate_report():
    """Generate comprehensive position report"""
    data = load_positions()
    if not data:
        return "No position data available"
    
    positions = data.get('unrealized_positions', [])
    
    # Separate by source
    gemini_positions = [p for p in positions if p.get('source') == 'gemini']
    binance_positions = [p for p in positions if p.get('source') == 'binance_26crypto']
    
    # Calculate totals
    total_gemini_value = sum(p.get('current_value', 0) for p in gemini_positions)
    total_gemini_pnl = sum(p.get('unrealized_pnl', 0) for p in gemini_positions)
    total_gemini_risk = sum(p.get('capital_at_risk', 0) for p in gemini_positions)
    
    total_binance_value = sum(p.get('current_value', 0) for p in binance_positions)
    total_binance_pnl = sum(p.get('unrealized_pnl', 0) for p in binance_positions)
    total_binance_risk = sum(p.get('capital_at_risk', 0) for p in binance_positions)
    
    # Create report
    report = []
    report.append("="*80)
    report.append("📊 CURRENT POSITIONS REPORT - INDIVIDUAL P&L")
    report.append("="*80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Total Positions: {len(positions)} ({len(gemini_positions)} Gemini, {len(binance_positions)} Binance)")
    report.append("")
    
    # Gemini Positions
    if gemini_positions:
        report.append("🔵 GEMINI POSITIONS (LONG)")
        report.append("-"*40)
        for i, pos in enumerate(gemini_positions, 1):
            pnl = pos.get('unrealized_pnl', 0)
            pnl_percent = pos.get('unrealized_pnl_percent', 0)
            pnl_sign = "+" if pnl >= 0 else ""
            pnl_color = "🟢" if pnl >= 0 else "🔴"
            
            report.append(f"{i}. {pos.get('symbol', 'N/A')}")
            report.append(f"   Side: {pos.get('side', 'N/A').upper()}")
            report.append(f"   Entry: ${pos.get('entry_price', 0):.2f}")
            report.append(f"   Current: ${pos.get('current_price', 0):.2f}")
            report.append(f"   Quantity: {pos.get('quantity', 0):.6f}")
            report.append(f"   Entry Value: ${pos.get('entry_value', 0):.2f}")
            report.append(f"   Current Value: ${pos.get('current_value', 0):.2f}")
            report.append(f"   P&L: {pnl_color} ${pnl_sign}{pnl:.2f} ({pnl_sign}{pnl_percent:.2f}%)")
            report.append(f"   Days Held: {pos.get('days_held', 0):.2f}")
            report.append(f"   Trade ID: {pos.get('trade_id', 'N/A')}")
            report.append("")
    
    # Binance Positions
    if binance_positions:
        report.append("🟡 BINANCE POSITIONS (SHORT with 3x Leverage)")
        report.append("-"*40)
        for i, pos in enumerate(binance_positions, 1):
            pnl = pos.get('unrealized_pnl', 0)
            pnl_percent = pos.get('unrealized_pnl_percent', 0)
            pnl_sign = "+" if pnl >= 0 else ""
            pnl_color = "🟢" if pnl >= 0 else "🔴"
            
            report.append(f"{i}. {pos.get('symbol', 'N/A')}")
            report.append(f"   Side: {pos.get('side', 'N/A').upper()} (SHORT)")
            report.append(f"   Entry: ${pos.get('entry_price', 0):.2f}")
            report.append(f"   Current: ${pos.get('current_price', 0):.2f}")
            report.append(f"   Quantity: {pos.get('quantity', 0):.6f}")
            report.append(f"   Position Value: ${pos.get('entry_value', 0):.2f}")
            report.append(f"   Capital at Risk: ${pos.get('capital_at_risk', 0):.2f}")
            report.append(f"   Leverage: {pos.get('leverage', 1)}x")
            report.append(f"   P&L: {pnl_color} ${pnl_sign}{pnl:.2f} ({pnl_sign}{pnl_percent:.2f}%)")
            report.append(f"   Days Held: {pos.get('days_held', 0):.2f}")
            report.append("")
    
    # Summary
    report.append("💰 POSITION SUMMARY")
    report.append("-"*40)
    
    if gemini_positions:
        report.append(f"Gemini Total:")
        report.append(f"  • Positions: {len(gemini_positions)}")
        report.append(f"  • Total Value: ${total_gemini_value:.2f}")
        report.append(f"  • Total P&L: ${total_gemini_pnl:+.2f}")
        report.append(f"  • Capital at Risk: ${total_gemini_risk:.2f}")
    
    if binance_positions:
        report.append(f"Binance Total:")
        report.append(f"  • Positions: {len(binance_positions)}")
        report.append(f"  • Total Position Value: ${total_binance_value:.2f}")
        report.append(f"  • Total P&L: ${total_binance_pnl:+.2f}")
        report.append(f"  • Total Capital at Risk: ${total_binance_risk:.2f}")
        report.append(f"  • Leverage: 3x")
    
    report.append("")
    report.append("📈 PERFORMANCE ANALYSIS")
    report.append("-"*40)
    
    # Winning vs Losing
    winning_positions = [p for p in positions if p.get('unrealized_pnl', 0) >= 0]
    losing_positions = [p for p in positions if p.get('unrealized_pnl', 0) < 0]
    
    report.append(f"Winning Positions: {len(winning_positions)}")
    report.append(f"Losing Positions: {len(losing_positions)}")
    
    if positions:
        win_rate = (len(winning_positions) / len(positions)) * 100
        report.append(f"Current Win Rate: {win_rate:.1f}%")
    
    # Best and Worst performers
    if positions:
        best_position = max(positions, key=lambda x: x.get('unrealized_pnl_percent', 0))
        worst_position = min(positions, key=lambda x: x.get('unrealized_pnl_percent', 0))
        
        report.append(f"Best Performer: {best_position.get('symbol')} - ${best_position.get('unrealized_pnl', 0):+.2f} ({best_position.get('unrealized_pnl_percent', 0):+.2f}%)")
        report.append(f"Worst Performer: {worst_position.get('symbol')} - ${worst_position.get('unrealized_pnl', 0):+.2f} ({worst_position.get('unrealized_pnl_percent', 0):+.2f}%)")
    
    report.append("")
    report.append("🚨 CAPITAL ALLOCATION ISSUE")
    report.append("-"*40)
    report.append("Binance Free Balance: $3.47 (TRADING BLOCKED)")
    report.append("Binance Total Balance: $76.61")
    report.append(f"Capital Tied in Positions: ${total_binance_risk:.2f}")
    report.append("")
    report.append("To use entire $76:")
    report.append("1. Close positions → Free up ${:.2f}".format(total_binance_risk))
    report.append("2. Use full $76.61 for new aggressive trading")
    report.append("")
    report.append("="*80)
    
    return "\n".join(report)

def create_html_report():
    """Create HTML version for dashboard"""
    data = load_positions()
    if not data:
        return "<h2>No position data available</h2>"
    
    positions = data.get('unrealized_positions', [])
    
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>📊 Current Positions with P&L</title>
    <style>
        body { font-family: monospace; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
        th { background-color: #f2f2f2; }
        .positive { color: green; font-weight: bold; }
        .negative { color: red; font-weight: bold; }
        .gemini { background-color: #e6f3ff; }
        .binance { background-color: #fff8e6; }
        .warning { background-color: #ffe6e6; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>📊 Current Positions with Individual P&L</h1>
    <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
"""
    
    # Create tables
    gemini_positions = [p for p in positions if p.get('source') == 'gemini']
    binance_positions = [p for p in positions if p.get('source') == 'binance_26crypto']
    
    if gemini_positions:
        html += """
    <h2>🔵 Gemini Positions (LONG)</h2>
    <table class="gemini">
        <tr>
            <th>Symbol</th><th>Side</th><th>Entry</th><th>Current</th>
            <th>Quantity</th><th>Value</th><th>P&L</th><th>P&L%</th>
        </tr>
"""
        for pos in gemini_positions:
            pnl = pos.get('unrealized_pnl', 0)
            pnl_class = "positive" if pnl >= 0 else "negative"
            pnl_sign = "+" if pnl >= 0 else ""
            
            html += f"""
        <tr>
            <td>{pos.get('symbol', 'N/A')}</td>
            <td>{pos.get('side', '').upper()}</td>
            <td>${pos.get('entry_price', 0):.2f}</td>
            <td>${pos.get('current_price', 0):.2f}</td>
            <td>{pos.get('quantity', 0):.6f}</td>
            <td>${pos.get('current_value', 0):.2f}</td>
            <td class="{pnl_class}">{pnl_sign}${pnl:.2f}</td>
            <td class="{pnl_class}">{pnl_sign}{pos.get('unrealized_pnl_percent', 0):.2f}%</td>
        </tr>
"""
        html += "</table>"
    
    if binance_positions:
        html += """
    <h2>🟡 Binance Positions (SHORT - 3x Leverage)</h2>
    <table class="binance">
        <tr>
            <th>Symbol</th><th>Side</th><th>Entry</th><th>Current</th>
            <th>Quantity</th><th>Position</th><th>Risk</th><th>P&L</th><th>P&L%</th>
        </tr>
"""
        for pos in binance_positions:
            pnl = pos.get('unrealized_pnl', 0)
            pnl_class = "positive" if pnl >= 0 else "negative"
            pnl_sign = "+" if pnl >= 0 else ""
            
            html += f"""
        <tr>
            <td>{pos.get('symbol', 'N/A')}</td>
            <td>{pos.get('side', '').upper()}</td>
            <td>${pos.get('entry_price', 0):.2f}</td>
            <td>${pos.get('current_price', 0):.2f}</td>
            <td>{pos.get('quantity', 0):.6f}</td>
            <td>${pos.get('entry_value', 0):.2f}</td>
            <td>${pos.get('capital_at_risk', 0):.2f}</td>
            <td class="{pnl_class}">{pnl_sign}${pnl:.2f}</td>
            <td class="{pnl_class}">{pnl_sign}{pos.get('unrealized_pnl_percent', 0):.2f}%</td>
        </tr>
"""
        html += "</table>"
    
    # Summary
    total_binance_risk = sum(p.get('capital_at_risk', 0) for p in binance_positions)
    
    html += f"""
    <div class="warning">
        <h3>🚨 CAPITAL ALLOCATION ISSUE</h3>
        <p><strong>Binance Free Balance:</strong> $3.47 (TRADING BLOCKED)</p>
        <p><strong>Binance Total Balance:</strong> $76.61</p>
        <p><strong>Capital Tied in Positions:</strong> ${total_binance_risk:.2f}</p>
        <p><strong>To use entire $76:</strong> Close positions → Free up ${total_binance_risk:.2f} → Use full $76.61</p>
    </div>
    
    <button onclick="window.location.href='http://localhost:5004'">Back to Dashboard</button>
</body>
</html>
"""
    
    return html

if __name__ == '__main__':
    # Generate text report
    report = generate_report()
    print(report)
    
    # Save to file
    with open('current_positions_report.txt', 'w') as f:
        f.write(report)
    
    print("\n✅ Report saved to: current_positions_report.txt")
    
    # Also create HTML version
    html_report = create_html_report()
    with open('current_positions_report.html', 'w') as f:
        f.write(html_report)
    
    print("✅ HTML report saved to: current_positions_report.html")
    print("📊 Open in browser: file://" + os.path.join(BASE_DIR, 'current_positions_report.html'))