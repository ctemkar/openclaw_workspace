#!/usr/bin/env python3
"""
Market Analysis Script for Gemini Exchange
"""

import requests
import json
from datetime import datetime

def get_gemini_ticker(symbol):
    """Get ticker data from Gemini"""
    url = f'https://api.gemini.com/v1/pubticker/{symbol}'
    response = requests.get(url)
    return response.json()

def get_gemini_order_book(symbol):
    """Get order book data from Gemini"""
    url = f'https://api.gemini.com/v1/book/{symbol}'
    response = requests.get(url)
    return response.json()

def analyze_market(symbol):
    """Analyze market conditions for a trading pair"""
    ticker = get_gemini_ticker(symbol)
    order_book = get_gemini_order_book(symbol)
    
    current_price = float(ticker['last'])
    change_24h = float(ticker.get('percentChange24h', 0))
    
    # Calculate bid/ask volume for sentiment
    bids = order_book.get('bids', [])
    asks = order_book.get('asks', [])
    
    bid_volume = sum(float(bid['amount']) for bid in bids[:5]) if bids else 0
    ask_volume = sum(float(ask['amount']) for ask in asks[:5]) if asks else 0
    
    if bid_volume > ask_volume * 1.2:
        sentiment = 'BULLISH'
    elif ask_volume > bid_volume * 1.2:
        sentiment = 'BEARISH'
    else:
        sentiment = 'NEUTRAL'
    
    # Calculate support/resistance
    if len(bids) >= 3:
        support = sum(float(bid['price']) for bid in bids[:3]) / 3
    else:
        support = current_price * 0.98
    
    if len(asks) >= 3:
        resistance = sum(float(ask['price']) for ask in asks[:3]) / 3
    else:
        resistance = current_price * 1.02
    
    return {
        'symbol': symbol.upper(),
        'price': current_price,
        'change_24h': change_24h,
        'sentiment': sentiment,
        'support': support,
        'resistance': resistance,
        'bid_volume': bid_volume,
        'ask_volume': ask_volume
    }

def main():
    """Main analysis function"""
    print('=' * 60)
    print('CRYPTO MARKET ANALYSIS - Gemini Exchange')
    print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)
    
    pairs = ['btcusd', 'ethusd']
    results = []
    
    for pair in pairs:
        analysis = analyze_market(pair)
        results.append(analysis)
        
        print(f'\n{pair.upper()}:')
        print(f'  Current Price: ${analysis["price"]:,.2f}')
        print(f'  24h Change: {analysis["change_24h"]:+.2f}%')
        print(f'  Market Sentiment: {analysis["sentiment"]}')
        print(f'  Support Level: ${analysis["support"]:,.2f}')
        print(f'  Resistance Level: ${analysis["resistance"]:,.2f}')
        if analysis['ask_volume'] > 0:
            print(f'  Bid/Ask Volume Ratio: {analysis["bid_volume"]/analysis["ask_volume"]:.2f}')
    
    print('\n' + '=' * 60)
    print('TRADING RECOMMENDATIONS:')
    print('=' * 60)
    
    for analysis in results:
        if analysis['resistance'] > analysis['support']:
            price_position = (analysis['price'] - analysis['support']) / (analysis['resistance'] - analysis['support'])
        else:
            price_position = 0.5
        
        if analysis['sentiment'] == 'BULLISH' and price_position < 0.3:
            recommendation = 'CONSIDER BUY - Price near support with bullish sentiment'
        elif analysis['sentiment'] == 'BEARISH' and price_position > 0.7:
            recommendation = 'CONSIDER SELL - Price near resistance with bearish sentiment'
        else:
            recommendation = 'HOLD - Wait for better entry point'
        
        print(f'\n{analysis["symbol"]}: {recommendation}')
        print(f'  Price Position: {price_position:.1%} between support/resistance')
    
    print('\n' + '=' * 60)
    print('RISK PARAMETERS:')
    print('=' * 60)
    print('• Capital: $1,000')
    print('• Stop Loss: 5%')
    print('• Take Profit: 10%')
    print('• Max Daily Trades: 2')
    print('• Conservative Position Size: 25% of capital per trade')
    
    # Save analysis to file
    output = {
        'timestamp': datetime.now().isoformat(),
        'analyses': results,
        'parameters': {
            'capital': 1000,
            'stop_loss_pct': 5,
            'take_profit_pct': 10,
            'max_daily_trades': 2
        }
    }
    
    with open('market_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print('\nAnalysis saved to market_analysis.json')

if __name__ == "__main__":
    main()