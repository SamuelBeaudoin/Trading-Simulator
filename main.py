import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
import copy
import sqlite3
import time

#function to make a list into a normal string
def listToString(s):
    # initialize an empty string
    str1 = " "

    # return string
    return (str1.join(s))

# Download historical data (monthly) for DJI constituent stocks
def main(portfolio):

    tickers = ["AXP", "AMZN", "BA", "CAT", "CSCO", "KO", "XOM", "GE", "GS", "HD",
               "IBM", "INTC", "JNJ", "JPM", "MCD", "MRK", "MSFT", "NKE", "PFE", "PG", "TRV",
               "UNH", "VZ", "V", "WMT", "DIS"]

    ohlc_mon = {}  # directory with ohlc value for each stock
    start = dt.datetime.today() - dt.timedelta(days=10)
    end = dt.datetime.today()

    # looping over tickers and creating a dataframe with close prices
    for ticker in tickers:
        ohlc_mon[ticker] = yf.download(ticker, start, end, interval='5d')
        ohlc_mon[ticker].dropna(inplace=True, how="all")

    tickers = ohlc_mon.keys()  # redefine tickers variable after removing any tickers with corrupted data

    # calculating monthly return for each stock and consolidating return info by stock in a separate dataframe
    ohlc_dict = copy.deepcopy(ohlc_mon)
    return_df = pd.DataFrame()
    for ticker in tickers:
        print("calculating 5 day return for ", ticker)
        ohlc_dict[ticker]["week_ret"] = ohlc_dict[ticker]["Adj Close"].pct_change()
        ohlc_dict[ticker]["Added_ret"] = ohlc_dict[ticker]["week_ret"].sum(skipna=True)
        return_df[ticker] = ohlc_dict[ticker]["Added_ret"]
    return_df.dropna(inplace=True)
    return_df.drop_duplicates(subset=None, keep="first", inplace=True)


    # function to calculate portfolio return iteratively
    def pflio(DF, portfolio, m=6, x=3):
        df = DF.copy()
        weekly_ret = 0
        for i in range(len(df)):
            if len(portfolio) > 0:
                weekly_ret = (df[portfolio].iloc[i, :].sum())
                bad_stocks = df[portfolio].iloc[i, :].sort_values(ascending=True)[:x].index.values.tolist()
                portfolio = [t for t in portfolio if t not in bad_stocks]
            fill = m - len(portfolio)
            new_picks = df.iloc[i, :].sort_values(ascending=False)[:fill].index.values.tolist()
            portfolio = portfolio + new_picks
            print(listToString(new_picks))
            print(weekly_ret)

            week_profit = 5000*weekly_ret
            balance=50000

            ##########Adding to database###################
            con = sqlite3.connect('TradingProgress.db')
            cur = con.cursor()
            cur.execute("select * from stocks")
            results = cur.fetchall()
            for row in cur.execute("SELECT * FROM stocks WHERE week=:weekNumber", {"weekNumber":len(results)}):
                balance=row[2]+week_profit
            cur.execute("INSERT INTO stocks VALUES (?, ?, ?, ?, ?, ?, ?)", (len(results)+1, (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), balance, weekly_ret, listToString(new_picks), listToString(portfolio),5000))
            con.commit()
            con.close()

        return portfolio


    portfolio = pflio(return_df, portfolio)
    return portfolio



portfolio = []

starttime=time.time()
timeout = time.time() + 60  # meaning it will run for 60 seconds with 10 second intervals as shows below
while time.time() <= timeout:
    try:
        print("passthrough at ",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        portfolio=main(portfolio)
        time.sleep(10 - ((time.time() - starttime) % 10)) # 10 second intervals
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()


#################ACTUAL CODE THAT RUNS FOR 30 intervals of 5 days############################
# portfolio = []
#
# starttime=time.time()
# timeout = time.time() + 60*60*24*5*30  # meaning it will run for 30 intervals of 5 days
# while time.time() <= timeout:
#     try:
#         print("passthrough at ",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
#         portfolio=main(portfolio)
#         time.sleep((60*60*24*5) - ((time.time() - starttime) % (60*60*24*5))) # 5 days of sleep since I am getting data for last 5 days
#     except KeyboardInterrupt:
#         print('\n\nKeyboard exception received. Exiting.')
#         exit()



##########CODE TO CREATE DATABASE TABLE####################
# cur.execute('''CREATE TABLE stocks (
#     week INTEGER PRIMARY KEY,
#     date TEXT,
#     balance REAL,
#     percentProfit DOUBLE(10,3),
#     newPicks TEXT,
#     portfolio TEXT,
#     investment int)''')