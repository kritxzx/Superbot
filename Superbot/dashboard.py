# dashboard.py
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import MetaTrader5 as mt5
import time
import json
import os
from datetime import datetime, timedelta

# Import Modules
import config
import data_manager

# ==========================================
# 1. การเชื่อมต่อและการดึงข้อมูล
# ==========================================
def stable_connect():
    target_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    if not mt5.initialize(path=target_path):
        mt5.initialize()
    return mt5.account_info()

def load_bot_status():
    if os.path.exists("bot_status.json"):
        try:
            with open("bot_status.json", "r") as f:
                return json.load(f)
        except:
            return None
    return None

def get_perf_stats():
    try:
        from_date = datetime.now() - timedelta(days=365)
        to_date = datetime.now() + timedelta(days=1)
        deals = mt5.history_deals_get(from_date, to_date)
    except:
        return {"count": 0, "net_profit": 0.0, "win_rate": 0.0, "wins": 0, "losses": 0}, pd.DataFrame()
    
    stats = {"count": 0, "net_profit": 0.0, "win_rate": 0.0, "wins": 0, "losses": 0}
    df_clean = pd.DataFrame()

    if deals is not None and len(deals) > 0:
        df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
        if not df.empty and 'profit' in df.columns:
            df_closed = df[(df['entry'].isin([1, 2])) & (df['type'] <= 1)].copy()
            if not df_closed.empty:
                df_closed['net_profit'] = df_closed['profit'] + df_closed.get('swap', 0) + df_closed.get('commission', 0)
                stats["count"] = len(df_closed)
                stats["net_profit"] = df_closed['net_profit'].sum()
                stats["wins"] = len(df_closed[df_closed['net_profit'] > 0])
                stats["losses"] = len(df_closed[df_closed['net_profit'] <= 0])
                stats["win_rate"] = (stats["wins"] / stats["count"] * 100) if stats["count"] > 0 else 0
                df_closed['time'] = pd.to_datetime(df_closed['time'], unit='s')
                df_closed['type_str'] = df_closed['type'].apply(lambda x: 'BUY' if x==0 else 'SELL')
                df_clean = df_closed[['time', 'symbol', 'type_str', 'volume', 'net_profit']].sort_values('time', ascending=False)
    return stats, df_clean

# ==========================================
# 2. ตั้งค่าหน้าจอ UI
# ==========================================
st.set_page_config(page_title="SuperBot V2 War Room", layout="wide")
st.markdown("""
    <style>
    .stMetric { background-color: #11151c; border: 1px solid #313d4f; padding: 15px; border-radius: 10px; }
    div[data-testid="stExpander"] { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

account = stable_connect()
if not account:
    st.error("🚨 เชื่อมต่อ MT5 ไม่ได้ กรุณาเปิดโปรแกรม MT5 ค้างไว้")
    st.stop()

stats, df_hist = get_perf_stats()
positions = mt5.positions_get()
status = load_bot_status()

# --- Header ---
st.title("🤖 SuperBot V2.0 | Tactical Control")
st.caption(f"Account: {account.login} | Server: {account.server} | Last Update: {datetime.now().strftime('%H:%M:%S')}")

# --- Metrics Row ---
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 Balance", f"${account.balance:,.2f}")
c2.metric("📈 Equity", f"${account.equity:,.2f}", delta=f"{account.profit:,.2f}")
c3.metric("🏆 Win Rate", f"{stats['win_rate']:.1f}%", f"{stats['wins']}W - {stats['losses']}L")
c4.metric("💵 Total Profit", f"${stats['net_profit']:,.2f}")
c5.metric("📦 Closed Trades", stats['count'])

st.divider()

# --- Sidebar Control ---
st.sidebar.header("🛡️ Tactical Intelligence")
if status:
    mode_color = "#00FF00" if "HUNTER" in status['mode'] else "#00DBFF" if "GRID" in status['mode'] else "#FF4B4B"
    st.sidebar.markdown(f"### Current Mode:<br><span style='color:{mode_color}; font-size:24px;'>{status['mode'].replace('MODE_', '')}</span>", unsafe_allow_html=True)
    st.sidebar.metric("📊 Live Price", f"{status.get('price', 0):.2f}")
    
    st.sidebar.divider()
    st.sidebar.subheader("Regime Analysis")
    # ER คือความแข็งแกร่งเทรนด์
    st.sidebar.progress(min(max(status.get('corr', 0), 0.0), 1.0), text=f"Trend Strength (ER): {status.get('corr', 0):.2f}")
    # Vol Z-Score
    vol_z = status.get('vol', 0)
    st.sidebar.write(f"Volatility Z-Score: `{vol_z:.2f}`")
    if abs(vol_z) > 2.0:
        st.sidebar.warning("⚠️ High Volatility Detected!")

# --- Main Layout ---
col_L, col_R = st.columns([2, 1])

with col_L:
    st.subheader("🕯️ Market Context (M5)")
    df_m5 = data_manager.get_market_data(config.SYMBOL_MAIN, config.TIMEFRAME_MICRO)
    if df_m5 is not None:
        fig = go.Figure(data=[go.Candlestick(
            x=df_m5['time'], open=df_m5['open'], high=df_m5['high'], low=df_m5['low'], close=df_m5['close'],
            increasing_line_color='#00ff88', decreasing_line_color='#ff3366'
        )])
        fig.update_layout(height=500, margin=dict(t=0,b=0,l=0,r=0), template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

with col_R:
    st.subheader("📋 Running Positions")
    if positions:
        df_p = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
        df_p['type_str'] = df_p['type'].apply(lambda x: 'BUY' if x==0 else 'SELL')
        st.dataframe(df_p[['symbol', 'type_str', 'volume', 'profit']], hide_index=True, use_container_width=True)
    else:
        st.info("No active trades. Scanning for entry...")

    st.subheader("📜 Recent History")
    if not df_hist.empty:
        st.dataframe(df_hist.head(10), hide_index=True, use_container_width=True)
    else:
        st.write("History is empty.")

# --- Auto Refresh ---
time.sleep(5)
st.rerun()