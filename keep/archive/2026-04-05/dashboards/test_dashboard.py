#!/usr/bin/env python3
"""
Simple test dashboard to verify data
"""

from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Read system_status.json
    with open('system_status.json', 'r') as f:
        data = json.load(f)
    
    return jsonify(data)

@app.route('/capital')
def capital():
    # Read capital.json
    with open('trading_data/capital.json', 'r') as f:
        data = json.load(f)
    
    return jsonify(data)

@app.route('/simple')
def simple():
    # Simple HTML with data
    with open('system_status.json', 'r') as f:
        data = json.load(f)
    
    capital_data = data['api']['capital_allocation']
    
    html = f"""
    <html>
    <head><title>Trading Dashboard Test</title></head>
    <body>
        <h1>Trading Dashboard Test</h1>
        <h2>Real Data (Updated: {capital_data['last_updated']})</h2>
        <table border="1">
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Capital</td><td>${capital_data['total']:.2f}</td></tr>
            <tr><td>Gemini</td><td>${capital_data['gemini']:.2f}</td></tr>
            <tr><td>Binance</td><td>${capital_data['binance']:.2f}</td></tr>
            <tr><td>Deployed</td><td>${capital_data['deployed']:.2f}</td></tr>
            <tr><td>Available</td><td>${capital_data['available_total']:.2f}</td></tr>
            <tr><td>P&L</td><td>${capital_data['pnl']:.2f}</td></tr>
            <tr><td>P&L %</td><td>{capital_data['pnl_percent']:.2f}%</td></tr>
            <tr><td>Positions</td><td>{capital_data['position_count']}</td></tr>
        </table>
        <p><em>Note: This shows REAL current data, not stale data.</em></p>
    </body>
    </html>
    """
    
    return html

if __name__ == '__main__':
    app.run(port=5011, debug=True)