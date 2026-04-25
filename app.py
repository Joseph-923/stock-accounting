import streamlit as st
from database import SessionLocal, init_db
from stock_service import (
    get_portfolio, get_realized_profit, add_transaction,
    add_dividend, get_all_transactions, delete_transaction
)
from datetime import datetime

st.set_page_config(page_title="股票記帳", layout="wide")

# 初始化資料庫
init_db()

st.title("📈 股票記帳系統")

# 側邊欄導航
page = st.sidebar.selectbox(
    "選擇功能",
    ["📊 儀表板", "➕ 新增交易", "💰 股利記錄", "📝 交易記錄", "📉 已實現損益"]
)

db = SessionLocal()

if page == "📊 儀表板":
    st.header("投資組合總覽")

    portfolio = get_portfolio(db)

    if not portfolio:
        st.info("目前沒有持倉，請先新增交易。")
    else:
        # 計算總統計
        total_cost = sum(data['cost'] + data['fees'] for data in portfolio.values())
        total_market_value = sum(data['market_value'] for data in portfolio.values())
        total_profit_loss = total_market_value - total_cost

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("總成本", f"${total_cost:,.0f}")
        with col2:
            st.metric("目前市值", f"${total_market_value:,.0f}")
        with col3:
            st.metric("未實現損益", f"${total_profit_loss:,.0f}")
        with col4:
            ret_rate = (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
            st.metric("報酬率", f"{ret_rate:.2f}%")

        st.subheader("持倉明細")

        for symbol, data in portfolio.items():
            with st.expander(f"{symbol} - {data['name']} | 股數: {data['quantity']} | 報酬: {data['return_rate']:.2f}%"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("平均成本", f"${data['avg_cost']:.2f}")
                with col2:
                    st.metric("目前價格", f"${data['current_price']:.2f}")
                with col3:
                    st.metric("市值", f"${data['market_value']:,.0f}")
                with col4:
                    st.metric("損益", f"${data['profit_loss']:,.0f}")

elif page == "➕ 新增交易":
    st.header("新增股票交易")

    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("股票代號 (例: 2330)", "").upper()
        name = st.text_input("股票名稱 (例: 台積電)")
    with col2:
        trans_type = st.selectbox("交易類型", ["買入", "賣出"])
        quantity = st.number_input("股數", min_value=1, step=1)

    col1, col2 = st.columns(2)
    with col1:
        price = st.number_input("成交價", min_value=0.0, step=0.01)
        fee = st.number_input("手續費", min_value=0.0, step=1.0)
    with col2:
        trans_date = st.date_input("交易日期", datetime.now())

    if st.button("✅ 新增交易", use_container_width=True):
        if symbol and name:
            add_transaction(
                db, symbol, name, trans_type,
                quantity, price, fee, datetime.combine(trans_date, datetime.min.time())
            )
            st.success(f"已新增 {name} ({symbol}) 的 {trans_type} 交易！")
            st.rerun()
        else:
            st.error("請輸入股票代號和名稱")

elif page == "💰 股利記錄":
    st.header("股利記錄")

    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("股票代號", "").upper()
        name = st.text_input("股票名稱")
    with col2:
        div_type = st.selectbox("股利類型", ["現金股利", "股票股利"])
        amount = st.number_input("股利金額", min_value=0.0, step=0.01)

    div_date = st.date_input("除息日", datetime.now())

    if st.button("✅ 新增股利", use_container_width=True):
        if symbol and name:
            add_dividend(db, symbol, name, div_type, amount, datetime.combine(div_date, datetime.min.time()))
            st.success(f"已新增 {name} ({symbol}) 的股利！")
            st.rerun()
        else:
            st.error("請輸入股票代號和名稱")

elif page == "📝 交易記錄":
    st.header("所有交易記錄")

    transactions = get_all_transactions(db)

    if not transactions:
        st.info("目前沒有交易記錄")
    else:
        for trans in transactions:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"{trans.stock_symbol} - {trans.stock_name}")
            with col2:
                st.write(f"{trans.transaction_type}")
            with col3:
                st.write(f"{trans.quantity} 股 @ ${trans.price}")
            with col4:
                if st.button(f"刪除", key=f"del_{trans.id}"):
                    delete_transaction(db, trans.id)
                    st.rerun()

            st.caption(f"日期: {trans.date.strftime('%Y-%m-%d')} | 手續費: ${trans.fee}")
            st.divider()

elif page == "📉 已實現損益":
    st.header("已實現損益")

    realized = get_realized_profit(db)

    if not realized:
        st.info("目前沒有已實現損益")
    else:
        total_realized = sum(data['profit_loss'] for data in realized.values())

        st.metric("總已實現損益", f"${total_realized:,.0f}")
        st.divider()

        for symbol, data in realized.items():
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"{symbol} - {data['name']}")
            with col2:
                st.metric("損益", f"${data['profit_loss']:,.0f}")

db.close()
