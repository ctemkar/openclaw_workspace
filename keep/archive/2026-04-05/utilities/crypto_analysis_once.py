#!/usr/bin/env python3
import ccxt
import json
import os
from datetime import datetime
import time

def log_bot(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_gemini_keys():
    try:
        with open("/Users/chetantemkar/.openclaw/workspace/app/.gemini_key", "r") as f:
            k = f.read().strip()
        with open("/Users/chetantemkar/.openclaw/workspace/app/.gemini_secret", "r") as f:
            s = f.read().strip()
        return k, s
    except Exception as e:
        log_bot(f"❌ Error reading API keys: {e}")
        return None, None

def analyze_market(exchange):
    """Analyze current market conditions"""
    try:
        # Get BTC/USD ticker
        ticker = exchange.fetch_ticker('BTC/USD')
        
        # Get recent trades
        trades = exchange.fetch_trades('BTC/USD', limit=10)
        
        # Get order book
        orderbook = exchange.fetch_order_book('BTC/USD', limit=5)
        
        return {
            'price': ticker['last'],
            'bid': ticker['bid'],
            'ask': ticker['ask'],
            'volume': ticker['baseVolume'],
            'change': ticker['percentage'],
            'high_24h': ticker['high'],
            'low_24h': ticker['low'],
            'recent_trades': len(trades),
            'bid_depth': sum([bid[1] for bid in orderbook['bids'][:3]]),
            'ask_depth': sum([ask[1] for ask in orderbook['asks'][:3]])
        }
    except Exception as e:
        log_bot(f"❌ Market analysis error: {e}")
        return None

def make_trading_decision(market_data, strategy):
    """Make trading decision based on market data and strategy"""
    if not market_data:
        return "No market data available"
    
    price = market_data['price']
    change = market_data['change']
    bid_depth = market_data['bid_depth']
    ask_depth = market_data['ask_depth']
    
    decision = {
        'timestamp': datetime.now().isoformat(),
        'price': price,
        'analysis': {},
        'decision': 'HOLD',
        'reason': 'No clear signal',
        'risk_level': 'LOW'
    }
    
    # Simple trading logic based on strategy
    if 'Gemini_Longs_Binance_Shorts' in strategy.get('name', ''):
        # Check for long conditions (Gemini)
        if change < -1.0:  # Price down > 1%
            if bid_depth > ask_depth * 1.5:  # Strong bid support
                decision['decision'] = 'CONSIDER_LONG'
                decision['reason'] = 'Price dip with strong bid support'
                decision['risk_level'] = 'MEDIUM'
        
        # Check for short conditions (would be Binance in dual strategy)
        elif change > 1.0:  # Price up > 1%
            if ask_depth > bid_depth * 1.5:  # Strong ask resistance
                decision['decision'] = 'CONSIDER_SHORT'
                decision['reason'] = 'Price rise with strong ask resistance'
                decision['risk_level'] = 'HIGH'
    
    decision['analysis'] = {
        'price_change_24h': f"{change:.2f}%",
        'bid_ask_ratio': f"{bid_depth/ask_depth:.2f}" if ask_depth > 0 else "N/A",
        'market_depth': f"Bid: {bid_depth:.4f} BTC, Ask: {ask_depth:.4f} BTC"
    }
    
    return decision

def main():
    log_bot("🚀 CRYPTO TRADING ANALYSIS - SINGLE RUN")
    log_bot("========================================")
    
    # Load strategy
    strategy_file = "/Users/chetantemkar/.openclaw/workspace/app/dual_exchange_strategy.json"
    try:
        with open(strategy_file, 'r') as f:
            strategy = json.load(f)
        log_bot(f"📊 Loaded strategy: {strategy['name']}")
        log_bot(f"📝 Description: {strategy['description']}")
    except Exception as e:
        log_bot(f"❌ Error loading strategy: {e}")
        strategy = {}
    
    # Connect to exchange
    api_key, secret = get_gemini_keys()
    if not api_key:
        log_bot("❌ Cannot proceed without API keys")
        return
    
    try:
        exchange = ccxt.gemini({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True
        })
        log_bot("✅ Connected to Gemini exchange")
    except Exception as e:
        log_bot(f"❌ Connection error: {e}")
        return
    
    # Analyze market
    log_bot("📈 Analyzing market conditions...")
    market_data = analyze_market(exchange)
    
    if market_data:
        price = market_data.get('price', 0) or 0
        change = market_data.get('change', 0) or 0
        high = market_data.get('high_24h', 0) or 0
        low = market_data.get('low_24h', 0) or 0
        volume = market_data.get('volume', 0) or 0
        
        log_bot(f"💰 Current BTC/USD Price: ${price:,.2f}")
        log_bot(f"📊 24h Change: {change:.2f}%")
        log_bot(f"📈 24h High: ${high:,.2f}")
        log_bot(f"📉 24h Low: ${low:,.2f}")
        log_bot(f"💹 Volume: {volume:.2f} BTC")
    
    # Make trading decision
    log_bot("🤖 Making trading decision...")
    decision = make_trading_decision(market_data, strategy)
    
    log_bot("🎯 TRADING DECISION:")
    log_bot(f"   Decision: {decision['decision']}")
    log_bot(f"   Reason: {decision['reason']}")
    log_bot(f"   Risk Level: {decision['risk_level']}")
    
    if decision['analysis']:
        log_bot("📊 ANALYSIS METRICS:")
        for key, value in decision['analysis'].items():
            log_bot(f"   {key}: {value}")
    
    log_bot("========================================")
    log_bot("✅ Analysis complete")
    
    # Print summary for cron delivery
    print("\n" + "="*50)
    print("CRYPTO TRADING BOT SUMMARY")
    print("="*50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Exchange: Gemini")
    if market_data:
        price = market_data.get('price', 0) or 0
        change = market_data.get('change', 0) or 0
        print(f"BTC/USD Price: ${price:,.2f}")
        print(f"24h Change: {change:.2f}%")
    print(f"Strategy: {strategy.get('name', 'Default')}")
    print(f"Decision: {decision['decision']}")
    print(f"Reason: {decision['reason']}")
    print(f"Risk Level: {decision['risk_level']}")
    print("="*50)

if __name__ == "__main__":
    main()