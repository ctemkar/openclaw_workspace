import sqlite3
import pandas as pd

conn = sqlite3.connect('trading_bot.db')
df = pd.read_sql_query('SELECT * FROM trades', conn)
print(f'Total trades: {len(df)}')
if len(df) > 0:
    df['profit'] = df['sell_price'] - df['buy_price']
    df['profit_pct'] = (df['profit'] / df['buy_price']) * 100
    wins = df[df['profit'] > 0]
    losses = df[df['profit'] < 0]
    print(f'Wins: {len(wins)}')
    print(f'Losses: {len(losses)}')
    print(f'Win rate: {len(wins)/len(df)*100:.1f}%')
    print(f'Avg profit %: {df["profit_pct"].mean():.2f}%')
    print(f'Max drawdown %: {df["profit_pct"].min():.2f}%')
    print(f'Total profit: ${df["profit"].sum():.2f}')
    print('\nRecent trades:')
    print(df[['symbol', 'buy_price', 'sell_price', 'profit', 'profit_pct']].tail())
conn.close()