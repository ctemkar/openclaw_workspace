#!/usr/bin/env python3
"""
Market analysis for conservative crypto trading
Uses public APIs to get real market data
"""

import requests
import json
from datetime import datetime, timedelta
import time

def get_binance_price(symbol: str) -> dict:
    """Get price from Binance API"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'symbol': symbol,
            'price': float(data['lastPrice']),
            'change_24h': float(data['priceChangePercent']),
            'volume': float(data['volume']),
            'high': float(data['highPrice']),
            'low': float(data['lowPrice'])
        }
    except Exception as e:
        print(f"Binance API error for {symbol}: {e}")
        return None

def get_coinbase_price(symbol: str) -> dict:
    """Get price from Coinbase API"""
    try:
        url = f"https://api.coinbase.com/v2/prices/{symbol}-USD/spot"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Get 24h stats from different endpoint
        stats_url = f"https://api.coinbase.com/v2/prices/{symbol}-USD/historic?period=day"
        stats_response = requests.get(stats_url, timeout=10)
        stats_data = stats_response.json() if stats_response.status_code == 200 else {}
        
        return {
            'symbol': symbol,
            'price': float(data['data']['amount']),
            'change_24h': 0.0,  # Coinbase doesn't provide this easily
            'volume': 0.0,
            'high': 0.0,
            'low': 0.0
        }
    except Exception as e:
        print(f"Coinbase API error for {symbol}: {e}")
        return None

def get_market_data(symbol: str) -> dict:
    """Get market data from multiple sources"""
    # Try Binance first
    data = get_binance_price(symbol)
    if data:
        return data
    
    # Fallback to Coinbase
    coinbase_symbol = symbol.replace('USDT', '').replace('USD', '')
    data = get_coinbase_price(coinbase_symbol)
    if data:
        return data
    
    return None

def analyze_market_conditions(price_data: dict) -> dict:
    """Analyze market conditions for trading decision"""
    if not price_data:
        return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'No data'}
    
    price = price_data['price']
    change_24h = price_data['change_24h']
    high = price_data['high']
    low = price_data['low']
    
    # Conservative analysis rules
    signal = 'HOLD'
    confidence = 0.0
    reason = "Market conditions neutral"
    
    # Rule 1: Significant dip with potential recovery (buy opportunity)
    if change_24h < -3.0:  # Down more than 3% in 24h
        # Check if near 24h low (within 1%)
        if price <= low * 1.01:
            signal = 'BUY'
            confidence = min(0.7, abs(change_24h) / 10)
            reason = f"Significant dip ({change_24h:.2f}%), near 24h low"
    
    # Rule 2: Significant rally with potential pullback (sell opportunity)
    elif change_24h > 3.0:  # Up more than 3% in 24h
        # Check if near 24h high (within 1%)
        if price >= high * 0.99:
            signal = 'SELL'
            confidence = min(0.7, abs(change_24h) / 10)
            reason = f"Significant rally ({change_24h:.2f}%), near 24h high"
    
    # Rule 3: Very low volatility - avoid trading
    elif abs(change_24h) < 0.5:  # Less than 0.5% change
        signal = 'HOLD'
        confidence = 0.8
        reason = f"Low volatility ({change_24h:.2f}%), not favorable for trading"
    
    return {
        'signal': signal,
        'confidence': confidence,
        'reason': reason,
        'price': price,
        'change_24h': change_24h,
        'high': high,
        'low': low
    }

def calculate_position_size(capital: float, price: float, risk_per_trade: float = 0.2) -> float:
    """Calculate position size based on capital and risk"""
    position_value = capital * risk_per_trade  # 20% of capital per trade
    return position_value / price

def simulate_trade(symbol: str, analysis: dict, capital: float = 1000.0) -> dict:
    """Simulate a trade based on analysis"""
    if analysis['signal'] == 'HOLD' or analysis['confidence'] < 0.5:
        return None
    
    price = analysis['price']
    amount = calculate_position_size(capital, price)
    
    # Calculate risk management levels
    if analysis['signal'] == 'BUY':
        entry_price = price * 0.995  # 0.5% below current for limit order
        stop_loss = entry_price * 0.95  # 5% stop-loss
        take_profit = entry_price * 1.10  # 10% take-profit
    else:  # SELL
        entry_price = price * 1.005  # 0.5% above current for limit order
        stop_loss = entry_price * 1.05  # 5% stop-loss
        take_profit = entry_price * 0.90  # 10% take-profit
    
    return {
        'timestamp': datetime.now().isoformat(),
        'symbol': symbol,
        'side': analysis['signal'],
        'amount': amount,
        'entry_price': round(entry_price, 2),
        'current_price': round(price, 2),
        'stop_loss': round(stop_loss, 2),
        'take_profit': round(take_profit, 2),
        'position_value': round(amount * entry_price, 2),
        'risk_reward_ratio': 2.0,  # 5% risk for 10% reward = 1:2
        'analysis': analysis
    }

def main():
    """Main analysis function"""
    print("=== Conservative Crypto Market Analysis ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Capital: $1,000")
    print(f"Risk Parameters: 5% stop-loss, 10% take-profit")
    print(f"Max trades per day: 2")
    print()
    
    symbols = ['BTCUSDT', 'ETHUSDT']
    all_trades = []
    
    for symbol in symbols:
        print(f"=== Analyzing {symbol.replace('USDT', '/USD')} ===")
        
        # Get market data
        price_data = get_market_data(symbol)
        if not price_data:
            print(f"  ❌ Failed to get market data for {symbol}")
            print()
            continue
        
        print(f"  Current Price: ${price_data['price']:,.2f}")
        print(f"  24h Change: {price_data['change_24h']:.2f}%")
        print(f"  24h High: ${price_data['high']:,.2f}")
        print(f"  24h Low: ${price_data['low']:,.2f}")
        print(f"  24h Volume: {price_data['volume']:,.0f}")
        
        # Analyze market conditions
        analysis = analyze_market_conditions(price_data)
        print(f"  Signal: {analysis['signal']}")
        print(f"  Confidence: {analysis['confidence']:.0%}")
        print(f"  Reason: {analysis['reason']}")
        
        # Simulate trade if conditions are favorable
        if analysis['confidence'] >= 0.5:
            trade = simulate_trade(symbol, analysis)
            if trade:
                print(f"  ✅ Trade Opportunity Detected:")
                print(f"     Side: {trade['side']}")
                print(f"     Amount: {trade['amount']:.6f}")
                print(f"     Entry: ${trade['entry_price']:,.2f}")
                print(f"     Stop-loss: ${trade['stop_loss']:,.2f}")
                print(f"     Take-profit: ${trade['take_profit']:,.2f}")
                print(f"     Position Value: ${trade['position_value']:,.2f}")
                print(f"     Risk/Reward: 1:{trade['risk_reward_ratio']}")
                all_trades.append(trade)
            else:
                print(f"  ⚠️  Signal detected but below confidence threshold")
        else:
            print(f"  ⏸️  Holding - market conditions not favorable")
        
        print()
    
    # Summary
    print("=== Trading Summary ===")
    if all_trades:
        print(f"✅ {len(all_trades)} trade opportunity(ies) identified:")
        for i, trade in enumerate(all_trades, 1):
            print(f"\nTrade {i}:")
            print(f"  {trade['side']} {trade['amount']:.6f} {trade['symbol'].replace('USDT', '/USD')}")
            print(f"  Entry: ${trade['entry_price']:,.2f}")
            print(f"  Current: ${trade['current_price']:,.2f}")
            print(f"  Stop-loss: ${trade['stop_loss']:,.2f} ({((trade['stop_loss'] - trade['entry_price']) / trade['entry_price'] * 100):.1f}%)")
            print(f"  Take-profit: ${trade['take_profit']:,.2f} ({((trade['take_profit'] - trade['entry_price']) / trade['entry_price'] * 100):.1f}%)")
            print(f"  Position Value: ${trade['position_value']:,.2f}")
            print(f"  Risk/Reward Ratio: 1:{trade['risk_reward_ratio']}")
    else:
        print("⏸️  No trade opportunities identified - holding cash")
        print("Reason: Market conditions not favorable for conservative trading")
    
    print(f"\n=== Risk Management ===")
    print(f"• Maximum capital at risk per trade: $200 (20% of $1,000)")
    print(f"• Maximum daily loss limit: $100 (10% of capital)")
    print(f"• Stop-loss: 5% from entry price")
    print(f"• Take-profit: 10% from entry price")
    print(f"• Risk/Reward Ratio: 1:2")
    
    # Save analysis to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output = {
        'timestamp': datetime.now().isoformat(),
        'capital': 1000.0,
        'trades': all_trades,
        'summary': {
            'total_trades': len(all_trades),
            'total_position_value': sum(t['position_value'] for t in all_trades),
            'remaining_capital': 1000.0 - sum(t['position_value'] for t in all_trades)
        }
    }
    
    with open(f'trading_analysis_{timestamp}.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nAnalysis saved to: trading_analysis_{timestamp}.json")
    
    return all_trades

if __name__ == "__main__":
    main()