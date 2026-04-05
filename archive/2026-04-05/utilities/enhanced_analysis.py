#!/usr/bin/env python3
"""
Enhanced Crypto Analysis with Simulated Trade Example
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Initialize exchange (sandbox mode)
exchange = ccxt.gemini({
    'sandbox': True,
    'enableRateLimit': True,
})

def get_detailed_analysis(symbol):
    """Get detailed technical analysis for a symbol"""
    print(f"\n{'='*60}")
    print(f"DETAILED ANALYSIS: {symbol}")
    print(f"{'='*60}")
    
    # Fetch OHLCV data
    ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=100)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Calculate indicators
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['SMA_50'] = df['close'].rolling(window=50).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
    df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
    
    # Get current ticker
    ticker = exchange.fetch_ticker(symbol)
    
    latest = df.iloc[-1]
    
    print(f"Current Price: ${ticker['last']:.2f}")
    print(f"24h Change: {ticker['percentage']:.2f}%")
    print(f"24h High: ${ticker['high']:.2f}")
    print(f"24h Low: ${ticker['low']:.2f}")
    print(f"24h Volume: {ticker['baseVolume']:.2f}")
    print(f"\nTechnical Indicators:")
    print(f"  SMA 20: ${latest['SMA_20']:.2f}")
    print(f"  SMA 50: ${latest['SMA_50']:.2f}")
    print(f"  RSI: {latest['RSI']:.2f}")
    print(f"  Bollinger Upper: ${latest['BB_upper']:.2f}")
    print(f"  Bollinger Lower: ${latest['BB_lower']:.2f}")
    
    # Generate signal
    signal = "HOLD"
    reason = []
    
    if latest['RSI'] < 30:
        signal = "BUY"
        reason.append("RSI indicates oversold conditions")
    elif latest['RSI'] > 70:
        signal = "SELL"
        reason.append("RSI indicates overbought conditions")
    
    if latest['close'] > latest['SMA_20'] > latest['SMA_50']:
        if signal == "HOLD":
            signal = "BUY"
        reason.append("Bullish SMA alignment")
    elif latest['close'] < latest['SMA_20'] < latest['SMA_50']:
        if signal == "HOLD":
            signal = "SELL"
        reason.append("Bearish SMA alignment")
    
    print(f"\nTrading Signal: {signal}")
    if reason:
        print(f"Reason: {'; '.join(reason)}")
    
    return signal, ticker['last']

def simulate_conservative_trade():
    """Simulate a conservative trade with risk management"""
    print(f"\n{'='*60}")
    print(f"SIMULATED CONSERVATIVE TRADE EXAMPLE")
    print(f"{'='*60}")
    
    capital = 1000
    position_size_pct = 40
    stop_loss_pct = 5
    take_profit_pct = 10
    
    # Simulate BTC/USD trade
    symbol = "BTC/USD"
    entry_price = 67000.00
    position_value = capital * (position_size_pct / 100)
    quantity = position_value / entry_price
    
    stop_loss = entry_price * (1 - stop_loss_pct / 100)
    take_profit = entry_price * (1 + take_profit_pct / 100)
    
    print(f"Symbol: {symbol}")
    print(f"Entry Price: ${entry_price:.2f}")
    print(f"Position Size: ${position_value:.2f} ({position_size_pct}% of capital)")
    print(f"Quantity: {quantity:.6f} BTC")
    print(f"Stop-Loss: ${stop_loss:.2f} ({stop_loss_pct}% below entry)")
    print(f"Take-Profit: ${take_profit:.2f} ({take_profit_pct}% above entry)")
    print(f"\nRisk/Reward Ratio: 1:{take_profit_pct/stop_loss_pct:.1f}")
    print(f"Maximum Loss: ${position_value * (stop_loss_pct/100):.2f}")
    print(f"Potential Profit: ${position_value * (take_profit_pct/100):.2f}")
    
    return {
        'symbol': symbol,
        'entry': entry_price,
        'quantity': quantity,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'risk_amount': position_value * (stop_loss_pct/100),
        'reward_amount': position_value * (take_profit_pct/100)
    }

def main():
    print("ENHANCED CRYPTO MARKET ANALYSIS")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Timezone: Asia/Bangkok (GMT+7)")
    
    # Analyze major pairs
    symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD']
    
    signals = {}
    for symbol in symbols:
        try:
            signal, price = get_detailed_analysis(symbol)
            signals[symbol] = {'signal': signal, 'price': price}
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
    
    # Simulate conservative trade
    trade = simulate_conservative_trade()
    
    # Generate final recommendation
    print(f"\n{'='*60}")
    print(f"FINAL RECOMMENDATION")
    print(f"{'='*60}")
    
    buy_signals = [s for s in signals.values() if s['signal'] == 'BUY']
    sell_signals = [s for s in signals.values() if s['signal'] == 'SELL']
    
    if buy_signals:
        print(f"BUY Opportunities ({len(buy_signals)}):")
        for symbol, data in signals.items():
            if data['signal'] == 'BUY':
                print(f"  • {symbol} at ${data['price']:.2f}")
    
    if sell_signals:
        print(f"\nSELL Opportunities ({len(sell_signals)}):")
        for symbol, data in signals.items():
            if data['signal'] == 'SELL':
                print(f"  • {symbol} at ${data['price']:.2f}")
    
    if not buy_signals and not sell_signals:
        print("No strong trading signals detected.")
        print("Recommendation: HOLD and wait for clearer market direction.")
    
    print(f"\nConservative Strategy Reminder:")
    print(f"• Maximum 2 trades per day")
    print(f"• 5% stop-loss on all positions")
    print(f"• 10% take-profit targets")
    print(f"• 40% position sizing per trade")
    print(f"• Total capital: $1,000")
    
    print(f"\nNext analysis scheduled in 1 hour.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()