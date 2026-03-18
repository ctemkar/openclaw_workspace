#!/usr/bin/env python3
"""
AGGRESSIVE CRYPTO MOMENTUM TRADING - PAPER TRADING ONLY
Executes aggressive momentum trading with $25,000 paper balance
Checks BTC/USD, ETH/USD, SOL/USD for momentum opportunities
"""

import requests
import time
from datetime import datetime
import json

print("=" * 80)
print("AGGRESSIVE CRYPTO MOMENTUM TRADING EXECUTION")
print("=" * 80)
print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
print(f"Paper Balance: $25,000")
print(f"Risk Parameters: 8% stop-loss, 15% take-profit")
print(f"Max Trades/Day: 5 | Leverage: 2x (paper trading only)")
print()

# CoinGecko API for real-time data
def get_crypto_price(coin_id):
    """Get current price from CoinGecko"""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd',
            'include_market_cap': 'false',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        return data.get(coin_id, {})
    except Exception as e:
        print(f"Error fetching {coin_id}: {e}")
        return {}

def get_market_chart(coin_id, days=1):
    """Get hourly price data for momentum analysis"""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'hourly'
        }
        response = requests.get(url, params=params, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error fetching chart for {coin_id}: {e}")
        return {'prices': [], 'total_volumes': []}

def analyze_momentum(prices, volumes):
    """Analyze momentum from price data"""
    if len(prices) < 2:
        return 0, 0, 0, 0, 0
    
    # Current and previous hour
    current_price = prices[-1][1]
    hour_ago_price = prices[-2][1] if len(prices) >= 2 else current_price
    two_hours_ago = prices[-3][1] if len(prices) >= 3 else hour_ago_price
    
    # Calculate momentum
    hour_change = ((current_price - hour_ago_price) / hour_ago_price) * 100
    two_hour_change = ((current_price - two_hours_ago) / two_hours_ago) * 100
    
    # Volume analysis
    current_volume = volumes[-1][1] if volumes else 0
    avg_volume = sum(v[1] for v in volumes[-6:-1]) / 5 if len(volumes) >= 6 else current_volume
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
    
    # Volatility (last 6 hours)
    if len(prices) >= 7:
        recent_prices = [p[1] for p in prices[-7:]]
        price_changes = [(recent_prices[i] - recent_prices[i-1])/recent_prices[i-1] for i in range(1, len(recent_prices))]
        volatility = (sum((x - (sum(price_changes)/len(price_changes)))**2 for x in price_changes) / len(price_changes))**0.5 * 100
    else:
        volatility = abs(hour_change)
    
    return current_price, hour_change, two_hour_change, volume_ratio, volatility

def generate_trading_signals():
    """Generate aggressive momentum trading signals"""
    print("📊 FETCHING MARKET DATA...")
    print()
    
    cryptos = [
        {'id': 'bitcoin', 'symbol': 'BTC', 'name': 'Bitcoin'},
        {'id': 'ethereum', 'symbol': 'ETH', 'name': 'Ethereum'},
        {'id': 'solana', 'symbol': 'SOL', 'name': 'Solana'}
    ]
    
    signals = []
    
    for crypto in cryptos:
        print(f"Analyzing {crypto['symbol']}/USD ({crypto['name']})...")
        
        # Get current price
        price_data = get_crypto_price(crypto['id'])
        current_price = price_data.get('usd', 0)
        daily_change = price_data.get('usd_24h_change', 0)
        
        # Get hourly data for momentum
        chart_data = get_market_chart(crypto['id'], 1)
        prices = chart_data.get('prices', [])
        volumes = chart_data.get('total_volumes', [])
        
        if len(prices) >= 3:
            current_price, hour_change, two_hour_change, volume_ratio, volatility = analyze_momentum(prices, volumes)
            
            print(f"  Current: ${current_price:,.2f}")
            print(f"  1h Change: {hour_change:+.2f}%")
            print(f"  2h Change: {two_hour_change:+.2f}%")
            print(f"  Volume Ratio: {volume_ratio:.2f}x")
            print(f"  Volatility: {volatility:.2f}%")
            
            # AGGRESSIVE MOMENTUM CRITERIA
            momentum_signals = []
            
            # Primary momentum signal (5%+ in last hour)
            if hour_change >= 5.0:
                momentum_signals.append(f"🚀 STRONG MOMENTUM: +{hour_change:.2f}% in 1h")
            elif hour_change >= 2.5:
                momentum_signals.append(f"📈 MODERATE MOMENTUM: +{hour_change:.2f}% in 1h")
            
            # Volume spike
            if volume_ratio >= 1.5:
                momentum_signals.append(f"📊 HIGH VOLUME: {volume_ratio:.2f}x average")
            elif volume_ratio >= 1.2:
                momentum_signals.append(f"📈 ELEVATED VOLUME: {volume_ratio:.2f}x average")
            
            # Volatility
            if volatility >= 3.0:
                momentum_signals.append(f"⚡ HIGH VOLATILITY: {volatility:.2f}%")
            
            # Trend confirmation
            if hour_change > 0 and two_hour_change > 0:
                momentum_signals.append(f"📈 CONFIRMED UPTREND: +{two_hour_change:.2f}% in 2h")
            
            if momentum_signals:
                print("  Signals detected:")
                for signal in momentum_signals:
                    print(f"    • {signal}")
                
                # AGGRESSIVE TRADING DECISION
                # Buy if: strong momentum OR (moderate momentum + volume spike)
                buy_conditions = []
                
                if hour_change >= 5.0:
                    buy_conditions.append("Strong momentum (5%+)")
                elif hour_change >= 2.5 and volume_ratio >= 1.2:
                    buy_conditions.append("Moderate momentum + volume")
                
                if volatility >= 2.0:
                    buy_conditions.append("High volatility")
                
                if len(buy_conditions) >= 1:  # AGGRESSIVE: Only need 1 condition
                    print(f"  🎯 AGGRESSIVE BUY SIGNAL!")
                    
                    # Calculate position size (aggressive: 40% of paper balance)
                    position_value = 25000 * 0.40 * 2.0  # 40% with 2x leverage
                    position_size = position_value / current_price
                    
                    stop_loss = current_price * 0.92  # 8% stop-loss
                    take_profit = current_price * 1.15  # 15% take-profit
                    
                    risk = (position_size * current_price) * 0.08
                    reward = (position_size * current_price) * 0.15
                    risk_reward = reward / risk if risk > 0 else 0
                    
                    signals.append({
                        'symbol': f"{crypto['symbol']}/USD",
                        'action': 'BUY',
                        'price': current_price,
                        'position_size': position_size,
                        'position_value': position_value,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'risk': risk,
                        'reward': reward,
                        'risk_reward': risk_reward,
                        'momentum': hour_change,
                        'volume': volume_ratio,
                        'volatility': volatility,
                        'conditions': buy_conditions
                    })
                    
                    print(f"    Position: {position_size:.6f} {crypto['symbol']}")
                    print(f"    Value: ${position_value:,.2f} (with 2x leverage)")
                    print(f"    Stop-loss: ${stop_loss:,.2f} (-8%)")
                    print(f"    Take-profit: ${take_profit:,.2f} (+15%)")
                    print(f"    Risk/Reward: 1:{risk_reward:.1f}")
                else:
                    print(f"  ⚠️  WATCH: Conditions not met for aggressive entry")
            else:
                print("  ⏸️  No momentum signals")
        else:
            print(f"  ⚠️  Insufficient data for analysis")
        
        print()
    
    return signals

def main():
    """Main execution function"""
    print("🔍 SCANNING FOR AGGRESSIVE MOMENTUM OPPORTUNITIES...")
    print()
    
    signals = generate_trading_signals()
    
    print("=" * 80)
    print("📋 AGGRESSIVE PAPER TRADING EXECUTION SUMMARY")
    print("=" * 80)
    print()
    
    if signals:
        print(f"🎯 FOUND {len(signals)} AGGRESSIVE TRADING OPPORTUNITIES:")
        print()
        
        total_position_value = 0
        total_risk = 0
        total_reward = 0
        
        for i, signal in enumerate(signals, 1):
            print(f"{i}. {signal['symbol']} - {signal['action']}")
            print(f"   Entry Price: ${signal['price']:,.2f}")
            print(f"   Position Size: {signal['position_size']:.6f}")
            print(f"   Position Value: ${signal['position_value']:,.2f}")
            print(f"   Stop-loss: ${signal['stop_loss']:,.2f} (-8%)")
            print(f"   Take-profit: ${signal['take_profit']:,.2f} (+15%)")
            print(f"   Risk: ${signal['risk']:,.2f}")
            print(f"   Potential Reward: ${signal['reward']:,.2f}")
            print(f"   Risk/Reward Ratio: 1:{signal['risk_reward']:.1f}")
            print(f"   Conditions: {', '.join(signal['conditions'])}")
            print(f"   Metrics: Momentum={signal['momentum']:.2f}%, Volume={signal['volume']:.2f}x, Vol={signal['volatility']:.2f}%")
            print()
            
            total_position_value += signal['position_value']
            total_risk += signal['risk']
            total_reward += signal['reward']
        
        print("📊 PORTFOLIO SUMMARY:")
        print(f"   Total Position Value: ${total_position_value:,.2f}")
        print(f"   Total Risk Exposure: ${total_risk:,.2f}")
        print(f"   Total Potential Reward: ${total_reward:,.2f}")
        print(f"   Risk as % of Paper Balance: {(total_risk/25000)*100:.1f}%")
        print(f"   Reward as % of Paper Balance: {(total_reward/25000)*100:.1f}%")
        print()
        
        # Risk management
        if len(signals) > 5:
            print(f"⚠️  WARNING: Would exceed max 5 trades per day")
            print(f"   Limiting to top 5 opportunities")
        
        if total_risk > 25000 * 0.5:
            print(f"⚠️  WARNING: High risk exposure ({(total_risk/25000)*100:.1f}%)")
        elif total_risk > 25000 * 0.3:
            print(f"⚠️  MODERATE RISK: {(total_risk/25000)*100:.1f}% exposure")
        else:
            print(f"✅ ACCEPTABLE RISK: {(total_risk/25000)*100:.1f}% exposure")
        
        print()
        print("✅ PAPER TRADING EXECUTION READY")
        print("   All positions calculated with 2x leverage")
        print("   Stop-losses and take-profits set")
        print("   Risk management parameters applied")
        
    else:
        print("⏸️  NO AGGRESSIVE MOMENTUM SIGNALS FOUND")
        print()
        print("Market Analysis:")
        print("• Markets may be in consolidation phase")
        print("• Insufficient momentum for aggressive strategy")
        print("• Consider checking again in 30-60 minutes")
        print("• Alternative: Look for breakout patterns on lower timeframes")
    
    print()
    print("=" * 80)
    print("⚠️  DISCLAIMER: PAPER TRADING ONLY - NO REAL FUNDS")
    print("• $25,000 paper balance simulation")
    print("• 2x leverage for paper trading only")
    print("• 8% stop-loss, 15% take-profit risk parameters")
    print("• Max 5 trades per day limit")
    print("• Data source: CoinGecko API")
    print("=" * 80)

if __name__ == '__main__':
    main()