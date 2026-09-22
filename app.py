import streamlit as st
import os, tempfile
import yfinance as yf
yf.set_tz_cache_location(os.path.join(tempfile.gettempdir(), "yf_tz_cache"))
import pandas as pd
import feedparser
from datetime import datetime, timedelta
import pytz
import time
import plotly.express as px
from streamlit_plotly_events import plotly_events
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

st.set_page_config(page_title="TradingPro FINAL", layout="wide", initial_sidebar_state="expanded")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
<style>
.stApp { background-color: #0e121b; color: #e6e8ec; }
[data-testid="stSidebar"] { background-color: #080c14; border-right: 1px solid #1e2a3e; }
[data-testid="stSidebar"] * { color: #e6e8ec!important; font-size: 17px!important; font-weight: 700!important; }
.stButton>button { background: linear-gradient(90deg, #00d084, #00b371); color: white; border: 0; border-radius: 10px; font-weight: 800; height: 48px; }
.green-box { background: #0e2318; border: 1px solid #00d084; border-radius: 14px; padding: 16px; text-align:center; font-weight:800; font-size:18px; }
.red-box { background: #231010; border: 1px solid #ff4d4d; border-radius: 14px; padding: 16px; text-align:center; font-weight:800; font-size:18px; }
</style>
""", unsafe_allow_html=True)

def draw_half_chart(symbol, pct_info=""):
    try:
        today_ist = datetime.now(IST).date()
        df = pd.DataFrame()
        try:
            df_1m = yf.Ticker(f"{symbol}.NS").history(period="1d", interval="1m", auto_adjust=True)
            if not df_1m.empty:
                if df_1m.index.tz is not None:
                    df_1m.index = df_1m.index.tz_convert(IST)
                else:
                    df_1m.index = df_1m.index.tz_localize('UTC').tz_convert(IST)
                df_1m = df_1m[df_1m.index.date == today_ist]
                if len(df_1m) > 3:
                    df = df_1m.resample('5min').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
        except: pass
        if df.empty or len(df) < 3:
            try:
                df_5 = yf.Ticker(f"{symbol}.NS").history(period="1d", interval="5m", auto_adjust=True)
                if not df_5.empty:
                    if df_5.index.tz is not None:
                        df_5.index = df_5.index.tz_convert(IST)
                    df_5 = df_5[df_5.index.date == today_ist]
                    if len(df_5) >= 2:
                        df = df_5
            except: pass
        if df.empty:
            st.caption(f"{symbol} - Market khula nahi")
            return
        df = df.tail(80)
        fig, ax = plt.subplots(figsize=(11, 5.5), facecolor='#0e121b')
        ax.set_facecolor('#0e121b')
        FIXED_CANDLE_WIDTH = 0.002
        for i in range(len(df)):
            o,h,l,c = float(df['Open'].iloc[i]), float(df['High'].iloc[i]), float(df['Low'].iloc[i]), float(df['Close'].iloc[i])
            x = mdates.date2num(df.index[i].to_pydatetime())
            col = '#00d084' if c >= o else '#ff4d4d'
            ax.plot([x,x],[l,h], color=col, linewidth=1.8)
            bh = abs(c-o)
            if bh < (h-l)*0.08: bh = (h-l)*0.08
            if bh == 0: bh = (h-l)*0.1 if h!=l else 0.1
            rect = Rectangle((x-FIXED_CANDLE_WIDTH/2, min(o,c)), FIXED_CANDLE_WIDTH, bh, facecolor=col, edgecolor=col, linewidth=0)
            ax.add_patch(rect)
        market_start = IST.localize(datetime.combine(today_ist, datetime.min.time().replace(hour=9, minute=15)))
        market_end = IST.localize(datetime.combine(today_ist, datetime.min.time().replace(hour=15, minute=30)))
        ax.set_xlim(mdates.date2num(market_start), mdates.date2num(market_end))
        ax.set_title(f"{symbol} {pct_info} - TODAY 5MIN", color='#00d084', fontsize=14, fontweight='bold', pad=10)
        ax.tick_params(colors='#aaa', labelsize=9)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=IST))
        for spine in ax.spines.values(): spine.set_color('#1e2a3e')
        ax.grid(True, color='#1e2a3e', alpha=0.3)
        plt.xticks(rotation=30)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    except Exception as e:
        st.error(f"{symbol}: {e}")

FNO = ["360ONE","ABB","APLAPOLLO","AUBANK","ADANIENSOL","ADANIENT","ADANIGREEN","ADANIPORTS","ADANIPOWER","ABCAPITAL","ALKEM","AMBER","AMBUJACEM","ANGELONE","APOLLOHOSP","ASHOKLEY","ASIANPAINT","ASTRAL","ATHERENERG","AUROPHARMA","DMART","AXISBANK","BSE","BAJAJ-AUTO","BAJFINANCE","BAJAJFINSV","BAJAJHLDNG","BANDHANBNK","BANKBARODA","BANKINDIA","MAHABANK","BDL","BEL","BHARATFORG","BHEL","BPCL","BHARTIARTL","BIOCON","BLUESTARCO","BOSCHLTD","BRITANNIA","CGPOWER","CANBK","CDSL","CHOLAFIN","CIPLA","COALINDIA","COCHINSHIP","COFORGE","COLPAL","CAMS","CONCOR","CROMPTON","CUMMINSIND","DLF","DABUR","DELHIVERY","DIVISLAB","DIXON","DRREDDY","ETERNAL","EICHERMOT","FORCEMOT","NYKAA","FORTIS","GAIL","GVT&D","GMRAIRPORT","GLENMARK","GODFRYPHLP","GODREJCP","GODREJPROP","GRASIM","HCLTECH","HDFCAMC","HDFCBANK","HDFCLIFE","HAVELLS","HEROMOTOCO","HINDALCO","HAL","HINDPETRO","HINDUNILVR","HINDZINC","POWERINDIA","HYUNDAI","ICICIBANK","ICICIGI","ICICIPRULI","IDFCFIRSTB","ITC","INDIANB","IEX","IOC","IRFC","IREDA","INDUSTOWER","INDUSINDBK","NAUKRI","INFY","INOXWIND","INDIGO","JINDALSTEL","JSWENERGY","JSWSTEEL","JIOFIN","JUBLFOOD","KEI","KPITTECH","KALYANKJIL","KAYNES","KFINTECH","KOTAKBANK","L
