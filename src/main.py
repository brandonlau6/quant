from database import *
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from strategy import *
from nicegui import ui
import numpy as np
from calculations import metrics

init_db()

startDate = '2020-01-01'
endDate = '2020-10-01'
ticker = 'AMZN'
strategy = 'constantPrice'

buy = 50
sell = 60

uiTable = pd.DataFrame([])

columns=[{'name': 'Metric', 'label': 'Metric', 'field': 'Metric'},
             {'name': 'Value', 'label': 'Value', 'field': 'Value'}]
rows = metrics(uiTable)

with ui.input('Start Date').bind_value(globals(), 'startDate') as date_input:
    with ui.menu() as menu:
        ui.date(on_change=lambda: ui.notify(f'Date: {startDate}')).bind_value(date_input)
    with date_input.add_slot('append'):
        ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')


with ui.input('End Date').bind_value(globals(), 'endDate') as date_input:
    with ui.menu() as menu:
        ui.date(on_change=lambda: ui.notify(f'Date: {endDate}')).bind_value(date_input)
    with date_input.add_slot('append'):
        ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')



ui.input('Ticker').bind_value(globals(), 'ticker')

ui.input('Strategy').bind_value(globals(), 'strategy')

ui.input('Buy Threshold').bind_value(globals(),'buy')

ui.input('Sell Threshold').bind_value(globals(),'sell')

ui.button('Backtest', on_click=lambda: updateTable())

ui.button("Download CSV", on_click=lambda: ui.download(bytes(uiTable.to_csv(lineterminator='\r\n', index=False), encoding='utf-8'), filename="output.csv"))

#ui.button('Backtest', on_click=lambda: ui_backtest())

@ui.refreshable
def tradesTable():
    with ui.column().classes('items-left justify-left w-full'):
            ui.table.from_pandas(uiTable)

@ui.refreshable
def metricsTable():
    ui.table(columns=columns, rows=rows, row_key='name')

metricsTable()
tradesTable()



ui.run()

def updateTable():
        global uiTable, rows
        uiTable = backtest(strategy, float(buy), float(sell), startDate,endDate,ticker)
        rows = metrics(uiTable)
        tradesTable.refresh()
        metricsTable.refresh()




    



def ui_backtest():
    backtest(strategy, float(buy), float(sell), startDate,endDate,ticker)

    tradesTable()

