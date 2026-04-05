#!/usr/bin/env python3
"""
SIMPLE SAFETY MONITOR - No TA-Lib dependency
Basic crash detection and news monitoring
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger(__name__)

class SimpleSafetyMonitor:
    """Simple safety monitoring without TA-Lib dependency"""
    
    def __init__(self):
        self.crash_threshold = -15.0  # -15% in 5 minutes = crash
        self.price_history = {}
        
    # 1. MARKET CRASH DETECTION (Flash Crash Protection)
    def detect_market_crash(self, symbol: str, current_price: float) -> List[Dict]:
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
            
            # Check for extreme volatility (simple version)
            if len(recent_prices) >= 3:
                max_price = max(recent_prices)
                min_price = min(recent_prices)
                volatility = ((max_price - min_price) / min_price) * 100
                
                if volatility > 10.0:  # >10% range
                    alerts.append({
                        'type': 'HIGH_VOLATILITY',
                        'severity': 'HIGH',
                        'message': f'⚡ High volatility: {symbol} range {volatility:.1f}%',
                        'action': 'REDUCE_POSITIONS'
                    })
        
        return alerts
    
    # 2. SIMPLE TECHNICAL INDICATORS (No TA-Lib)
    def check_simple_indicators(self, symbol: str, prices: List[float]) -> List[Dict]:
        """Check simple technical indicators without TA-Lib"""
        alerts = []
        
        if len(prices) < 20:  # Need some data
            return alerts
        
        # Simple moving averages
        short_ma = sum(prices[-10:]) / min(10, len(prices[-10:]))
        long_ma = sum(prices[-20:]) / min(20, len(prices[-20:]))
        current_price = prices[-1]
        
        # Price vs moving averages
        if current_price > short_ma * 1.1:  # 10% above short MA
            alerts.append({
                'type': 'PRICE_ABOVE_MA',
                'severity': 'MEDIUM',
                'message': f'📊 {symbol} price >10% above short MA',
                'action': 'CONSIDER_SELLING'
            })
        
        if current_price < short_ma * 0.9:  # 10% below short MA
            alerts.append({
                'type': 'PRICE_BELOW_MA',
                'severity': 'MEDIUM',
                'message': f'📊 {symbol} price >10% below short MA',
                'action': 'CONSIDER_BUYING'
            })
        
        # Simple RSI calculation (simplified)
        gains = []
        losses = []
        for i in range(1, min(15, len(prices))):
            change = prices[-i] - prices[-i-1]
            if change > 0:
                gains.append(change)
            else:
                losses.append(abs(change))
        
        if gains or losses:
            avg_gain = sum(gains) / len(gains) if gains else 0
            avg_loss = sum(losses) / len(losses) if losses else 0
            
            if avg_loss > 0:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                
                if rsi > 70:
                    alerts.append({
                        'type': 'OVERBOUGHT',
                        'severity': 'MEDIUM',
                        'message': f'📊 {symbol} RSI-ish: {rsi:.1f} (overbought)',
                        'action': 'CONSIDER_SELLING'
                    })
                elif rsi < 30:
                    alerts.append({
                        'type': 'OVERSOLD',
                        'severity': 'MEDIUM',
                        'message': f'📊 {symbol} RSI-ish: {rsi:.1f} (oversold)',
                        'action': 'CONSIDER_BUYING'
                    })
        
        return alerts
    
    # 3. NEWS CHECK (Simplified)
    def check_negative_keywords(self) -> List[Dict]:
        """Check for negative keywords in recent context"""
        alerts = []
        
        # Negative keywords that might indicate trouble
        negative_context = [
            "market crash", "flash crash", "liquidation", "margin call",
            "exchange hack", "withdrawal suspended", "regulatory crackdown",
            "bear market", "recession", "inflation spike"
        ]
        
        # In a real implementation, would check news APIs
        # For now, just return empty (can be expanded later)
        
        return alerts
    
    # MAIN SAFETY CHECK
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
        
        # 2. Simple technical indicators
        if price_history and len(price_history) >= 20:
            tech_alerts = self.check_simple_indicators(symbol, price_history)
            all_alerts.extend(tech_alerts)
        
        # 3. Negative keyword check
        news_alerts = self.check_negative_keywords()
        all_alerts.extend(news_alerts)
        
        # Process alerts
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
            if alert['severity'] in ['CRITICAL', 'HIGH']:
                logger.info(f"🔔 Safety Alert [{alert['severity']}]: {alert['message']}")
        
        return recommendations

# Global safety monitor instance
simple_safety_monitor = SimpleSafetyMonitor()

if __name__ == '__main__':
    # Test the safety monitor
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing Simple Safety Monitor...")
    
    # Simulate price history with a crash
    test_prices = [100 + i for i in range(20)] + [85, 80, 75, 70, 65]  # Simulated crash
    
    # Run safety check
    result = simple_safety_monitor.run_safety_checks(
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