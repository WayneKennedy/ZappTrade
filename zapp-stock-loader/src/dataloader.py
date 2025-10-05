import time
import re
import psycopg2
import datetime as dt
import pandas as pd
import yfinance as yf
from pytickersymbols import PyTickerSymbols

#Define our connection string
conn_string = "host='zapp-stock-db' dbname='zapp_stock_db' user='docker' password='docker'"

load_interval_seconds = 600

stock_data = PyTickerSymbols()

def clean_ticker(raw_ticker):
    ticker = re.sub(r'^[\W_]+|[\W_]+$', '', raw_ticker)
    if '.' not in ticker:
        return ticker + '.L'
    return ticker

def load_stocks():
    uk_stocks = stock_data.get_stocks_by_index('FTSE 100')

    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()

    sqlAddStock = "INSERT INTO stocks (ticker, index, source, yahoo_ticker, company_name) VALUES (%s, %s, %s, %s, %s) ON CONFLICT ON CONSTRAINT stocks_pkey DO NOTHING;"

    for stock in uk_stocks:
        raw_ticker = stock['symbol']
        ticker = clean_ticker(raw_ticker)
        name = stock['name']
        cursor.execute(sqlAddStock, (raw_ticker, 'FTSE 100', 'PyTickerSymbols', ticker, name))

    conn.commit()
    cursor.close()
    conn.close()

def load_dailies():
    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()

    # Get all tickers from stocks table
    cursor.execute ('select yahoo_ticker from stocks')
    tickers = cursor.fetchall()

    sql = "SELECT date FROM daily WHERE ticker = %s ORDER BY date DESC LIMIT 1"
    sqlDaily = "INSERT INTO daily values(%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (date, ticker) DO NOTHING;"

    # For each, find last entry in daily table
    for t in tickers:
        ticker = t[0]
        cursor.execute(sql, [ticker])
        daily = cursor.fetchall()

        # Determine date range for getting data
        dateStart = dt.date(2000, 1, 1)
        dateEnd = dt.date.today()
        if len(daily) > 0:
            dateStart = daily[0][0].date() + dt.timedelta(days=1)
        
        if dateStart < dateEnd:
            print(f"Require data from {ticker} for dates [{dateStart}] to [{dateEnd}]")

            # Get the data from Yahoo using yfinance
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(start=dateStart, end=dateEnd)

                if not df.empty:
                    for index, row in df.iterrows():
                        cursor.execute(sqlDaily, (
                            index.date(),
                            ticker,
                            float(row['High']) if pd.notna(row['High']) else None,
                            float(row['Low']) if pd.notna(row['Low']) else None,
                            float(row['Open']) if pd.notna(row['Open']) else None,
                            float(row['Close']) if pd.notna(row['Close']) else None,
                            int(row['Volume']) if pd.notna(row['Volume']) else None,
                            float(row['Close']) if pd.notna(row['Close']) else None
                        ))
                    conn.commit()
                    print(f"Loaded {len(df)} records for {ticker}")
                else:
                    print(f"No data available for {ticker}")
            except Exception as ex:
                print(f'Unable to get data for {ticker}: {ex}')

    cursor.close()
    conn.close()

# ************ Main *************
while True:
    load_stocks()
    load_dailies()
    time.sleep(load_interval_seconds)
