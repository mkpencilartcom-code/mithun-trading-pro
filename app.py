import streamlit as st
import pandas as pd
import json, time, os, requests
from SmartApi import SmartConnect
import pyotp
from datetime import datetime
import pytz

st.set_page_config(page_title="Mithun Trading Pro", layout="wide")
st.title("Mithun Trading Pro - Angel One Live")

# --- 1. LOGIN ---
try:
    API_KEY = st.secrets["API_KEY"]
    CLIENT_ID = st.secrets["CLIENT_ID"]
    MPIN = st.secrets["MPIN"]
    TOTP_SECRET = st.secrets["TOTP_SECRET"]
except:
    st.error("Pehle Streamlit Cloud > Settings > Secrets me API_KEY, CLIENT_ID, MPIN, TOTP_SECRET dalo")
    st.stop()

@st.cache_resource
def get_connection():
    obj = SmartConnect(api_key=API_KEY)
    totp = pyotp.TOTP(TOTP_SECRET).now()
    data = obj.generateSession(CLIENT_ID, MPIN, totp)
    return obj

try:
    obj = get_connection()
    st.success("Angel One se connected!")
except Exception as e:
    st.error(f"Login fail: {e}")
    st.stop()

# --- 2. TOKEN MAP ---
TOKEN_FILE = "token_map.json"

st.header("Step 1: Token Map")
if st.button("1. Pehli baar Token Map Download karo"):
    with st.spinner("Download ho raha hai..."):
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        data = requests.get(url).json()
        token_map = {}
        for item in data:
            if item.get("exch_seg") == "NSE" and item.get("instrumenttype") in ["OPTSTK", "OPTIDX"]:
                key = f"{item['name']}_{item['expiry']}_{item['strike']}_{item['symbol'].split()[-1]}"
                token_map[key] = item["token"]
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_map, f)
        st.success(f"{len(token_map)} tokens mil gaye!")

# --- 3. LIVE SCAN ---
st.header("Step 2: Live Scan")

def get_ltp_batch(tokens):
    try:
        # Angel ka naya LTP API
        params = {
            "exchange": "NSE",
            "tradingsymbol": "",
            "symboltoken": ""
        }
        # Hum simple searchScrip use karenge
        result = []
        for exch, token in tokens[:50]: # pehle 50 ek saath
            try:
                ltp_data = obj.ltpData(exch, "NIFTY", token)
                if ltp_data and "data" in ltp_data:
                    d = ltp_data["data"]
                    result.append({
                        "TOKEN": token,
                        "LTP": float(d.get("ltp", 0)),
                        "CLOSE": float(d.get("close", d.get("ltp", 0))),
                        "VOLUME": int(d.get("volume", 0))
                    })
            except:
                continue
        return pd.DataFrame(result)
    except Exception as e:
        st.error(f"LTP error: {e}")
        return pd.DataFrame()

if st.button("2. SCAN NOW - Live"):
    if not os.path.exists(TOKEN_FILE):
        st.warning("Pehle Step 1 wala button dabao")
    else:
        with open(TOKEN_FILE) as f:
            token_map = json.load(f)

        # Sample ke liye pehle 20 token lo, baad me poora laga dena
        sample_tokens = list(token_map.items())[:20]
        tokens_for_api = [("NFO", token) for name, token in sample_tokens]

        df = get_ltp_batch(tokens_for_api)

        if df.empty:
            st.warning("Koi data nahi aaya. Market band ho sakta hai.")
        else:
            # YEHI WO FIX HAI
            if "CLOSE" in df.columns and "LTP" in df.columns:
                df["CLOSE"] = pd.to_numeric(df["CLOSE"], errors='coerce').fillna(df["LTP"])
                df["CHANGE"] = (df["LTP"] - df["CLOSE"]) / df["CLOSE"] * 100
            else:
                df["CHANGE"] = 0.0

            df = df.sort_values("CHANGE", ascending=False)
            st.dataframe(df, use_container_width=True)
            st.success("Scan poora hua!")
