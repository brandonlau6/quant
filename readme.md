# Introduction
This basic application will simulate backtested trades on a given ticker, allowing for user input start and end dates as well as ticker, and the program will run a trade simulation, returning a list of trades to the user, as well as several metrics including profit/loss, annualized return, max drawdown and win probability

# Overview
Stack consists of NiceGUI frontend /backend and PostGresql database packaged in docker compose. The backtesting algorithm is built using [Backtrader](https://www.backtrader.com/)
