import time
import re
import psycopg2
import datetime as dt
import pandas as pd
import pandas_datareader.data as web
from pytickersymbols import PyTickerSymbols
from datetime import date

#Define our connection string
conn_string = "host='zapp-stock-db' dbname='zapp_stock_db' user='docker' password='docker'"

load_interval_seconds = 600

stock_data = PyTickerSymbols()

def clean_ticker(raw_ticker):
    ticker = re.sub(r'^[\W_]+|[\W_]+$', '', raw_ticker)
    contains_period = False
    for c in ticker:
        if c == '.':
            contains_period = True
    if not contains_period:
        return ticker + '.L'
    else:
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
        #re.sub('[^A-Za-z0-9]+', '', raw_ticker) + '.L'
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
        # print(sql)
        # print (ticker)
        cursor.execute(sql, [ticker])
        daily = cursor.fetchall()

        # Determine date range for getting data
        dateStart = dt.date(2000, 1, 1)
        dateEnd = dt.date.today()
        if len(daily) > 0:
            dateStart = daily[0][0].date() + dt.timedelta(days=1)
        
        if dateStart < dateEnd:
            print(f"Require data from {ticker} for dates [{dateStart}] to [{dateEnd}]")

            # Get the data from Yahoo
            try:
                df = web.DataReader(ticker, 'yahoo', dateStart, dateEnd)
                for row in df.itertuples():
                    # print(row)
                    cursor.execute(sqlDaily, (row[0].date(), ticker, row[1], row[2], row[3], row[4], row[5], row[6]))

                conn.commit()
            except Exception as ex:
                print('Unable to get data for {}'.format(ticker))

    cursor.close()
    conn.close()

# ************ Main *************
while True:
    load_stocks()
    load_dailies()
    time.sleep(load_interval_seconds)
