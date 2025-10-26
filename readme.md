# Introduction
This basic application will simulate backtested trades on a given ticker, allowing for user input start and end dates as well as ticker, and the program will run a trade simulation, returning a list of trades to the user, as well as several metrics including profit/loss, annualized return, max drawdown and win probability

# Overview
Stack consists of React Frontend, FastAPI backend and PostGresql database packaged in docker compose. The backtesting algorithm is built using [Backtrader](https://www.backtrader.com/)

As the user requests for backtesting, the ingester script will automatically populate the database with price information on that ticker and retrieve it to perform the backtesting, if the data is not present in the database it will retrieve it via [yfinance](https://pypi.org/project/yfinance/)

# Trading Strategy
I have implemented a simple constant price threshold trading strategy, however the application should support alternative trading strategies and reflect changes appropriately. All code for the trading strategy is contained within strategy.py

# Deployment
## Requirements
- Docker and Docker compose installed
- Git 
## Instructions
1. Clone the repository
```
git clone https://github.com/brandonlau6/quant.git
cd quant
```
2. Edit docker compose
This is optional but you can change the port of the frontend and database if necessary

3. Build and run stack
```
docker compose up -d 
```

4. Once started, navigate to http://localhost:8080

# Development
This application was developed using nix, you can run ``nix develop`` to enter into a development environment with all dependencies

Alternatively:
1. Create and enter a [[python virtual environment]](https://docs.python.org/3/library/venv.html)
2. Enter into the source directory
```
cd src
```
3. Run this command to install all dependencies
```
pip install -r requirements.txt
```

# API endpoints
``POST /api/v1/backtest``
Peforms backtest with given start, end, ticker and strategy name, as well as buy and sell threshold

```
{
  "start": "string",
  "end": "string",
  "ticker": "string",
  "strategy": "string",
  "buy": 0,
  "sell": 0
}
```
eg:
```
{
  "start": "2020-01-01",
  "end": "2021-01-01",
  "ticker": "AAPL",
  "strategy": "strategy1",
  "buy": 50,
  "sell": 60
}
```


Will save trading data to database

---
``GET /api/v1/getBacktest``
Retrieves backtest information from database, given strategy name, start, end and ticker.

---
``POST /api/v1/metrics``
Retrieves strategy metrics given strategy name, start, end and ticker

```
{
  "start": "string",
  "end": "string",
  "ticker": "string",
  "strategy": "string"
}
```

eg:
```
{
  "start": "2020-01-01",
  "end": "2020-10-01",
  "ticker": "AAPL",
  "strategy": "test1"
}
```
response:
```
[
  {
    "Metric": "Profit",
    "Value": 37.44499969482422
  },
  {
    "Metric": "Win Probability",
    "Value": 0.5555555555555556
  },
  {
    "Metric": "maxDrawdown",
    "Value": 8.397506713867188
  },
  {
    "Metric": "annualized",
    "Value": 5.7233562057236564e+22
  }
]
```
