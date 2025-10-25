from ingester import *
from sqlalchemy import create_engine

from datetime import datetime

from database import *

from getMissing import *

def main():
    print("Ingest data to database")
    ticker = input("Enter Ticker: ")
    startDate = input("Enter start date: ")
    endDate = input("Enter end date: ")

    db_ticker(startDate,endDate,ticker)

    sampleData = retrieveTicker(startDate, endDate, ticker).tail()

    print(f"Tail: \n {sampleData}")
main()
