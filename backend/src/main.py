from fastapi import FastAPI
from pydantic import BaseModel
from database import *
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from strategy import *
from calculations import metrics

app = FastAPI()

init_db()

origins_env = os.getenv("FRONTEND_ORIGINS", "")
#origins_env = "http://localhost:5173"
origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # or ["*"] for testing
    allow_credentials=True,
    allow_methods=["*"],          # allow POST, GET, etc.
    allow_headers=["*"],
)

class backtestRequest(BaseModel):
    start: str
    end: str
    ticker: str
    strategy:str
    buy: float
    sell: float

## Send request to backend for backtesting
@app.post("/api/v1/backtest")
def doBacktest(body:backtestRequest):
    try:
        backDb(body.buy, body.sell, body.start, body.end, body.ticker, body.strategy)
        return "Backtesting Successful"
    except:
        return "Error backtesting"

# get backtesting results
@app.get("/api/v1/getBacktest")
def backtest_endpoint(start: str, end: str, ticker:str, strategy:str, size: int=10, offset:int=0):
    return getTradesPaginated(start,end,ticker,strategy,size=size, offset=offset)

class metricsRequest(BaseModel):
    start: str
    end: str
    ticker: str
    strategy: str


# get 
@app.post("/api/v1/metrics")
def metrics_endpoint(body:metricsRequest):
    try:
        tradeMetrics = metrics(get_trades(body.start,body.end,body.ticker,body.strategy))
        return tradeMetrics
    except:
        return "Calculation Failed"

