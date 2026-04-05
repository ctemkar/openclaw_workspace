#!/usr/bin/env python3
"""
SAFETY MONITOR - Advanced risk protection for trading bots
Includes: Crash detection, news monitoring, technical indicators, social media alerts
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
import talib
import numpy as np
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class SafetyMonitor:
    """Advanced safety monitoring for trading bots"""
    
    def __init__(self):
        self.crash_threshold = -15.0  # -15% in 5 minutes = crash
        self.last_prices = {}
        self.price_history = {}
        self.last_news_check = None
        self.last_social_check = None
        
    # 1. MARKET CRASH DETECTION (Flash Crash Protection)
    def detect_market_crash(self, symbol: str, current_price: float) -> Dict:
        """Detect flash crashes and extreme volatility"""
        alerts = []
        
        # Track price history
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append({
            'timestamp': datetime.now(),
            'price': current_price
        })
        
        # Keep only last 30 minutes of data
        cutoff = datetime.now() - timedelta(minutes=30)
        self.price_history[symbol] = [
            p for p in self.price_history[symbol] 
            if p['timestamp'] > cutoff
        ]
        
        if len(self.price_history[symbol]) >= 10:  # Need enough data
            # Check for rapid price drop (>15% in 5 minutes)
            recent_prices = [p['price'] for p in self.price_history[symbol][-10:]]
            if len(recent_prices) >= 5:
                oldest_price = recent_prices[0]
                newest_price = recent_prices[-1]
                drop_percent = ((newest_price - oldest_price) / oldest_price) * 100
                
                if drop_percent < self.crash_threshold:
                    alerts.append({
                        'type': 'CRASH_DETECTED',
                        'severity': 'CRITICAL',
                        'message': f'🚨 FLASH CRASH: {symbol} dropped {abs(drop_percent):.1f}% in 5 minutes',
                        'action': 'IMMEDIATE_SELL'
                    })
            
            # Check for extreme volatility
            price_changes = []
            for i in range(1, len(recent_prices)):
                change = ((recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]) * 100
                price_changes.append(abs(change))
            
            if price_changes:
                avg_volatility = sum(price_changes) / len(price_changes)
                if avg_volatility > 5.0:  # >5% average change
                    alerts.append({
                        'type': 'EXTREME_VOLATILITY',
                        'severity': 'HIGH',
                        'message': f'⚡ Extreme volatility: {symbol} avg change {avg_volatility:.1f}%',
                        'action': 'REDUCE_POSITIONS'
                    })
        
        return alerts
    
    # 2. NEWS SENTIMENT MONITORING
    def check_news_sentiment(self, symbol: str = "crypto") -> List[Dict]:
        """Check for negative news that could impact markets"""
        alerts = []
        
        # Only check every 15 minutes to avoid rate limits
        if (self.last_news_check and 
            (datetime.now() - self.last_news_check).seconds < 900):
            return alerts
        
        self.last_news_check = datetime.now()
        
        try:
            # Check CryptoPanic API for crypto news
            response = requests.get(
                "https://cryptopanic.com/api/v1/posts/",
                params={
                    "auth_token": "",  # Would need API key
                    "currencies": "BTC,ETH",
                    "kind": "news"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                for post in data.get('results', [])[:5]:  # Check latest 5
                    title = post.get('title', '').lower()
                    votes = post.get('votes', {})
                    
                    # Check for negative keywords
                    negative_keywords = [
                        'hack', 'exploit', 'rug pull', 'scam', 'fraud',
                        'regulation', 'ban', 'lawsuit', 'sec', 'cfdc',
                        'crash', 'collapse', 'bankrupt', 'default'
                    ]
                    
                    for keyword in negative_keywords:
                        if keyword in title:
                            alerts.append({
                                'type': 'NEGATIVE_NEWS',
                                'severity': 'HIGH',
                                'message': f'📰 Negative news: {title[:100]}...',
                                'action': 'CONSIDER_SELLING',
                                'source': 'CryptoPanic'
                            })
                            break
        except Exception as e:
            logger.debug(f"News check failed: {e}")
        
        return alerts
    
    # 3. TECHNICAL INDICATORS (RSI, MACD, etc.)
    def check_technical_indicators(self, symbol: str, prices: List[float]) -> List[Dict]:
        """Check technical indicators for extreme signals"""
        alerts = []
        
        if len(prices) < 50:  # Need enough data
            return alerts
        
        # Convert to numpy array
        np_prices = np.array(prices)
        
        # RSI (Relative Strength Index)
        rsi = talib.RSI(np_prices, timeperiod=14)
        if len(rsi) > 0:
            current_rsi = rsi[-1]
            
            if current_rsi > 80:  # Overbought
                alerts.append({
                    'type': 'RSI_OVERBOUGHT',
                    'severity': 'MEDIUM',
                    'message': f'📊 {symbol} RSI: {current_rsi:.1f} (OVERBOUGHT >80)',
                    'action': 'CONSIDER_SELLING'
                })
            elif current_rsi < 20:  # Oversold
                alerts.append({
                    'type': 'RSI_OVERSOLD',
                    'severity': 'MEDIUM',
                    'message': f'📊 {symbol} RSI: {current_rsi:.1f} (OVERSOLD <20)',
                    'action': 'CONSIDER_BUYING'
                })
        
        # MACD (Moving Average Convergence Divergence)
        macd, macd_signal, macd_hist = talib.MACD(np_prices)
        if len(macd) > 0 and len(macd_signal) > 0:
            current_macd = macd[-1]
            current_signal = macd_signal[-1]
            
            # Strong bearish crossover
            if current_macd < current_signal and macd[-2] > macd_signal[-2]:
                alerts.append({
                    'type': 'MACD_BEARISH_CROSS',
                    'severity': 'MEDIUM',
                    'message': f'📊 {symbol} MACD bearish crossover',
                    'action': 'CONSIDER_SELLING'
                })
            
            # Strong bullish crossover
            if current_macd > current_signal and macd[-2] < macd_signal[-2]:
                alerts.append({
                    'type': 'MACD_BULLISH_CROSS',
                    'severity': 'MEDIUM',
                    'message': f'📊 {symbol} MACD bullish crossover',
                    'action': 'CONSIDER_BUYING'
                })
        
        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(np_prices)
        if len(upper) > 0 and len(lower) > 0:
            current_price = prices[-1]
            current_upper = upper[-1]
            current_lower = lower[-1]
            
            # Price above upper band (overbought)
            if current_price > current_upper:
                alerts.append({
                    'type': 'BOLLINGER_OVERBOUGHT',
                    'severity': 'MEDIUM',
                    'message': f'📊 {symbol} above Bollinger upper band',
                    'action': 'CONSIDER_SELLING'
                })
            
            # Price below lower band (oversold)
            if current_price < current_lower:
                alerts.append({
                    'type': 'BOLLINGER_OVERSOLD',
                    'severity': 'MEDIUM',
                    'message': f'📊 {symbol} below Bollinger lower band',
                    'action': 'CONSIDER_BUYING'
                })
        
        return alerts
    
    # 4. SOCIAL MEDIA ALERTS (Twitter/Reddit sentiment)
    def check_social_sentiment(self) -> List[Dict]:
        """Check social media for panic/fear sentiment"""
        alerts = []
        
        # Only check every 30 minutes
        if (self.last_social_check and 
            (datetime.now() - self.last_social_check).seconds < 1800):
            return alerts
        
        self.last_social_check = datetime.now()
        
        try:
            # Check Reddit r/CryptoCurrency for panic posts
            # Note: Would need Reddit API credentials for real implementation
            # This is a simplified version
            
            # Simulated check - in real implementation would use API
            panic_keywords = [
                'panic sell', 'market crash', 'getting out', 'losing everything',
                'rug pull', 'scammed', 'exit now', 'dump it', 'sell everything'
            ]
            
            # For now, return empty (would need API implementation)
            # alerts.append({
            #     'type': 'SOCIAL_PANIC',
            #     'severity': 'MEDIUM',
            #     'message': 'Social media showing fear sentiment',
            #     'action': 'MONITOR_CLOSELY'
            # })
            
            pass
            
        except Exception as e:
            logger.debug(f"Social check failed: {e}")
        
        return alerts
    
    # MAIN SAFETY CHECK - Run all monitors
    def run_safety_checks(self, symbol: str, current_price: float, 
                         price_history: List[float] = None) -> Dict:
        """Run all safety checks and return recommendations"""
        
        all_alerts = []
        recommendations = {
            'trade_allowed': True,
            'suggested_action': 'NORMAL',
            'alerts': []
        }
        
        # 1. Market crash detection
        crash_alerts = self.detect_market_crash(symbol, current_price)
        all_alerts.extend(crash_alerts)
        
        # 2. News sentiment
        news_alerts = self.check_news_sentiment(symbol.split('/')[0])
        all_alerts.extend(news_alerts)
        
        # 3. Technical indicators (if price history provided)
        if price_history and len(price_history) >= 50:
            tech_alerts = self.check_technical_indicators(symbol, price_history)
            all_alerts.extend(tech_alerts)
        
        # 4. Social media alerts
        social_alerts = self.check_social_sentiment()
        all_alerts.extend(social_alerts)
        
        # Process alerts and make recommendations
        critical_alerts = [a for a in all_alerts if a['severity'] == 'CRITICAL']
        high_alerts = [a for a in all_alerts if a['severity'] == 'HIGH']
        
        if critical_alerts:
            recommendations['trade_allowed'] = False
            recommendations['suggested_action'] = 'IMMEDIATE_SELL'
            logger.warning(f"🚨 CRITICAL ALERTS: Trading halted - {len(critical_alerts)} critical issues")
        
        elif high_alerts:
            recommendations['trade_allowed'] = True
            recommendations['suggested_action'] = 'REDUCE_RISK'
            logger.warning(f"⚠️ HIGH ALERTS: {len(high_alerts)} high-risk issues detected")
        
        recommendations['alerts'] = all_alerts
        
        # Log all alerts
        for alert in all_alerts:
            logger.info(f"🔔 Safety Alert [{alert['severity']}]: {alert['message']}")
        
        return recommendations

# Global safety monitor instance
safety_monitor = SafetyMonitor()

if __name__ == '__main__':
    # Test the safety monitor
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing Safety Monitor...")
    
    # Simulate price history
    test_prices = [100 + i + np.random.randn() for i in range(100)]
    
    # Run safety check
    result = safety_monitor.run_safety_checks(
        symbol="BTC/USD",
        current_price=test_prices[-1],
        price_history=test_prices
    )
    
    print(f"\n📊 Safety Check Results:")
    print(f"  Trade Allowed: {result['trade_allowed']}")
    print(f"  Suggested Action: {result['suggested_action']}")
    print(f"  Alerts Found: {len(result['alerts'])}")
    
    for alert in result['alerts']:
        print(f"    - [{alert['severity']}] {alert['message']}")