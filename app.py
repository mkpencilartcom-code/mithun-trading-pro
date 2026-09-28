import streamlit as st
import pandas as pd
import pyotp
from SmartApi import SmartConnect
from datetime import datetime, date
import pytz
import json
import requests

st.set_page_config(page_title="Alpha Discovery - Angel Live", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

# ---------- ANGEL CONNECTION ----------
@st.cache_resource
def get_angel():
    obj = SmartConnect(api_key=st.secrets["API_KEY"])
    totp = pyotp.TOTP(st.secrets["TOTP_SECRET"]).now()
    obj.generateSession(st.secrets["CLIENT_ID"], st.secrets["MPIN"], totp)
    return obj

# Tumhari FNO list
FNO = ["RELIANCE","HDFCBANK","INFY","TCS","SBIN","ICICIBANK","AXISBANK","ITC","LT","TATAMOTORS"]
# poori 200 wali list yaha paste kar lena tumhari purani wali

@st.cache_data(ttl=86400)
def build_token_map():
    # Angel master json
    url = "https://margincalculator.angelone.in/OpenAPI_File/files/OpenAPIScripMaster.json"
    data = requests.get(url).json()
    mp = {}
    for d in data:
        if d.get("exch_seg")=="NSE" and d.get("symbol") in FNO:
            # symbol like RELIANCE-EQ
            base = d["symbol"].replace("-EQ","")
            if base in FNO:
                mp[base] = d["token"]
    return mp

def get_live_data(symbols, token_map):
    obj = get_angel()
    out = []
    for sym in symbols:
        token = token_map.get(sym)
        if not token: continue
        try:
            q = obj.ltpData("NSE", sym, token)["data"]
            out.append({
                "SYM": sym,
                "LTP": float(q["ltp"]),
                "OPEN": float(q["open"]),
                "HIGH": float(q["high"]),
                "LOW": float(q["low"]),
                "CLOSE": float(q["close"])
            })
        except: continue
    return pd.DataFrame(out)

# ---------- UI ----------
st.title("Alpha Discovery - Angel One Live")

if st.button("1. Pehli baar Token Map Download karo"):
    tm = build_token_map()
    st.session_state["token_map"] = tm
    st.success(f"{len(tm)} tokens mil gaye!")

if "token_map" in st.session_state:
    tm = st.session_state["token_map"]
    if st.button("2. SCAN NOW - Live", type="primary"):
        df = get_live_data(FNO, tm)
        st.session_state["live_df"] = df

    if "live_df" in st.session_state:
        df = st.session_state["live_df"]
        # Tumhara 1% wala logic
        df["CHANGE"] = (df["LTP"]-df["CLOSE"])/df["CLOSE"]*100
        st.dataframe(df.sort_values("CHANGE", ascending=False), use_container_width=True)
else:
    st.info("Pehle Token Map download karo")
