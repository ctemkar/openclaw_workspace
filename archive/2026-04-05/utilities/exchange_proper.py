
if __name__ == '__main__':
    print("="*70)
    print("💰 EXCHANGE SIMPLE DASHBOARD")
    print("="*70)
    print("✅ Shows EXACT holdings on each exchange")
    print("✅ Separate tables for Gemini and Binance")
    print("✅ No filtering, no heuristics - matches exchange data")
    print("="*70)
    print("Dashboard: http://localhost:5015/")
    print("API Endpoints:")
    print("  • Gemini: http://localhost:5015/api/gemini")
    print("  • Binance: http://localhost:5015/api/binance")
    print("  • All: http://localhost:5015/api/all")
    print("="*70)
    
    app.run(host='0.0.0.0', port=5015, debug=False)
