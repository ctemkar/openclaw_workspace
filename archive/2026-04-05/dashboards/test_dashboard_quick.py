#!/usr/bin/env python3
"""
Quick test of the dashboard
"""
import requests
import time

def test_dashboard():
    print("Testing Real-Time Trades Dashboard...")
    
    try:
        # Try multiple times with short timeout
        for attempt in range(3):
            try:
                print(f"Attempt {attempt + 1}...")
                r = requests.get('http://localhost:5011/', timeout=3)
                
                if r.status_code == 200:
                    print("✅ Dashboard HTTP 200 OK")
                    
                    # Check for key elements
                    content = r.text
                    
                    checks = [
                        ("Real-Time Trades Dashboard", "Dashboard title"),
                        ("GEMINI LONG POSITIONS", "Gemini section"),
                        ("BINANCE SHORT POSITIONS", "Binance section"),
                        ("GEMINI TOTAL:", "Gemini total row"),
                        ("BINANCE TOTAL:", "Binance total row")
                    ]
                    
                    print("\n🎯 FEATURES FOUND:")
                    for text, desc in checks:
                        if text in content:
                            print(f"   ✅ {desc}")
                        else:
                            print(f"   ❌ {desc} NOT FOUND")
                    
                    # Show sample of content
                    print("\n📋 SAMPLE CONTENT (first 1000 chars):")
                    print(content[:1000])
                    
                    return True
                    
                else:
                    print(f"❌ HTTP {r.status_code}")
                    
            except requests.exceptions.Timeout:
                print("⏱️ Timeout, retrying...")
                time.sleep(1)
                continue
            except requests.exceptions.ConnectionError:
                print("🔌 Connection error, retrying...")
                time.sleep(1)
                continue
                
        print("❌ All attempts failed")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_dashboard()