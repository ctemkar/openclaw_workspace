#!/usr/bin/env python3
"""
Check current crypto holdings and trading status
"""

import json
from datetime import datetime

def main():
    print("CURRENT TRADING STATUS ANALYSIS")
    print("=" * 60)
    
    try:
        # Check current holdings from accurate_capital.json
        with open('accurate_capital.json', 'r') as f:
            data = json.load(f)
        
        print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC+7')}")
        print()
        
        # Capital information
        initial_capital = data.get("initial_capital", 0)
        current_capital = data.get("current_capital", 0)
        cash = data.get("cash", 0)
        
        print("CAPITAL SUMMARY:")
        print(f"• Initial Capital: ${initial_capital:,.2f}")
        print(f"• Current Total Value: ${current_capital:,.2f}")
        print(f"• Available Cash: ${cash:,.2f}")
        
        # Calculate performance
        if initial_capital > 0:
            total_return = current_capital - initial_capital
            total_return_pct = (total_return / initial_capital) * 100
            print(f"• Total Return: ${total_return:,.2f} ({total_return_pct:.2f}%)")
        
        # Crypto holdings
        crypto_holdings = data.get("crypto_holdings", {})
        if crypto_holdings and "BTC" in crypto_holdings:
            btc = crypto_holdings["BTC"]
            print()
            print("BTC HOLDINGS:")
            print(f"• Amount: {btc.get('amount', 0):.6f} BTC")
            print(f"• Average Buy Price: ${btc.get('average_buy_price', 0):,.2f}")
            print(f"• Current Price: ${btc.get('current_price', 0):,.2f}")
            print(f"• Current Value: ${btc.get('current_value', 0):,.2f}")
            
            unrealized_pnl = btc.get('unrealized_pnl', 0)
            unrealized_pnl_pct = btc.get('unrealized_pnl_percent', 0)
            print(f"• Unrealized P&L: ${unrealized_pnl:,.2f} ({unrealized_pnl_pct:.2f}%)")
            
            # Calculate if we should add to position or hold
            current_price = btc.get('current_price', 0)
            avg_price = btc.get('average_buy_price', 0)
            
            if current_price > 0 and avg_price > 0:
                price_diff_pct = ((current_price - avg_price) / avg_price) * 100
                if price_diff_pct < -2:  # Down more than 2%
                    print(f"• Status: Position underwater by {abs(price_diff_pct):.2f}% - Consider holding")
                elif price_diff_pct > 5:  # Up more than 5%
                    print(f"• Status: Position profitable by {price_diff_pct:.2f}% - Consider taking partial profits")
                else:
                    print(f"• Status: Position stable ({price_diff_pct:.2f}%) - Hold")
        
        # Today's trades
        today_trades = data.get("today_trades", [])
        if today_trades:
            print()
            print(f"TODAY'S TRADES ({len(today_trades)}):")
            for i, trade in enumerate(today_trades, 1):
                symbol = trade.get("symbol", "Unknown")
                side = trade.get("side", "").upper()
                amount = trade.get("amount", 0)
                price = trade.get("price", 0)
                cost = trade.get("cost", 0)
                time = trade.get("time", "")
                
                print(f"  {i}. {time}: {side} {amount:.6f} {symbol} @ ${price:,.2f} (${cost:,.2f})")
        
        # Performance metrics
        performance = data.get("performance", {})
        if performance:
            print()
            print("PERFORMANCE METRICS:")
            print(f"• Daily Trades: {performance.get('daily_trades', 0)}")
            print(f"• Daily Volume: ${performance.get('daily_volume', 0):,.2f}")
        
        print()
        print(f"Last Updated: {data.get('last_updated', 'Unknown')}")
        
        # Trading recommendations based on current holdings
        print()
        print("TRADING RECOMMENDATIONS:")
        
        if crypto_holdings and "BTC" in crypto_holdings:
            btc_amount = crypto_holdings["BTC"].get("amount", 0)
            btc_value = crypto_holdings["BTC"].get("current_value", 0)
            
            # Conservative position sizing check
            max_position_value = 1000 * 0.5  # 50% of $1,000 capital
            current_position_pct = (btc_value / 1000) * 100
            
            if btc_value > max_position_value:
                print(f"• ⚠️  Position size (${btc_value:,.2f}) exceeds conservative limit (${max_position_value:,.2f})")
                print(f"  Consider reducing position to maintain 50% max allocation")
            else:
                print(f"• ✅ Position size (${btc_value:,.2f}) within conservative limits")
                print(f"  Current allocation: {current_position_pct:.1f}% of $1,000 capital")
            
            # Check if we've reached daily trade limit
            if len(today_trades) >= 2:
                print(f"• ⚠️  Daily trade limit ({len(today_trades)}/2) reached")
                print(f"  No more trades recommended today")
            else:
                trades_remaining = 2 - len(today_trades)
                print(f"• ✅ Trades remaining today: {trades_remaining}")
                
                if cash >= 500:  # Enough for max position
                    print(f"  Available for new position: ${cash:,.2f}")
                else:
                    print(f"  Limited cash available: ${cash:,.2f}")
        
        else:
            print("• No current crypto holdings")
            if cash >= 500:
                print(f"  ✅ ${cash:,.2f} available for new position (up to 50% of capital)")
            else:
                print(f"  ⚠️  Limited cash: ${cash:,.2f} available")
        
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"Error analyzing holdings: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()