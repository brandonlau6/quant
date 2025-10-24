import yfinance as yf 
import uuid
import time
import os
import pandas as pd
from sqlalchemy import create_engine

from models import Base

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/ssmif")

Base.metadata.create_all(engine)

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


def test_ingest1(start_date,end_date,ticker):
    tickerData = yf.download(ticker, start_date, end_date, group_by=ticker, auto_adjust=False)[ticker]
    tickerData.index = tickerData.index.tz_localize(None)
    return tickerData

def test_ingest2():
    ingest_data('2020-01-01','2025-01-01','AAPL')
    