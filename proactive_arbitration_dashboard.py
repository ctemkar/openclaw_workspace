#!/usr/bin/env python3
"""
PROACTIVE ARBITRATION TRADING SYSTEM DASHBOARD
Shows LIVE arbitration trading systems with 5-minute refresh
AND can auto-restart stopped bots with user confirmation
"""

import os
import json
import subprocess
import threading
import time
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Configuration for each bot
BOT_CONFIGS = {
    'forex': {
        'name': '💰 FOREX Arbitration Bot',
        'file': 'forex_bot_with_schwab.py',
        'backup_file': 'active_forex_trader.py',
        'description': 'Schwab Account #13086459 • $220 Balance',
        'command': 'python3 forex_bot_with_schwab.py',
        'log_file': 'active_forex_trading.log',
        'auto_restart': False,  # Set to True for auto-restart
        'max_restarts': 3,
        'restart_delay': 60  # seconds
    },
    'arbitrage': {
        'name': 'Auto Arbitrage Bot',
        'file': 'auto_arbitrage_bot.py',
        'description': 'Gemini vs Binance arbitrage',
        'command': 'python3 auto_arbitrage_bot.py',
        'log_file': 'arbitrage_bot_restart.log',
        'auto_restart': False,
        'max_restarts': 3,
        'restart_delay': 60
    },
    'market_maker': {
        'name': 'Market Maker Analyzer',
        'file': 'market_maker_analyzer.py',
        'description': 'Market making viability analysis',
        'command': 'python3 market_maker_analyzer.py',
        'log_file': 'market_maker.log',
        'auto_restart': False,
        'max_restarts': 3,
        'restart_delay': 60
    },
    'practical_profit': {
        'name': 'Practical Profit Bot',
        'file': 'practical_profit_bot.py',
        'description': 'Made $5.08 real profit (63 trades)',
        'command': 'python3 practical_profit_bot.py',
        'log_file': 'practical_profit_output.log',
        'auto_restart': False,
        'max_restarts': 3,
        'restart_delay': 60
    },
    'multi_llm': {
        'name': 'Multi-LLM Trading Bot',
        'file': 'multi_llm_trading_bot_fixed_order.py',
        'description': 'LLM consensus voting (DeepSeek + Ollama)',
        'command': 'python3 multi_llm_trading_bot_fixed_order.py',
        'log_file': 'multi_llm_trading.log',
        'auto_restart': False,
        'max_restarts': 3,
        'restart_delay': 60
    }
}

# Track restart attempts
restart_history = {}

def check_bot_running(bot_key):
    """Check if a bot is running"""
    config = BOT_CONFIGS[bot_key]
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        # Check primary file
        if config['file'] in result.stdout:
            for line in result.stdout.split('\n'):
                if config['file'] in line:
                    parts = line.split()
                    if len(parts) > 1:
                        return {'running': True, 'pid': parts[1]}
        
        # Check backup file if exists
        if 'backup_file' in config and config['backup_file'] in result.stdout:
            for line in result.stdout.split('\n'):
                if config['backup_file'] in line:
                    parts = line.split()
                    if len(parts) > 1:
                        return {'running': True, 'pid': parts[1], 'using_backup': True}
        
        return {'running': False}
    except Exception as e:
        return {'running': False, 'error': str(e)}

def get_bot_status(bot_key):
    """Get detailed status for a bot"""
    config = BOT_CONFIGS[bot_key]
    status = check_bot_running(bot_key)
    
    bot_info = {
        'key': bot_key,
        'name': config['name'],
        'file': config['file'],
        'description': config['description'],
        'status': '✅ RUNNING' if status.get('running') else '❌ NOT RUNNING',
        'auto_restart': config['auto_restart']
    }
    
    if status.get('running'):
        bot_info['pid'] = status.get('pid')
        if status.get('using_backup'):
            bot_info['status'] = '✅ RUNNING (Backup)'
    
    # Add specific data for each bot type
    if bot_key == 'forex':
        bot_info['balance'] = 220.00
        bot_info['account'] = 'Schwab #13086459'
        
        # Try to get actual balance from log
        if os.path.exists(config['log_file']):
            try:
                with open(config['log_file'], 'r') as f:
                    lines = f.readlines()
                    for line in reversed(lines[-20:]):
                        if 'balance:' in line.lower() and '$' in line:
                            import re
                            balance_match = re.search(r'\$([0-9]+\.[0-9]+)', line)
                            if balance_match:
                                bot_info['balance'] = float(balance_match.group(1))
                                break
            except:
                pass
    
    elif bot_key == 'practical_profit':
        bot_info['total_profit'] = 5.08  # Updated from logs
        bot_info['total_trades'] = 63     # Updated from logs
        
        # Try to get actual profit from log
        if os.path.exists('practical_profits.log'):
            try:
                with open('practical_profits.log', 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        if 'Total:' in last_line:
                            profit_match = re.search(r'Total: \$([0-9]+\.[0-9]+)', last_line)
                            if profit_match:
                                bot_info['total_profit'] = float(profit_match.group(1))
            except:
                pass
    
    elif bot_key == 'multi_llm':
        bot_info['capital'] = 'Gemini $434.35, Binance $36.70'
    
    return bot_info

def start_bot(bot_key):
    """Start a bot"""
    config = BOT_CONFIGS[bot_key]
    
    if bot_key not in restart_history:
        restart_history[bot_key] = {'attempts': 0, 'last_attempt': None}
    
    # Check if we've exceeded max restarts
    if restart_history[bot_key]['attempts'] >= config['max_restarts']:
        return {'success': False, 'message': f'Max restart attempts ({config["max_restarts"]}) exceeded'}
    
    try:
        # Start the bot in background
        import subprocess
        process = subprocess.Popen(
            config['command'].split(),
            stdout=open(config['log_file'], 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        
        restart_history[bot_key]['attempts'] += 1
        restart_history[bot_key]['last_attempt'] = datetime.now().isoformat()
        
        # Wait a moment to check if it started
        time.sleep(2)
        status = check_bot_running(bot_key)
        
        if status.get('running'):
            return {'success': True, 'message': f'Bot started successfully (PID: {status.get("pid")})', 'pid': status.get('pid')}
        else:
            return {'success': False, 'message': 'Bot failed to start - check logs'}
            
    except Exception as e:
        return {'success': False, 'message': f'Error starting bot: {str(e)}'}

def auto_restart_check():
    """Check and auto-restart bots if configured"""
    for bot_key, config in BOT_CONFIGS.items():
        if config['auto_restart']:
            status = check_bot_running(bot_key)
            if not status.get('running'):
                print(f"[AUTO-RESTART] {bot_key} is not running, attempting restart...")
                result = start_bot(bot_key)
                print(f"[AUTO-RESTART] Result: {result}")

@app.route('/')
def dashboard():
    """Main dashboard page"""
    systems = []
    total_profit = 0
    forex_balance = 0
    running_systems = 0
    
    for bot_key in BOT_CONFIGS.keys():
        bot_info = get_bot_status(bot_key)
        systems.append(bot_info)
        
        if bot_info['status'].startswith('✅'):
            running_systems += 1
        
        if 'total_profit' in bot_info:
            total_profit += bot_info['total_profit']
        
        if 'balance' in bot_info:
            forex_balance = bot_info['balance']
    
    system_status = {
        'total_systems': len(BOT_CONFIGS),
        'running_systems': running_systems,
        'total_profit': total_profit,
        'forex_balance': forex_balance,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>⚖️ PROACTIVE ARBITRATION TRADING SYSTEM</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #0f172a; color: #e2e8f0; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; padding: 20px; background: #1e293b; border-radius: 10px; }
            .header h1 { margin: 0; color: #60a5fa; font-size: 2.5em; }
            .header p { margin: 10px 0 0; color: #94a3b8; }
            .card { background: #1e293b; padding: 20px; margin-bottom: 20px; border-radius: 10px; border-left: 5px solid #3b82f6; }
            .card h2 { margin-top: 0; color: #60a5fa; border-bottom: 2px solid #334155; padding-bottom: 10px; }
            .systems-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .system-card { background: #334155; padding: 15px; border-radius: 8px; }
            .system-name { font-weight: bold; font-size: 1.2em; color: #f8fafc; margin-bottom: 5px; }
            .system-status { margin: 10px 0; }
            .running { color: #10b981; font-weight: bold; }
            .stopped { color: #ef4444; font-weight: bold; }
            .profit { color: #10b981; font-weight: bold; }
            .action-buttons { margin-top: 15px; display: flex; gap: 10px; }
            .btn { padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
            .btn-start { background: #10b981; color: white; }
            .btn-stop { background: #ef4444; color: white; }
            .btn-auto { background: #3b82f6; color: white; }
            .btn:hover { opacity: 0.9; }
            .refresh-info { text-align: center; margin-top: 30px; padding: 15px; background: #1e293b; border-radius: 10px; }
            .refresh-btn { padding: 10px 20px; background: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; }
            .refresh-btn:hover { background: #2563eb; }
            .stats { display: flex; justify-content: space-around; margin: 20px 0; }
            .stat-item { text-align: center; padding: 15px; background: #334155; border-radius: 8px; min-width: 150px; }
            .stat-value { font-size: 1.5em; font-weight: bold; color: #60a5fa; }
            .stat-label { color: #94a3b8; margin-top: 5px; }
            .auto-restart-status { margin-top: 10px; font-size: 0.9em; color: #94a3b8; }
            .auto-on { color: #10b981; }
            .auto-off { color: #ef4444; }
        </style>
        <script>
            function refreshDashboard() {
                location.reload();
            }
            
            function startBot(botKey) {
                if (!confirm(`Start ${botKey} bot?`)) return;
                
                fetch(`/start/${botKey}`)
                    .then(response => response.json())
                    .then(data => {
                        alert(data.message);
                        if (data.success) {
                            setTimeout(() => location.reload(), 2000);
                        }
                    })
                    .catch(error => {
                        alert('Error: ' + error);
                    });
            }
            
            function toggleAutoRestart(botKey) {
                fetch(`/toggle_auto/${botKey}`)
                    .then(response => response.json())
                    .then(data => {
                        alert(data.message);
                        location.reload();
                    })
                    .catch(error => {
                        alert('Error: ' + error);
                    });
            }
            
            // Auto-refresh every 5 minutes (300,000 ms)
            setTimeout(function() {
                location.reload();
            }, 300000);
            
            // Update countdown timer
            function updateCountdown() {
                let seconds = 300;
                const timerElement = document.getElementById('countdown');
                if (timerElement) {
                    const interval = setInterval(() => {
                        seconds--;
                        const minutes = Math.floor(seconds / 60);
                        const secs = seconds % 60;
                        timerElement.textContent = `${minutes}:${secs.toString().padStart(2, '0')}`;
                        if (seconds <= 0) {
                            clearInterval(interval);
                            location.reload();
                        }
                    }, 1000);
                }
            }
            document.addEventListener('DOMContentLoaded', updateCountdown);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚖️ PROACTIVE ARBITRATION TRADING SYSTEM</h1>
                <p>Live monitoring with auto-restart capability • Auto-refresh every 5 minutes</p>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{{ system_status.running_systems }}/{{ system_status.total_systems }}</div>
                    <div class="stat-label">Systems Running</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${{ "%.2f"|format(system_status.total_profit) }}</div>
                    <div class="stat-label">Crypto Profit</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${{ "%.2f"|format(system_status.forex_balance) }}</div>
                    <div class="stat-label">Forex Balance</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="countdown">5:00</div>
                    <div class="stat-label">Next Refresh</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ system_status.timestamp.split(' ')[1] }}</div>
                    <div class="stat-label">Last Update</div>
                </div>
            </div>
            
            <div class="card">
                <h2>🤖 ARBITRATION TRADING SYSTEMS (Click to Manage)</h2>
                <div class="systems-grid">
                    {% for system in systems %}
                    <div class="system-card">
                        <div class="system-name">{{ system.name }}</div>
                        <div class="system-status {{ 'running' if 'RUNNING' in system.status else 'stopped' }}">
                            {{ system.status }}
                            {% if system.get('pid') %}
                            <span style="color: #94a3b8; font-size: 0.9em;"> (PID: {{ system.pid }})</span>
                            {% endif %}
                        </div>
                        <div style="margin: 10px 0; color: #cbd5e1;">{{ system.description }}</div>
                        
                        {% if system.get('total_profit') %}
                        <div class="profit">💰 Profit: ${{ "%.2f"|format(system.total_profit) }}</div>
                        {% endif %}
                        {% if system.get('balance') %}
                        <div class="profit" style="color: #fbbf24;">💰 Balance: ${{ "%.2f"|format(system.balance) }}</div>
                        {% endif %}
                        {% if system.get('total_trades') %}
                        <div style="color: #94a3b8;">📊 Trades: {{ system.total_trades }}</div>
                        {% endif %}
                        {% if system.get('capital') %}
                        <div style="color: #94a3b8;">💼 Capital: {{ system.capital }}</div>
                        {% endif %}
                        
                        <div class