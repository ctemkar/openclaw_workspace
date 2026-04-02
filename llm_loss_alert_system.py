#!/usr/bin/env python3
"""
LLM LOSS ALERT SYSTEM
Monitors P&L and alerts on losses, data inconsistencies, and risks
"""

import json
import os
import ccxt
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

print("="*70)
print("🚨 LLM LOSS ALERT SYSTEM - ACTIVATED")
print("="*70)

class LossAlertSystem:
    def __init__(self):
        self.alerts = []
        self.critical_threshold = -5.0  # -5% P&L threshold
        self.data_mismatch_threshold = 0.01  # 1% difference
        
    def check_pnl_losses(self):
        """Check for significant P&L losses"""
        print("\n🔍 CHECKING P&L LOSSES...")
        
        try:
            with open('trading_data/trades.json', 'r') as f:
                trades = json.load(f)
            
            total_pnl = 0
            loss_positions = []
            
            for trade in trades:
                pnl_percent = trade.get('pnl_percent', 0)
                pnl_amount = trade.get('pnl', 0)
                
                if pnl_percent < self.critical_threshold:
                    loss_positions.append({
                        'symbol': trade['symbol'],
                        'pnl_percent': pnl_percent,
                        'pnl_amount': pnl_amount,
                        'amount': trade.get('amount', 0)
                    })
                
                total_pnl += pnl_amount
            
            if loss_positions:
                alert = {
                    'type': 'CRITICAL_LOSS',
                    'timestamp': datetime.now().isoformat(),
                    'title': f'CRITICAL: {len(loss_positions)} positions with >{abs(self.critical_threshold)}% losses',
                    'details': loss_positions,
                    'total_pnl': total_pnl
                }
                self.alerts.append(alert)
                
                print(f"🚨 Found {len(loss_positions)} positions with critical losses:")
                for pos in loss_positions:
                    print(f"  • {pos['symbol']}: {pos['pnl_percent']:.2f}% (${pos['pnl_amount']:.2f})")
            else:
                print("✅ No critical losses found")
                
        except Exception as e:
            print(f"❌ Error checking P&L: {e}")
    
    def check_data_consistency(self):
        """Check if dashboard data matches exchange reality"""
        print("\n🔍 CHECKING DATA CONSISTENCY...")
        
        try:
            # Load dashboard data
            with open('trading_data/trades.json', 'r') as f:
                dashboard_trades = json.load(f)
            
            # Get actual positions from Gemini API
            env = self._load_env()
            gemini_key = env.get('GEMINI_API_KEY')
            gemini_secret = env.get('GEMINI_API_SECRET')
            
            if gemini_key and gemini_secret:
                exchange = ccxt.gemini({
                    'apiKey': gemini_key,
                    'secret': gemini_secret,
                    'enableRateLimit': True,
                })
                
                balance = exchange.fetch_balance()
                
                # Compare with dashboard
                mismatches = []
                
                for trade in dashboard_trades:
                    symbol = trade['symbol']
                    if '/' in symbol:
                        asset = symbol.split('/')[0]
                        
                        dashboard_amount = trade['amount']
                        
                        # Get actual amount from exchange
                        actual_amount = balance['free'].get(asset, 0)
                        
                        if dashboard_amount > 0 and actual_amount > 0:
                            difference = abs(dashboard_amount - actual_amount) / dashboard_amount
                            
                            if difference > self.data_mismatch_threshold:
                                mismatches.append({
                                    'asset': asset,
                                    'dashboard': dashboard_amount,
                                    'actual': actual_amount,
                                    'difference_pct': difference * 100
                                })
                
                if mismatches:
                    alert = {
                        'type': 'DATA_MISMATCH',
                        'timestamp': datetime.now().isoformat(),
                        'title': f'CRITICAL: {len(mismatches)} data mismatches found',
                        'details': mismatches,
                        'message': 'Dashboard data does not match exchange reality!'
                    }
                    self.alerts.append(alert)
                    
                    print(f"🚨 Found {len(mismatches)} data mismatches:")
                    for mismatch in mismatches:
                        print(f"  • {mismatch['asset']}: Dashboard={mismatch['dashboard']:.6f}, Actual={mismatch['actual']:.6f} ({mismatch['difference_pct']:.1f}% diff)")
                else:
                    print("✅ Data consistency verified")
            else:
                print("⚠️ Gemini API keys not available for consistency check")
                
        except Exception as e:
            print(f"❌ Error checking data consistency: {e}")
    
    def check_risk_exposure(self):
        """Check for excessive risk exposure"""
        print("\n🔍 CHECKING RISK EXPOSURE...")
        
        try:
            with open('trading_data/trades.json', 'r') as f:
                trades = json.load(f)
            
            total_value = sum(t.get('value', 0) for t in trades)
            
            # Check if any single position is too large
            large_positions = []
            for trade in trades:
                position_value = trade.get('value', 0)
                if position_value > 0:
                    position_pct = (position_value / total_value * 100) if total_value > 0 else 0
                    
                    if position_pct > 30:  # More than 30% in one position
                        large_positions.append({
                            'symbol': trade['symbol'],
                            'value': position_value,
                            'percentage': position_pct
                        })
            
            if large_positions:
                alert = {
                    'type': 'RISK_EXPOSURE',
                    'timestamp': datetime.now().isoformat(),
                    'title': f'WARNING: {len(large_positions)} positions with excessive exposure',
                    'details': large_positions,
                    'message': 'Consider diversifying to reduce risk'
                }
                self.alerts.append(alert)
                
                print(f"⚠️ Found {len(large_positions)} positions with excessive exposure:")
                for pos in large_positions:
                    print(f"  • {pos['symbol']}: ${pos['value']:.2f} ({pos['percentage']:.1f}% of portfolio)")
            else:
                print("✅ Risk exposure within acceptable limits")
                
        except Exception as e:
            print(f"❌ Error checking risk exposure: {e}")
    
    def generate_recommendations(self):
        """Generate LLM recommendations based on findings"""
        print("\n🔍 GENERATING LLM RECOMMENDATIONS...")
        
        recommendations = []
        
        if self.alerts:
            # Analyze alerts and generate recommendations
            for alert in self.alerts:
                if alert['type'] == 'CRITICAL_LOSS':
                    rec = {
                        'type': 'LOSS_MANAGEMENT',
                        'priority': 'HIGH',
                        'action': 'Consider setting stop-loss orders or reducing position sizes',
                        'reason': f"{len(alert['details'])} positions with significant losses",
                        'details': [f"{pos['symbol']}: {pos['pnl_percent']:.2f}% loss" for pos in alert['details'][:3]]
                    }
                    recommendations.append(rec)
                
                elif alert['type'] == 'DATA_MISMATCH':
                    rec = {
                        'type': 'DATA_INTEGRITY',
                        'priority': 'CRITICAL',
                        'action': 'Immediately reconcile dashboard data with exchange APIs',
                        'reason': 'Dashboard shows different positions than actual exchange',
                        'details': [f"{m['asset']}: {m['difference_pct']:.1f}% mismatch" for m in alert['details'][:3]]
                    }
                    recommendations.append(rec)
            
            # Add general recommendations
            recommendations.append({
                'type': 'SYSTEM_IMPROVEMENT',
                'priority': 'MEDIUM',
                'action': 'Implement automated loss alerts and risk monitoring',
                'reason': 'Current system lacks proactive loss detection',
                'details': ['LLM system should monitor P&L continuously']
            })
        
        return recommendations
    
    def _load_env(self):
        """Load environment variables"""
        env_vars = {}
        try:
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
            return env_vars
        except:
            return {}
    
    def run_checks(self):
        """Run all checks"""
        self.check_pnl_losses()
        self.check_data_consistency()
        self.check_risk_exposure()
        
        recommendations = self.generate_recommendations()
        
        # Save alerts and recommendations
        self.save_results(recommendations)
        
        return self.alerts, recommendations
    
    def save_results(self, recommendations):
        """Save alerts and recommendations to file"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'alerts': self.alerts,
            'recommendations': recommendations,
            'summary': {
                'total_alerts': len(self.alerts),
                'critical_alerts': len([a for a in self.alerts if a['type'] in ['CRITICAL_LOSS', 'DATA_MISMATCH']]),
                'recommendations_count': len(recommendations)
            }
        }
        
        output_file = 'trading_data/llm_loss_alerts.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Results saved to: {output_file}")

def main():
    system = LossAlertSystem()
    alerts, recommendations = system.run_checks()
    
    print("\n" + "="*70)
    print("📋 ALERT SUMMARY")
    print("="*70)
    
    if alerts:
        print(f"🚨 TOTAL ALERTS: {len(alerts)}")
        for alert in alerts:
            print(f"\n{alert['type']}: {alert['title']}")
            if 'details' in alert and alert['details']:
                print("  Details:")
                for detail in alert['details'][:3]:
                    if 'symbol' in detail:
                        print(f"    • {detail['symbol']}")
    else:
        print("✅ No alerts generated")
    
    print("\n" + "="*70)
    print("💡 LLM RECOMMENDATIONS")
    print("="*70)
    
    if recommendations:
        for rec in recommendations:
            print(f"\n[{rec['priority']}] {rec['type']}:")
            print(f"  Action: {rec['action']}")
            print(f"  Reason: {rec['reason']}")
    else:
        print("No recommendations generated")
    
    print("\n" + "="*70)
    print("🎯 IMMEDIATE ACTIONS REQUIRED:")
    print("="*70)
    
    if alerts:
        print("1. Review loss positions and consider stop-loss orders")
        print("2. Reconcile dashboard data with exchange reality")
        print("3. Implement regular loss monitoring")
        print("4. Set up alert notifications for future losses")
    else:
        print("System appears stable. Continue monitoring.")
    
    print("="*70)

if __name__ == "__main__":
    main()