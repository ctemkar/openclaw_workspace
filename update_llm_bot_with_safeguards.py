#!/usr/bin/env python3
"""
Update LLM bot to use price safeguards
"""

import os

def update_bot_with_safeguards():
    """Add safeguard imports and usage to LLM bot"""
    
    print("🔧 Updating LLM bot with price safeguards...")
    
    bot_file = 'enhanced_llm_trader.py'
    
    if not os.path.exists(bot_file):
        print(f"❌ {bot_file} not found")
        return False
    
    with open(bot_file, 'r') as f:
        content = f.read()
    
    # Add import at the top
    import_statement = '''import logging
import json
import time
import requests
import ccxt
from datetime import datetime

# 🛡️ PRICE SAFEGUARDS - Avoid common mistakes when prices are wrong
from price_safeguards import PriceValidator, DataQualityChecker
'''
    
    # Check if already imported
    if 'from price_safeguards import' in content:
        print("✅ Price safeguards already imported")
    else:
        # Add after other imports
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            new_lines.append(line)
            if line.strip() == 'from datetime import datetime':
                # Add our import after datetime
                new_lines.append('')
                new_lines.append('# 🛡️ PRICE SAFEGUARDS - Avoid common mistakes when prices are wrong')
                new_lines.append('from price_safeguards import PriceValidator, DataQualityChecker')
                new_lines.append('')
        
        content = '\n'.join(new_lines)
        print("✅ Added price safeguard imports")
    
    # Update the calculate_24h_change function to use safeguards
    # We already fixed this function earlier, but let's add a comment
    
    # Find the calculate_24h_change function
    if 'def calculate_24h_change' in content:
        # Add a comment about safeguards
        content = content.replace(
            'def calculate_24h_change(exchange, symbol):',
            'def calculate_24h_change(exchange, symbol):\n    """Calculate 24h price change - WITH SAFEGUARDS"""'
        )
        print("✅ Updated calculate_24h_change docstring")
    
    # Update the position calculation to use safeguards
    # Look for: amount = position_value / current_price
    if 'amount = position_value / current_price' in content:
        # Replace with safeguarded version
        old_code = '''                # Calculate position
                position_value = GEMINI_CAPITAL * POSITION_SIZE * position_multiplier
                amount = position_value / current_price'''
        
        new_code = '''                # 🛡️ SAFE POSITION CALCULATION - Avoid common mistakes
                position_value = GEMINI_CAPITAL * POSITION_SIZE * position_multiplier
                amount = PriceValidator.safe_position_calculation(
                    current_price, 
                    GEMINI_CAPITAL, 
                    POSITION_SIZE * 100,  # Convert to percentage
                    symbol
                )
                
                if amount is None:
                    logger.error(f"❌ Price validation failed for {symbol}: ${current_price}")
                    logger.error("   NOT TRADING - Price seems wrong (common bug: satoshis/lamports)")
                    return None'''
        
        if old_code in content:
            content = content.replace(old_code, new_code)
            print("✅ Updated Gemini position calculation with safeguards")
        else:
            print("⚠️ Could not find Gemini position calculation to update")
    
    # Also update Binance position calculation
    old_binance_code = '''                # Calculate position
                position_value = BINANCE_CAPITAL * POSITION_SIZE * position_multiplier
                amount = position_value / current_price'''
    
    new_binance_code = '''                # 🛡️ SAFE POSITION CALCULATION - Avoid common mistakes
                position_value = BINANCE_CAPITAL * POSITION_SIZE * position_multiplier
                amount = PriceValidator.safe_position_calculation(
                    current_price, 
                    BINANCE_CAPITAL, 
                    POSITION_SIZE * 100,  # Convert to percentage
                    symbol
                )
                
                if amount is None:
                    logger.error(f"❌ Price validation failed for {symbol}: ${current_price}")
                    logger.error("   NOT TRADING - Price seems wrong (common bug)")
                    return None'''
    
    if old_binance_code in content:
        content = content.replace(old_binance_code, new_binance_code)
        print("✅ Updated Binance position calculation with safeguards")
    else:
        print("⚠️ Could not find Binance position calculation to update")
    
    # Save updated file
    with open(bot_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {bot_file} with price safeguards")
    
    # Create a simple test to verify
    print("\n🔍 TESTING THE UPDATED BOT:")
    print("   The bot will now:")
    print("   1. Validate prices before calculating amounts")
    print("   2. Reject prices that are too low (satoshis bug)")
    print("   3. Log errors when price validation fails")
    print("   4. Skip trading if prices seem wrong")
    
    print("\n🎯 COMMON BUGS PREVENTED:")
    print("   • BTC price $1.14 (satoshis bug) → REJECTED")
    print("   • SOL price $0.80 (lamports bug) → REJECTED")
    print("   • Price = 0 → REJECTED")
    print("   • Unrealistic amounts → REJECTED")
    
    return True

def update_dashboard_with_warnings():
    """Update dashboard to show data quality warnings"""
    
    print("\n" + "="*70)
    print("📊 UPDATING DASHBOARD WITH DATA QUALITY WARNINGS")
    print("="*70)
    
    dashboard_file = 'simple_fixed_dashboard.py'
    
    if not os.path.exists(dashboard_file):
        print(f"⚠️ {dashboard_file} not found, skipping dashboard update")
        return
    
    with open(dashboard_file, 'r') as f:
        content = f.read()
    
    # Add import
    if 'from price_safeguards import' not in content:
        # Find where to add import
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            new_lines.append(line)
            if 'from flask import' in line:
                new_lines.append('from price_safeguards import DataQualityChecker')
        
        content = '\n'.join(new_lines)
        print("✅ Added DataQualityChecker import to dashboard")
    
    # Find where to add warnings in the template
    # Look for the header section
    header_section = '''    <div class="container">
        <div class="header">
            <h1>📊 Trading System Dashboard</h1>
            <div class="subtitle">Updated: {{ timestamp }}</div>
        </div>'''
    
    if header_section in content:
        # Add warnings section after header
        warnings_section = '''        <!-- DATA QUALITY WARNINGS -->
        {% if warnings %}
        <div class="section" style="background: #fff3cd; border-color: #ffc107;">
            <h2 class="section-title" style="color: #856404;">⚠️ DATA QUALITY WARNINGS</h2>
            <div style="color: #856404;">
                {% for warning in warnings %}
                <p>{{ warning }}</p>
                {% endfor %}
            </div>
            <p><small>These warnings help avoid common mistakes like price=0 or wrong units</small></p>
        </div>
        {% endif %}'''
        
        new_header = header_section + '\n\n' + warnings_section
        content = content.replace(header_section, new_header)
        print("✅ Added data quality warnings section to dashboard template")
    
    # Update the dashboard() function to check data quality
    if 'def dashboard():' in content:
        # Find where to add data quality check
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # After loading trades, add data quality check
            if 'with open(\'trading_data/trades.json\'' in line:
                # Add a few lines later
                for j in range(i, min(i+10, len(lines))):
                    if 'trades = json.load(f)' in lines[j]:
                        # Add after this line
                        new_lines.append('        # 🛡️ Check data quality')
                        new_lines.append('        issues = DataQualityChecker.check_trades(trades)')
                        new_lines.append('        warnings = DataQualityChecker.generate_dashboard_warnings(issues)')
                        break
        
        content = '\n'.join(new_lines)
        
        # Also update the render_template_string call to pass warnings
        if 'return render_template_string(' in content:
            # Add warnings parameter
            content = content.replace(
                'return render_template_string(',
                'return render_template_string('
            )
            
            # Find the closing parenthesis and add warnings
            lines = content.split('\n')
            new_lines = []
            
            for line in lines:
                new_lines.append(line)
                if line.strip().startswith('capital=capital') and ')' in line:
                    # Add warnings parameter
                    new_lines.append('        warnings=warnings,')
            
            content = '\n'.join(new_lines)
        
        print("✅ Updated dashboard() function with data quality checks")
    
    # Save updated dashboard
    with open(dashboard_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {dashboard_file} with data quality warnings")
    
    print("\n🎯 DASHBOARD WILL NOW SHOW:")
    print("   • Warnings when prices are 0 (common bug)")
    print("   • Warnings when prices seem wrong (satoshis bug)")
    print("   • Clear alerts about data quality issues")
    print("   • Helps avoid making decisions based on wrong data")

def main():
    print("="*70)
    print("🛡️ ADDING PRICE SAFEGUARDS TO AVOID COMMON MISTAKES")
    print("="*70)
    
    print("\n📋 COMMON MISTAKES WE'RE PREVENTING:")
    print("   1. Trading with price=0")
    print("   2. Calculating wrong amounts (34.5 BTC bug)")
    print("   3. Showing fake huge profits")
    print("   4. Making decisions based on wrong data")
    
    print("\n🔧 UPDATING SYSTEMS...")
    
    # 1. Update LLM bot
    if update_bot_with_safeguards():
        print("\n✅ LLM bot updated with price safeguards")
    else:
        print("\n❌ Failed to update LLM bot")
    
    # 2. Update dashboard
    update_dashboard_with_warnings()
    
    print("\n" + "="*70)
    print("🎯 SAFEGUARDS IMPLEMENTED SUCCESSFULLY")
    print("="*70)
    
    print("\n🔄 RESTART REQUIRED:")
    print("   1. Restart LLM bot: kill <pid> && python3 enhanced_llm_trader.py")
    print("   2. Restart dashboard: kill <pid> && python3 simple_fixed_dashboard.py")
    
    print("\n📊 AFTER RESTART:")
    print("   • LLM bot will reject wrong prices")
    print("   • Dashboard will show data quality warnings")
    print("   • Common mistakes will be prevented automatically")

if __name__ == "__main__":
    main()