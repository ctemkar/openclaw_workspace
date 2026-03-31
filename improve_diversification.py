#!/usr/bin/env python3
"""
Improve trading diversification
"""

import json
from datetime import datetime

print('📈 IMPROVING TRADING DIVERSIFICATION')
print('=' * 70)

# 1. Analyze current positions
print('1. 📊 CURRENT POSITION ANALYSIS:')
try:
    import requests
    response = requests.get('http://localhost:5001/api/data', timeout=5)
    data = response.json()
    
    positions = data.get('positions', [])
    
    if positions:
        # Group by symbol
        symbol_counts = {}
        symbol_values = {}
        
        for pos in positions:
            symbol = pos.get('symbol', 'unknown')
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
            symbol_values[symbol] = symbol_values.get(symbol, 0) + pos.get('value', 0)
        
        print(f'   • Total positions: {len(positions)}')
        print(f'   • Unique symbols: {len(symbol_counts)}')
        
        for symbol, count in symbol_counts.items():
            value = symbol_values.get(symbol, 0)
            print(f'   • {symbol}: {count} positions (${value:.2f})')
        
        # Check diversification
        if len(symbol_counts) == 1:
            print('   ⚠️ WARNING: All positions in single symbol')
            current_symbol = list(symbol_counts.keys())[0]
            print(f'   • Current: 100% in {current_symbol}')
            
    else:
        print('   • No open positions')
        
except Exception as e:
    print(f'   ❌ Error analyzing positions: {e}')

print()

# 2. Check available cryptocurrencies
print('2. 🔍 AVAILABLE CRYPTOCURRENCIES:')
all_cryptos = [
    'BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
    'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI', 'SNX', 'MKR', 'BAT',
    'ZRX', 'OMG', 'ENJ', 'MATIC', 'SUSHI', 'CRV'
]

gemini_cryptos = [
    'BTC', 'ETH', 'SOL', 'XRP', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
    'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI'
]

print(f'   • Total in 26-crypto list: {len(all_cryptos)} cryptos')
print(f'   • Available on Gemini: {len(gemini_cryptos)} cryptos')
print(f'   • Currently trading: 1 crypto (SOL)')

print()

# 3. Diversification strategy
print('3. 🎯 DIVERSIFICATION STRATEGY:')
print('   A. CAPITAL ALLOCATION:')
print('      • Current: 100% in SOL')
print('      • Target: Spread across 3-5 top cryptos')
print()
print('   B. SYMBOL SELECTION:')
print('      • Tier 1 (Market leaders):')
print('        1. BTC/USD - Bitcoin (market cap leader)')
print('        2. ETH/USD - Ethereum (smart contracts)')
print('        3. SOL/USD - Solana (already trading)')
print()
print('      • Tier 2 (Established alts):')
print('        4. XRP/USD - Ripple (payments)')
print('        5. ADA/USD - Cardano (research-focused)')
print('        6. DOT/USD - Polkadot (interoperability)')
print()
print('   C. POSITION SIZING:')
print('      • Max 20% per symbol')
print('      • Ideal: 3 symbols at ~33% each')
print('      • Or: 5 symbols at ~20% each')

print()

# 4. Implementation plan
print('4. 🚀 IMPLEMENTATION PLAN:')
print('   STEP 1: Review bot thresholds')
print('      • Current: 1.0% dip for LONG, 1.0% rally for SHORT')
print('      • Consider: 0.8% for more opportunities')
print()
print('   STEP 2: Enable multi-symbol trading')
print('      • Bot already monitors 26 cryptos')
print('      • Need to execute on multiple symbols')
print()
print('   STEP 3: Adjust position limits')
print('      • Current: MAX_POSITIONS = 3')
print('      • But we have 5 SOL positions (violating limit)')
print('      • Fix: Enforce position limits across symbols')
print()
print('   STEP 4: Monitor and adjust')
print('      • Track performance by symbol')
print('      • Adjust allocation based on performance')

print()

# 5. Create monitoring dashboard
print('5. 📊 DIVERSIFICATION MONITOR:')
monitor_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>📈 Diversification Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px; }
        .data-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .data-card { background: white; padding: 15px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .positive { color: green; }
        .negative { color: red; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 Trading Diversification Monitor</h1>
        
        <div class="section">
            <h2>Current Allocation</h2>
            <div id="allocation-chart">
                <!-- Will be populated by JavaScript -->
            </div>
        </div>
        
        <div class="section">
            <h2>Symbol Performance</h2>
            <table id="symbol-table">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Positions</th>
                        <th>Value</th>
                        <th>% of Portfolio</th>
                        <th>P&L</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Will be populated by JavaScript -->
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Diversification Score</h2>
            <div class="data-grid">
                <div class="data-card">
                    <h3>Symbol Count</h3>
                    <div id="symbol-count" style="font-size: 2em;">1</div>
                    <p>Target: 3-5 symbols</p>
                </div>
                <div class="data-card">
                    <h3>Max Allocation</h3>
                    <div id="max-allocation" style="font-size: 2em;">100%</div>
                    <p>Target: < 33% per symbol</p>
                </div>
                <div class="data-card">
                    <h3>Diversification</h3>
                    <div id="diversification-score" style="font-size: 2em;">POOR</div>
                    <p>Needs improvement</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Fetch data from API
        async function fetchData() {
            try {
                const response = await fetch('http://localhost:5001/api/data');
                const data = await response.json();
                updateDashboard(data);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
        
        function updateDashboard(data) {
            const positions = data.positions || [];
            
            // Calculate allocation
            const allocation = {};
            let totalValue = 0;
            
            positions.forEach(pos => {
                const symbol = pos.symbol || 'unknown';
                const value = pos.value || 0;
                allocation[symbol] = (allocation[symbol] || 0) + value;
                totalValue += value;
            });
            
            // Update table
            const tableBody = document.querySelector('#symbol-table tbody');
            tableBody.innerHTML = '';
            
            Object.entries(allocation).forEach(([symbol, value]) => {
                const percent = totalValue > 0 ? (value / totalValue * 100).toFixed(1) : 0;
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${symbol}</td>
                    <td>${positions.filter(p => p.symbol === symbol).length}</td>
                    <td>$${value.toFixed(2)}</td>
                    <td>${percent}%</td>
                    <td class="${value >= 0 ? 'positive' : 'negative'}">$${value.toFixed(2)}</td>
                    <td>${percent > 33 ? '⚠️ Over-concentrated' : '✅ Balanced'}</td>
                `;
                tableBody.appendChild(row);
            });
            
            // Update metrics
            document.getElementById('symbol-count').textContent = Object.keys(allocation).length;
            
            const maxPercent = Math.max(...Object.values(allocation).map(v => totalValue > 0 ? (v / totalValue * 100) : 0));
            document.getElementById('max-allocation').textContent = maxPercent.toFixed(1) + '%';
            
            const score = Object.keys(allocation).length >= 3 && maxPercent <= 40 ? 'GOOD' : 
                         Object.keys(allocation).length >= 2 && maxPercent <= 60 ? 'FAIR' : 'POOR';
            document.getElementById('diversification-score').textContent = score;
            document.getElementById('diversification-score').className = 
                score === 'GOOD' ? 'positive' : score === 'FAIR' ? '' : 'negative';
        }
        
        // Initial load and refresh every 30 seconds
        fetchData();
        setInterval(fetchData, 30000);
    </script>
</body>
</html>
'''

with open('diversification_monitor.html', 'w') as f:
    f.write(monitor_html)

print('   ✅ Created diversification_monitor.html')
print('   • Shows current allocation by symbol')
print('   • Calculates diversification score')
print('   • Updates every 30 seconds')
print('   • Access: file://' + os.path.abspath('diversification_monitor.html'))

print()
print('=' * 70)
print('✅ DIVERSIFICATION IMPROVEMENT PLAN READY')
print()
print('📋 ACTION ITEMS:')
print('1. Review bot to ensure it trades multiple symbols')
print('2. Check why only SOL is being traded (market conditions?)')
print('3. Consider adjusting thresholds for more opportunities')
print('4. Monitor diversification with new dashboard')
print('5. Aim for 3-5 symbols with < 33% allocation each')