import ccxt
import os
import time
from dotenv import load_dotenv
load_dotenv(override=True)
exchange = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET'),
})
def diagnose():
    print(f"Testing Key: {os.getenv('BINANCE_API_KEY')[:10]}...")
    try:
        # Check system status directly from Binance SAPI
        res = exchange.sapi_get_account_apirestrictions()
        status = res.get('enableRestrictions', {})
        
        print("\n--- SERVER-SIDE PERMISSIONS ---")
        print(f"Spot Trading:      {status.get('enableSpotAndMarginTrading')}")
        print(f"Futures:           {status.get('enableFutures')}")
        print(f"Internal Transfer: {status.get('enableInternalTransfer')}")
        print(f"Universal Trans:   {status.get('permitsUniversalTransfer')}")
        print("-------------------------------\n")

        if not status.get('permitsUniversalTransfer') and not status.get('enableInternalTransfer'):
            print("VERDICT: The server still says Transfers are DISABLED.")
            print("1. Go to Binance -> API Management.")
            print("2. Click 'Edit Restrictions'.")
            print("3. Ensure 'Restrict access to trusted IPs' is selected.")
            print("4. Check 'Permits Universal Transfer'.")
            print("5. IMPORTANT: Scroll up and click the yellow 'SAVE' button.")
            print("6. Enter your 2FA code.")
        else:
            print("VERDICT: Permissions look GOOD. If it still fails, check your .env for hidden spaces.")

    except Exception as e:
        print(f"\nFAILED: {e}")
        if "API-key format invalid" in str(e):
            print("Check your .env file. Use single quotes: BINANCE_API_KEY='...'")

if __name__ == "__main__":
    diagnose()
