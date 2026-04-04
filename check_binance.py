import ccxt
import os
from dotenv import load_dotenv

# Load keys
load_dotenv()

exchange = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET'),
})

def check_permissions():
    try:
        print("Checking API Key Permissions...")
        
        # In newer CCXT, the method is exactly as the Binance docs (snake_case)
        # Endpoint: GET /sapi/v1/account/apiRestrictions
        res = exchange.sapi_get_account_apirestrictions()
        
        status = res.get('enableRestrictions', {})
        
        print("\n--- BINANCE API PERMISSIONS ---")
        can_read = status.get('enableReading', False)
        can_spot = status.get('enableSpotAndMarginTrading', False)
        can_futures = status.get('enableFutures', False)
        can_transfer = status.get('enableInternalTransfer', False)
        universal_transfer = status.get('permitsUniversalTransfer', False)
        
        print(f"Read Info:         {can_read}")
        print(f"Spot Trading:      {can_spot}")
        print(f"Futures Trading:   {can_futures}")
        print(f"Internal Trans:    {can_transfer}")
        print(f"Universal Trans:   {universal_transfer} <--- (Fixes -1002 error)")
        print(f"Withdrawals:       {status.get('enableWithdrawals', False)}")
        print("-------------------------------\n")
        
        if can_spot or can_futures:
            print("VERDICT: YOU CAN TRADE")
        else:
            print("VERDICT: TRADING IS DISABLED")
            print("Action: Enable 'Spot' or 'Futures' in Binance API settings.")
            
        if not universal_transfer:
            print("\nWARNING: 'Universal Transfer' is DISABLED.")
            print("This is why your 'wipe_binance.py' failed with error -1002.")

    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nPossible fixes:")
        print("1. Ensure keys in .env are inside single quotes: BINANCE_API_KEY='...'")
        print("2. Confirm the key has 'Enable Reading' checked on Binance.")

if __name__ == "__main__":
    check_permissions()
