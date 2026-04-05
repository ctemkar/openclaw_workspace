#!/bin/bash
# RUN ALL ESSENTIAL SERVICES
echo "Starting essential trading system services..."

# Dashboards
python3 gateway_5000.py &
python3 truthful_dashboard.py &
python3 nocache_dashboard.py &
python3 real_time_top10_dashboard.py &

# Trading bots (if needed)
# python3 make_money_now.py &
# python3 fixed_practical_profit_bot.py &
# python3 real_26_crypto_arbitrage_bot.py &
# python3 microsecond_arbitrage_bot.py &

echo "Services started. Check ports:"
echo "  Gateway: http://localhost:5001"
echo "  Truthful Dashboard: http://localhost:5024"
echo "  Sorted Spreads: http://localhost:5025"
echo "  REAL-TIME Top 10: http://localhost:5026"
