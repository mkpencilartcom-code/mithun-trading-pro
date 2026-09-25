import streamlit as st
import os, tempfile, json, math, requests
import yfinance as yf
yf.set_tz_cache_location(os.path.join(tempfile.gettempdir(), "yf_tz_cache"))
import pandas as pd
import feedparser
from datetime import datetime, date
import pytz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

# ===== ANGEL KEYS =====
ANGEL_API_KEY = "5yhJRvRM"
ANGEL_CLIENT_ID = "M980287"
ANGEL_MPIN = "2580"
ANGEL_TOTP_SECRET = "AVEMT5XQYCGPXSFAPYQMVP5K2A"
try:
    from SmartApi import SmartConnect
    import pyotp
    HAS_ANGEL=True
except:
    HAS_ANGEL=False

def angel_login():
    if not HAS_ANGEL:
        return None
    try:
        smart=SmartConnect(ANGEL_API_KEY)
        totp=pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        smart.generateSession(ANGEL_CLIENT_ID, ANGEL_MPIN, totp)
        return smart
    except Exception as e:
        return None

@st.cache_data(ttl=86400)
def get_angel_tokens():
    try:
        url="https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        data=requests.get(url, timeout=30).json()
        m={}
        for d in data:
            if d.get('exch_seg')=='NSE' and d.get('symbol','').endswith('-EQ'):
                name=d['symbol'].replace('-EQ','')
                m[name.replace('-','')]=d['token']
                m[name]=d['token']
        return m
    except:
        return {}

st.set_page_config(page_title="TradingPro Angel Live", layout="wide")
IST=pytz.timezone('Asia/Kolkata')

st.markdown("""<style>
.stApp{background:#0e121b;color:#e6e8ec}
[data-testid="stSidebar"]{background:#080c14}
[data-testid="stSidebar"] *{color:#e6e8ec!important;font-size:17px!important;font-weight:700!important}
.stButton>button{background:linear-gradient(90deg,#00d084,#00b371);color:white;border:0;border-radius:10px;font-weight:800;height:48px}
.news-wrapper{height:600px;overflow-y:auto;border:1px solid #1e2a3e;border-radius:12px;background:#0e121b}
.news-header{position:sticky;top:0;background:#151a26;padding:10px;border-bottom:2px solid #00d084;z-index:10;font-weight:800;color:#00d084}
.news-card-black{background:#151a26;color:#e6e8ec;padding:12px;border-radius:8px;margin:8px;border:1px solid #1e2a3e;border-left:4px solid #00d084}
.news-card-black a{color:#00d084;text-decoration:none;font-weight:700;font-size:13px}
.sector-box{padding:14px;border-radius:12px;margin:6px;text-align:center;font-weight:800;color:white;min-height:90px;display:flex;flex-direction:column;justify-content:center}
.sector-header{background:#151a26;padding:10px 14px;border-radius:10px;margin-top:18px;font-weight:800;border:1px solid #1e2a3e}
</style>""", unsafe_allow_html=True)

FNO=["360ONE","ABB","APLAPOLLO","AUBANK","ADANIENSOL","ADANIENT","ADANIGREEN","ADANIPORTS","ADANIPOWER","
