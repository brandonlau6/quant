from database import *
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from strategy import *
import numpy as np

def metrics(tradesDf):
    try:
        #tradesDf = pd.DataFrame(get_trades(start_date, end_date, ticker, strategy))
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

        #return {"profit": profit, "winProbability": win_probability, "maxDrawdown": max_drawdown, "annualized": annualized_return}
        return [{'Metric': 'Profit','Value': profit},{'Metric':'Win Probability','Value': win_probability},{'Metric':'maxDrawdown','Value': max_drawdown},{'Metric':'annualized','Value':annualized_return}]
    except:
        return "Calculation Failed"