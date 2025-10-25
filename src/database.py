from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

engine = create_engine("postgresql+psycopg2://postgres:postgres@db:5432/ssmif")

def init_db():
    Base.metadata.create_all(engine)

class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adj_close = Column(Float)
    volume = Column(Float)

    __table_args__ = (UniqueConstraint("symbol", "date", name="unique_prices_symbol_date"),)

class Trades(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    signal = Column(String, nullable = False)
    strategy = Column(String, nullable = True)
    price = Column(Float)
    profit = Column(Float)
    __table_args__ = (UniqueConstraint("symbol", "date", name="unique_trades_symbol_date"),)