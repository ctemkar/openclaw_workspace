from flask import Flask, render_template_string
import json
import datetime

app = Flask(__name__)

def load_config():
    """Load single source of truth"""
    try:
        with open('arbitrage_config.json', 'r') as f:
            return json.load(f)
    except:
        return {"error": "Config not found"}

@app.route('/')
def index():
    config = load_config()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f'''
    <!DOCTYPE html>
<html>
<head>
    <title>Unified Arbitrage Dashboard</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #0f172a; color: white; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 40px; padding: 30px; background: #1e293b; border-radius: 10px; }}
        .single-truth {{ background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); padding: 25px; border-radius: 10px; margin-bottom: 30px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 40px; }}
        .stat-card {{ background: #334155; padding: 20px; border-radius: 10px; text-align: center; }}
        .progress-bar {{ height: 20px; background: #475569; border-radius: 10px; margin: 10px 0; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #10b981 0%, #34d399 100%); }}
        .crypto-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; margin: 20px 0; }}
        .crypto-item {{ background: #475569; padding: 10px; border-radius: 5px; text-align: center; font-size: 0.9em; }}
        .telegram-promise {{ background: #fef3c7; color: #92400e; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 6px solid #f59e0b; }}
        .section {{ background: #1e293b; padding: 25px; border-radius: 10px; margin-bottom: 30px; }}
        .badge {{ padding: 5px 10px; border-radius: 15px; font-size: 0.8em; font-weight: bold; }}
        .badge.success {{ background: #10b981; color: white; }}
        .badge.warning {{ background: #f59e0b; color: white; }}
        .badge.danger {{ background: #ef4444; color: white; }}
        .badge.info {{ background: #3b82f6; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 UNIFIED ARBITRAGE DASHBOARD</h1>
            <p>Single Source of Truth | Updated: {current_time}</p>
            <p>Config Updated: {config.get('updated_at', 'N/A')}</p>
        </div>
        
        <div class="single-truth">
            <h2>🎯 SINGLE SOURCE OF TRUTH</h2>
            <p>All data comes from <code>arbitrage_config.json</code></p>
            <p>No more different values in different places!</p>
        </div>
        
        <div class="telegram-promise">
            <h3>📱 TELEGRAM PROMISE: 50+ CRYPTOS</h3>
            <p><strong>Status:</strong> {config.get('crypto_stats', {{}}).get('status', 'N/A')}</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {(config.get('crypto_stats', {{}}).get('total_monitored', 0) / 50 * 100) if config.get('crypto_stats') else 0}%"></div>
            </div>
            <p>Target: 50 cryptos | Current: {config.get('crypto_stats', {{}}).get('total_monitored', 0)}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Monitored</h3>
                <h1>{config.get('crypto_stats', {{}}).get('total_monitored', 0)}</h1>
                <p>Cryptos</p>
            </div>
            <div class="stat-card">
                <h3>Checked</h3>
                <h1>{config.get('crypto_stats', {{}}).get('total_checked', 0)}</h1>
                <p>Potential</p>
            </div>
            <div class="stat-card">
                <h3>Progress</h3>
                <h1>{int((config.get('crypto_stats', {{}}).get('total_monitored', 0) / 50 * 100) if config.get('crypto_stats') else 0)}%</h1>
                <p>To 50 target</p>
            </div>
            <div class="stat-card">
                <h3>Bot Status</h3>
                <h1>✅</h1>
                <p>PID: {config.get('bot_status', {{}}).get('pid', 'N/A')}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 SUPPORTED CRYPTOS ({config.get('crypto_stats', {{}}).get('total_monitored', 0)} total)</h2>
            <div class="crypto-list">
                {"".join([f'<div class="crypto-item">{crypto}</div>' for crypto in config.get('supported_cryptos', [])])}
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 BOT STATUS</h2>
            <p><strong>Name:</strong> {config.get('bot_status', {{}}).get('name', 'N/A')}</p>
            <p><strong>Strategy:</strong> {config.get('bot_status', {{}}).get('strategy', 'N/A')}</p>
            <p><strong>Scan Interval:</strong> {config.get('bot_status', {{}}).get('scan_interval_seconds', 'N/A')} seconds</p>
            <p><strong>Min Spread:</strong> {config.get('bot_status', {{}}).get('min_spread_percent', 'N/A')}%</p>
            <p><strong>Min Profit:</strong> ${config.get('bot_status', {{}}).get('min_profit_usd', 'N/A')}</p>
        </div>
        
        <div class="section">
            <h2>⏰ MISSED OPPORTUNITIES (BUG FIXED)</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th style="padding: 12px; text-align: left; border-bottom: 1px solid #444;">Crypto</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 1px solid #444;">Spread</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 1px solid #444;">Time</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 1px solid #444;">Missed Profit</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 1px solid #444;">Reason</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #444;"><strong>{opp.get('crypto', 'N/A')}</strong></td>
                        <td style="padding: 12px; border-bottom: 1px solid #444;"><span class="badge danger">{opp.get('spread_percent', 0)}%</span></td>
                        <td style="padding: 12px; border-bottom: 1px solid #444;">{opp.get('time', 'N/A')}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #444;">${opp.get('missed_profit_usd', 0)}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #444;">{opp.get('reason', 'N/A')}</td>
                    </tr>
                    ''' for opp in config.get('missed_opportunities', [])])}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>🌐 ALL DASHBOARDS</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px;">
                {"".join([f'''
                <div style="background: #334155; padding: 15px; border-radius: 8px;">
                    <strong>{name.upper()}</strong><br>
                    <a href="{url}" style="color: #60a5fa;">{url}</a>
                </div>
                ''' for name, url in config.get('dashboards', {{}}).items()])}
            </div>
        </div>
        
        <div class="section">
            <h2>🚀 NEXT STEPS (TO REACH 50 CRYPTOS)</h2>
            <ul>
                <li><strong>Add Kraken:</strong> {config.get('next_steps', {{}}).get('add_kraken', False)}</li>
                <li><strong>Target Cryptos:</strong> {config.get('next_steps', {{}}).get('target_cryptos', 0)}</li>
                <li><strong>Multi-exchange:</strong> {config.get('next_steps', {{}}).get('multi_exchange', False)}</li>
                <li><strong>Triangular Arbitrage:</strong> {config.get('next_steps', {{}}).get('triangular_arbitrage', False)}</li>
            </ul>
            <p style="margin-top: 15px; color: #10b981;">
                ✅ <strong>TELEGRAM PROMISE WILL BE DELIVERED WITH KRAKEN ADDITION</strong>
            </p>
        </div>
    </div>
</body>
</html>
    '''
    
    return html

if __name__ == '__main__':
    print("🚀 Starting Unified Dashboard on http://localhost:5013")
    print("   Single Source of Truth from arbitrage_config.json")
    app.run(host='0.0.0.0', port=5013, debug=False)