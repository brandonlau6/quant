import backtrader as bt
from ingester import *

## strategy to buy or sell depending on threshhold
class ThresholdStrategy(bt.Strategy):
    params = (
        ("buy_threshold", 100),   # Buy if price goes above this
        ("sell_threshold", 105),  # Sell if price goes above this
    )

    def next(self):
        if not self.position:  # Not in a trade
            if self.data.close[0] >= self.params.buy_threshold:
                self.buy()
                print(f"BUY at {self.data.close[0]}")
        else:  # Already in a trade
            if self.data.close[0] >= self.params.sell_threshold:
                self.sell()
                print(f"SELL at {self.data.close[0]}")

# Set up cerebro engine
cerebro = bt.Cerebro()

## change later, imports data frame from ingester script
df = test_ingest1('2020-01-01','2021-01-01','MSFT') # Replace with your CSV

## ???
data = bt.feeds.PandasData(dataname=df)

## adds data to crebro 
cerebro.adddata(data)
cerebro.addstrategy(ThresholdStrategy, buy_threshold=100, sell_threshold=110)
cerebro.run()
#cerebro.plot()