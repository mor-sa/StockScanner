import yfinance
from pydantic import BaseModel

from database import SessionLocal
from models import Stock


class StockRequest(BaseModel):
    symbol: str


def fetch_stock_data(id: int):
    db = SessionLocal()
    stock = db.query(Stock).filter(Stock.id == id).first()

    stock_data = yfinance.Ticker(stock.symbol)

    stock.ma200 = stock_data.info['twoHundredDayAverage'] if stock_data.info['twoHundredDayAverage'] else 0
    stock.ma50 = stock_data.info['fiftyDayAverage'] if stock_data.info['fiftyDayAverage'] else 0
    stock.price = stock_data.info['previousClose'] if stock_data.info['previousClose'] else 0
    stock.forward_pe = stock_data.info['forwardPE'] if stock_data.info['forwardPE'] else 0
    stock.forward_eps = stock_data.info['forwardEps'] if stock_data.info['forwardEps'] else 0
    stock.dividend_yield = stock_data.info['dividendYield'] * 100 if stock_data.info['dividendYield'] else 0

    db.add(stock)
    db.commit()

# def del_stock(id: int):
#     db = SessionLocal()
#     db.query(Stock).filter(Stock.id == id).delete()
#     db.commit()