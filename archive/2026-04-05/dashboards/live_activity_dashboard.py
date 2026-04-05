#!/usr/bin/env python3
"""
LIVE ACTIVITY TRADING DASHBOARD
Shows real-time activity for each trading bot
Click on any bot to see exactly what it's doing right now
"""

import os
import json
import subprocess
import time
import re
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Bot configurations with activity tracking
BOTS = [
    {
        'id': 'forex',
        'name': '💰 FOREX Arbitration Bot',
        'file': 'forex_bot_with_schwab.py',
        'log': 'active_forex_trading.log',
        'status': '❌ NOT RUNNING',
        'pid': None,
        'activity': 'No recent activity',
        'last_action': 'Never',
        'current_pair': 'None',
        'profit': 0.0,
        'trades': 0,
        'balance': 220.00
    },
    {
        'id': 'arbitrage',
        'name': 'Auto Arbitrage Bot',
        'file': 'auto_arbitrage_bot.py',
        'log': 'arbitrage_bot_restart.log',
        'status': '❌ NOT RUNNING',
        'pid': None,
        'activity': 'No recent activity',
        'last_action': 'Never',
        'current_pair': 'None',
        'opportunities': 0,
        'spread': '0.00%'
    },
    {
        'id': 'practical_profit',
        'name': 'Practical Profit Bot',
        'file': 'practical_profit_bot.py',
        'log': 'practical_profit_output.log',
        'status': '❌ NOT RUNNING',
        'pid': None,
        'activity': 'No recent activity',
        'last_action': 'Never',
        'current_pair': 'MANA/USD',
        'profit': 5.08,
        'trades': 63,
        'last_trade': 'Unknown'
    },
    {
        'id': 'multi_llm',
        'name': 'Multi-LLM Trading Bot',
        'file': 'multi_llm_trading_bot_fixed_order.py',
        'log': 'multi_llm_trading.log',
        'status': '❌ NOT RUNNING',
        'pid': None,
        'activity': 'No recent activity',
        'last_action': 'Never',
        'current_pair': 'Multiple',
        'llm_votes': '0/0',
        'consensus': 'No decision'
    }
]

def get_recent_activity(log_file, lines=10):
    """Get recent activity from log file"""
    if not os.path.exists(log_file):
        return ["Log file not found"]
    
    try:
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            return all_lines[-lines:] if len(all_lines) > lines else all_lines
    except:
        return ["Error reading log"]

def parse_forex_activity(lines):
    """Parse Forex bot activity"""
    activity = "Idle"
    last_action = "Unknown"
    current_pair = "None"
    profit = 0.0
    trades = 0
    
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
            
        # Extract timestamp
        if ' - INFO - ' in line:
            timestamp = line.split(' - INFO - ')[0]
            message = line.split(' - INFO - ')[1]
            
            # Look for trading activity
            if 'EXECUTING TRADE' in message or 'TRADE WON' in message or 'TRADE LOST' in message:
                activity = message
                last_action = timestamp
                
                # Extract currency pair
                if 'EUR/USD' in message:
                    current_pair = 'EUR/USD'
                elif 'USD/JPY' in message:
                    current_pair = 'USD/JPY'
                elif 'AUD/USD' in message:
                    current_pair = 'AUD/USD'
                elif 'GBP/USD' in message:
                    current_pair = 'GBP/USD'
            
            # Extract profit
            elif 'profit:' in message.lower() and '$' in message:
                match = re.search(r'\$([0-9]+\.[0-9]+)', message)
                if match:
                    profit = float(match.group(1))
            
            # Extract trade count
            elif 'trades executed:' in message.lower():
                match = re.search(r'(\d+)', message)
                if match:
                    trades = int(match.group(1))
    
    return {
        'activity': activity,
        'last_action': last_action,
        'current_pair': current_pair,
        'profit': profit,
        'trades': trades
    }

def parse_arbitrage_activity(lines):
    """Parse Arbitrage bot activity"""
    activity = "Scanning"
    last_action = "Unknown"
    opportunities = 0
    spread = "0.00%"
    
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
            
        if ' - INFO - ' in line:
            timestamp = line.split(' - INFO - ')[0]
            message = line.split(' - INFO - ')[1]
            
            if 'ARBITRAGE FOUND' in message or 'Executing arbitrage' in message:
                activity = message
                last_action = timestamp
                
                # Extract spread
                if '%' in message:
                    match = re.search(r'(\d+\.\d+)%', message)
                    if match:
                        spread = f"{match.group(1)}%"
            
            elif 'opportunities:' in message.lower():
                match = re.search(r'(\d+)', message)
                if match:
                    opportunities = int(match.group(1))
    
    return {
        'activity': activity,
        'last_action': last_action,
        'opportunities': opportunities,
        'spread': spread
    }

def parse_practical_activity(lines):
    """Parse Practical Profit bot activity"""
    activity = "Monitoring"
    last_action = "Unknown"
    last_trade = "Unknown"
    
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
            
        if ' - INFO - ' in line:
            timestamp = line.split(' - INFO - ')[0]
            message = line.split(' - INFO - ')[1]
            
            if 'BUY' in message or 'SELL' in message or 'TRADE' in message:
                activity = message
                last_action = timestamp
                last_trade = message
            
            elif 'Profit:' in message and 'Trades:' in message:
                # This is a summary line
                activity = "Active trading"
    
    return {
        'activity': activity,
        'last_action': last_action,
        'last_trade': last_trade
    }

def parse_llm_activity(lines):
    """Parse LLM bot activity"""
    activity = "Analyzing"
    last_action = "Unknown"
    llm_votes = "0/0"
    consensus = "No decision"
    
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
            
        if ' - INFO - ' in line:
            timestamp = line.split(' - INFO - ')[0]
            message = line.split(' - INFO - ')[1]
            
            if 'LLM VOTE' in message or 'CONSENSUS' in message or 'Executing trade' in message:
                activity = message
                last_action = timestamp
                
                # Extract votes
                if 'votes:' in message.lower():
                    match = re.search(r'(\d+)/(\d+)', message)
                    if match:
                        llm_votes = f"{match.group(1)}/{match.group(2)}"
                
                # Extract consensus
                if 'BUY' in message or 'SELL' in message or 'HOLD' in message:
                    consensus = message.split(':')[-1].strip()
    
    return {
        'activity': activity,
        'last_action': last_action,
        'llm_votes': llm_votes,
        'consensus': consensus
    }

def update_bot_activities():
    """Update activity for all bots"""
    for bot in BOTS:
        # Check if running
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if bot['file'] in result.stdout:
                for line in result.stdout.split('\n'):
                    if bot['file'] in line:
                        parts = line.split()
                        if len(parts) > 1:
                            bot['status'] = '✅ RUNNING'
                            bot['pid'] = parts[1]
                            break
            else:
                bot['status'] = '❌ NOT RUNNING'
                bot['pid'] = None
        except:
            bot['status'] = '❌ ERROR CHECKING'
        
        # Get recent activity
        log_lines = get_recent_activity(bot['log'], 20)
        
        # Parse activity based on bot type
        if bot['id'] == 'forex':
            activity_info = parse_forex_activity(log_lines)
            bot.update(activity_info)
            
        elif bot['id'] == 'arbitrage':
            activity_info = parse_arbitrage_activity(log_lines)
            bot.update(activity_info)
            
        elif bot['id'] == 'practical_profit':
            activity_info = parse_practical_activity(log_lines)
            bot.update(activity_info)
            
        elif bot['id'] == 'multi_llm':
            activity_info = parse_llm_activity(log_lines)
            bot.update(activity_info)
        
        # If no recent activity found, show generic status
        if bot['activity'] == 'No recent activity' and log_lines and len(log_lines) > 0:
            last_line = log_lines[-1].strip()
            if ' - INFO - ' in last_line:
                bot['activity'] = last_line.split(' - INFO - ')[1]
                bot['last_action'] = last_line.split(' - INFO - ')[0]

@app.route('/')
def dashboard():
    """Main dashboard"""
    update_bot_activities()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎯 LIVE TRADING ACTIVITY DASHBOARD</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #0f172a; color: #e2e8f0; }
            .container { max-width: 1400px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; padding: 20px; background: #1e293b; border-radius: 10px; }
            .header h1 { margin: 0; color: #60a5fa; font-size: 2.5em; }
            .header p { margin: 10px 0 0; color: #94a3b8; }
            .systems-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(600px, 1fr)); gap: 20px; }
            .system-card { background: #1e293b; padding: 20px; border-radius: 10px; border-left: 5px solid #3b82f6; }
            .system-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
            .system-name { font-weight: bold; font-size: 1.3em; color: #f8fafc; }
            .system-status { font-weight: bold; padding: 5px 10px; border-radius: 5px; }
            .status-running { background: #10b981; color: white; }
            .status-stopped { background: #ef4444; color: white; }
            .activity-section { background: #334155; padding: 15px; border-radius: 8px; margin: 15px 0; }
            .activity-title { color: #60a5fa; font-weight: bold; margin-bottom: 10px; }
            .activity-text { color: #cbd5e1; font-family: monospace; white-space: pre-wrap; }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 15px 0; }
            .metric { background: #334155; padding: 10px; border-radius: 5px; text-align: center; }
            .metric-label { color: #94a3b8; font-size: 0.9em; }
            .metric-value { color: #60a5fa; font-weight: bold; font-size: 1.1em; }
            .log-section { max-height: 200px; overflow-y: auto; background: #0f172a; padding: 10px; border-radius: 5px; margin-top: 10px; }
            .log-line { font-family: monospace; font-size: 0.9em; color: #94a3b8; border-bottom: 1px solid #334155; padding: 3px 0; }
            .timestamp { color: #f59e0b; }
            .info { color: #60a5fa; }
            .success { color: #10b981; }
            .warning { color: #f59e0b; }
            .error { color: #ef4444; }
            .refresh-btn { padding: 10px 20px; background: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; margin-top: 20px; }
            .refresh-btn:hover { background: #2563eb; }
        </style>
        <script>
            function refreshDashboard() {
                location.reload();
            }
            
            function toggleLogs(botId) {
                const logSection = document.getElementById('logs-' + botId);
                if (logSection.style.display === 'none') {
                    logSection.style.display = 'block';
                } else {
                    logSection.style.display = 'none';
                }
            }
            
            // Auto-refresh every 30 seconds
            setTimeout(function() {
                location.reload();
            }, 30000);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 LIVE TRADING ACTIVITY DASHBOARD</h1>
                <p>See exactly what each bot is doing right now • Auto-refresh every 30 seconds</p>
                <button class="refresh-btn" onclick="refreshDashboard()">🔄 Refresh Now</button>
            </div>
            
            <div class="systems-grid">
    '''
    
    for bot in BOTS:
        is_running = bot['status'] == '✅ RUNNING'
        
        html += f'''
                <div class="system-card">
                    <div class="system-header">
                        <a href="/bot_details.html?bot={bot['id']}" target="_blank" style="text-decoration: none; color: inherit;">
                            <div class="system-name" style="cursor: pointer; color: #60a5fa;">
                                {bot['name']} <span style="font-size: 0.8em; color: #94a3b8;">↗</span>
                            </div>
                        </a>
                        <div class="system-status {'status-running' if is_running else 'status-stopped'}">
                            {bot['status']} {f"(PID: {bot['pid']})" if bot['pid'] else ''}
                        </div>
                    </div>
                    
                    <div class="activity-section">
                        <div class="activity-title">📊 CURRENT ACTIVITY</div>
                        <div class="activity-text">{bot['activity']}</div>
                        <div style="color: #94a3b8; font-size: 0.9em; margin-top: 5px;">
                            Last action: {bot['last_action']}
                        </div>
                    </div>
                    
                    <div class="metrics-grid">
        '''
        
        # Add metrics based on bot type
        if bot['id'] == 'forex':
            html += f'''
                        <div class="metric">
                            <div class="metric-label">Current Pair</div>
                            <div class="metric-value">{bot['current_pair']}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Profit</div>
                            <div class="metric-value" style="color: #10b981;">${bot['profit']:.2f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Trades</div>
                            <div class="metric-value">{bot['trades']}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Balance</div>
                            <div class="metric-value" style="color: #fbbf24;">${bot['balance']:.2f}</div>
                        </div>
            '''
        
        elif bot['id'] == 'arbitrage':
            html += f'''
                        <div class="metric">
                            <div class="metric-label">Opportunities</div>
                            <div class="metric-value">{bot['opportunities']}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Best Spread</div>
                            <div class="metric-value" style="color: #10b981;">{bot['spread']}</div>
                        </div>
            '''
        
        elif bot['id'] == 'practical_profit':
            html += f'''
                        <div class="metric">
                            <div class="metric-label">Current Pair</div>
                            <div class="metric-value">{bot['current_pair']}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Total Profit</div>
                            <div class="metric-value" style="color: #10b981;">${bot['profit']:.2f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Total Trades</div>
                            <div class="metric-value">{bot['trades']}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Last Trade</div>
                            <div class="metric-value">{bot['last_trade'][:30]}{'...' if len(bot['last_trade']) > 30 else ''}</div>
                        </div>
            '''
        
        elif bot['id'] == 'multi_llm':
            html += f'''
                        <div class="metric">
                            <div class="metric-label">LLM Votes</div>
                            <div class="metric-value">{bot['llm_votes']}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Consensus</div>
                            <div class="metric-value">{bot['consensus'][:20]}{'...' if len(bot['consensus']) > 20 else ''}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Current Pair</div>
                            <div class="metric-value">{bot['current_pair']}</div>
                        </div>
            '''
        
        html += '''
                    </div>
                    
                    <button onclick="toggleLogs(''' + "'" + bot['id'] + "'" + ''')" style="padding: 5px 10px; background: #334155; color: #94a3b8; border: none; border-radius: 3px; cursor: pointer; font-size: 0.9em; margin-top: 10px;">
                        📝 Show Recent Logs
                    </button>
                    
                    <div id="logs-''' + bot['id'] + '''" class="log-section" style="display: none;">
        '''
        
        # Add recent logs
        log_lines = get_recent_activity(bot['log'], 15)
        for line in log_lines:
            line = line.strip()
            if line:
                # Color code log lines
                line_class = 'log-line'
                if 'ERROR' in line or 'FAILED' in line:
                    line_class += ' error'
                elif 'SUCCESS' in line or 'WON' in line or 'profit' in line.lower():
                    line_class += ' success'
                elif 'WARNING' in line or 'CAUTION' in line:
                    line_class += ' warning'
                elif 'INFO' in line:
                    line_class += ' info'
                
                html += f'<div class="{line_class}">{line}</div>\n'
        
        html += '''
                    </div>
                    
                    <div style="margin-top: 15px; font-size: 0.9em; color: #64748b;">
                        File: ''' + bot['file'] + '''<br>
                        Log: ''' + bot['log'] + '''
                    </div>
                </div>
        '''
    
    html += '''
            </div>
            
            <div style="text-align: center; margin-top: 30px; color: #94a3b8;">
                Last updated: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ''' (Asia/Bangkok)<br>
                Auto-refresh in 30 seconds
            </div>
        </div>
    </body>
    </html>
    '''
    
    return html

@app.route('/api/activity/<bot_id>')
def get_activity(bot_id):
    """API endpoint to get activity for a specific bot"""
    update_bot_activities()
    for bot in BOTS:
        if bot['id'] == bot_id:
            return jsonify(bot)
    return jsonify({'error': 'Bot not found'}), 404

@app.route('/api/all_activity')
def get_all_activity():
    """API endpoint to get all bot activities"""
    update_bot_activities()
    return jsonify(BOTS)

@app.route('/api/bot/<bot_id>/status')
def get_bot_status(bot_id):
    """API endpoint for control UI to get bot real-time status"""
    update_bot_activities()
    for bot in BOTS:
        if bot['id'] == bot_id:
            # Format response for control UI
            return jsonify({
                'id': bot['id'],
                'name': bot['name'],
                'status': bot['status'],
                'pid': bot['pid'],
                'activity': bot['activity'],
                'last_action': bot['last_action'],
                'real_time': True,
                'timestamp': datetime.now().isoformat()
            })
    return jsonify({'error': 'Bot not found'}), 404

@app.route('/api/bots/summary')
def get_bots_summary():
    """API endpoint for control UI to get all bots summary"""
    update_bot_activities()
    summary = []
    for bot in BOTS:
        summary.append({
            'id': bot['id'],
            'name': bot['name'],
            'status': bot['status'],
            'pid': bot['pid'],
            'activity': bot['activity'][:50] + '...' if len(bot['activity']) > 50 else bot['activity']
        })
    return jsonify(summary)

@app.route('/bot_details.html')
def bot_details_page():
    """Serve the bot details HTML page"""
    bot_id = request.args.get('bot', 'forex')
    
    # Read the HTML file
    try:
        with open('bot_details.html', 'r') as f:
            html_content = f.read()
        
        # Update the page title with bot name
        update_bot_activities()
        bot_name = 'Unknown Bot'
        for bot in BOTS:
            if bot['id'] == bot_id:
                bot_name = bot['name']
                break
        
        html_content = html_content.replace('<title>Bot Real-Time Details</title>', 
                                           f'<title>Real-Time: {bot_name}</title>')
        
        return html_content
    except FileNotFoundError:
        return 'Bot details page not found. Please check if bot_details.html exists.', 404

if __name__ == '__main__':
    print("🎯 Starting Live Activity Trading Dashboard...")
    print("🌐 Dashboard available at: http://localhost:5022")
    print("📊 Shows real-time activity for each bot")
    print("🔄 Auto-refresh every 30 seconds")
    print("🛑 Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5022, debug=False)