import yfinance as yf
from sqlalchemy.orm import Session
from models import Transaction, Dividend
from typing import List, Dict
from datetime import datetime

def get_stock_price(symbol: str):
    """取得股票目前價格"""
    try:
        stock = yf.Ticker(f"{symbol}.TW")
        data = stock.history(period='1d')
        if len(data) > 0:
            return float(data['Close'].iloc[-1])
        return None
    except:
        return None

def get_portfolio(db: Session) -> Dict:
    """計算當前持倉"""
    transactions = db.query(Transaction).all()

    portfolio = {}
    for trans in transactions:
        symbol = trans.stock_symbol
        if symbol not in portfolio:
            portfolio[symbol] = {
                'name': trans.stock_name,
                'quantity': 0,
                'cost': 0,
                'fees': 0
            }

        if trans.transaction_type == "買入":
            portfolio[symbol]['quantity'] += trans.quantity
            portfolio[symbol]['cost'] += trans.quantity * trans.price
            portfolio[symbol]['fees'] += trans.fee
        else:  # 賣出
            portfolio[symbol]['quantity'] -= trans.quantity
            portfolio[symbol]['cost'] -= trans.quantity * trans.price
            portfolio[symbol]['fees'] += trans.fee

    # 移除沒持倉的股票
    portfolio = {k: v for k, v in portfolio.items() if v['quantity'] > 0}

    # 加入市價和報酬
    for symbol, data in portfolio.items():
        current_price = get_stock_price(symbol)
        data['current_price'] = current_price or 0
        data['market_value'] = data['quantity'] * data['current_price']
        data['avg_cost'] = data['cost'] / data['quantity'] if data['quantity'] > 0 else 0
        data['profit_loss'] = data['market_value'] - data['cost'] - data['fees']
        data['return_rate'] = (data['profit_loss'] / (data['cost'] + data['fees']) * 100) if (data['cost'] + data['fees']) > 0 else 0

    return portfolio

def get_realized_profit(db: Session) -> Dict:
    """計算已實現損益"""
    transactions = db.query(Transaction).all()

    realized = {}

    for trans in transactions:
        if trans.transaction_type == "賣出":
            symbol = trans.stock_symbol
            if symbol not in realized:
                realized[symbol] = {'name': trans.stock_name, 'profit_loss': 0, 'count': 0}

            # 簡化計算：找到對應的買入價格
            buy_trans = [t for t in transactions
                        if t.stock_symbol == symbol
                        and t.transaction_type == "買入"
                        and t.date < trans.date]

            if buy_trans:
                avg_buy_price = sum(t.price * t.quantity for t in buy_trans) / sum(t.quantity for t in buy_trans)
                profit = (trans.price - avg_buy_price) * trans.quantity - trans.fee
                realized[symbol]['profit_loss'] += profit
                realized[symbol]['count'] += 1

    return realized

def add_transaction(db: Session, symbol: str, name: str, trans_type: str,
                   quantity: int, price: float, fee: float = 0, date: datetime = None):
    """新增交易"""
    if date is None:
        date = datetime.now()

    transaction = Transaction(
        stock_symbol=symbol,
        stock_name=name,
        transaction_type=trans_type,
        quantity=quantity,
        price=price,
        fee=fee,
        date=date
    )
    db.add(transaction)
    db.commit()
    return transaction

def add_dividend(db: Session, symbol: str, name: str, div_type: str,
                amount: float, date: datetime = None):
    """新增股利"""
    if date is None:
        date = datetime.now()

    dividend = Dividend(
        stock_symbol=symbol,
        stock_name=name,
        dividend_type=div_type,
        amount=amount,
        date=date
    )
    db.add(dividend)
    db.commit()
    return dividend

def get_all_transactions(db: Session) -> List[Transaction]:
    """取得所有交易記錄"""
    return db.query(Transaction).order_by(Transaction.date.desc()).all()

def delete_transaction(db: Session, trans_id: int):
    """刪除交易"""
    trans = db.query(Transaction).filter(Transaction.id == trans_id).first()
    if trans:
        db.delete(trans)
        db.commit()
        return True
    return False
