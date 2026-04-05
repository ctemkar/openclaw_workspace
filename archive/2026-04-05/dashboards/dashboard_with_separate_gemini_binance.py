            data['binance']['pnl_percent'] = trade.get('pnl_percent', 0)
            
        elif exchange == 'gemini' and trade_type == 'cash':
            # Gemini cash
            data['gemini']['cash'] = trade.get('value', 0)
            
        elif exchange == 'binance' and trade_type == 'cash':
            # Binance cash
            data['binance']['cash'] = trade.get('value', 0)
            
        elif exchange == 'gemini' and trade_type == 'spot':
            # Gemini positions
            data['gemini']['positions'].append(trade)
            data['gemini']['position_value'] += trade.get('value', 0)
            data['total']['position_value'] += trade.get('value', 0)
            
        elif exchange == 'binance' and trade_type == 'spot':
            # Binance positions
            data['binance']['positions'].append(trade)
            data['binance']['position_value'] += trade.get('value', 0)
            data['total']['position_value'] += trade.get('value', 0)
    
    # Calculate percentages
    total_current = data['total']['current']
    data['gemini']['percent_of_total'] = round((data['gemini']['current'] / total_current * 100), 1) if total_current > 0 else 0
    data['binance']['percent_of_total'] = round((data['binance']['current'] / total_current * 100), 1) if total_current > 0 else 0
    
    return data

def get_bot_status():
    """Check if trading bot is running"""
    try:
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'enhanced_llm_trader.py' in result.stdout:
            return '🟢 RUNNING', 'Enhanced LLM bot active'
        elif 'simple_llm_trader.py' in result.stdout:
            return '🟢 RUNNING', 'Simple LLM bot active'
        elif 'gemini_only_trader.py' in result.stdout:
            return '🟢 RUNNING', 'Gemini-only bot active'
        else:
            return '🔴 STOPPED', 'No trading bot running'
    except:
        return '⚪ UNKNOWN', 'Could not check bot status'

@app.route('/')
def dashboard():
    try:
        # Analyze trades
        data = analyze_trades()
        
        # Get bot status
        bot_status, bot_note = get_bot_status()
        
        # Get all positions
        all_positions = data['gemini']['positions'] + data['binance']['positions']
        
        # Calculate win rate
        winning_trades = sum(1 for p in all_positions if p.get('pnl', 0) > 0)
        total_trades = len(all_positions)
        win_rate = round((winning_trades / total_trades * 100), 1) if total_trades > 0 else 0
        
        # Prepare template data
        template_data = {
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'gemini': data['gemini'],
            'binance': data['binance'],
            'total': data['total'],
            'positions': all_positions,
            'bot_status': bot_status,
            'bot_note': bot_note,
            'total_trades': total_trades,
            'win_rate': win_rate
        }
        
        return render_template_string(HTML_TEMPLATE, **template_data)
        
    except Exception as e:
        return f"Error loading dashboard: {str(e)}", 500

@app.route('/api/data')
def api_data():
    """API endpoint for JSON data"""
    try:
        data = analyze_trades()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=False)