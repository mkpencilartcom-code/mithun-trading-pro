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

ANGEL_API_KEY = "5yhJRvRM"
ANGEL_CLIENT_ID = "M980287"
ANGEL_MPIN = "2580"
ANGEL_TOTP_SECRET = "AVEMT5XQYCGPXSFAPYQMVP5K2A"
try:
    from SmartApi import SmartConnect
    import pyotp
    HAS_ANGEL = True
except:
    HAS_ANGEL = False

def angel_login():
    if not HAS_ANGEL:
        return None
    try:
        smart = SmartConnect(ANGEL_API_KEY)
        totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        smart.generateSession(ANGEL_CLIENT_ID, ANGEL_MPIN, totp)
        return smart
    except:
        return None

@st.cache_data(ttl=86400)
def get_angel_tokens():
    try:
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        data = requests.get(url, timeout=30).json()
        m = {}
        for d in data:
            if d.get('exch_seg') == 'NSE' and d.get('symbol','').endswith('-EQ'):
                name = d['symbol'].replace('-EQ','')
                m[name.replace('-','')] = d['token']
                m[name] = d['token']
        return m
    except:
        return {}

st.set_page_config(page_title="TradingPro Angel Live", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

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

FNO = [
"360ONE","ABB","APLAPOLLO","AUBANK","ADANIENSOL","ADANIENT",
"ADANIGREEN","ADANIPORTS","ADANIPOWER","ABCAPITAL","ALKEM","AMBER",
"AMBUJACEM","ANGELONE","APOLLOHOSP","ASHOKLEY","ASIANPAINT","ASTRAL",
"ATHERENERG","AUROPHARMA","DMART","AXISBANK","BSE","BAJAJ-AUTO",
"BAJFINANCE","BAJAJFINSV","BAJAJHLDNG","BANDHANBNK","BANKBARODA",
"BANKINDIA","MAHABANK","BDL","BEL","BHARATFORG","BHEL","BPCL",
"BHARTIARTL","BIOCON","BLUESTARCO","BOSCHLTD","BRITANNIA","CGPOWER",
"CANBK","CDSL","CHOLAFIN","CIPLA","COALINDIA","COCHINSHIP","COFORGE",
"COLPAL","CAMS","CONCOR","CROMPTON","CUMMINSIND","DLF","DABUR",
"DELHIVERY","DIVISLAB","DIXON","DRREDDY","ETERNAL","EICHERMOT",
"FORCEMOT","NYKAA","FORTIS","GAIL","GVT&D","GMRAIRPORT","GLENMARK",
"GODFRYPHLP","GODREJCP","GODREJPROP","GRASIM","HCLTECH","HDFCAMC",
"HDFCBANK","HDFCLIFE","HAVELLS","HEROMOTOCO","HINDALCO","HAL",
"HINDPETRO","HINDUNILVR","HINDZINC","POWERINDIA","HYUNDAI","ICICIBANK",
"ICICIGI","ICICIPRULI","IDFCFIRSTB","ITC","INDIANB","IEX","IOC",
"IRFC","IREDA","INDUSTOWER","INDUSINDBK","NAUKRI","INFY","INOXWIND",
"INDIGO","JINDALSTEL","JSWENERGY","JSWSTEEL","JIOFIN","JUBLFOOD",
"KEI","KPITTECH","KALYANKJIL","KAYNES","KFINTECH","KOTAKBANK","LTF",
"LICHSGFIN","LTM","LT","LAURUSLABS","LICI","LODHA","LUPIN","M&M",
"MANAPPURAM","MANKIND","MARICO","MARUTI","MFSL","MAXHEALTH","MAZDOCK",
"MOTILALOFS","MPHASIS","MCX","MUTHOOTFIN","NBCC","NHPC","NMDC",
"NTPC","NATIONALUM","NESTLEIND","NAM-INDIA","OBEROIRLTY","ONGC","OIL",
"PAYTM","OFSS","POLICYBZR","PGEL","PIIND","PNBHOUSING","PAGEIND",
"PATANJALI","PERSISTENT","PETRONET","PIDILITIND","POLYCAB","PFC",
"POWERGRID","PREMIERENE","PRESTIGE","PNB","RBLBANK","RECLTD","RADICO",
"RVNL","RELIANCE","SAGILITY","SBICARD","SBILIFE","SHREECEM","SRF",
"MOTHERSON","SHRIRAMFIN","SIEMENS","SOLARINDS","SONACOMS","SBIN",
"SAIL","SUNPHARMA","SUPREMEIND","SUZLON","SWIGGY","TATACONSUM",
"TVSMOTOR","TCS","TATAELXSI","TMPV","TATAPOWER","TATASTEEL","TECHM",
"FEDERALBNK","INDHOTEL","PHOENIXLTD","TITAN","TORNTPHARM","TRENT",
"TIINDIA","UNOMINDA","UPL","ULTRACEMCO","UNIONBANK","UNITDSPR","VBL",
"VEDL","VMM","IDEA","VOLTAS","WAAREEENER","WIPRO","YESBANK","ZYDUSLIFE"
]

SECTOR_MAP_FULL = {
"BRITANNIA":"FMCG","GODREJCP":"FMCG","NESTLEIND":"FMCG","DABUR":"FMCG",
"HINDUNILVR":"FMCG","PATANJALI":"FMCG","COLPAL":"FMCG","MARICO":"FMCG",
"LT":"Cement and Construction","ULTRACEMCO":"Cement and Construction",
"GRASIM":"Cement and Construction","HDFCBANK":"Banking and Finance",
"ICICIBANK":"Banking and Finance","SBIN":"Banking and Finance",
"AXISBANK":"Banking and Finance","KOTAKBANK":"Banking and Finance",
"RELIANCE":"Oil & Gas","ONGC":"Oil & Gas","BPCL":"Oil & Gas","IOC":"Oil & Gas",
"INFY":"Software & Services","TCS":"Software & Services","HCLTECH":"Software & Services",
"WIPRO":"Software & Services","TECHM":"Software & Services",
"MARUTI":"Automobiles & Auto Components","M&M":"Automobiles & Auto Components",
"TATAPOWER":"Utilities","POWERGRID":"Utilities","NTPC":"Utilities",
"SUNPHARMA":"Pharmaceuticals & Biotechnology","CIPLA":"Pharmaceuticals & Biotechnology",
"DRREDDY":"Pharmaceuticals & Biotechnology","TATASTEEL":"Metals & Mining",
"JSWSTEEL":"Metals & Mining","HINDALCO":"Metals & Mining"
}

RSS_FEEDS = {
"INDIA MARKET":{
"MoneyControl Top":"https://www.moneycontrol.com/rss/MCtopnews.xml",
"ET Markets":"https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
},
"GLOBAL MARKET":{
"Reuters Business":"http://feeds.reuters.com/reuters/businessNews",
"CNBC Top":"https://www.cnbc.com/id/100003114/device/rss/rss.html"
}
}

def scan_fno():
    up, down = [], []
    use_angel = st.session_state.get('use_angel_live', False)
    bar = st.progress(0, text="Scanning FNO BODY...")
    for i, sym in enumerate(FNO):
        try:
            d = yf.Ticker(f"{sym}.NS").history(period="5d", auto_adjust=True)
            if d.empty:
                continue
            o = float(d['Open'].iloc[-1])
            c = float(d['Close'].iloc[-1])
            bl = min(o, c)
            bh = max(o, c)
            if bl == 0:
                continue
            lu = (c - bl) / bl * 100
            hd = (bh - c) / bh * 100
            if lu >= 1:
                up.append({"SYM":sym,"OPEN":round(o,2),"BODY_LOW":round(bl,2),"LTP":round(c,2),"LOW_UP %":round(lu,2),"LIVE":"Angel" if use_angel else "YF"})
            if hd >= 1:
                down.append({"SYM":sym,"OPEN":round(o,2),"BODY_HIGH":round(bh,2),"LTP":round(c,2),"HIGH_DOWN %":round(hd,2),"LIVE":"Angel" if use_angel else "YF"})
        except:
            pass
        bar.progress((i+1)/len(FNO))
    bar.empty()
    return pd.DataFrame(up), pd.DataFrame(down)

@st.cache_data(ttl=90)
def fetch_news():
    all_news = {}
    for cat, feeds in RSS_FEEDS.items():
        lst = []
        for src, url in feeds.items():
            try:
                f = feedparser.parse(url)
                for e in f.entries[:4]:
                    dt = datetime(*e.published_parsed[:6]) if hasattr(e,'published_parsed') and e.published_parsed else datetime.now()
                    lst.append({"TIME":dt.strftime("%H:%M"),"SRC":src,"TITLE":e.title,"LINK":e.link,"DT":dt})
            except:
                continue
        all_news[cat] = sorted(lst, key=lambda x:x['DT'], reverse=True)
    return all_news

with st.sidebar:
    st.markdown("## TradingPro Angel Live")
    st.checkbox("Angel One Live use karo (pehle wale me bhi)", key="use_angel_live")
    menu = st.radio("Navigation",["FNO Scanner - 1%","FNO Live - Angel One","Cash Live - Angel One","Sector Heatmap - SAME DESIGN","NEWS - 87 Sources"],label_visibility="collapsed")
    st.caption(datetime.now(IST).strftime('%d %b %Y %I:%M %p') + " IST")

if menu == "FNO Scanner - 1%":
    st.title("FNO BODY - LOW/HIGH 1% + Angel Live")
    if st.session_state.get('use_angel_live'):
        st.success("Angel Live ON")
    if st.button("SCAN NOW", type="primary", use_container_width=True):
        df_u, df_d = scan_fno()
        st.session_state['df_u'] = df_u
        st.session_state['df_d'] = df_d
    if 'df_u' in st.session_state:
        df_u = st.session_state['df_u']
        df_d = st.session_state['df_d']
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"### BODY LOW se UP: {len(df_u)}")
            st.dataframe(df_u, use_container_width=True)
        with c2:
            st.markdown(f"### BODY HIGH se DOWN: {len(df_d)}")
            st.dataframe(df_d, use_container_width=True)

elif menu == "FNO Live - Angel One":
    st.title("FNO LIVE - Angel One")
    if st.button("LOAD FNO LIVE", type="primary", key="fno_live_btn"):
        smart = angel_login()
        token_map = get_angel_tokens()
        if smart:
            st.success("Angel Connected")
        else:
            st.warning("Angel login fail, YF live se dikha raha")
        rows = []
        bar = st.progress(0, text="Loading FNO Live...")
        for i, sym in enumerate(FNO):
            try:
                ltp = None
                if smart and token_map:
                    tk = token_map.get(sym.replace('-','')) or token_map.get(sym)
                    if tk:
                        try:
                            r = smart.ltpData("NSE", sym+"-EQ", tk)
                            ltp = float(r['data']['ltp'])
                        except:
                            pass
                fi = yf.Ticker(f"{sym}.NS").fast_info
                if ltp is None:
                    ltp = float(fi['last_price'])
                prev = float(fi['previous_close'])
                ch = (ltp-prev)/prev*100 if prev else 0
                rows.append({"SYM":sym,"LTP":round(ltp,2),"CHANGE %":round(ch,2),"PREV":round(prev,2)})
            except:
                pass
            if i % 10 == 0:
                bar.progress((i+1)/len(FNO))
        bar.empty()
        if rows:
            st.dataframe(pd.DataFrame(rows).sort_values("CHANGE %", ascending=False), use_container_width=True)
            st.success(f"{len(rows)} stocks loaded")
        else:
            st.error("Data nahi aaya")

elif menu == "Cash Live - Angel One":
    st.title("CASH LIVE - Angel One")
    if st.button("LOAD CASH LIVE", type="primary", key="cash_live_btn"):
        smart = angel_login()
        token_map = get_angel_tokens()
        if smart:
            st.success("Angel Connected - Cash")
        else:
            st.warning("Angel fail, YF live")
        rows = []
        bar = st.progress(0, text="Loading Cash Live...")
        for i, sym in enumerate(FNO):
            try:
                ltp = None
                if smart and token_map:
                    tk = token_map.get(sym.replace('-','')) or token_map.get(sym)
                    if tk:
                        try:
                            r = smart.ltpData("NSE", sym+"-EQ", tk)
                            ltp = float(r['data']['ltp'])
                        except:
                            pass
                fi = yf.Ticker(f"{sym}.NS").fast_info
                if ltp is None:
                    ltp = float(fi['last_price'])
                o = float(fi['open'])
                h = float(fi['day_high'])
                l = float(fi['day_low'])
                prev = float(fi['previous_close'])
                ch = (ltp-prev)/prev*100 if prev else 0
                rows.append({"SYM":sym,"LTP":round(ltp,2),"OPEN":round(o,2),"HIGH":round(h,2),"LOW":round(l,2),"CHANGE %":round(ch,2),"SEGMENT":"CASH"})
            except:
                pass
            if i % 10 == 0:
                bar.progress((i+1)/len(FNO))
        bar.empty()
        if rows:
            st.dataframe(pd.DataFrame(rows).sort_values("CHANGE %", ascending=False), use_container_width=True)
            st.success(f"{len(rows)} cash stocks loaded")
        else:
            st.error("Data nahi aaya")

elif menu == "Sector Heatmap - SAME DESIGN":
    st.markdown("### NSE INDIA - STOCK MARKET HEATMAP")
    if st.button("GENERATE SAME DESIGN", type="primary", use_container_width=True):
        heat_data = []
        bar = st.progress(0)
        for i, sym in enumerate(FNO):
            try:
                fi = yf.Ticker(f"{sym}.NS").fast_info
                c = float(fi['last_price'])
                prev = float(fi['previous_close'])
                if prev == 0:
                    continue
                ch = (c-prev)/prev*100
                heat_data.append({"SYM":sym,"SECTOR":SECTOR_MAP_FULL.get(sym,"Others"),"CHANGE":round(ch,2),"LTP":round(c,2)})
            except:
                continue
            bar.progress((i+1)/len(FNO))
        bar.empty()
        st.session_state['df_h'] = pd.DataFrame(heat_data)
    if 'df_h' in st.session_state and not st.session_state['df_h'].empty:
        df_h = st.session_state['df_h']
        for sec in sorted(df_h['SECTOR'].unique()):
            sec_df = df_h[df_h['SECTOR']==sec].sort_values('CHANGE', ascending=False)
            st.markdown(f"<div class='sector-header'>{sec} - {len(sec_df)} Stocks</div>", unsafe_allow_html=True)
            cols = st.columns(5)
            for idx, (_, row) in enumerate(sec_df.iterrows()):
                bg = '#00CB53' if row['CHANGE'] >= 0 else '#D50000'
                with cols[idx % 5]:
                    st.markdown(f"<div class='sector-box' style='background:{bg}'>{row['SYM']}<br>{row['CHANGE']}%<br>Rs.{row['LTP']:,.0f}</div>", unsafe_allow_html=True)

elif menu == "NEWS - 87 Sources":
    st.title("LIVE NEWS")
    news_data = fetch_news()
    c1, c2 = st.columns(2)
    cols = [c1, c2]
    idx = 0
    for cat, lst in news_data.items():
        with cols[idx % 2]:
            html = f"<div class='news-wrapper'><div class='news-header'>{cat}</div>"
            for n in lst[:10]:
                html += f"<div class='news-card-black'><b>{n['TIME']} | {n['SRC']}</b><br>{n['TITLE']}<br><a href='{n['LINK']}' target='_blank'>Read More</a></div>"
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
        idx += 1
