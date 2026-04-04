#!/usr/bin/env python3
"""
Top 10 Spreads Report
Compare Binance vs Gemini prices to find arbitrage opportunities
"""

import ccxt
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cryptos available on both exchanges
COMMON_CRYPTOS = [
    'BTC', 'ETH', 'SOL', 'XRP', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
    'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI'
]

def get_binance_prices():
    """Get prices from Binance (public data)"""
    exchange = ccxt.binance({'enableRateLimit': True})
    prices = {}
    
    logger.info("📊 Fetching Binance prices...")
    for crypto in COMMON_CRYPTOS:
        try:
            symbol = f"{crypto}/USDT"
            ticker = exchange.fetch_ticker(symbol)
            prices[crypto] = {
                'price': ticker['last'],
                'change': ticker['percentage']
            }
            logger.info(f"  {crypto}: ${ticker['last']:.4f}")
        except Exception as e:
            logger.error(f"❌ Error fetching {crypto} from Binance: {e}")
    
    return prices

def get_gemini_prices():
    """Get prices from Gemini (public data)"""
    exchange = ccxt.gemini({'enableRateLimit': True})
    prices = {}
    
    logger.info("📊 Fetching Gemini prices...")
    for crypto in COMMON_CRYPTOS:
        try:
            symbol = f"{crypto}/USD"  # Gemini uses USD, not USDT
            ticker = exchange.fetch_ticker(symbol)
            prices[crypto] = {
                'price': ticker['last'],
                'change': ticker['percentage']
            }
            logger.info(f"  {crypto}: ${ticker['last']:.4f}")
        except Exception as e:
            logger.error(f"❌ Error fetching {crypto} from Gemini: {e}")
    
    return prices

def calculate_spreads(binance_prices, gemini_prices):
    """Calculate spreads between Binance and Gemini"""
    spreads = []
    
    for crypto in COMMON_CRYPTOS:
        if crypto in binance_prices and crypto in gemini_prices:
            binance_price = binance_prices[crypto]['price']
            gemini_price = gemini_prices[crypto]['price']
            
            if gemini_price > 0:  # Avoid division by zero
                spread_percent = ((binance_price - gemini_price) / gemini_price) * 100
                
                spreads.append({
                    'crypto': crypto,
                    'binance_price': binance_price,
                    'gemini_price': gemini_price,
                    'spread_abs': binance_price - gemini_price,
                    'spread_percent': spread_percent,
                    'opportunity': 'BUY_ON_GEMINI' if spread_percent > 0 else 'BUY_ON_BINANCE'
                })
    
    # Sort by absolute spread percentage (highest first)
    spreads.sort(key=lambda x: abs(x['spread_percent']), reverse=True)
    
    return spreads

def generate_report(spreads):
    """Generate top 10 spreads report"""
    report = []
    report.append("=" * 80)
    report.append("📈 TOP 10 CRYPTO SPREADS REPORT - Binance vs Gemini")
    report.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")
    report.append("Rank | Crypto | Binance Price | Gemini Price | Spread ($) | Spread (%) | Opportunity")
    report.append("-" * 80)
    
    for i, spread in enumerate(spreads[:10], 1):
        report.append(
            f"{i:4d} | {spread['crypto']:6s} | "
            f"${spread['binance_price']:12.4f} | "
            f"${spread['gemini_price']:12.4f} | "
            f"{spread['spread_abs']:10.4f} | "
            f"{spread['spread_percent']:10.2f}% | "
            f"{spread['opportunity']}"
        )
    
    report.append("")
    report.append("📊 SUMMARY:")
    report.append(f"  • Total cryptos analyzed: {len(spreads)}")
    if spreads:
        report.append(f"  • Highest spread: {spreads[0]['crypto']} ({spreads[0]['spread_percent']:.2f}%)")
        report.append(f"  • Average spread: {sum(abs(s['spread_percent']) for s in spreads)/len(spreads):.2f}%")
    
    report.append("")
    report.append("💡 OPPORTUNITY INTERPRETATION:")
    report.append("  • BUY_ON_GEMINI: Binance price > Gemini price (buy on Gemini, sell on Binance)")
    report.append("  • BUY_ON_BINANCE: Gemini price > Binance price (buy on Binance, sell on Gemini)")
    report.append("  • Positive spread % means Binance price is higher")
    report.append("  • Negative spread % means Gemini price is higher")
    report.append("=" * 80)
    
    return "\n".join(report)

def main():
    """Main function to generate spreads report"""
    logger.info("🔍 Starting Top 10 Spreads Report...")
    
    # Get prices from both exchanges
    binance_prices = get_binance_prices()
    gemini_prices = get_gemini_prices()
    
    # Calculate spreads
    spreads = calculate_spreads(binance_prices, gemini_prices)
    
    # Generate and print report
    report = generate_report(spreads)
    print(report)
    
    # Save report to file
    report_file = "top_10_spreads_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"✅ Report saved to {report_file}")
    
    # Also log the top 3 opportunities
    if spreads:
        logger.info("🏆 TOP 3 ARBITRAGE OPPORTUNITIES:")
        for i, spread in enumerate(spreads[:3], 1):
            logger.info(f"  {i}. {spread['crypto']}: {spread['spread_percent']:.2f}% "
                       f"({spread['opportunity']})")
    
    return spreads

if __name__ == "__main__":
    main()