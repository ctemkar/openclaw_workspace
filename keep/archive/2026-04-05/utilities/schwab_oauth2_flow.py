#!/usr/bin/env python3
"""
IMPLEMENT Schwab OAuth2 Flow to get Access Token
"""
import os
import webbrowser
import http.server
import socketserver
import urllib.parse
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('SCHWAB_API_KEY')
api_secret = os.getenv('SCHWAB_API_SECRET')
account_id = os.getenv('SCHWAB_ACCOUNT_ID')

print("🚀 IMPLEMENTING SCHWAB OAUTH2 FLOW")
print("=" * 60)

print(f"\n📋 Your credentials:")
print(f"   Client ID: {api_key[:20]}...")
print(f"   Client Secret: {api_secret[:20]}...")
print(f"   Account ID: {account_id}")

print("\n🎯 WHAT WE'RE DOING:")
print("   1. Open browser for you to login to Schwab")
print("   2. You approve the application")
print("   3. Get authorization code")
print("   4. Exchange code for Access Token")
print("   5. Save token to .env file")

# OAuth2 configuration
redirect_uri = "http://localhost:8080/callback"
auth_url = f"https://api.schwabapi.com/v1/oauth/authorize"
token_url = "https://api.schwabapi.com/v1/oauth/token"

# Build authorization URL
params = {
    "response_type": "code",
    "client_id": api_key,
    "redirect_uri": redirect_uri,
    "scope": "read_account trade"
}

auth_full_url = f"{auth_url}?{urllib.parse.urlencode(params)}"

print(f"\n🔗 Authorization URL:")
print(f"   {auth_full_url}")

print("\n🎯 STEP 1: You need to open this URL in browser")
print("   I'll try to open it for you automatically...")

try:
    webbrowser.open(auth_full_url)
    print("   ✅ Browser opened (or will open)")
except:
    print("   ⚠️  Could not open browser automatically")
    print(f"   📋 PLEASE MANUALLY OPEN THIS URL:")
    print(f"   {auth_full_url}")

print("\n🎯 STEP 2: What happens in browser:")
print("   1. Schwab login page appears")
print("   2. Login with your Schwab credentials")
print("   3. Approve the application permissions")
print("   4. You'll be redirected to localhost:8080/callback")
print("   5. URL will contain 'code=...' parameter")

print("\n🎯 STEP 3: I'll capture the code")
print("   Starting local web server on port 8080...")
print("   Waiting for you to complete login...")

# Create a simple HTTP server to capture the callback
class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the callback URL
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        
        if 'code' in query:
            auth_code = query['code'][0]
            print(f"\n🎉 SUCCESS! Got authorization code: {auth_code[:20]}...")
            
            # Exchange code for token
            print("🔁 Exchanging code for Access Token...")
            
            credentials = f"{api_key}:{api_secret}"
            encoded = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": redirect_uri
            }
            
            try:
                response = requests.post(token_url, headers=headers, data=data, timeout=10)
                
                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data['access_token']
                    refresh_token = token_data.get('refresh_token', '')
                    
                    print(f"✅ SUCCESS! Got Access Token!")
                    print(f"   Token: {access_token[:50]}...")
                    print(f"   Expires in: {token_data.get('expires_in')} seconds")
                    
                    if refresh_token:
                        print(f"   Refresh Token: {refresh_token[:50]}...")
                    
                    # Save to .env
                    print("\n💾 Saving to .env file...")
                    with open('.env', 'a') as f:
                        f.write(f"\n# Schwab OAuth2 Tokens (generated {os.popen('date').read().strip()})\n")
                        f.write(f"SCHWAB_ACCESS_TOKEN={access_token}\n")
                        if refresh_token:
                            f.write(f"SCHWAB_REFRESH_TOKEN={refresh_token}\n")
                    
                    print("✅ Tokens saved to .env!")
                    print("\n🚀 RESTART THE FOREX BOT NOW!")
                    print("   It will use REAL API calls with this token!")
                    
                else:
                    print(f"❌ Failed to get token: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error exchanging code: {e}")
            
            # Send response to browser
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Success! You can close this window.</h1><p>Check the terminal for next steps.</p>")
            
            # Stop the server
            import threading
            threading.Thread(target=self.server.shutdown).start()
            
        else:
            # No code in URL
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Error: No authorization code found</h1>")
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

print("\n⏳ Waiting for callback on http://localhost:8080/callback")
print("   Complete the login in browser, then check back here...")

try:
    # Start server
    with socketserver.TCPServer(("", 8080), CallbackHandler) as httpd:
        print("   Server started on port 8080")
        print("   Press Ctrl+C to cancel")
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\n⚠️  Cancelled by user")
except Exception as e:
    print(f"❌ Server error: {e}")

print("\n📋 ALTERNATIVE: Manual Method")
print("   If browser flow doesn't work:")
print("   1. Manually open: " + auth_full_url)
print("   2. Login and approve")
print("   3. You'll get redirected to an error page (localhost:8080 won't work)")
print("   4. COPY the 'code=' parameter from URL")
print("   5. Tell me the code, I'll exchange it for token")