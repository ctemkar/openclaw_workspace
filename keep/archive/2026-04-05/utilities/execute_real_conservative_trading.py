#!/usr/bin/env python3
"""
Execute Real Conservative Crypto Trading
Uses actual Gemini API credentials for real trading
"""

import os
import sys
import json
from datetime import datetime

# Set Gemini API credentials from secure keys
def load_gemini_credentials():
    """Load Gemini API credentials from secure key files"""
    try:
        with open('/Users/chetantemkar/.openclaw/workspace/app/secure_keys/.gemini_key', 'r') as f:
            api_key = f.read().strip()
        with open('/Users/chetantemkar/.openclaw/workspace/app/secure_keys/.gemini_secret', 'r') as f:
            api_secret = f.read().strip()
        
        # Set environment variables
        os.environ['GEMINI_API_KEY'] = api_key
        os.environ['GEMINI_API_SECRET'] = api_secret
        
        print(f"✅ Gemini API credentials loaded")
        print(f"   API Key: {api_key[:10]}...{api_key[-10:]}")
        print(f"   API Secret: {api_secret[:5]}...{api_secret[-5:]}")
        
        return True
    except Exception as e:
        print(f"❌ Error loading Gemini credentials: {e}")
        return False

def main():
    print("=" * 70)
    print("REAL CONSERVATIVE CRYPTO TRADING EXECUTION")
    print("=" * 70)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC+7)")
    
    # Load credentials
    if not load_gemini_credentials():
        print("❌ Failed to load Gemini credentials. Exiting.")
        return None
    
    # Import and run the conservative trading script
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import the conservative trading module
        from conservative_crypto_trading import main as trading_main
        
        # Run the trading analysis with real API
        print("\n" + "=" * 70)
        print("RUNNING CONSERVATIVE TRADING ANALYSIS WITH REAL API")
        print("=" * 70)
        
        # Capture the summary output
        summary = trading_main()
        
        return summary
        
    except Exception as e:
        print(f"❌ Error running trading analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    summary = main()
    if summary:
        print("\n" + "=" * 70)
        print("REAL TRADING ANALYSIS COMPLETE")
        print("=" * 70)
        
        # Save summary to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = f"real_trading_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        print(f"✅ Summary saved to: {summary_file}")
    else:
        print("\n❌ Trading analysis failed")