#!/usr/bin/env python3
import json
import datetime

def analyze_portfolio():
    # Load trades
    with open('completed_trades.json', 'r') as f:
        trades = json.load(f)

    # Load config
    with open('trading_config.json', 'r') as f:
        config = json.load(f)

    # Calculate portfolio
    total_btc = sum(t['amount'] for t in trades if t['side'] == 'buy')
    total_invested = sum(t['amount'] * t['price'] for t in trades if t['side'] == 'buy')
    avg_price = total_invested / total_btc if total_btc > 0 else 0

    # Current BTC price (from CoinGecko)
    btc_price = 74358.00

    # Calculate current value and P&L
    current_value = total_btc * btc_price
    pnl = current_value - total_invested
    pnl_pct = (pnl / total_invested * 100) if total_invested > 0 else 0

    # Risk calculations
    stop_loss_price = avg_price * (1 - config['stop_loss_pct'])
    take_profit_price = avg_price * (1 + config['take_profit_pct'])

    print('=== PORTFOLIO ANALYSIS {} ==='.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print('BTC Holdings: {:.8f} BTC'.format(total_btc))
    print('Current BTC Price: ${:,.2f}'.format(btc_price))
    print('Current Portfolio Value: ${:.2f}'.format(current_value))
    print('Investment: ${:.2f}'.format(total_invested))
    print('Current P&L: ${:.2f} ({:.2f}%)'.format(pnl, pnl_pct))
    print('Average Entry Price: ${:.2f}'.format(avg_price))
    print('Current BTC Price vs Entry: {:.2f}%'.format(((btc_price - avg_price) / avg_price * 100)))
    print()
    print('=== RISK PARAMETERS ===')
    print('Stop Loss: -{:.1f}% (${:.2f})'.format(config['stop_loss_pct']*100, stop_loss_price))
    print('Take Profit: +{:.1f}% (${:.2f})'.format(config['take_profit_pct']*100, take_profit_price))
    print('Critical Drawdown: -5.00% (${:.2f})'.format(avg_price * 0.95))
    print()
    print('=== DISTANCE TO TRIGGERS ===')
    print('Stop Loss Distance: {:.2f}%'.format(((btc_price - stop_loss_price) / avg_price * 100)))
    print('Take Profit Distance: {:.2f}%'.format(((take_profit_price - btc_price) / avg_price * 100)))
    print('Critical Drawdown Distance: {:.2f}%'.format(((btc_price - (avg_price * 0.95)) / avg_price * 100)))
    
    return {
        'total_btc': total_btc,
        'btc_price': btc_price,
        'current_value': current_value,
        'total_invested': total_invested,
        'pnl': pnl,
        'pnl_pct': pnl_pct,
        'avg_price': avg_price,
        'stop_loss_price': stop_loss_price,
        'take_profit_price': take_profit_price,
        'critical_drawdown_price': avg_price * 0.95
    }

if __name__ == '__main__':
    analyze_portfolio()