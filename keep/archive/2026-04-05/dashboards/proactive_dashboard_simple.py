#!/usr/bin/env python3
"""
PROACTIVE ARBITRATION TRADING DASHBOARD
Dashboard that can START bots directly from the web interface
"""

import os
import json
import subprocess
import time
import re
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Bot configurations
BOTS = [
    {
        'id': 'forex',
        'name': '💰 FOREX Arbitration Bot',
        'file': 'forex_bot_with_schwab.py',
        'description': 'Schwab Account #13086459 • $220 Balance',
        'command': 'python3 forex_bot_with_schwab.py',
        'log': 'active_forex_trading.log',
        'balance': 220.00,
        'status': '❌ NOT RUNNING',
        'pid': None
    },
    {
        'id': 'arbitrage',
        'name': 'Auto Arbitrage Bot',
        'file': 'auto_arbitrage_bot.py',
        'description': 'Gemini vs Binance arbitrage',
        'command': 'python3 auto_arbitrage_bot.py',
        'log': 'arbitrage_bot_restart.log',
        'status': '❌ NOT RUNNING',
        'pid': None
    },
    {
        'id': 'market_maker',
        'name': 'Market Maker Analyzer',
        'file': 'market_maker_analyzer.py',
        'description': 'Market making viability analysis',
        'command': 'python3 market_maker_analyzer.py',
        'log': 'market_maker.log',
        'status': '❌ NOT RUNNING',
        'pid': None
    },
    {
        'id': 'practical_profit',
        'name': 'Practical Profit Bot',
        'file': 'practical_profit_bot.py',
        'description': 'Made $5.08 real profit (63 trades)',
        'command': 'python3 practical_profit_bot.py',
        'log': 'practical_profit_output.log',
        'profit': 5.08,
        'trades': 63,
        'status': '❌ NOT RUNNING',
        'pid': None
    },
    {
        'id': 'multi_llm',
        'name': 'Multi-LLM Trading Bot',
        'file': 'multi_llm_trading_bot_fixed_order.py',
        'description': 'LLM consensus voting (DeepSeek + Ollama)',
        'command': 'python3 multi_llm_trading_bot_fixed_order.py',
        'log': 'multi_llm_trading.log',
        'capital': 'Gemini $434.35, Binance $36.70',
        'status': '❌ NOT RUNNING',
        'pid': None
    }
]

def check_running():
    """Check which bots are running"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        for bot in BOTS:
            bot['status'] = '❌ NOT RUNNING'
            bot['pid'] = None
            
            if bot['file'] in result.stdout:
                for line in result.stdout.split('\n'):
                    if bot['file'] in line:
                        parts = line.split()
                        if len(parts) > 1:
                            bot['status'] = '✅ RUNNING'
                            bot['pid'] = parts[1]
                            break
    except Exception as e:
        print(f"Error checking processes: {e}")

def start_bot(bot_id):
    """Start a specific bot"""
    for bot in BOTS:
        if bot['id'] == bot_id:
            try:
                # Start the bot
                process = subprocess.Popen(
                    bot['command'].split(),
                    stdout=open(bot['log'], 'a'),
                    stderr=subprocess.STDOUT,
                    start_new_session=True
                )
                
                # Wait and check if it started
                time.sleep(2)
                check_running()
                
                # Check if now running
                for updated_bot in BOTS:
                    if updated_bot['id'] == bot_id and updated_bot['status'] == '✅ RUNNING':
                        return {'success': True, 'message': f'{bot["name"]} started successfully!', 'pid': updated_bot['pid']}
                
                return {'success': False, 'message': 'Bot started but not detected as running'}
                
            except Exception as e:
                return {'success': False, 'message': f'Error: {str(e)}'}
    
    return {'success': False, 'message': 'Bot not found'}

@app.route('/')
def dashboard():
    """Main dashboard"""
    check_running()
    
    # Count running systems
    running = sum(1 for bot in BOTS if bot['status'] == '✅ RUNNING')
    total = len(BOTS)
    
    # Calculate total profit
    total_profit = sum(bot.get('profit', 0) for bot in BOTS)
    
    # Get forex balance
    forex_balance = next((bot.get('balance', 0) for bot in BOTS if bot['id'] == 'forex'), 0)
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>⚖️ PROACTIVE TRADING DASHBOARD</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #0f172a; color: #e2e8f0; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ text-align: center; margin-bottom: 30px; padding: 20px; background: #1e293b; border-radius: 10px; }}
            .header h1 {{ margin: 0; color: #60a5fa; font-size: 2.5em; }}
            .header p {{ margin: 10px 0 0; color: #94a3b8; }}
            .card {{ background: #1e293b; padding: 20px; margin-bottom: 20px; border-radius: 10px; border-left: 5px solid #3b82f6; }}
            .card h2 {{ margin-top: 0; color: #60a5fa; border-bottom: 2px solid #334155; padding-bottom: 10px; }}
            .systems-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
            .system-card {{ background: #334155; padding: 15px; border-radius: 8px; }}
            .system-name {{ font-weight: bold; font-size: 1.2em; color: #f8fafc; margin-bottom: 5px; }}
            .system-status {{ margin: 10px 0; }}
            .running {{ color: #10b981; font-weight: bold; }}
            .stopped {{ color: #ef4444; font-weight: bold; }}
            .profit {{ color: #10b981; font-weight: bold; }}
            .action-buttons {{ margin-top: 15px; }}
            .btn {{ padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; margin-right: 10px; }}
            .btn-start {{ background: #10b981; color: white; }}
            .btn-stop {{ background: #ef4444; color: white; }}
            .btn:hover {{ opacity: 0.9; }}
            .refresh-info {{ text-align: center; margin-top: 30px; padding: 15px; background: #1e293b; border-radius: 10px; }}
            .refresh-btn {{ padding: 10px 20px; background: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; }}
            .refresh-btn:hover {{ background: #2563eb; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat-item {{ text-align: center; padding: 15px; background: #334155; border-radius: 8px; min-width: 150px; }}
            .stat-value {{ font-size: 1.5em; font-weight: bold; color: #60a5fa; }}
            .stat-label {{ color: #94a3b8; margin-top: 5px; }}
        </style>
        <script>
            function startBot(botId) {{
                if (!confirm('Start this bot?')) return;
                
                fetch('/start/' + botId)
                    .then(response => response.json())
                    .then(data => {{
                        alert(data.message);
                        if (data.success) {{
                            setTimeout(() => location.reload(), 2000);
                        }}
                    }})
                    .catch(error => {{
                        alert('Error: ' + error);
                    }});
            }}
            
            function refreshDashboard() {{
                location.reload();
            }}
            
            // Auto-refresh every 5 minutes
            setTimeout(function() {{
                location.reload();
            }}, 300000);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚖️ PROACTIVE TRADING DASHBOARD</h1>
                <p>Monitor and START trading bots directly • Auto-refresh every 5 minutes</p>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{running}/{total}</div>
                    <div class="stat-label">Systems Running</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${total_profit:.2f}</div>
                    <div class="stat-label">Crypto Profit</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${forex_balance:.2f}</div>
                    <div class="stat-label">Forex Balance</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{datetime.now().strftime('%H:%M:%S')}</div>
                    <div class="stat-label">Last Update</div>
                </div>
            </div>
            
            <div class="card">
                <h2>🤖 TRADING SYSTEMS (Click START to launch)</h2>
                <div class="systems-grid">
    '''
    
    for bot in BOTS:
        is_running = bot['status'] == '✅ RUNNING'
        html += f'''
                    <div class="system-card">
                        <div class="system-name">{bot['name']}</div>
                        <div class="system-status {'running' if is_running else 'stopped'}">
                            {bot['status']}
                            {f"<span style='color: #94a3b8; font-size: 0.9em;'> (PID: {bot['pid']})</span>" if bot['pid'] else ''}
                        </div>
                        <div style="margin: 10px 0; color: #cbd5e1;">{bot['description']}</div>
        '''
        
        if 'profit' in bot:
            html += f'''<div class="profit">💰 Profit: ${bot['profit']:.2f}</div>'''
        
        if 'balance' in bot:
            html += f'''<div class="profit" style="color: #fbbf24;">💰 Balance: ${bot['balance']:.2f}</div>'''
        
        if 'trades' in bot:
            html += f'''<div style="color: #94a3b8;">📊 Trades: {bot['trades']}</div>'''
        
        if 'capital' in bot:
            html += f'''<div style="color: #94a3b8;">💼 Capital: {bot['capital']}</div>'''
        
        html += f'''
                        <div class="action-buttons">
                            {'' if is_running else f'<button class="btn btn-start" onclick="startBot(\'{bot["id"]}\')">▶️ START NOW</button>'}
                            {f'<button class="btn btn-stop" onclick="alert(\'Stop feature coming soon\')">⏹️ Stop</button>' if is_running else ''}
                        </div>
                        <div style="margin-top: 10px; font-size: 0.9em; color: #64748b;">
                            File: {bot['file']}
                        </div>
                    </div>
        '''
    
    html += '''
                </div>
            </div>
            
            <div class="refresh-info">
                <button class="refresh-btn" onclick="refreshDashboard()">🔄 Refresh Now</button>
                <p style="margin-top: 10px; color: #94a3b8;">
                    Last updated: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ''' (Asia/Bangkok)<br>
                    Auto-refresh in 5 minutes
                </p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return html

@app.route('/start/<bot_id>')
def start_bot_endpoint(bot_id):
    """API endpoint to start a bot"""
    result = start_bot(bot_id)
    return jsonify(result)

@app.route('/status')
def status_api():
    """API endpoint for bot status"""
    check_running()
    return jsonify(BOTS)

if __name__ == '__main__':
    print("🚀 Starting Proactive Trading Dashboard...")
    print("🌐 Dashboard available at: http://localhost:5021")
    print("▶️  You can START bots directly from the web interface!")
    print("🔄 Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5021, debug=False)