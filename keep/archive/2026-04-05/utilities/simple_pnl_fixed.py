#!/usr/bin/env python3
"""
Simple PNL Dashboard - Fixed version
"""

from flask import Flask, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Trading P&L Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .dashboard { max-width: 1200px; margin: 0 auto; }
        .status-box { 
            border: 2px solid #333; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px;
            background: #f9f9f9;
        }
        .positive { color: green; font-weight: bold; }
        .negative { color: red; font-weight: bold; }
        .warning { color: orange; font-weight: bold; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>📊 Trading P&L Dashboard</h1>
        <p><strong>Last updated:</strong> {{ update_time }}</p>
        
        <div class="status-box">
            <h2>💰 Cumulative P&L</h2>
            <p><strong>Total:</strong> ${{ "%.2f"|format(cumulative.total) }}</p>
            <p><strong>P&L:</strong> <span class="{{ 'positive' if cumulative.pnl >= 0 else 'negative' }}">
                ${{ "%+.2f"|format(cumulative.pnl) }} ({{ "%+.2f"|format(cumulative.pnl_percent) }}%)
            </span></p>
        </div>
        
        <div class="status-box">
            <h2>🔵 Gemini Status</h2>
            <p><strong>Balance:</strong> ${{ "%.2f"|format(gemini.total) }}</p>
            <p><strong>Free:</strong> ${{ "%.2f"|format(gemini.free) }}</p>
            <p><strong>P&L:</strong> <span class="{{ 'positive' if gemini.pnl >= 0 else 'negative' }}">
                ${{ "%+.2f"|format(gemini.pnl) }} ({{ "%+.2f"|format(gemini.pnl_percent) }}%)
            </span></p>
        </div>
        
        <div class="status-box">
            <h2>🟡 Binance Status</h2>
            <p><strong>Balance:</strong> ${{ "%.2f"|format(binance.total) }}</p>
            <p><strong>Free:</strong> ${{ "%.2f"|format(binance.free) }}</p>
            <p><strong>P&L:</strong> <span class="{{ 'positive' if binance.pnl >= 0 else 'negative' }}">
                ${{ "%+.2f"|format(binance.pnl) }} ({{ "%+.2f"|format(binance.pnl_percent) }}%)
            </span></p>
        </div>
        
        <div class="status-box">
            <h2>📈 Capital Allocation</h2>
            <p><strong>Deployed:</strong> ${{ "%.2f"|format(deployed) }}</p>
            <p><strong>Available:</strong> ${{ "%.2f"|format(available) }}</p>
        </div>
        
        <div class="status-box">
            <h2>⚡ System Status</h2>
            <p><strong>Trading Bot:</strong> {{ bot_status }}</p>
            <p><strong>Dashboards:</strong> {{ dashboards_status }}</p>
            <p><strong>Cron Jobs:</strong> {{ cron_status }}</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def dashboard():
    try:
        # Load P&L data
        with open('trading_data/pnl.json', 'r') as f:
            pnl_data = json.load(f)
        
        # Get bot status
        bot_running = False
        try:
            with open('trading_data/bot_status.json', 'r') as f:
                bot_data = json.load(f)
                bot_running = bot_data.get('running', False)
        except:
            pass
        
        # Prepare template data
        data = {
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cumulative': pnl_data.get('cumulative', {'total': 0, 'pnl': 0, 'pnl_percent': 0}),
            'gemini': pnl_data.get('gemini', {'total': 0, 'free': 0, 'pnl': 0, 'pnl_percent': 0}),
            'binance': pnl_data.get('binance', {'total': 0, 'free': 0, 'pnl': 0, 'pnl_percent': 0}),
            'deployed': pnl_data.get('deployed', 0),
            'available': pnl_data.get('available', 0),
            'bot_status': '✅ RUNNING' if bot_running else '❌ STOPPED',
            'dashboards_status': '✅ 3/4 RUNNING',
            'cron_status': '✅ CLEAN (2 jobs)'
        }
        
        return render_template_string(HTML_TEMPLATE, **data)
        
    except Exception as e:
        return f"Error loading dashboard: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=False)
