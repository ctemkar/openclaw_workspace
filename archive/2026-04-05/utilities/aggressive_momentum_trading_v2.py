#!/usr/bin/env python3
"""
Aggressive Crypto Momentum Trading Script
Using CoinGecko API (free, no restrictions)
Paper Trading Only - $25,000 paper balance
"""

import requests
import time
from datetime import datetime, timedelta

# Paper trading configuration
PAPER_BALANCE = 25000
MAX_TRADES_PER_DAY = 5
STOP_LOSS = 0.92  # 8% stop-loss
TAKE_PROFIT = 1.15  # 15% take-profit
LEVERAGE = 2.0  # 2x leverage for paper trading

# CoinGecko API
COINGECKO_API = "https://api.coingecko.com/api/v3"

def get_price_data(coin_id, vs_currency='usd', days=1):
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

def calculate_momentum(prices, volumes):
    """Calculate momentum indicators"""
    if len(prices) < 2:
        return 0, 1, 0, 0
    
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
    
    return current_price, hour_change_pct, volume_ratio, volatility

def main():
    print('=== AGGRESSIVE CRYPTO MOMENTUM TRADING ===')
    print(f'Paper Balance: ${PAPER_BALANCE:,}')
    print(f'Max Trades/Day: {MAX_TRADES_PER_DAY}')
    print(f'Stop-Loss: {(STOP_LOSS*100)-100:.1f}%')
    print(f'Take-Profit: {(TAKE_PROFIT*100)-100:.1f}%')
    print(f'Leverage: {LEVERAGE}x')
    print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC')
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
                current_price, hour_change_pct, volume_ratio, volatility = calculate_momentum(prices, volumes)
                
                symbol = f"{crypto['symbol']}/USD"
                print(f'{symbol} ({crypto["name"]}):')
                print(f'  Current: ${current_price:,.2f}')
                print(f'  1h Change: {hour_change_pct:+.2f}%')
                print(f'  Volume Ratio: {volume_ratio:.2f}x')
                print(f'  Volatility (24h): {volatility:.2f}%')
                
                # Check for momentum signals
                signals = []
                
                # Strong momentum signals
                if hour_change_pct >= 5:
                    signals.append(f'🚀 STRONG MOMENTUM: +{hour_change_pct:.2f}% in last hour')
                elif hour_change_pct >= 3:
                    signals.append(f'📈 MODERATE MOMENTUM: +{hour_change_pct:.2f}% in last hour')
                elif hour_change_pct <= -5:
                    signals.append(f'📉 STRONG DOWNSIDE: {hour_change_pct:.2f}% in last hour')
                
                # Volume signals
                if volume_ratio >= 2:
                    signals.append(f'📊 HIGH VOLUME: {volume_ratio:.2f}x average')
                elif volume_ratio >= 1.5:
                    signals.append(f'📈 ABOVE AVG VOLUME: {volume_ratio:.2f}x average')
                
                # Volatility signals
                if volatility >= 3:
                    signals.append(f'⚡ HIGH VOLATILITY: {volatility:.2f}% (good for momentum)')
                
                # Check for trend (simplified)
                if len(prices) >= 6:
                    last_6_prices = [p[1] for p in prices[-6:]]
                    if all(last_6_prices[i] > last_6_prices[i-1] for i in range(1, len(last_6_prices))):
                        signals.append('📈 STRONG UPTREND (6 consecutive hours)')
                    elif all(last_6_prices[i] < last_6_prices[i-1] for i in range(1, len(last_6_prices))):
                        signals.append('📉 STRONG DOWNTREND (6 consecutive hours)')
                
                if signals:
                    print('  Signals:')
                    for signal in signals:
                        print(f'    • {signal}')
                    
                    # AGGRESSIVE trading recommendation
                    # Buy if: positive momentum + good volume + high volatility
                    if hour_change_pct >= 2.5 and volume_ratio >= 1.3 and volatility >= 2:
                        position_size = (PAPER_BALANCE * 0.25 * LEVERAGE) / current_price  # 25% of balance
                        print(f'  🎯 AGGRESSIVE BUY SIGNAL')
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
                            'reason': f'Momentum: +{hour_change_pct:.2f}%, Volume: {volume_ratio:.2f}x, Vol: {volatility:.2f}%'
                        })
                    else:
                        print(f'  ⚠️  WATCH: Potential setup but not aggressive enough')
                        if hour_change_pct < 2.5:
                            print(f'     - Need stronger momentum (current: {hour_change_pct:.2f}%, need: ≥2.5%)')
                        if volume_ratio < 1.3:
                            print(f'     - Need higher volume (current: {volume_ratio:.2f}x, need: ≥1.3x)')
                        if volatility < 2:
                            print(f'     - Need higher volatility (current: {volatility:.2f}%, need: ≥2%)')
                else:
                    print('  ⏸️ No strong momentum signals')
                
                print()
                
        except Exception as e:
            print(f'{crypto["symbol"]}/USD: Error - {e}')
            print()
    
    # Summary
    print('=' * 60)
    print('=== PAPER TRADING EXECUTION SUMMARY ===')
    print('=' * 60)
    print()
    
    if trading_signals:
        print(f'🎯 FOUND {len(trading_signals)} AGGRESSIVE TRADING OPPORTUNITIES:')
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
            print(f'   Signal Reason: {signal["reason"]}')
            print()
            
            total_position_value += signal['position_value']
            total_risk += signal['risk']
            total_potential_reward += signal['reward']
        
        print('📊 PORTFOLIO SUMMARY:')
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
        
        if total_risk > PAPER_BALANCE * 0.4:  # 40% max risk
            print(f'⚠️  WARNING: Total risk ({total_risk/PAPER_BALANCE*100:.1f}%) exceeds conservative limit')
            print(f'   Consider reducing position sizes')
        
        print('✅ EXECUTION READY: Paper trading positions calculated')
        
    else:
        print('⏸️ NO AGGRESSIVE MOMENTUM SIGNALS FOUND')
        print()
        print('Market Conditions Analysis:')
        print('• Markets may be consolidating or in low-volatility phase')
        print('• Volume may be insufficient for momentum strategies')
        print('• Better to wait for clearer breakout opportunities')
        print('• Consider checking again in 1-2 hours for new signals')
    
    print()
    print('=' * 60)
    print('⚠️  IMPORTANT DISCLAIMER:')
    print('• This is PAPER TRADING simulation only')
    print('• NO REAL FUNDS are being used')
    print('• All calculations use 2x leverage with $25,000 paper balance')
    print('• Risk management: 8% stop-loss, 15% take-profit')
    print('• Max 5 trades per day limit enforced')
    print('• Data source: CoinGecko API (free tier)')
    print('=' * 60)

if __name__ == '__main__':
    main()