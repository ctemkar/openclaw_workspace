import json
import subprocess
import sys
from datetime import datetime

def get_market_data():
    # Get current prices
    result = subprocess.run(
        ['curl', '-s', 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24h_change=true'],
        capture_output=True,
        text=True
    )
    prices = json.loads(result.stdout)
    
    # Get detailed market data
    result = subprocess.run(
        ['curl', '-s', 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin,ethereum&order=market_cap_desc&per_page=2&page=1&sparkline=false&price_change_percentage=24h'],
        capture_output=True,
        text=True
    )
    detailed = json.loads(result.stdout)
    
    return prices, detailed

def analyze_market(prices, detailed):
    btc_price = prices['bitcoin']['usd']
    eth_price = prices['ethereum']['usd']
    
    btc_data = detailed[0]
    eth_data = detailed[1]
    
    print("=== MARKET ANALYSIS ===")
    print(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    print("BTC/USD:")
    print(f"  Price: ${btc_price:,.0f}")
    print(f"  24h Change: {btc_data['price_change_percentage_24h']:.2f}%")
    print(f"  24h Range: ${btc_data['low_24h']:,.0f} - ${btc_data['high_24h']:,.0f}")
    print(f"  Volume: ${btc_data['total_volume']:,.0f}")
    print()
    print("ETH/USD:")
    print(f"  Price: ${eth_price:,.2f}")
    print(f"  24h Change: {eth_data['price_change_percentage_24h']:.2f}%")
    print(f"  24h Range: ${eth_data['low_24h']:,.2f} - ${eth_data['high_24h']:,.2f}")
    print(f"  Volume: ${eth_data['total_volume']:,.0f}")
    print()
    
    # Market sentiment analysis
    btc_sentiment = "NEUTRAL"
    if btc_data['price_change_percentage_24h'] > 1:
        btc_sentiment = "BULLISH"
    elif btc_data['price_change_percentage_24h'] < -1:
        btc_sentiment = "BEARISH"
    
    eth_sentiment = "NEUTRAL"
    if eth_data['price_change_percentage_24h'] > 1:
        eth_sentiment = "BULLISH"
    elif eth_data['price_change_percentage_24h'] < -1:
        eth_sentiment = "BEARISH"
    
    print("=== SENTIMENT ===")
    print(f"BTC: {btc_sentiment} ({btc_data['price_change_percentage_24h']:.2f}%)")
    print(f"ETH: {eth_sentiment} ({eth_data['price_change_percentage_24h']:.2f}%)")
    print()
    
    # Support and resistance levels (simplified)
    btc_support = btc_data['low_24h']
    btc_resistance = btc_data['high_24h']
    eth_support = eth_data['low_24h']
    eth_resistance = eth_data['high_24h']
    
    print("=== KEY LEVELS ===")
    print(f"BTC Support: ${btc_support:,.0f}")
    print(f"BTC Resistance: ${btc_resistance:,.0f}")
    print(f"ETH Support: ${eth_support:,.2f}")
    print(f"ETH Resistance: ${eth_resistance:,.2f}")
    
    return {
        'btc': {
            'price': btc_price,
            'change_24h': btc_data['price_change_percentage_24h'],
            'support': btc_support,
            'resistance': btc_resistance,
            'sentiment': btc_sentiment
        },
        'eth': {
            'price': eth_price,
            'change_24h': eth_data['price_change_percentage_24h'],
            'support': eth_support,
            'resistance': eth_resistance,
            'sentiment': eth_sentiment
        }
    }

def conservative_trading_strategy(analysis, capital=1000, max_trades=2):
    print("\n=== TRADING DECISION ===")
    trades = []
    
    # Conservative strategy rules:
    # 1. Only trade if sentiment is clear (bullish or bearish > 1%)
    # 2. Look for prices near support (for buys) or resistance (for sells)
    # 3. Small position sizes (10-20% of capital per trade)
    # 4. Use tight stop-loss (5%) and take-profit (10%)
    
    btc = analysis['btc']
    eth = analysis['eth']
    
    # Calculate position size (15% of capital per trade)
    position_size = capital * 0.15
    
    # Check BTC
    btc_position = btc['price'] / btc['support']
    btc_to_resistance = btc['resistance'] / btc['price']
    
    if btc['sentiment'] == "BULLISH" and btc_position < 1.02:  # Within 2% of support
        # Buy signal
        entry = btc['price']
        stop_loss = entry * 0.95  # 5% stop-loss
        take_profit = entry * 1.10  # 10% take-profit
        quantity = position_size / entry
        
        trades.append({
            'asset': 'BTC/USD',
            'side': 'BUY',
            'entry': entry,
            'quantity': quantity,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'reason': f"Bullish sentiment ({btc['change_24h']:.2f}%), near support (${btc['support']:,.0f})"
        })
    
    elif btc['sentiment'] == "BEARISH" and btc_to_resistance < 1.02:  # Within 2% of resistance
        # Sell signal (short)
        entry = btc['price']
        stop_loss = entry * 1.05  # 5% stop-loss
        take_profit = entry * 0.90  # 10% take-profit
        quantity = position_size / entry
        
        trades.append({
            'asset': 'BTC/USD',
            'side': 'SELL',
            'entry': entry,
            'quantity': quantity,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'reason': f"Bearish sentiment ({btc['change_24h']:.2f}%), near resistance (${btc['resistance']:,.0f})"
        })
    
    # Check ETH
    eth_position = eth['price'] / eth['support']
    eth_to_resistance = eth['resistance'] / eth['price']
    
    if eth['sentiment'] == "BULLISH" and eth_position < 1.02:  # Within 2% of support
        # Buy signal
        entry = eth['price']
        stop_loss = entry * 0.95  # 5% stop-loss
        take_profit = entry * 1.10  # 10% take-profit
        quantity = position_size / entry
        
        trades.append({
            'asset': 'ETH/USD',
            'side': 'BUY',
            'entry': entry,
            'quantity': quantity,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'reason': f"Bullish sentiment ({eth['change_24h']:.2f}%), near support (${eth['support']:.2f})"
        })
    
    elif eth['sentiment'] == "BEARISH" and eth_to_resistance < 1.02:  # Within 2% of resistance
        # Sell signal (short)
        entry = eth['price']
        stop_loss = entry * 1.05  # 5% stop-loss
        take_profit = entry * 0.90  # 10% take-profit
        quantity = position_size / entry
        
        trades.append({
            'asset': 'ETH/USD',
            'side': 'SELL',
            'entry': entry,
            'quantity': quantity,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'reason': f"Bearish sentiment ({eth['change_24h']:.2f}%), near resistance (${eth['resistance']:.2f})"
        })
    
    # Limit to max trades per day
    if len(trades) > max_trades:
        trades = trades[:max_trades]
        print(f"Limited to {max_trades} trades as per daily limit")
    
    return trades

def main():
    prices, detailed = get_market_data()
    analysis = analyze_market(prices, detailed)
    trades = conservative_trading_strategy(analysis)
    
    print("\n=== TRADE EXECUTION SUMMARY ===")
    if not trades:
        print("No trades executed - market conditions don't meet conservative criteria")
        print("Reason: Prices not near key levels with clear sentiment signals")
    else:
        total_risk = 0
        for i, trade in enumerate(trades, 1):
            print(f"\nTrade {i}:")
            print(f"  Asset: {trade['asset']}")
            print(f"  Side: {trade['side']}")
            print(f"  Entry: ${trade['entry']:,.2f}")
            print(f"  Quantity: {trade['quantity']:.6f}")
            print(f"  Stop Loss: ${trade['stop_loss']:,.2f}")
            print(f"  Take Profit: ${trade['take_profit']:,.2f}")
            print(f"  Risk: 5% (${trade['entry'] * trade['quantity'] * 0.05:.2f})")
            print(f"  Potential Reward: 10% (${trade['entry'] * trade['quantity'] * 0.10:.2f})")
            print(f"  Reason: {trade['reason']}")
            
            position_value = trade['entry'] * trade['quantity']
            total_risk += position_value * 0.05
        
        print(f"\nTotal capital at risk: ${total_risk:.2f} ({total_risk/1000*100:.1f}% of capital)")
    
    return trades

if __name__ == "__main__":
    main()