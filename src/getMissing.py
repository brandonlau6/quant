import pandas as pd
from datetime import datetime, date, timedelta


## Generated with chatgpt
# ------------------------------
# Helper to compute nth weekday
# ------------------------------
def nth_weekday_of_month(year, month, weekday, n):
    """
    Return the date of the nth weekday of a month.
    weekday: 0=Monday, 6=Sunday
    n: 1=first, 3=third, etc.
    """
    d = date(year, month, 1)
    days_ahead = (weekday - d.weekday() + 7) % 7
    first_occurrence = d + timedelta(days=days_ahead)
    return first_occurrence + timedelta(weeks=n-1)

# ------------------------------
# Compute US market holidays
# ------------------------------
def get_us_market_holidays(year):
    holidays = [
        nth_weekday_of_month(year, 1, 0, 3),   # MLK Day, 3rd Monday Jan
        nth_weekday_of_month(year, 2, 0, 3),   # Presidents Day, 3rd Monday Feb
        date(year, 7, 4),                      # Independence Day
        nth_weekday_of_month(year, 9, 0, 1),   # Labor Day, 1st Monday Sep
        date(year, 12, 25),                     # Christmas
    ]
    return holidays

# ------------------------------
# Main function to get missing intervals
# ------------------------------
def get_missing_intervals_with_holidays(engine, symbol: str, start_date: str, end_date: str):
    """
    Returns missing trading intervals for a symbol, skipping weekends and US market holidays.
    """
    # Validate dates
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)

    # 1️⃣ Fetch existing dates from DB
    query = """
    SELECT date
    FROM Prices
    WHERE symbol = %(symbol)s
      AND date BETWEEN %(start)s AND %(end)s
    ORDER BY date
    """
    existing = pd.read_sql(query, engine, params={"symbol": symbol, "start": start_date, "end": end_date})
    existing_dates = pd.to_datetime(existing['date'])

    # 2️⃣ Generate full range of business days
    full_range = pd.date_range(start=start_dt, end=end_dt, freq='B')

    # 3️⃣ Compute holidays for each year in range
    years = range(start_dt.year, end_dt.year + 1)
    holidays = []
    for y in years:
        holidays.extend(get_us_market_holidays(y))
    holidays = pd.to_datetime(holidays)

    # 4️⃣ Remove holidays from business days
    valid_days = full_range.difference(holidays)

    # 5️⃣ Compute missing dates
    missing_dates = valid_days.difference(existing_dates)

    if missing_dates.empty:
        return []

    # 6️⃣ Convert missing dates to contiguous intervals
    intervals = []
    start = end = missing_dates[0]
    for d in missing_dates[1:]:
        if (d - end).days == 1:
            end = d
        else:
            intervals.append((start.date(), end.date()))
            start = end = d
    intervals.append((start.date(), end.date()))

    return intervals
