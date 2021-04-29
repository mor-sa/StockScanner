from typing import Optional

from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import models
from models import Stock
import libs.utils

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
@app.get("/dashboard")
def dashboard(request: Request, forward_pe=None, dividend_yield=None, ma50=None, ma200=None,
              db: Session = Depends(get_db)):
    """
    Displays the stock screener dashboard.
    """

    stocks = db.query(Stock)

    if forward_pe:
        stocks = stocks.filter(Stock.forward_pe < forward_pe)

    if dividend_yield:
        stocks = stocks.filter(Stock.dividend_yield > dividend_yield)

    if ma50:
        stocks = stocks.filter(Stock.price > Stock.ma50)

    if ma200:
        stocks = stocks.filter(Stock.price > Stock.ma200)

    stocks = stocks.all()

    print(stocks)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stocks": stocks,
        "dividend_yield": dividend_yield,
        "forward_pe": forward_pe,
        "ma50": ma50,
        "ma200": ma200
    })


@app.post("/add_stock")
# Does the same thing:
# @app.route("/stock", methods=["POST", "GET"])
async def create_stock(stock_request: libs.utils.StockRequest, background_tasks: BackgroundTasks,
                       db: Session = Depends(get_db)):
    stock = Stock()
    stock.symbol = stock_request.symbol

    db.add(stock)
    db.commit()

    background_tasks.add_task(libs.utils.fetch_stock_data, stock.id)

    return {
        "code": "success",
        "message": "stock added to database"
    }

# async def delete_stock(stock_request: libs.utils.StockRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
#     stock = Stock()
#     stock.symbol = stock_request.symbol
#
#     background_tasks.add_task(libs.del_stock, stock.id)
#
#     return {
#         "code": "success",
#         "message": "stock deleted from database"
#     }
