#!/usr/bin/env python3
"""
ARBITRATION TRADING SYSTEM DASHBOARD
Shows LIVE arbitration trading systems with 5-minute refresh
"""

import os
import json
import subprocess
from datetime import datetime
from flask import Flask, render_template_string
import time

app = Flask(__name__)

def get_arbitration_systems():
    """Get status of all arbitration trading systems"""
    systems = []
    
    # 1. FOREX ARBITRATION BOT ($220 Schwab Account)
    forex_status = {
        'name': '💰 FOREX Arbitration Bot',
        'file': 'forex_bot_with_schwab.py',
        'description': 'Schwab Account #13086459 • $220 Balance',
        'status': '❌ NOT RUNNING',
        'balance': 220.00,
        'account': 'Schwab #13086459',
        'last_active': 'Unknown'
    }
    
    # Check if Forex bot is running
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'forex_bot_with_schwab.py' in result.stdout:
            forex_status['status'] = '✅ RUNNING'
            # Extract PID
            for line in result.stdout.split('\n'):
                if 'forex_bot_with_schwab.py' in line:
                    parts = line.split()
                    if len(parts) > 1:
                        forex_status['pid'] = parts[1]
                        
            # Check log for last activity
            if os.path.exists('forex_trading_with_schwab.log'):
                with open('forex_trading_with_schwab.log', 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1]
                        if 'Waiting' in last_line or 'scan' in last_line:
                            forex_status['last_active'] = 'Recently active'
    except:
        pass
    
    systems.append(forex_status)
    
    # 2. Auto Arbitrage Bot (Crypto)
    arbitrage_status = {
        'name': 'Auto Arbitrage Bot',
        'file': 'auto_arbitrage_bot.py',
        'description': 'Gemini vs Binance arbitrage',
        'status': '❌ NOT RUNNING',
        'profit': 0.0,
        'trades': 0,
        'last_active': 'Unknown'
    }
    
    # Check if running
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'auto_arbitrage_bot.py' in result.stdout:
            arbitrage_status['status'] = '✅ RUNNING'
            # Extract PID
            for line in result.stdout.split('\n'):
                if 'auto_arbitrage_bot.py' in line:
                    parts = line.split()
                    if len(parts) > 1:
                        arbitrage_status['pid'] = parts[1]
        else:
            arbitrage_status['status'] = '❌ NOT RUNNING'
    except:
        pass
    
    systems.append(arbitrage_status)
    
    # 2. Market Maker Analyzer
    maker_status = {
        'name': 'Market Maker Analyzer',
        'file': 'market_maker_analyzer.py',
        'description': 'Market making viability analysis',
        'status': '❌ NOT RUNNING',
        'spreads': 'Unknown',
        'opportunities': 0
    }
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'market_maker_analyzer.py' in result.stdout:
            maker_status['status'] = '✅ RUNNING'
            for line in result.stdout.split('\n'):
                if 'market_maker_analyzer.py' in line:
                    parts = line.split()
                    if len(parts) > 1:
                        maker_status['pid'] = parts[1]
    except:
        pass
    
    systems.append(maker_status)
    
    # 3. Practical Profit Bot (PROVEN - made $2.60)
    profit_status = {
        'name': 'Practical Profit Bot',
        'file': 'practical_profit_bot.py',
        'description': 'Made $2.60 real profit (35 trades)',
        'status': '❌ NOT RUNNING',
        'total_profit': 2.60,
        'total_trades': 35,
        'win_rate': 'High (proven)'
    }
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'practical_profit_bot.py' in result.stdout:
            profit_status['status'] = '✅ RUNNING'
            for line in result.stdout.split('\n'):
                if 'practical_profit_bot.py' in line:
                    parts = line.split()
                    if len(parts) > 1:
                        profit_status['pid'] = parts[1]
    except:
        pass
    
    systems.append(profit_status)
    
    # 4. Multi-LLM Trading Bot
    llm_status = {
        'name': 'Multi-LLM Trading Bot',
        'file': 'multi_llm_trading_bot_fixed_order.py',
        'description': 'LLM consensus voting (DeepSeek + Ollama)',
        'status': '❌ NOT RUNNING',
        'capital': 'Gemini $434.35, Binance $36.70',
        'activity': 'Processing cryptos'
    }
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'multi_llm_trading_bot_fixed_order.py' in result.stdout:
            llm_status['status'] = '✅ RUNNING'
            for line in result.stdout.split('\n'):
                if 'multi_llm_trading_bot_fixed_order.py' in line:
                    parts = line.split()
                    if len(parts) > 1:
                        llm_status['pid'] = parts[1]
    except:
        pass
    
    systems.append(llm_status)
    
    return systems

def get_system_status():
    """Get overall system status"""
    # Calculate total investment (Forex + Crypto)
    total_investment = 220.00  # Forex
    total_investment += 2.60   # Crypto profit
    
    return {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'timezone': 'Asia/Bangkok (GMT+7)',
        'refresh_interval': '5 minutes',
        'total_systems': 5,  # Now includes Forex
        'running_systems': 0,
        'total_profit': 2.60,
        'total_investment': total_investment,
        'forex_balance': 220.00
    }

def get_live_opportunities():
    """Get live arbitrage opportunities"""
    opportunities = []
    
    # 1. Check Forex opportunities first
    if os.path.exists('forex_opportunities.json'):
        try:
            with open('forex_opportunities.json', 'r') as f:
                forex_data = json.load(f)
                if isinstance(forex_data, list):
                    for opp in forex_data[:3]:  # Show first 3 Forex opportunities
                        if isinstance(opp, dict):
                            opportunities.append({
                                'type': '💰 FOREX',
                                'pair': opp.get('pair', 'Unknown'),
                                'spread': f"{opp.get('spread_pips', 0)} pips",
                                'profit_potential': opp.get('potential_profit', 0),
                                'brokers': f"{opp.get('buy_broker', '?')} → {opp.get('sell_broker', '?')}"
                            })
        except:
            pass
    
    # 2. Check crypto opportunities
    opportunity_files = [
        'arbitrage_opportunities.json',
        'market_making_opportunities.json',
        'trading_signals.json'
    ]
    
    for file in opportunity_files:
        if os.path.exists(file):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        for opp in data[:2]:  # Show first 2 crypto opportunities
                            if isinstance(opp, dict):
                                opportunities.append({
                                    'type': '⚡ CRYPTO',
                                    'pair': opp.get('pair', opp.get('symbol', 'Unknown')),
                                    'spread': f"{opp.get('spread', opp.get('spread_percent', 0))}%",
                                    'profit_potential': opp.get('profit_potential', opp.get('potential_profit', 0)),
                                    'exchange': opp.get('exchange', 'Unknown')
                                })
            except:
                pass
    
    return opportunities[:6]  # Return max 6 opportunities

@app.route('/')
def dashboard():
    """Main dashboard page"""
    
    # Get all status information
    systems = get_arbitration_systems()
    system_status = get_system_status()
    opportunities = get_live_opportunities()
    
    # Count running systems
    running_count = sum(1 for s in systems if 'RUNNING' in s['status'])
    system_status['running_systems'] = running_count
    
    # HTML template
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>⚖️ ARBITRATION TRADING SYSTEM</title>
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
            .opportunity { background: #1e293b; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #f59e0b; }
            .refresh-info { text-align: center; margin-top: 30px; padding: 15px; background: #1e293b; border-radius: 10px; }
            .refresh-btn { padding: 10px 20px; background: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; }
            .refresh-btn:hover { background: #2563eb; }
            .stats { display: flex; justify-content: space-around; margin: 20px 0; }
            .stat-item { text-align: center; padding: 15px; background: #334155; border-radius: 8px; min-width: 150px; }
            .stat-value { font-size: 1.5em; font-weight: bold; color: #60a5fa; }
            .stat-label { color: #94a3b8; margin-top: 5px; }
        </style>
        <script>
            function refreshDashboard() {
                location.reload();
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
                <h1>⚖️ ARBITRATION TRADING SYSTEM</h1>
                <p>Live monitoring of all arbitration trading systems • Auto-refresh every 5 minutes</p>
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
                <h2>🤖 ARBITRATION TRADING SYSTEMS</h2>
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
                        <div style="margin-top: 10px; font-size: 0.9em; color: #64748b;">
                            File: {{ system.file }}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            {% if opportunities %}
            <div class="card">
                <h2>🎯 LIVE OPPORTUNITIES</h2>
                {% for opp in opportunities %}
                <div class="opportunity">
                    <div style="font-weight: bold; color: {% if opp.type == '💰 FOREX' %}#fbbf24{% else %}#60a5fa{% endif %};">
                        {{ opp.type }}: {{ opp.pair }}
                    </div>
                    {% if opp.get('spread') %}
                    <div style="color: #f59e0b;">Spread: {{ opp.spread }}</div>
                    {% endif %}
                    {% if opp.get('profit_potential') %}
                    <div style="color: #10b981;">Profit: ${{ "%.2f"|format(opp.profit_potential) }}</div>
                    {% endif %}
                    {% if opp.get('brokers') %}
                    <div style="color: #94a3b8;">Arbitrage: {{ opp.brokers }}</div>
                    {% endif %}
                    {% if opp.get('exchange') %}
                    <div style="color: #94a3b8;">Exchange: {{ opp.exchange }}</div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            <div class="refresh-info">
                <button class="refresh-btn" onclick="refreshDashboard()">🔄 Refresh Now</button>
                <p style="margin-top: 10px; color: #94a3b8;">
                    Last updated: {{ system_status.timestamp }} ({{ system_status.timezone }})<br>
                    Auto-refresh in: <span id="countdown-text">5:00</span> minutes
                </p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(
        html,
        systems=systems,
        system_status=system_status,
        opportunities=opportunities
    )

if __name__ == '__main__':
    print("🚀 Starting ARBITRATION TRADING SYSTEM DASHBOARD...")
    print("⚖️  Dashboard: http://localhost:5020")
    print("⏰ Auto-refresh: Every 5 minutes")
    print("📊 Shows: ALL arbitration systems (Crypto + Forex)")
    print("💰 Includes: $220 Forex balance (Schwab #13086459)")
    app.run(host='0.0.0.0', port=5020, debug=False)