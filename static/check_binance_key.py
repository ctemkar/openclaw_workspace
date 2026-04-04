import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

# Load the .env file from the project root directory
load_dotenv()

# Retrieve keys from environment variables
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

def check_binance_keys():
    # 1. Validation Check: Are keys present in .env?
    if not API_KEY or not API_SECRET:
        print("❌ Error: API keys not found in .env file.")
        print("Ensure your .env file is in the root directory and formatted as:")
        print("BINANCE_API_KEY=your_key\nBINANCE_API_SECRET=your_secret")
        return

    # Initialize client (Use tld='us' for Binance.US users)
    client = Client(API_KEY, API_SECRET)

    try:
        # Attempt a basic 'Read' request
        account = client.get_account()
        print("✅ Success! Your API keys are working.")
        print(f"Permissions: {account.get('permissions', 'Unknown')}")

    except BinanceAPIException as e:
        # 2. API Failure Troubleshooting
        print(f"❌ Binance API Error (Code {e.status_code}): {e.message}")
        
        if e.status_code == 401:
            print("   - Problem: Invalid Key or Secret. Double-check for typos/extra spaces.")
        elif e.status_code == 403:
            print("   - Problem: IP Restriction. Your current IP might not be whitelisted in API settings.")
        elif "Timestamp" in e.message:
            print("   - Problem: Time Sync Error. Your computer's clock is out of sync with Binance servers.")
            
    except BinanceRequestException as e:
        print(f"❌ Network Error: Could not connect to Binance servers. {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == '__main__':
    check_binance_keys()
