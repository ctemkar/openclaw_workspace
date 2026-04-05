#!/usr/bin/env python3
"""
PRICE VALIDATION SAFEGUARDS
Avoid common mistakes when prices are wrong
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceValidator:
    """Validate prices to avoid common mistakes"""
    
    # Minimum reasonable prices for common cryptos
    MIN_PRICES = {
        "BTC": 1000,      # BTC should be > $1,000
        "ETH": 100,       # ETH should be > $100
        "SOL": 1,         # SOL should be > $1
        "DEFAULT": 0.01   # Any crypto should be > $0.01
    }
    
    @staticmethod
    def validate_price(price, symbol=""):
        """Validate price to avoid common mistakes"""
        
        # Check 1: Price is not None
        if price is None:
            logger.error(f"🚨 Price is None for {symbol}")
            return False, "Price is None"
        
        # Check 2: Price is a number
        if not isinstance(price, (int, float)):
            logger.error(f"🚨 Price is not a number for {symbol}: {type(price)}")
            return False, f"Price is not a number: {type(price)}"
        
        # Check 3: Price > 0
        if price <= 0:
            logger.error(f"🚨 Price <= 0 for {symbol}: {price}")
            return False, f"Price is <= 0: {price}"
        
        # Check 4: Symbol-specific minimum price
        if symbol:
            symbol_upper = symbol.upper()
            
            # Find appropriate minimum price
            min_price = PriceValidator.MIN_PRICES["DEFAULT"]
            for key, value in PriceValidator.MIN_PRICES.items():
                if key in symbol_upper and key != "DEFAULT":
                    min_price = value
                    break
            
            if price < min_price:
                logger.error(f"🚨 Price too low for {symbol}: ${price} (min: ${min_price})")
                return False, f"Price too low: ${price} (expected > ${min_price})"
        
        # Price is valid
        logger.debug(f"✅ Price validated for {symbol}: ${price}")
        return True, "Price validated"
    
    @staticmethod
    def calculate_safe_pnl(entry_price, current_price, symbol=""):
        """Calculate P&L with validation"""
        
        # Validate both prices
        entry_valid, entry_msg = PriceValidator.validate_price(entry_price, symbol)
        current_valid, current_msg = PriceValidator.validate_price(current_price, symbol)
        
        if not entry_valid or not current_valid:
            error_msg = f"Invalid prices: entry={entry_msg}, current={current_msg}"
            logger.error(f"🚨 P&L calculation failed: {error_msg}")
            return {
                "pnl": 0,
                "pnl_percent": 0,
                "valid": False,
                "error": error_msg,
                "warning": "P&L set to 0 due to invalid prices"
            }
        
        # Calculate P&L
        pnl = current_price - entry_price
        pnl_percent = (pnl / entry_price * 100) if entry_price != 0 else 0
        
        # Check for unrealistic P&L (>1000% is suspicious)
        if abs(pnl_percent) > 1000:
            warning = f"Unrealistic P&L: {pnl_percent:.1f}%"
            logger.warning(f"⚠️ {warning} for {symbol}")
            return {
                "pnl": pnl,
                "pnl_percent": pnl_percent,
                "valid": False,
                "error": warning,
                "warning": "P&L seems unrealistic"
            }
        
        # P&L is reasonable
        logger.debug(f"✅ P&L calculated for {symbol}: ${pnl:+.2f} ({pnl_percent:+.1f}%)")
        return {
            "pnl": pnl,
            "pnl_percent": pnl_percent,
            "valid": True,
            "error": None,
            "warning": None
        }
    
    @staticmethod
    def safe_position_calculation(current_price, capital, position_size_percent, symbol=""):
        """Safely calculate position size"""
        
        # Validate price first
        valid, msg = PriceValidator.validate_price(current_price, symbol)
        if not valid:
            logger.error(f"🚨 Position calculation failed: {msg}")
            return None
        
        # Calculate position
        position_value = capital * (position_size_percent / 100)
        amount = position_value / current_price
        
        # Validate amount
        if amount <= 0:
            logger.error(f"🚨 Invalid amount: {amount}")
            return None
        
        # Check for suspicious amounts
        if symbol:
            symbol_upper = symbol.upper()
            
            # BTC: amount should be small (typically < 0.1 BTC for retail)
            if "BTC" in symbol_upper and amount > 0.1:
                logger.warning(f"⚠️ Large BTC amount: {amount:.6f} BTC")
                # Could return None here to prevent trading
            
            # ETH: amount should be reasonable (typically < 10 ETH for retail)
            if "ETH" in symbol_upper and amount > 10:
                logger.warning(f"⚠️ Large ETH amount: {amount:.4f} ETH")
        
        logger.info(f"✅ Position calculated for {symbol}: {amount:.8f} (value: ${position_value:.2f})")
        return amount

class DataQualityChecker:
    """Check data quality for dashboards and systems"""
    
    @staticmethod
    def check_trades(trades):
        """Check trades for common data quality issues"""
        
        issues = []
        
        for i, trade in enumerate(trades):
            symbol = trade.get("symbol", "UNKNOWN")
            trade_type = trade.get("type", "")
            
            # Skip summary entries (they have price=0 intentionally)
            if trade_type in ["summary", "investment_summary", "cash"]:
                continue
                
            entry_price = trade.get("price", 0)
            current_price = trade.get("current_price", 0)
            
            # Check prices
            entry_valid, entry_msg = PriceValidator.validate_price(entry_price, symbol)
            current_valid, current_msg = PriceValidator.validate_price(current_price, symbol)
            
            if not entry_valid:
                issues.append({
                    "type": "INVALID_ENTRY_PRICE",
                    "trade_index": i,
                    "symbol": symbol,
                    "price": entry_price,
                    "message": entry_msg,
                    "severity": "HIGH"
                })
            
            if not current_valid:
                issues.append({
                    "type": "INVALID_CURRENT_PRICE",
                    "trade_index": i,
                    "symbol": symbol,
                    "price": current_price,
                    "message": current_msg,
                    "severity": "HIGH"
                })
            
            # Check for price=0 (common mistake)
            if entry_price == 0:
                issues.append({
                    "type": "ZERO_ENTRY_PRICE",
                    "trade_index": i,
                    "symbol": symbol,
                    "message": "Entry price is 0 (common bug)",
                    "severity": "CRITICAL"
                })
            
            if current_price == 0:
                issues.append({
                    "type": "ZERO_CURRENT_PRICE",
                    "trade_index": i,
                    "symbol": symbol,
                    "message": "Current price is 0 (common bug)",
                    "severity": "CRITICAL"
                })
        
        return issues
    
    @staticmethod
    def generate_dashboard_warnings(issues):
        """Generate warning messages for dashboard"""
        
        if not issues:
            return []
        
        warnings = []
        for issue in issues:
            if issue["severity"] in ["HIGH", "CRITICAL"]:
                warnings.append(f"🚨 {issue['type']}: {issue['symbol']} - {issue['message']}")
            else:
                warnings.append(f"⚠️ {issue['type']}: {issue['symbol']} - {issue['message']}")
        
        return warnings

# Test the safeguards
def test_safeguards():
    """Test the price validation safeguards"""
    
    print("🧪 TESTING PRICE SAFEGUARDS")
    print("="*70)
    
    # Test cases based on our actual bugs
    test_cases = [
        ("BTC/USD", 0, "Zero price (common bug)"),
        ("BTC/USD", 1.14, "Too low (satoshis bug we had)"),
        ("BTC/USD", 65000, "Correct price"),
        ("SOL/USD", 0.80, "Too low (lamports bug we had)"),
        ("SOL/USD", 150, "Correct price"),
        ("ETH/USD", 50, "Too low"),
        ("ETH/USD", 3500, "Correct price"),
    ]
    
    print("\n🔍 Price Validation Tests:")
    for symbol, price, description in test_cases:
        valid, message = PriceValidator.validate_price(price, symbol)
        status = "✅" if valid else "❌"
        print(f"  {status} {symbol}: ${price} - {description}")
        if not valid:
            print(f"     Message: {message}")
    
    print("\n🔍 P&L Calculation Tests:")
    # Test P&L with wrong prices
    pnl_result = PriceValidator.calculate_safe_pnl(0, 65000, "BTC/USD")
    print(f"  Entry $0, Current $65,000: {pnl_result}")
    
    # Test P&L with correct prices
    pnl_result = PriceValidator.calculate_safe_pnl(64000, 65000, "BTC/USD")
    print(f"  Entry $64,000, Current $65,000: P&L ${pnl_result['pnl']:+.2f} ({pnl_result['pnl_percent']:+.1f}%)")
    
    print("\n🔍 Position Calculation Tests:")
    # Test with wrong price (satoshis bug)
    amount = PriceValidator.safe_position_calculation(1.14, 500, 10, "BTC/USD")
    print(f"  Wrong price ($1.14): {'❌ FAILED (good!)' if amount is None else '✅ Amount: ' + str(amount)}")
    
    # Test with correct price
    amount = PriceValidator.safe_position_calculation(65000, 500, 10, "BTC/USD")
    print(f"  Correct price ($65,000): {'❌ Failed' if amount is None else f'✅ Amount: {amount:.8f} BTC'}")

if __name__ == "__main__":
    test_safeguards()
    
    print("\n" + "="*70)
    print("🎯 HOW TO USE THESE SAFEGUARDS:")
    print("="*70)
    
    print("\n1. In trading bot (enhanced_llm_trader.py):")
    print("   from price_safeguards import PriceValidator")
    print("   amount = PriceValidator.safe_position_calculation(current_price, capital, 10, symbol)")
    print("   if amount is None: return  # Don't trade with wrong price")
    
    print("\n2. In dashboard (simple_fixed_dashboard.py):")
    print("   from price_safeguards import DataQualityChecker")
    print("   issues = DataQualityChecker.check_trades(trades)")
    print("   warnings = DataQualityChecker.generate_dashboard_warnings(issues)")
    print("   # Show warnings on dashboard")
    
    print("\n3. In P&L calculations:")
    print("   pnl_result = PriceValidator.calculate_safe_pnl(entry_price, current_price, symbol)")
    print("   if not pnl_result['valid']:")
    print("       print(f\"Warning: {pnl_result['error']}\")")
    print("       pnl = 0  # Use safe default")
    
    print("\n" + "="*70)
    print("🛡️ THESE SAFEGUARDS PREVENT:")
    print("   • Trading with price=0")
    print("   • Calculating wrong amounts (34.5 BTC bug)")
    print("   • Showing fake huge profits")
    print("   • Making decisions based on wrong data")
    print("="*70)