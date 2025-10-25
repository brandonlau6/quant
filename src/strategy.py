import backtrader as bt
from ingester import *
import pandas as pd
#import numpy as np
## strategy to buy or sell depending on threshhold
class ThresholdStrategy(bt.Strategy):
    params = (
        ("buy_threshold", 100),   # Buy if price goes above this
        ("sell_threshold", 105),  # Sell if price goes above this
    )

    def __init__(self):
        # initializes memory table
        self.trades = []
        self.strategyName = "constantPrice"
        #self.metrics = []

    def next(self):
        # 
        date = self.data.datetime.date(0)
        price = self.data.close[0]


        if not self.position:  # Not in a trade
            if self.data.close[0] >= self.params.buy_threshold:
                self.buy()
                self.trades.append({
                    "date": date,
                    "signal": "BUY",
                    "price": price,
                    "strategy": self.strategyName
                })
                #print(f"BUY at {self.data.close[0]}")
        else:  # Already in a trade
            if self.data.close[0] >= self.params.sell_threshold:
                self.sell()
                self.trades.append({
                    "date": date,
                    "signal": "SELL",
                    "price": price,
                    "strategy": self.strategyName
                })
                #print(f"SELL at {self.data.close[0]}")



def backtest(buy, sell, start, end, ticker):
    cerebro = bt.Cerebro()
    #df = test_ingest1(start, end, ticker) # replace with in place change, db_ticker(start,end,ticker) should be able to produce same output
    df = db_ticker(start,end, ticker)
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    cerebro.addstrategy(ThresholdStrategy, buy_threshold=buy, sell_threshold=sell)
    
    # records backtest results
    backtestResults = cerebro.run()
    
    stratResult = backtestResults[0]

    trades_df = pd.DataFrame(stratResult.trades)
    return trades_df

    #tradeDf = pd.Dataframe(strat)


def backDb(strategy, buy_threshhold, sell_threshold, start,end,ticker):
# sends backtested results to database
    backDf = backtest(strategy, buy_threshhold, sell_threshold, start, end, ticker)
    backDf['symbol'] = ticker
    #backDf['date'] = backDf.index
    backDf.columns = backDf.columns.str.lower().str.replace(" ", "_")
    backDf.to_sql(
        "trades",
        con=engine,
        if_exists="append",
        index =False
    )

def get_trades(start_date, end_date, ticker, strategy):
    '''Returns price data from db of start and end date with given ticker'''
    tradesDf = pd.read_sql(f"""
        SELECT date, signal, price, strategy
        FROM Trades
        WHERE symbol = '{ticker}' AND strategy = '{strategy}'
          AND date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY date
    """, engine)

    tradesDf['date'] = pd.to_datetime(tradesDf['date']).dt.date

    return tradesDf


