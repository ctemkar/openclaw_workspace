#!/usr/bin/env python3
"""
Simple test dashboard
"""
from flask import Flask, render_template_string
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def test_dashboard():
    try:
        # Load sample data
        with open('trading_data/trades.json', 'r') as f:
            trades = json.load(f)
        
        # Calculate totals
        gemini_trades = [t for t in trades if t.get('exchange') == 'gemini']
        binance_trades = [t for t in trades if t.get('exchange') == 'binance']
        
        gemini_total = sum(t.get('value', 0) for t in gemini_trades)
        binance_total = sum(t.get('value', 0) for t in binance_trades)
        
        # Simple template
        html = f'''
        <!DOCTYPE html>
        <html>
        <head><title>Test Dashboard</title></head>
        <body>
            <h1>Test Dashboard</h1>
            <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h2>Gemini Trades: {len(gemini_trades)}</h2>
            <p>Total Value: ${gemini_total:.2f}</p>
            
            <h2>Binance Trades: {len(binance_trades)}</h2>
            <p>Total Value: ${binance_total:.2f}</p>
            
            <h2>Binance Total Row (as requested):</h2>
            <table border="1">
                <tr>
                    <td colspan="8" style="text-align: right; font-weight: bold; color: #f0b90b;">
                        🟡 BINANCE TOTAL:
                    </td>
                    <td style="font-weight: bold;">{len(binance_trades)} trades</td>
                    <td style="font-weight: bold; color: #f0b90b;">${binance_total:.2f}</td>
                </tr>
            </table>
            
            <p><strong>✅ Binance Total row added AFTER all Binance trades!</strong></p>
        </body>
        </html>
        '''
        
        return html
        
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    print("Starting test dashboard on port 5012...")
    app.run(host='0.0.0.0', port=5012, debug=False)