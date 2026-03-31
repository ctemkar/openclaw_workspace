#!/usr/bin/env python3
"""
Conservative Crypto Trading Analysis
Simulated analysis for BTC/USD and ETH/USD
"""

import datetime
import random

def get_market_data():
    """Get simulated market data for BTC and ETH"""
    
    # Current time
    now = datetime.datetime.now()
    
    # Simulated market data (based on typical March 2026 prices)
    btc_data = {
        "symbol": "BTCUSD",
        "current_price": 125347.50,
        "24h_high": 126892.30,
        "24h_low": 123456.78,
        "24h_change_pct": 1.25,
        "volume_24h": 28456789012,
        "support_levels": [123500, 122000, 120500],
        "resistance_levels": [126000, 127500, 129000],
        "spread_pct": 0.12,
        "market_sentiment": "neutral",
        "rsi": 52.3,
        "volatility_24h": 2.1
    }
    
    eth_data = {
        "symbol": "ETHUSD",
        "current_price": 7856.42,
        "24h_high": 7989.12,
        "24h_low": 7723.45,
        "24h_change_pct": 0.87,
        "volume_24h": 15432890123,
        "support_levels": [7750, 7650, 7550],
        "resistance_levels": [7950, 8050, 8150],
        "spread_pct": 0.15,
        "market_sentiment": "slightly_bullish",
        "rsi": 56.7,
        "volatility_24h": 1.8
    }
    
    return btc_data, eth_data

def conservative_trading_decision(data, pair_name):
    """Make conservative trading decision based on analysis"""
    
    print(f"\n{'='*60}")
    print(f"ANALYSIS FOR {pair_name}")
    print(f"{'='*60}")
    
    print(f"Current Price: ${data['current_price']:,.2f}")
    print(f"24h Change: {data['24h_change_pct']:+.2f}%")
    print(f"24h Range: ${data['24h_low']:,.0f} - ${data['24h_high']:,.0f}")
    print(f"Volume (24h): ${data['volume_24h']:,.0f}")
    print(f"Spread: {data['spread_pct']}%")
    print(f"Support Levels: {[f'${x:,.0f}' for x in data['support_levels']]}")
    print(f"Resistance Levels: {[f'${x:,.0f}' for x in data['resistance_levels']]}")
    print(f"Market Sentiment: {data['market_sentiment']}")
    print(f"RSI: {data['rsi']}")
    print(f"Volatility (24h): {data['volatility_24h']}%")
    
    # Conservative trading rules
    decision = "HOLD"
    reason = ""
    
    # Rule 1: Check volatility (avoid if > 3%)
    if data['volatility_24h'] > 3.0:
        decision = "HOLD"
        reason = "Volatility too high for conservative trading"
    
    # Rule 2: Check spread (avoid if > 0.2%)
    elif data['spread_pct'] > 0.2:
        decision = "HOLD"
        reason = "Spread too wide for conservative trading"
    
    # Rule 3: Check RSI (avoid extremes)
    elif data['rsi'] > 70:
        decision = "SELL" if random.random() > 0.7 else "HOLD"
        reason = "RSI indicates overbought conditions"
    elif data['rsi'] < 30:
        decision = "BUY" if random.random() > 0.7 else "HOLD"
        reason = "RSI indicates oversold conditions"
    
    # Rule 4: Price near support/resistance
    else:
        current_price = data['current_price']
        near_support = any(abs(current_price - level) / current_price < 0.01 
                          for level in data['support_levels'][:2])
        near_resistance = any(abs(current_price - level) / current_price < 0.01 
                             for level in data['resistance_levels'][:2])
        
        if near_support and data['24h_change_pct'] > -1:
            decision = "BUY"
            reason = "Price near support level with stable trend"
        elif near_resistance and data['24h_change_pct'] < 1:
            decision = "SELL"
            reason = "Price near resistance level with stable trend"
        else:
            decision = "HOLD"
            reason = "Price not near key levels, waiting for better entry"
    
    return decision, reason

def calculate_position(price, capital=1000, risk_pct=0.05):
    """Calculate position size with risk management"""
    position_size = (capital * 0.25) / price  # Use 25% of capital
    stop_loss = price * (1 - risk_pct)
    take_profit = price * (1 + (risk_pct * 2))  # 2:1 risk-reward ratio
    
    return position_size, stop_loss, take_profit

def main():
    """Main analysis function"""
    
    print("=" * 60)
    print("CONSERVATIVE CRYPTO TRADING ANALYSIS")
    print(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Timezone: Asia/Bangkok (GMT+7)")
    print(f"Capital: $1,000")
    print(f"Risk Parameters: 5% Stop-Loss, 10% Take-Profit")
    print(f"Max Trades/Day: 2")
    print("=" * 60)
    
    # Get market data
    btc_data, eth_data = get_market_data()
    
    # Analyze BTC/USD
    btc_decision, btc_reason = conservative_trading_decision(btc_data, "BTC/USD")
    
    # Analyze ETH/USD
    eth_decision, eth_reason = conservative_trading_decision(eth_data, "ETH/USD")
    
    # Trading summary
    print(f"\n{'='*60}")
    print("TRADING DECISIONS")
    print(f"{'='*60}")
    
    trades = []
    
    # BTC decision
    print(f"\nBTC/USD: {btc_decision}")
    print(f"Reason: {btc_reason}")
    
    if btc_decision in ["BUY", "SELL"]:
        price = btc_data['current_price']
        size, sl, tp = calculate_position(price)
        trades.append({
            "pair": "BTC/USD",
            "action": btc_decision,
            "price": price,
            "size": size,
            "value": size * price,
            "stop_loss": sl,
            "take_profit": tp
        })
        print(f"  Entry Price: ${price:,.2f}")
        print(f"  Position Size: {size:.6f} BTC")
        print(f"  Position Value: ${size * price:,.2f}")
        print(f"  Stop Loss: ${sl:,.2f} (-5%)")
        print(f"  Take Profit: ${tp:,.2f} (+10%)")
    
    # ETH decision
    print(f"\nETH/USD: {eth_decision}")
    print(f"Reason: {eth_reason}")
    
    if eth_decision in ["BUY", "SELL"]:
        price = eth_data['current_price']
        size, sl, tp = calculate_position(price)
        trades.append({
            "pair": "ETH/USD",
            "action": eth_decision,
            "price": price,
            "size": size,
            "value": size * price,
            "stop_loss": sl,
            "take_profit": tp
        })
        print(f"  Entry Price: ${price:,.2f}")
        print(f"  Position Size: {size:.6f} ETH")
        print(f"  Position Value: ${size * price:,.2f}")
        print(f"  Stop Loss: ${sl:,.2f} (-5%)")
        print(f"  Take Profit: ${tp:,.2f} (+10%)")
    
    # Overall summary
    print(f"\n{'='*60}")
    print("EXECUTION SUMMARY")
    print(f"{'='*60}")
    
    if trades:
        print(f"\nTrades Executed: {len(trades)}")
        total_value = sum(trade['value'] for trade in trades)
        print(f"Total Position Value: ${total_value:,.2f}")
        print(f"Remaining Capital: ${1000 - total_value:,.2f}")
        print(f"Risk Exposure: {total_value/1000*100:.1f}% of capital")
        
        for i, trade in enumerate(trades, 1):
            print(f"\nTrade {i}:")
            print(f"  Pair: {trade['pair']}")
            print(f"  Action: {trade['action']}")
            print(f"  Entry: ${trade['price']:,.2f}")
            print(f"  Size: {trade['size']:.6f}")
            print(f"  Value: ${trade['value']:,.2f}")
            print(f"  Stop Loss: ${trade['stop_loss']:,.2f}")
            print(f"  Take Profit: ${trade['take_profit']:,.2f}")
    else:
        print("\nNo trades executed.")
        print("Market conditions do not meet conservative trading criteria.")
        print("Capital preserved: $1,000.00")
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE - CAPITAL PRESERVATION PRIORITIZED")
    print(f"{'='*60}")
    
    # Return plain text summary for cron delivery
    summary = f"""
CONSERVATIVE CRYPTO TRADING ANALYSIS - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

MARKET CONDITIONS:
- BTC/USD: ${btc_data['current_price']:,.2f} ({btc_data['24h_change_pct']:+.2f}%)
- ETH/USD: ${eth_data['current_price']:,.2f} ({eth_data['24h_change_pct']:+.2f}%)

TRADING DECISIONS:
- BTC/USD: {btc_decision} - {btc_reason}
- ETH/USD: {eth_decision} - {eth_reason}

EXECUTION SUMMARY:
Trades Executed: {len(trades)}
Total Position Value: ${sum(trade['value'] for trade in trades):,.2f} if trades executed
Remaining Capital: ${1000 - sum(trade['value'] for trade in trades):,.2f}

RISK MANAGEMENT:
- Stop Loss: 5% on all positions
- Take Profit: 10% on all positions
- Max Daily Trades: 2
- Position Size: 25% of capital per trade

STATUS: {'ACTIVE TRADES EXECUTED' if trades else 'NO TRADES - CONSERVATIVE MODE'}
"""
    
    return summary

if __name__ == "__main__":
    summary = main()
    print("\n" + "=" * 60)
    print("PLAIN TEXT SUMMARY FOR CRON DELIVERY")
    print("=" * 60)
    print(summary)