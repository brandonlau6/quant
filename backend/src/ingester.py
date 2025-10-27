import yfinance as yf 
import uuid
import time
import os
import pandas as pd
from sqlalchemy import create_engine

from datetime import datetime

from database import *

from getMissing import *



def ingest_data(start_date, end_date, ticker):
    tickerData = yf.download(ticker, start_date, end_date, group_by=ticker, auto_adjust=False)[ticker]
    #return data.tail()
    tickerDf = pd.DataFrame(tickerData)
    tickerDf['symbol'] = ticker
    tickerDf['date'] = tickerDf.index
    # convert  to date time object
    #tickerDf["Date"] = pd.to_datetime(tickerDf["Date"])
    tickerDf.columns = tickerDf.columns.str.lower().str.replace(" ", "_")

    tickerDf.to_sql(
        "prices",
        con=engine,
        if_exists="append",
        index =False
    )

def retrieveTicker(start_date,end_date,ticker):
    '''Returns price data from db of start and end date with given ticker'''
    tickerDf = pd.read_sql(f"SELECT * FROM Prices WHERE symbol = '{ticker}' AND date BETWEEN '{start_date}' AND '{end_date}'", engine)

    # sets date to python date/time format
    tickerDf['date'] = pd.to_datetime(tickerDf['date'])
    # formats index to be same as yahoo fiannce
    tickerDf.set_index('date', inplace=True)
    tickerDf.index = tickerDf.index.tz_localize(None)

    return tickerDf

def db_ticker(start_date,end_date,ticker):    
    '''Returns price data from database from start to end period and will retrieve missing data'''
    # check if the start-end time period is empty, if so will skip and invest data
    if retrieveTicker(start_date,end_date,ticker).empty == True:
        ingest_data(start_date,end_date,ticker)
    else:
        # will look for missing intervals with getmissing
        missing = get_missing_intervals_with_holidays(engine, ticker, start_date, end_date)
        for i in missing:
            startStr = i[0].strftime("%Y-%m-%d")
            endStr = i[1].strftime("%Y-%m-%d")
            ingest_data(startStr, endStr, ticker)
    # returns retrieved info from database
    return retrieveTicker(start_date,end_date,ticker)

