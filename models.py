from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    stock_symbol = Column(String(10), nullable=False)  # 股票代號 e.g. "2330"
    stock_name = Column(String(50), nullable=False)    # 股票名稱 e.g. "台積電"
    transaction_type = Column(String(10), nullable=False)  # "買入" 或 "賣出"
    quantity = Column(Integer, nullable=False)  # 股數
    price = Column(Float, nullable=False)  # 成交價
    fee = Column(Float, default=0)  # 手續費
    date = Column(DateTime, nullable=False)  # 交易日期
    created_at = Column(DateTime, default=datetime.now)

class Dividend(Base):
    __tablename__ = "dividends"

    id = Column(Integer, primary_key=True)
    stock_symbol = Column(String(10), nullable=False)
    stock_name = Column(String(50), nullable=False)
    dividend_type = Column(String(20), nullable=False)  # "現金股利" 或 "股票股利"
    amount = Column(Float, nullable=False)  # 股利金額
    date = Column(DateTime, nullable=False)  # 除息日
    created_at = Column(DateTime, default=datetime.now)
