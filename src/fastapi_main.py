from fastapi import FastAPI
from pydantic import BaseModel
from database import *
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from strategy import *

app = FastAPI()

init_db()

@app.get("/api/v1/trades")
def get_trades_endpoint(start: str, end: str, ticker:str, strategy:str):
    trades = get_trades(start,end,ticker, strategy)
    return {"logs": trades}

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

    trades = tradesDf.to_dict(orient='records')
    return trades


class backtestRequest(BaseModel):
    start: str
    end: str
    ticker: str
    buy: float
    sell: float

@app.post("/api/v1/backtest")
def backtest_endpoint(body:backtestRequest):
    try:
        backDb(ThresholdStrategy, body.buy,body.sell,body.start,body.end,body.ticker)
    except:
        return "Please retry with correct ticker or start/end date."

class metricsRequest(BaseModel):
    start: str
    end: str
    ticker: str
    strategy: str

@app.post("/api/v1/metrics")
def metrics_endpoint(body:metricsRequest):
    try:
        tradesDf = pd.DataFrame(get_trades(body.start,body.end,body.ticker,body.strategy))
        # extract buy and sell data from table 
        buy = tradesDf[tradesDf['signal'] == 'BUY']['price'].values
        sell = tradesDf[tradesDf['signal']== 'SELL']['price'].values
        
        realizedTrades = min(len(buy),len(sell))

        profitData = sell[:realizedTrades] - buy[:realizedTrades]

        profit = np.sum(profitData)

        win_probability = np.mean(profitData > 0) if len(profitData) > 0 else np.nan

        equity_curve = np.cumsum(profitData)
        rolling_max = np.maximum.accumulate(equity_curve)
        drawdown = rolling_max - equity_curve
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0

        if not tradesDf.empty:
            days = (tradesDf['date'].iloc[-1] - tradesDf['date'].iloc[0]).days
            if days > 0:
                daily_return = profit / len(tradesDf)
                annualized_return = (1 + daily_return)**(252) - 1  # assuming daily data
            else:
                annualized_return = 0
        else:
            annualized_return = 0

        return {"profit": profit, "winProbability": win_probability, "maxDrawdown": max_drawdown, "annualized": annualized_return}
        
    except:
        return "Calculation Failed"