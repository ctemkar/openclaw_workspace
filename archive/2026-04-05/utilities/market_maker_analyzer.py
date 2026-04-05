#!/usr/bin/env python3
"""
Market Maker Analyzer - Analyzes market conditions for market making
Monitors order books, spreads, and volatility to determine if market making is viable
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
        logging.FileHandler('market_maker_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'api_keys.json')

# Cryptos to analyze (focus on liquid ones)
CRYPTOS = ['BTC', 'ETH', 'SOL', 'XRP']

class MarketMakerAnalyzer:
    def __init__(self):
        """Initialize exchange"""
        self.exchange = None
        self.initialize_exchange()
        
    def initialize_exchange(self):
        """Initialize Gemini exchange (primary for market making)"""
        try:
            # Load API keys
            with open(CONFIG_FILE, 'r') as f:
                api_keys = json.load(f)
            
            # Initialize Gemini
            self.exchange = ccxt.gemini({
                'apiKey': api_keys.get('gemini', {}).get('api_key', ''),
                'secret': api_keys.get('gemini', {}).get('api_secret', ''),
                'enableRateLimit': True,
            })
            logger.info("✅ Gemini exchange initialized for market making analysis")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize exchange: {e}")
            self.exchange = None
    
    def fetch_order_book(self, crypto: str, limit: int = 10) -> Dict:
        """Fetch order book for a crypto"""
        if not self.exchange:
            return {}
            
        try:
            symbol = f"{crypto}/USD"
            order_book = self.exchange.fetch_order_book(symbol, limit=limit)
            return order_book
        except Exception as e:
            logger.debug(f"⚠️ Could not fetch order book for {crypto}: {e}")
            return {}
    
    def analyze_order_book(self, crypto: str, order_book: Dict) -> Dict:
        """Analyze order book for market making opportunities"""
        if not order_book or 'bids' not in order_book or 'asks' not in order_book:
            return {}
        
        bids = order_book['bids']
        asks = order_book['asks']
        
        if not bids or not asks:
            return {}
        
        # Get best bid and ask
        best_bid = bids[0][0] if bids else 0
        best_ask = asks[0][0] if asks else 0
        
        if best_bid <= 0 or best_ask <= 0:
            return {}
        
        # Calculate spread
        spread_absolute = best_ask - best_bid
        spread_percent = (spread_absolute / best_bid) * 100
        
        # Calculate mid price
        mid_price = (best_bid + best_ask) / 2
        
        # Calculate bid/ask volumes
        bid_volume = sum(bid[1] for bid in bids[:5])  # Top 5 bids
        ask_volume = sum(ask[1] for ask in asks[:5])  # Top 5 asks
        
        # Calculate order book imbalance
        total_volume = bid_volume + ask_volume
        imbalance = (bid_volume - ask_volume) / total_volume if total_volume > 0 else 0
        
        # Calculate effective spread (weighted by volume)
        weighted_bid = sum(bid[0] * bid[1] for bid in bids[:3]) / bid_volume if bid_volume > 0 else best_bid
        weighted_ask = sum(ask[0] * ask[1] for ask in asks[:3]) / ask_volume if ask_volume > 0 else best_ask
        effective_spread = weighted_ask - weighted_bid
        effective_spread_percent = (effective_spread / weighted_bid) * 100
        
        return {
            'crypto': crypto,
            'best_bid': round(best_bid, 2),
            'best_ask': round(best_ask, 2),
            'mid_price': round(mid_price, 2),
            'spread_absolute': round(spread_absolute, 4),
            'spread_percent': round(spread_percent, 3),
            'effective_spread_percent': round(effective_spread_percent, 3),
            'bid_volume': round(bid_volume, 4),
            'ask_volume': round(ask_volume, 4),
            'imbalance': round(imbalance, 3),
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_market_making_potential(self, analysis: Dict) -> Dict:
        """Calculate market making profitability potential"""
        if not analysis:
            return {}
        
        # Market making parameters
        TARGET_SPREAD = 0.1  # Target 0.1% spread
        FEE_RATE = 0.0010    # 0.10% taker fee
        CAPITAL = 434.35     # Available Gemini capital
        
        current_spread = analysis['spread_percent']
        
        # Can we place orders inside the spread?
        can_place_inside = current_spread > (TARGET_SPREAD * 2)
        
        # Calculate potential profit per round trip
        if can_place_inside:
            # Place bid at mid_price - TARGET_SPREAD/2, ask at mid_price + TARGET_SPREAD/2
            our_bid = analysis['mid_price'] * (1 - TARGET_SPREAD/200)
            our_ask = analysis['mid_price'] * (1 + TARGET_SPREAD/200)
            our_spread = TARGET_SPREAD
        else:
            # Can't place inside, use current spread
            our_bid = analysis['best_bid']
            our_ask = analysis['best_ask']
            our_spread = current_spread
        
        # Calculate profit after fees
        profit_per_trade = (our_ask - our_bid) / our_bid * 100  # Percentage
        profit_after_fees = profit_per_trade - (FEE_RATE * 2 * 100)  # Both buy and sell fees
        
        # Calculate position size (1% of capital)
        position_size = CAPITAL * 0.01
        
        # Calculate absolute profit
        absolute_profit = position_size * (profit_after_fees / 100)
        
        # Assess viability
        viable = profit_after_fees > 0.01  # At least 0.01% profit after fees
        good_opportunity = profit_after_fees > 0.05  # Good if > 0.05%
        
        return {
            **analysis,
            'can_place_inside': can_place_inside,
            'target_spread': TARGET_SPREAD,
            'our_bid': round(our_bid, 2),
            'our_ask': round(our_ask, 2),
            'our_spread_percent': round(our_spread, 3),
            'profit_per_trade_percent': round(profit_per_trade, 3),
            'fee_percent': round(FEE_RATE * 2 * 100, 3),  # Both sides
            'profit_after_fees_percent': round(profit_after_fees, 3),
            'position_size': round(position_size, 2),
            'absolute_profit': round(absolute_profit, 2),
            'viable': viable,
            'good_opportunity': good_opportunity,
            'capital_required': round(position_size * 2, 2)  # Need both buy and sell sides
        }
    
    def analyze_markets(self):
        """Main analysis loop"""
        logger.info("=" * 70)
        logger.info("📊 MARKET MAKER ANALYZER")
        logger.info("Analyzing market conditions for market making viability")
        logger.info("=" * 70)
        
        cycle = 0
        
        while True:
            cycle += 1
            logger.info(f"\n🔄 ANALYSIS CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            all_opportunities = []
            
            for crypto in CRYPTOS:
                # Fetch order book
                order_book = self.fetch_order_book(crypto)
                
                if order_book:
                    # Analyze order book
                    analysis = self.analyze_order_book(crypto, order_book)
                    
                    if analysis:
                        # Calculate market making potential
                        opportunity = self.calculate_market_making_potential(analysis)
                        
                        if opportunity:
                            all_opportunities.append(opportunity)
                            
                            # Log basic info
                            logger.info(f"  {crypto}:")
                            logger.info(f"    Bid: ${opportunity['best_bid']:,} Ask: ${opportunity['best_ask']:,}")
                            logger.info(f"    Spread: {opportunity['spread_percent']}%")
                            logger.info(f"    Imbalance: {opportunity['imbalance']:+}")
            
            # Display best opportunities
            if all_opportunities:
                # Sort by profit after fees
                all_opportunities.sort(key=lambda x: x['profit_after_fees_percent'], reverse=True)
                
                logger.info("\n🎯 MARKET MAKING OPPORTUNITIES:")
                for opp in all_opportunities[:3]:  # Show top 3
                    if opp['viable']:
                        status = "✅ GOOD" if opp['good_opportunity'] else "⚠️ MARGINAL"
                        logger.info(f"  {opp['crypto']} - {status}")
                        logger.info(f"    Spread: {opp['spread_percent']}% → Target: {opp['our_spread_percent']}%")
                        logger.info(f"    Profit: {opp['profit_after_fees_percent']}% (${opp['absolute_profit']})")
                        logger.info(f"    Capital needed: ${opp['capital_required']}")
                
                # Save best opportunity
                best = all_opportunities[0]
                self.save_analysis(best)
                
                if best['good_opportunity']:
                    logger.info(f"\n🚀 BEST OPPORTUNITY: {best['crypto']}")
                    logger.info(f"   Expected profit: ${best['absolute_profit']} per trade")
                    logger.info(f"   Ready for market making bot implementation!")
                else:
                    logger.info(f"\n⏳ No good market making opportunities yet")
                    logger.info(f"   Best: {best['crypto']} ({best['profit_after_fees_percent']}% profit)")
            else:
                logger.info("⏳ No market data available")
            
            # Wait for next analysis
            logger.info(f"⏰ Next analysis in 120 seconds...")
            time.sleep(120)
    
    def save_analysis(self, opportunity: Dict):
        """Save analysis to file"""
        try:
            data_file = os.path.join(BASE_DIR, 'trading_data', 'market_making_analysis.json')
            os.makedirs(os.path.dirname(data_file), exist_ok=True)
            
            with open(data_file, 'w') as f:
                json.dump(opportunity, f, indent=2)
                
        except Exception as e:
            logger.debug(f"⚠️ Could not save analysis: {e}")

def main():
    """Main function"""
    analyzer = MarketMakerAnalyzer()
    
    try:
        analyzer.analyze_markets()
    except KeyboardInterrupt:
        logger.info("👋 Market maker analyzer stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()