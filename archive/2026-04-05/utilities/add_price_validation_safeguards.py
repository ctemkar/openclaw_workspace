#!/usr/bin/env python3
"""
ADD PRICE VALIDATION SAFEGUARDS
Avoid common mistakes when prices are wrong
"""

import json
from datetime import datetime

def analyze_common_mistakes():
    """Analyze and document common mistakes"""
    
    print("🔍 COMMON MISTAKES WHEN PRICE IS WRONG:")
    print("="*70)
    
    mistakes = [
        {
            "mistake": "Showing huge fake profits",
            "example": "P&L = Current Price - 0 = Current Price",
            "impact": "Shows $65,000 profit on BTC instead of actual P&L",
            "solution": "Validate price > 0 before P&L calculation"
        },
        {
            "mistake": "Making trading decisions based on wrong data",
            "example": "Trading bot uses price=0 to calculate position size",
            "impact": "Calculates wrong amounts (34.5 BTC instead of 0.0006 BTC)",
            "solution": "Add price validation in trading logic"
        },
        {
            "mistake": "Not detecting the error automatically",
            "example": "Dashboard shows wrong data without warning",
            "impact": "User doesn't know data is wrong",
            "solution": "Add data quality indicators and warnings"
        },
        {
            "mistake": "Not having validation checks",
            "example": "No checks for price=0 or unrealistic prices",
            "impact": "Errors propagate through system",
            "solution": "Add validation at data entry points"
        },
        {
            "mistake": "Not logging the error for debugging",
            "example": "Price bug happens but no record of it",
            "impact": "Hard to debug and fix",
            "solution": "Log all price validation failures"
        }
    ]
    
    for i, mistake in enumerate(mistakes, 1):
        print(f"\n{i}. {mistake['mistake']}")
        print(f"   Example: {mistake['example']}")
        print(f"   Impact: {mistake['impact']}")
        print(f"   Solution: {mistake['solution']}")
    
    return mistakes

def implement_safeguards():
    """Implement safeguards to avoid these mistakes"""
    
    print("\n" + "="*70)
    print("🛡️ IMPLEMENTING SAFEGUARDS")
    print("="*70)
    
    safeguards = [
        {
            "name": "Price Validation Function",
            "purpose": "Validate prices before use",
            "code": '''
def validate_price(price, symbol=""):
    """Validate price to avoid common mistakes"""
    
    # Common price validation rules
    if price is None:
        return False, "Price is None"
    
    if not isinstance(price, (int, float)):
        return False, f"Price is not a number: {type(price)}"
    
    if price <= 0:
        return False, f"Price is <= 0: {price}"
    
    # Symbol-specific validation
    if symbol:
        symbol_upper = symbol.upper()
        
        # BTC should be > $1,000
        if "BTC" in symbol_upper and price < 1000:
            return False, f"BTC price too low: ${price} (expected > $1,000)"
        
        # ETH should be > $100
        if "ETH" in symbol_upper and price < 100:
            return False, f"ETH price too low: ${price} (expected > $100)"
        
        # SOL should be > $1
        if "SOL" in symbol_upper and price < 1:
            return False, f"SOL price too low: ${price} (expected > $1)"
        
        # Generic crypto should be > $0.01
        if price < 0.01:
            return False, f"Price too low for crypto: ${price}"
    
    # Price seems reasonable
    return True, "Price validated"
'''
        },
        {
            "name": "Safe P&L Calculation",
            "purpose": "Calculate P&L with validation",
            "code": '''
def calculate_safe_pnl(entry_price, current_price, symbol=""):
    """Calculate P&L with price validation"""
    
    # Validate prices first
    entry_valid, entry_msg = validate_price(entry_price, symbol)
    current_valid, current_msg = validate_price(current_price, symbol)
    
    if not entry_valid or not current_valid:
        # Return safe defaults with error info
        error_msg = f"Invalid prices: entry={entry_msg}, current={current_msg}"
        return {
            "pnl": 0,
            "pnl_percent": 0,
            "valid": False,
            "error": error_msg,
            "entry_price": entry_price,
            "current_price": current_price
        }
    
    # Calculate P&L
    pnl = current_price - entry_price
    pnl_percent = (pnl / entry_price * 100) if entry_price != 0 else 0
    
    # Check for unrealistic P&L (common mistake)
    if abs(pnl_percent) > 1000:  # More than 1000% P&L is suspicious
        return {
            "pnl": pnl,
            "pnl_percent": pnl_percent,
            "valid": False,
            "error": f"Unrealistic P&L: {pnl_percent:.1f}%",
            "entry_price": entry_price,
            "current_price": current_price
        }
    
    # P&L seems reasonable
    return {
        "pnl": pnl,
        "pnl_percent": pnl_percent,
        "valid": True,
        "error": None,
        "entry_price": entry_price,
        "current_price": current_price
    }
'''
        },
        {
            "name": "Dashboard Data Quality Check",
            "purpose": "Add warnings to dashboard",
            "code": '''
def check_data_quality(trades):
    """Check data quality for dashboard"""
    
    issues = []
    
    for i, trade in enumerate(trades):
        symbol = trade.get("symbol", "")
        entry_price = trade.get("price", 0)
        current_price = trade.get("current_price", 0)
        
        # Check for price=0
        if entry_price == 0:
            issues.append(f"Trade {i} ({symbol}): Entry price is 0")
        
        if current_price == 0:
            issues.append(f"Trade {i} ({symbol}): Current price is 0")
        
        # Check for unrealistic prices
        if symbol and entry_price > 0:
            if "BTC" in symbol.upper() and entry_price < 1000:
                issues.append(f"Trade {i} ({symbol}): BTC price ${entry_price} seems too low")
            
            if "ETH" in symbol.upper() and entry_price < 100:
                issues.append(f"Trade {i} ({symbol}): ETH price ${entry_price} seems too low")
    
    return issues
'''
        },
        {
            "name": "Trading Bot Safety Check",
            "purpose": "Prevent trading with wrong prices",
            "code": '''
def safe_calculate_position(current_price, capital, position_size_percent, symbol=""):
    """Safely calculate position size with price validation"""
    
    # Validate price first
    valid, msg = validate_price(current_price, symbol)
    if not valid:
        print(f"🚨 PRICE VALIDATION FAILED: {msg}")
        print(f"   Symbol: {symbol}, Price: ${current_price}")
        print(f"   ❌ NOT TRADING - Price validation failed")
        return None
    
    # Calculate position
    position_value = capital * (position_size_percent / 100)
    amount = position_value / current_price
    
    # Validate amount is reasonable
    if amount <= 0:
        print(f"🚨 INVALID AMOUNT: {amount}")
        return None
    
    # For BTC, amount should be small (e.g., 0.001 BTC, not 34.5 BTC)
    if symbol and "BTC" in symbol.upper():
        if amount > 1:  # More than 1 BTC is suspicious for retail trading
            print(f"🚨 SUSPICIOUS BTC AMOUNT: {amount} BTC")
            print(f"   Price: ${current_price}, Position value: ${position_value}")
            print(f"   ❌ NOT TRADING - Amount seems wrong")
            return None
    
    return amount
'''
        }
    ]
    
    for i, safeguard in enumerate(safeguards, 1):
        print(f"\n{i}. {safeguard['name']}")
        print(f"   Purpose: {safeguard['purpose']}")
        print(f"   Code saved to: safeguards_{safeguard['name'].lower().replace(' ', '_')}.py")
        
        # Save each safeguard to a file
        filename = f"safeguards_{safeguard['name'].lower().replace(' ', '_')}.py"
        with open(filename, 'w') as f:
            f.write(safeguard['code'])
    
    return safeguards

def create_unified_safeguard_module():
    """Create a unified safeguard module"""
    
    print("\n" + "="*70)
    print("📦 CREATING UNIFIED SAFEGUARD MODULE")
    print("="*70)
    
    unified_code = '''#!/usr/bin/env python3
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

# Example usage
if __name__ == "__main__":
    print("🧪 Testing Price Validator...")
    
    # Test cases
    test_cases = [
        ("BTC/USD", 0, "Zero price"),
        ("BTC/USD", 1.14, "Too low (satoshis bug)"),
        ("BTC/USD", 65000, "Correct price"),
        ("SOL/USD", 0.80, "Too low (lamports bug)"),
        ("SOL/USD", 150, "Correct price"),
        ("ETH/USD", 50, "Too low"),
