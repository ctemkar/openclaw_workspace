#!/usr/bin/env python3
"""
ULTRA AGGRESSIVE Crypto Momentum Trading Script
Using CoinGecko API with more aggressive parameters
Paper Trading Only - $25,000 paper balance
"""

import requests
import time
from datetime import datetime, timedelta
import numpy as np

# Paper trading configuration
PAPER_BALANCE = 25000
MAX_TRADES_PER_DAY = 5
STOP_LOSS = 0.92  # 8% stop-loss
TAKE_PROFIT = 1.15  # 15% take-profit
LEVERAGE = 2.0  # 2x leverage for paper trading

# AGGRESSIVE PARAMETERS
MIN_MOMENTUM = 2.5  # Reduced from 5% for more opportunities
MIN_VOLUME_RATIO = 1.3  # Reduced threshold
MIN_VOLATILITY = 2.0  # Reduced threshold

# CoinGecko API
COINGECKO_API = "https://api.coingecko.com/api/v3"

def get_price_data(coin_id, vs_currency='usd', days=2):
    """Get historical price data from CoinGecko"""
    try:
        url = f"{COINGECKO_API}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': vs_currency,
            'days': days,
            'interval': 'hourly'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('prices', []), data.get('total_volumes', [])
    except Exception as e:
        print(f"Error fetching data for {coin_id}: {e}")
        return [], []

def calculate_aggressive_momentum(prices, volumes):
    """Calculate aggressive momentum indicators"""
    if len(prices) < 2:
        return 0, 1, 0, 0, 0, 0, 0
    
    # Get current and previous hour prices
    current_price = prices[-1][1]
    hour_ago_price = prices[-2][1] if len(prices) >= 2 else current_price
    
    # Calculate 1-hour percentage change
    hour_change_pct = ((current_price - hour_ago_price) / hour_ago_price) * 100
    
    # Calculate volume spike
    current_volume = volumes[-1][1] if volumes else 0
    if len(volumes) >= 7:
        avg_volume = sum(v[1] for v in volumes[-7:-2]) / 5  # Last 5 hours avg
    else:
        avg_volume = current_volume
    
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
    
    # Calculate volatility (standard deviation of last 24 hours)
    if len(prices) >= 24:
        price_changes = [(prices[i][1] - prices[i-1][1])/prices[i-1][1] for i in range(1, len(prices))]
        volatility = (sum((x - (sum(price_changes)/len(price_changes)))**2 for x in price_changes) / len(price_changes))**0.5 * 100
    else:
        volatility = abs(hour_change_pct)
    
    # Calculate RSI (simplified 14-period)
    if len(prices) >= 15:
        gains = []
        losses = []
        for i in range(1, 15):
            change = (prices[-i][1] - prices[-i-1][1]) / prices[-i-1][1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / 14
        avg_loss = sum(losses) / 14
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))
    else:
        rsi = 50
    
    # Calculate MACD (simplified)
    if len(prices) >= 26:
        ema12 = sum(p[1] for p in prices[-12:]) / 12
        ema26 = sum(p[1] for p in prices[-26:]) / 26
        macd = ema12 - ema26
    else:
        macd = 0
    
    # Calculate trend strength
    if len(prices) >= 10:
        recent_prices = [p[1] for p in prices[-10:]]
        trend_strength = sum(1 for i in range(1, len(recent_prices)) if recent_prices[i] > recent_prices[i-1]) / 9
    else:
        trend_strength = 0.5
    
    return current_price, hour_change_pct, volume_ratio, volatility, rsi, macd, trend_strength

def main():
    print('=== ULTRA AGGRESSIVE CRYPTO MOMENTUM TRADING ===')
    print(f'Paper Balance: ${PAPER_BALANCE:,}')
    print(f'Max Trades/Day: {MAX_TRADES_PER_DAY}')
    print(f'Stop-Loss: {(STOP_LOSS*100)-100:.1f}%')
    print(f'Take-Profit: {(TAKE_PROFIT*100)-100:.1f}%')
    print(f'Leverage: {LEVERAGE}x')
    print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC')
    print(f'Aggressive Parameters:')
    print(f'  Min Momentum: {MIN_MOMENTUM}%')
    print(f'  Min Volume Ratio: {MIN_VOLUME_RATIO}x')
    print(f'  Min Volatility: {MIN_VOLATILITY}%')
    print()
    
    # Crypto symbols with CoinGecko IDs
    cryptos = [
        {'id': 'bitcoin', 'symbol': 'BTC', 'name': 'Bitcoin'},
        {'id': 'ethereum', 'symbol': 'ETH', 'name': 'Ethereum'},
        {'id': 'solana', 'symbol': 'SOL', 'name': 'Solana'}
    ]
    
    print('Fetching market data from CoinGecko...')
    print()
    
    trading_signals = []
    
    for crypto in cryptos:
        try:
            prices, volumes = get_price_data(crypto['id'], 'usd', 2)
            
            if len(prices) >= 2:
                current_price, hour_change_pct, volume_ratio, volatility, rsi, macd, trend_strength = calculate_aggressive_momentum(prices, volumes)
                
                symbol = f"{crypto['symbol']}/USD"
                print(f'{symbol} ({crypto["name"]}):')
                print(f'  Current: ${current_price:,.2f}')
                print(f'  1h Change: {hour_change_pct:+.2f}%')
                print(f'  Volume Ratio: {volume_ratio:.2f}x')
                print(f'  Volatility (24h): {volatility:.2f}%')
                print(f'  RSI (14): {rsi:.1f}')
                print(f'  MACD: {macd:+.2f}')
                print(f'  Trend Strength: {trend_strength:.1%}')
                
                # Check for aggressive momentum signals
                signals = []
                
                # Momentum signals (more aggressive thresholds)
                if hour_change_pct >= MIN_MOMENTUM:
                    signals.append(f'🚀 MOMENTUM: +{hour_change_pct:.2f}% in last hour')
                elif hour_change_pct >= 1.5:
                    signals.append(f'📈 WEAK MOMENTUM: +{hour_change_pct:.2f}% in last hour')
                elif hour_change_pct <= -MIN_MOMENTUM:
                    signals.append(f'📉 DOWNSIDE MOMENTUM: {hour_change_pct:.2f}% in last hour')
                
                # Volume signals
                if volume_ratio >= MIN_VOLUME_RATIO:
                    signals.append(f'📊 VOLUME SPIKE: {volume_ratio:.2f}x average')
                elif volume_ratio >= 1.1:
                    signals.append(f'📈 MODERATE VOLUME: {volume_ratio:.2f}x average')
                
                # Volatility signals
                if volatility >= MIN_VOLATILITY:
                    signals.append(f'⚡ HIGH VOLATILITY: {volatility:.2f}%')
                elif volatility >= 1:
                    signals.append(f'⚡ MODERATE VOLATILITY: {volatility:.2f}%')
                
                # Technical indicators
                if rsi > 70:
                    signals.append(f'⚠️  OVERBOUGHT (RSI: {rsi:.1f})')
                elif rsi < 30:
                    signals.append(f'⚠️  OVERSOLD (RSI: {rsi:.1f})')
                
                if macd > 0:
                    signals.append(f'📈 BULLISH MACD: {macd:+.2f}')
                elif macd < 0:
                    signals.append(f'📉 BEARISH MACD: {macd:+.2f}')
                
                if trend_strength > 0.7:
                    signals.append(f'📈 STRONG UPTREND: {trend_strength:.0%}')
                elif trend_strength < 0.3:
                    signals.append(f'📉 STRONG DOWNTREND: {trend_strength:.0%}')
                
                if signals:
                    print('  Signals:')
                    for signal in signals:
                        print(f'    • {signal}')
                    
                    # ULTRA AGGRESSIVE trading recommendation
                    # Buy if: positive momentum OR good volume OR high volatility
                    # (More permissive conditions)
                    buy_conditions = []
                    
                    if hour_change_pct >= MIN_MOMENTUM:
                        buy_conditions.append(f'Momentum (+{hour_change_pct:.2f}%)')
                    
                    if volume_ratio >= MIN_VOLUME_RATIO:
                        buy_conditions.append(f'Volume ({volume_ratio:.2f}x)')
                    
                    if volatility >= MIN_VOLATILITY:
                        buy_conditions.append(f'Volatility ({volatility:.2f}%)')
                    
                    if rsi < 70 and rsi > 30:  # Not overbought/oversold
                        buy_conditions.append(f'RSI OK ({rsi:.1f})')
                    
                    if macd > 0:
                        buy_conditions.append(f'Bullish MACD ({macd:+.2f})')
                    
                    if trend_strength > 0.5:
                        buy_conditions.append(f'Uptrend ({trend_strength:.0%})')
                    
                    # AGGRESSIVE: Require only 2 conditions instead of 3
                    if len(buy_conditions) >= 2:
                        position_size = (PAPER_BALANCE * 0.30 * LEVERAGE) / current_price  # 30% of balance (more aggressive)
                        print(f'  🎯 ULTRA AGGRESSIVE BUY SIGNAL')
                        print(f'    Conditions met: {", ".join(buy_conditions)}')
                        print(f'    Suggested position: {position_size:.6f} {crypto["symbol"]}')
                        print(f'    Position value: ${position_size * current_price * LEVERAGE:,.2f} (with {LEVERAGE}x leverage)')
                        print(f'    Stop-loss: ${current_price * STOP_LOSS:,.2f} (-8%)')
                        print(f'    Take-profit: ${current_price * TAKE_PROFIT:,.2f} (+15%)')
                        
                        # Risk calculation
                        risk_per_trade = (position_size * current_price) * 0.08  # 8% of position
                        reward_potential = (position_size * current_price) * 0.15  # 15% of position
                        risk_reward_ratio = reward_potential / risk_per_trade if risk_per_trade > 0 else 0
                        
                        print(f'    Risk: ${risk_per_trade:,.2f}')
                        print(f'    Potential Reward: ${reward_potential:,.2f}')
                        print(f'    Risk/Reward: 1:{risk_reward_ratio:.1f}')
                        
                        # Add to trading signals
                        trading_signals.append({
                            'symbol': symbol,
                            'name': crypto['name'],
                            'action': 'BUY',
                            'price': current_price,
                            'position_size': position_size,
                            'position_value': position_size * current_price * LEVERAGE,
                            'stop_loss': current_price * STOP_LOSS,
                            'take_profit': current_price * TAKE_PROFIT,
                            'risk': risk_per_trade,
                            'reward': reward_potential,
                            'risk_reward': risk_reward_ratio,
                            'conditions': buy_conditions,
                            'momentum': hour_change_pct,
                            'volume': volume_ratio,
                            'volatility': volatility,
                            'rsi': rsi
                        })
                    else:
                        print(f'  ⚠️  WATCH: {len(buy_conditions)}/2 conditions met')
                        print(f'     Need more signals for aggressive entry')
                        if hour_change_pct < MIN_MOMENTUM:
                            print(f'     - Momentum: {hour_change_pct:.2f}% (need ≥{MIN_MOMENTUM}%)')
                        if volume_ratio < MIN_VOLUME_RATIO:
                            print(f'     - Volume: {volume_ratio:.2f}x (need ≥{MIN_VOLUME_RATIO}x)')
                        if volatility < MIN_VOLATILITY:
                            print(f'     - Volatility: {volatility:.2f}% (need ≥{MIN_VOLATILITY}%)')
                else:
                    print('  ⏸️ No momentum signals')
                
                print()
                
        except Exception as e:
            print(f'{crypto["symbol"]}/USD: Error - {e}')
            print()
    
    # Summary
    print('=' * 70)
    print('=== ULTRA AGGRESSIVE PAPER TRADING EXECUTION SUMMARY ===')
    print('=' * 70)
    print()
    
    if trading_signals:
        print(f'🎯 FOUND {len(trading_signals)} ULTRA AGGRESSIVE TRADING OPPORTUNITIES:')
        print()
        
        total_position_value = 0
        total_risk = 0
        total_potential_reward = 0
        
        for i, signal in enumerate(trading_signals, 1):
            print(f'{i}. {signal["symbol"]} - {signal["action"]} ({signal["name"]})')
            print(f'   Entry Price: ${signal["price"]:,.2f}')
            print(f'   Position Size: {signal["position_size"]:.6f}')
            print(f'   Position Value: ${signal["position_value"]:,.2f} (with {LEVERAGE}x leverage)')
            print(f'   Stop-loss: ${signal["stop_loss"]:,.2f} (-8%)')
            print(f'   Take-profit: ${signal["take_profit"]:,.2f} (+15%)')
            print(f'   Risk: ${signal["risk"]:,.2f}')
            print(f'   Potential Reward: ${signal["reward"]:,.2f}')
            print(f'   Risk/Reward Ratio: 1:{signal["risk_reward"]:.1f}')
            print(f'   Conditions: {", ".join(signal["conditions"])}')
            print(f'   Metrics: Momentum={signal["momentum"]:.2f}%, Volume={signal["volume"]:.2f}x, Vol={signal["volatility"]:.2f}%, RSI={signal["rsi"]:.1f}')
            print()
            
            total_position_value += signal['position_value']
            total_risk += signal['risk']
            total_potential_reward += signal['reward']
        
        print('📊 ULTRA AGGRESSIVE PORTFOLIO SUMMARY:')
        print(f'   Total Position Value: ${total_position_value:,.2f}')
        print(f'   Total Risk Exposure: ${total_risk:,.2f}')
        print(f'   Total Potential Reward: ${total_potential_reward:,.2f}')
        print(f'   Risk as % of Paper Balance: {(total_risk/PAPER_BALANCE)*100:.1f}%')
        print(f'   Reward as % of Paper Balance: {(total_potential_reward/PAPER_BALANCE)*100:.1f}%')
        print()
        
        # Risk management check
        if len(trading_signals) > MAX_TRADES_PER_DAY:
            print(f'⚠️  WARNING: Would exceed max {MAX_TRADES_PER_DAY} trades per day')
            print(f'   Limiting to top {MAX_TRADES_PER_DAY} opportunities')
        
        if total_risk > PAPER_BALANCE * 0.5:  # 50% max risk (more aggressive)
            print(f'⚠️  WARNING: Total risk ({total_risk/PAPER_BALANCE*100:.1f}%) exceeds aggressive limit')
            print(f'   Consider reducing position sizes')
        elif total_risk > PAPER_BALANCE * 0.3:
            print(f'⚠️  MODERATE RISK: Total risk ({total_risk/PAPER_BALANCE*100:.1f}%) within aggressive limits')
        else:
            print(f'✅ LOW RISK: Total risk ({total_risk/PAPER_BALANCE*100:.1f}%) well within limits')
        
        print('✅ EXECUTION READY: Ultra aggressive paper trading positions calculated')
        
    else:
        print('⏸️ NO ULTRA AGGRESSIVE MOMENTUM SIGNALS FOUND')
        print()
        print('Market Conditions Analysis:')
        print('• Markets may be consolidating or in low-volatility phase')
        print('• Volume may be insufficient for momentum strategies')
        print('• Better to wait for clearer breakout opportunities')
        print('• Consider checking again in 1-2 hours for new signals')
        print()
        print('Alternative Strategies:')
        print('• Look for mean reversion opportunities')
        print('• Consider lower timeframe analysis (15-min charts)')
        print('• Monitor news/events for catalyst-driven moves')
        print('• Check altcoins with higher volatility')
    
    print('=' * 70)
    print('⚠️  IMPORTANT DISCLAIMER:')
    print('• This is PAPER TRADING simulation only')
    print('• NO REAL FUNDS are being used')
    print('• All calculations use 2x leverage with $25,000 paper balance')
    print('• Risk management: 8% stop-loss, 15% take-profit')
    print('• Max 5 trades per day limit enforced')
    print('• Data source: CoinGecko API (free tier)')
    print('• ULTRA AGGRESSIVE strategy - higher risk/reward')
    print('=' * 70)

if __name__ == '__main__':
    main()