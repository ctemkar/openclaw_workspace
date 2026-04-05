#!/usr/bin/env python3
"""
Portfolio Rebalancer Bot - Automatically rebalances crypto portfolio
Monitors current holdings and rebalances to target allocations
"""

import os
import sys
import json
import time
import ccxt
from datetime import datetime
import logging
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('portfolio_rebalancer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'api_keys.json')

# Target portfolio allocation (percentages)
TARGET_ALLOCATION = {
    'BTC': 40.0,   # 40% Bitcoin
    'ETH': 30.0,   # 30% Ethereum  
    'SOL': 10.0,   # 10% Solana
    'XRP': 5.0,    # 5% XRP
    'ADA': 5.0,    # 5% Cardano
    'OTHER': 10.0  # 10% Other/Reserve
}

# Rebalancing threshold (trigger when deviation > threshold)
REBALANCE_THRESHOLD = 5.0  # 5% deviation triggers rebalance

class PortfolioRebalancer:
    def __init__(self):
        """Initialize exchange and load current portfolio"""
        self.exchange = None
        self.portfolio = {}
        self.total_value = 0.0
        self.initialize_exchange()
        
    def initialize_exchange(self):
        """Initialize Gemini exchange"""
        try:
            with open(CONFIG_FILE, 'r') as f:
                api_keys = json.load(f)
            
            self.exchange = ccxt.gemini({
                'apiKey': api_keys.get('gemini', {}).get('api_key', ''),
                'secret': api_keys.get('gemini', {}).get('api_secret', ''),
                'enableRateLimit': True,
            })
            logger.info("✅ Gemini exchange initialized for portfolio rebalancing")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize exchange: {e}")
            self.exchange = None
    
    def fetch_balances(self) -> Dict:
        """Fetch current balances from exchange"""
        if not self.exchange:
            return {}
            
        try:
            balances = self.exchange.fetch_balance()
            return balances
        except Exception as e:
            logger.error(f"❌ Failed to fetch balances: {e}")
            return {}
    
    def fetch_prices(self, cryptos: List[str]) -> Dict[str, float]:
        """Fetch current prices for cryptos"""
        prices = {}
        
        for crypto in cryptos:
            try:
                symbol = f"{crypto}/USD"
                ticker = self.exchange.fetch_ticker(symbol)
                prices[crypto] = ticker['last']
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch price for {crypto}: {e}")
                prices[crypto] = 0.0
        
        return prices
    
    def calculate_portfolio_value(self, balances: Dict, prices: Dict) -> Tuple[Dict, float]:
        """Calculate current portfolio value and allocation"""
        portfolio = {}
        total_value = 0.0
        
        # Calculate USD value for each crypto
        for crypto in TARGET_ALLOCATION.keys():
            if crypto == 'OTHER':
                continue
                
            # Get balance
            balance = balances.get(crypto, {}).get('free', 0.0)
            price = prices.get(crypto, 0.0)
            value = balance * price
            
            portfolio[crypto] = {
                'balance': balance,
                'price': price,
                'value': value,
                'allocation': 0.0
            }
            
            total_value += value
        
        # Calculate USD balance
        usd_balance = balances.get('USD', {}).get('free', 0.0)
        portfolio['USD'] = {
            'balance': usd_balance,
            'price': 1.0,
            'value': usd_balance,
            'allocation': 0.0
        }
        total_value += usd_balance
        
        # Calculate percentages
        if total_value > 0:
            for asset in portfolio.values():
                asset['allocation'] = (asset['value'] / total_value) * 100
        
        return portfolio, total_value
    
    def analyze_rebalancing_needs(self, portfolio: Dict, total_value: float) -> Dict:
        """Analyze if rebalancing is needed and calculate required trades"""
        rebalancing_plan = {}
        
        for crypto, target_pct in TARGET_ALLOCATION.items():
            if crypto == 'OTHER':
                # OTHER is for reserve/opportunistic allocation
                continue
                
            current = portfolio.get(crypto, {'allocation': 0.0, 'value': 0.0})
            current_pct = current['allocation']
            
            # Calculate deviation from target
            deviation = current_pct - target_pct
            
            # Check if rebalancing is needed
            if abs(deviation) > REBALANCE_THRESHOLD:
                # Calculate target value
                target_value = total_value * (target_pct / 100)
                
                # Calculate trade amount
                trade_value = target_value - current['value']
                
                rebalancing_plan[crypto] = {
                    'current_pct': round(current_pct, 2),
                    'target_pct': target_pct,
                    'deviation': round(deviation, 2),
                    'current_value': round(current['value'], 2),
                    'target_value': round(target_value, 2),
                    'trade_value': round(trade_value, 2),
                    'action': 'BUY' if trade_value > 0 else 'SELL',
                    'amount': abs(trade_value)
                }
        
        return rebalancing_plan
    
    def execute_rebalancing(self, rebalancing_plan: Dict, portfolio: Dict):
        """Execute rebalancing trades"""
        if not rebalancing_plan:
            logger.info("✅ Portfolio is balanced, no trades needed")
            return
        
        logger.info("🔄 EXECUTING PORTFOLIO REBALANCING")
        
        for crypto, plan in rebalancing_plan.items():
            logger.info(f"  {crypto}: {plan['current_pct']}% → {plan['target_pct']}%")
            logger.info(f"    Action: {plan['action']} ${plan['amount']:.2f}")
            
            # Execute trade
            if self.execute_trade(crypto, plan['action'], plan['amount']):
                logger.info(f"    ✅ {plan['action']} order executed")
            else:
                logger.warning(f"    ⚠️ {plan['action']} order failed")
    
    def execute_trade(self, crypto: str, action: str, amount_usd: float) -> bool:
        """Execute a trade for rebalancing"""
        if not self.exchange or amount_usd < 10.0:  # Minimum $10 trade
            return False
            
        try:
            symbol = f"{crypto}/USD"
            
            # Calculate amount in crypto
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            amount_crypto = amount_usd / price
            
            # Place order
            order = self.exchange.create_order(
                symbol=symbol,
                type='market',
                side=action.lower(),
                amount=amount_crypto
            )
            
            logger.info(f"    Order {order['id']}: {action} {amount_crypto:.6f} {crypto} @ ${price:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"    ❌ Trade execution failed: {e}")
            return False
    
    def monitor_and_rebalance(self):
        """Main monitoring and rebalancing loop"""
        logger.info("=" * 70)
        logger.info("⚖️ PORTFOLIO REBALANCER BOT")
        logger.info("Automatically rebalances portfolio to target allocation")
        logger.info("=" * 70)
        
        logger.info("🎯 TARGET ALLOCATION:")
        for crypto, pct in TARGET_ALLOCATION.items():
            logger.info(f"  {crypto}: {pct}%")
        
        logger.info(f"📊 Rebalance threshold: {REBALANCE_THRESHOLD}% deviation")
        
        cycle = 0
        
        while True:
            cycle += 1
            logger.info(f"\n🔄 REBALANCE CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            try:
                # 1. Fetch current balances
                balances = self.fetch_balances()
                if not balances:
                    logger.warning("⚠️ Could not fetch balances, skipping cycle")
                    time.sleep(300)
                    continue
                
                # 2. Fetch prices
                cryptos = [c for c in TARGET_ALLOCATION.keys() if c != 'OTHER']
                prices = self.fetch_prices(cryptos)
                
                # 3. Calculate portfolio
                portfolio, total_value = self.calculate_portfolio_value(balances, prices)
                self.portfolio = portfolio
                self.total_value = total_value
                
                # 4. Log current portfolio
                logger.info("📊 CURRENT PORTFOLIO:")
                logger.info(f"  Total Value: ${total_value:,.2f}")
                
                for asset, data in portfolio.items():
                    if data['value'] > 1.0:  # Only show assets with > $1 value
                        logger.info(f"  {asset}: ${data['value']:,.2f} ({data['allocation']:.1f}%)")
                
                # 5. Analyze rebalancing needs
                rebalancing_plan = self.analyze_rebalancing_needs(portfolio, total_value)
                
                # 6. Execute rebalancing if needed
                if rebalancing_plan:
                    logger.info("🎯 REBALANCING REQUIRED:")
                    for crypto, plan in rebalancing_plan.items():
                        logger.info(f"  {crypto}: {plan['current_pct']}% → {plan['target_pct']}% ({plan['action']} ${plan['amount']:.2f})")
                    
                    # Ask for confirmation (safety measure)
                    logger.info("⏳ Waiting 30 seconds before executing rebalancing...")
                    time.sleep(30)
                    
                    # Execute rebalancing
                    self.execute_rebalancing(rebalancing_plan, portfolio)
                else:
                    logger.info("✅ Portfolio is within target allocation")
                
                # 7. Wait for next cycle
                logger.info(f"💤 Next rebalance check in 1 hour...")
                time.sleep(3600)
                
            except Exception as e:
                logger.error(f"❌ Error in rebalance cycle: {e}")
                time.sleep(600)  # Wait 10 minutes on error

def main():
    """Main function"""
    rebalancer = PortfolioRebalancer()
    
    try:
        rebalancer.monitor_and_rebalance()
    except KeyboardInterrupt:
        logger.info("👋 Portfolio rebalancer stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()