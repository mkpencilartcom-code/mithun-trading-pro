import streamlit as st
import os, tempfile
import yfinance as yf
yf.set_tz_cache_location(os.path.join(tempfile.gettempdir(), "yf_tz_cache"))
import pandas as pd
import feedparser
from datetime import datetime
import pytz
import time
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64
import streamlit.components.v1 as components

st.set_page_config(page_title="TradingPro - FINAL", layout="wide", initial_sidebar_state="expanded")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
<style>
.stApp { background-color: #0e121b; color: #e6e8ec; }
[data-testid="stSidebar"] { background-color: #080c14; border-right: 1px solid #1e2a3e; }
[data-testid="stSidebar"] * { color: #e6e8ec!important; font-size: 17px!important; font-weight: 700!important; }
div[data-testid="stMetric"] { background: #131a28; border: 1px solid #1e2a3e; border-radius: 12px; padding: 12px; }
.stButton>button { background: linear-gradient(90deg, #00d084, #00b371); color: white; border: 0; border-radius: 10px; font-weight: 800; height: 45px; }
.green-box { background: #0e2318; border: 1px solid #00d084; border-radius: 14px; padding: 16px; text-align:center; font-weight:800; }
.red-box { background: #231010; border: 1px solid #ff4d4d; border-radius: 14px; padding: 16px; text-align:center; font-weight:800; }
h1, h2, h3 { color: white!important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=180)
def get_5m_base64(symbol):
    try:
        df = yf.Ticker(f"{symbol}.NS").history(period="1d", interval="5m", auto_adjust=True)
        if df.empty or len(df) < 10: return None
        df = df.tail(75)
        fig, ax = plt.subplots(figsize=(6, 3.2), facecolor='#0e121b')
        ax.set_facecolor('#0e121b')
        ax.plot(df.index, df['Close'], color='#00d084', linewidth=2.2)
        ax.fill_between(df.index, df['Close'], df['Close'].min(), alpha=0.15, color='#00d084')
        ax.set_title(f"{symbol} - 5 MIN LIVE", color='#00d084', fontsize=13, fontweight='bold')
        ax.tick_params(colors='#888', labelsize=8)
        for spine in ax.spines.values(): spine.set_color('#1e2a3e')
        ax.grid(True, color='#1e2a3e', alpha=0.4)
        plt.xticks(rotation=25)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=160, facecolor='#0e121b')
        plt.close(fig)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        return f"data:image/png;base64,{b64}"
    except: return None

def render_hover_table(df, sym_col="SYM"):
    if df.empty:
        st.warning("No data found")
        return
    cols = list(df.columns)
    header_html = "".join([f"<th style='padding:10px; text-align:left; border-bottom:2px solid #00d084; color:#00d084; font-size:12px;'>{c}</th>" for c in cols])
    rows_html = ""
    for _, row in df.iterrows():
        row_html = ""
        for c in cols:
            val = row[c]
            if c == sym_col:
                sym = str(val).replace(".NS","")
                img = get_5m_base64(sym)
                img_tag = f"<img src='{img}' style='width:100%; border-radius:12px;'>" if img else "<div style='color:white'>Loading...</div>"
                row_html += f"""<td style='padding:10px; border-bottom:1px solid #1e2a3e;'><span style='font-weight:900; color:white;'>📈 {sym}</span></td>"""
            else:
                row_html += f"<td style='padding:10px; border-bottom:1px solid #1e2a3e; color:#e6e8ec; font-size:13px;'>{val}</td>"
        rows_html += f"<tr style='background:#131a28;'>{row_html}</tr>"
    full_html = f"<html><body style='background:#0e121b; margin:0;'><table style='width:100%; border-collapse:collapse;'><tr>{header_html}</tr>{rows_html}</table></body></html>"
    h = 80 + len(df)*42
    h = min(h, 600)
    components.html(full_html, height=h, scrolling=True)

FNO = ["360ONE","ABB","APLAPOLLO","AUBANK","ADANIENSOL","ADANIENT","ADANIGREEN","ADANIPORTS","ADANIPOWER","ABCAPITAL","ALKEM","AMBER","AMBUJACEM","ANGELONE","APOLLOHOSP","ASHOKLEY","ASIANPAINT","ASTRAL","ATHERENERG","AUROPHARMA","DMART","AXISBANK","BSE","BAJAJ-AUTO","BAJFINANCE","BAJAJFINSV","BAJAJHLDNG","BANDHANBNK","BANKBARODA","BANKINDIA","MAHABANK","BDL","BEL","BHARATFORG","BHEL","BPCL","BHARTIARTL","BIOCON","BLUESTARCO","BOSCHLTD","BRITANNIA","CGPOWER","CANBK","CDSL","CHOLAFIN","CIPLA","COALINDIA","COCHINSHIP","COFORGE","COLPAL","CAMS","CONCOR","CROMPTON","CUMMINSIND","DLF","DABUR","DELHIVERY","DIVISLAB","DIXON","DRREDDY","ETERNAL","EICHERMOT","FORCEMOT","NYKAA","FORTIS","GAIL","GVT&D","GMRAIRPORT","GLENMARK","GODFRYPHLP","GODREJCP","GODREJPROP","GRASIM","HCLTECH","HDFCAMC","HDFCBANK","HDFCLIFE","HAVELLS","HEROMOTOCO","HINDALCO","HAL","HINDPETRO","HINDUNILVR","HINDZINC","POWERINDIA","HYUNDAI","ICICIBANK","ICICIGI","ICICIPRULI","IDFCFIRSTB","ITC","INDIANB","IEX","IOC","IRFC","IREDA","INDUSTOWER","INDUSINDBK","NAUKRI","INFY","INOXWIND","INDIGO","JINDALSTEL","JSWENERGY","JSWSTEEL","JIOFIN","JUBLFOOD","KEI","KPITTECH","KALYANKJIL","KAYNES","KFINTECH","KOTAKBANK","LTF","LICHSGFIN","LTM","LT","LAURUSLABS","LICI","LODHA","LUPIN","M&M","MANAPPURAM","MANKIND","MARICO","MARUTI","MFSL","MAXHEALTH","MAZDOCK","MOTILALOFS","MPHASIS","MCX","MUTHOOTFIN","NBCC","NHPC","NMDC","NTPC","NATIONALUM","NESTLEIND","NAM-INDIA","OBEROIRLTY","ONGC","OIL","PAYTM","OFSS","POLICYBZR","PGEL","PIIND","PNBHOUSING","PAGEIND","PATANJALI","PERSISTENT","PETRONET","PIDILITIND","POLYCAB","PFC","POWERGRID","PREMIERENE","PRESTIGE","PNB","RBLBANK","RECLTD","RADICO","RVNL","RELIANCE","SAGILITY","SBICARD","SBILIFE","SHREECEM","SRF","MOTHERSON","SHRIRAMFIN","SIEMENS","SOLARINDS","SONACOMS","SBIN","SAIL","SUNPHARMA","SUPREMEIND","SUZLON","SWIGGY","TATACONSUM","TVSMOTOR","TCS","TATAELXSI","TMPV","TATAPOWER","TATASTEEL","TECHM","FEDERALBNK","INDHOTEL","PHOENIXLTD","TITAN","TORNTPHARM","TRENT","TIINDIA","UNOMINDA","UPL","ULTRACEMCO","UNIONBANK","UNITDSPR","VBL","VEDL","VMM","IDEA","VOLTAS","WAAREEENER","WIPRO","YESBANK","ZYDUSLIFE"]
SECTOR_MAP_FULL = {"HDFCBANK":"Banking","ICICIBANK":"Banking","SBIN":"Banking","AXISBANK":"Banking","KOTAKBANK":"Banking","INDUSINDBK":"Banking","BANDHANBNK":"Banking","BANKBARODA":"Banking","BANKINDIA":"Banking","FEDERALBNK":"Banking","IDFCFIRSTB":"Banking","RBLBANK":"Banking","PNB":"Banking","INDIANB":"Banking","CANBK":"Banking","UNIONBANK":"Banking","MAHABANK":"Banking","YESBANK":"Banking","BAJFINANCE":"Finance","BAJAJFINSV":"Finance","SBILIFE":"Finance","HDFCLIFE":"Finance","ICICIPRULI":"Finance","ICICIGI":"Finance","SBICARD":"Finance","CHOLAFIN":"Finance","MUTHOOTFIN":"Finance","SHRIRAMFIN":"Finance","LICHSGFIN":"Finance","LTF":"Finance","RECLTD":"Finance","PFC":"Finance","BSE":"Finance","CDSL":"Finance","CAMS":"Finance","KFINTECH":"Finance","JIOFIN":"Finance","ABCAPITAL":"Finance","360ONE":"Finance","ANGELONE":"Finance","MOTILALOFS":"Finance","MANAPPURAM":"Finance","PNBHOUSING":"Finance","NAM-INDIA":"Finance","HDFCAMC":"Finance","MCX":"Finance","RELIANCE":"Energy","ONGC":"Energy","BPCL":"Energy","IOC":"Energy","HINDPETRO":"Energy","GAIL":"Energy","OIL":"Energy","NTPC":"Energy","POWERGRID":"Energy","JSWENERGY":"Energy","ADANIPOWER":"Energy","ADANIGREEN":"Energy","TATAPOWER":"Energy","NHPC":"Energy","ADANIENSOL":"Energy","INFY":"IT","TCS":"IT","HCLTECH":"IT","WIPRO":"IT","TECHM":"IT","COFORGE":"IT","MPHASIS":"IT","PERSISTENT":"IT","LTM":"IT","KPITTECH":"IT","OFSS":"IT","MARUTI":"Auto","M&M":"Auto","TMPV":"Auto","BAJAJ-AUTO":"Auto","EICHERMOT":"Auto","TVSMOTOR":"Auto","ASHOKLEY":"Auto","BHARATFORG":"Auto","BOSCHLTD":"Auto","MOTHERSON":"Auto","UNOMINDA":"Auto","SONACOMS":"Auto","TIINDIA":"Auto","SUNPHARMA":"Pharma","DRREDDY":"Pharma","CIPLA":"Pharma","DIVISLAB":"Pharma","LUPIN":"Pharma","AUROPHARMA":"Pharma","ALKEM":"Pharma","TORNTPHARM":"Pharma","ZYDUSLIFE":"Pharma","LAURUSLABS":"Pharma","BIOCON":"Pharma","MANKIND":"Pharma","ITC":"FMCG","HINDUNILVR":"FMCG","NESTLEIND":"FMCG","BRITANNIA":"FMCG","TATACONSUM":"FMCG","DABUR":"FMCG","GODREJCP":"FMCG","MARICO":"FMCG","COLPAL":"FMCG","VBL":"FMCG","GODFRYPHLP":"FMCG","RADICO":"FMCG","UNITDSPR":"FMCG","LT":"Capital Goods","BEL":"Capital Goods","BHEL":"Capital Goods","SIEMENS":"Capital Goods","ABB":"Capital Goods","CGPOWER":"Capital Goods","CUMMINSIND":"Capital Goods","POLYCAB":"Capital Goods","KEI":"Capital Goods","HAVELLS":"Capital Goods","POWERINDIA":"Capital Goods","GVT&D":"Capital Goods","VOLTAS":"Capital Goods","CROMPTON":"Capital Goods","BLUESTARCO":"Capital Goods","ASTRAL":"Capital Goods","DIXON":"Capital Goods","KAYNES":"Capital Goods","AMBER":"Capital Goods","PGEL":"Capital Goods","BDL":"Capital Goods","HAL":"Capital Goods","MAZDOCK":"Capital Goods","COCHINSHIP":"Capital Goods","JSWSTEEL":"Metals","TATASTEEL":"Metals","HINDALCO":"Metals","VEDL":"Metals","NMDC":"Metals","SAIL":"Metals","JINDALSTEL":"Metals","HINDZINC":"Metals","NATIONALUM":"Metals","ULTRACEMCO":"Cement","SHREECEM":"Cement","AMBUJACEM":"Cement","GRASIM":"Cement","DLF":"Realty","GODREJPROP":"Realty","OBEROIRLTY":"Realty","LODHA":"Realty","PRESTIGE":"Realty","PHOENIXLTD":"Realty","ADANIENT":"Adani","ADANIPORTS":"Adani","GMRAIRPORT":"Adani"}
RSS_FEEDS = {"🇮🇳 INDIA MARKET (22)": {"MoneyControl Top": "https://www.moneycontrol.com/rss/MCtopnews.xml","MoneyControl Market": "https://www.moneycontrol.com/rss/marketreports.xml","MoneyControl Business": "https://www.moneycontrol.com/rss/business.xml","MoneyControl Economy": "https://www.moneycontrol.com/rss/economy.xml","ET Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms","ET Stocks": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms","ET Sensex": "https://economictimes.indiatimes.com/markets/sensex/rssfeeds/477580.cms","ET Nifty": "https://economictimes.indiatimes.com/markets/nse-nifty/rssfeeds/1793823366.cms","LiveMint Markets": "https://www.livemint.com/rss/markets","LiveMint Companies": "https://www.livemint.com/rss/companies","BS Markets": "https://www.business-standard.com/rss/markets-106.rss","BS Economy": "https://www.business-standard.com/rss/economy-105.rss","BS Finance": "https://www.business-standard.com/rss/finance-103.rss","FE Market": "https://www.financialexpress.com/market/feed/","FE Economy": "https://www.financialexpress.com/economy/feed/","CNBC TV18 All": "https://www.cnbctv18.com/commonfeeds/v1/cnbcv18all.xml","CNBC TV18 Market": "https://www.cnbctv18.com/commonfeeds/v1/cnbcv18market.xml","CNBC TV18 Economy": "https://www.cnbctv18.com/commonfeeds/v1/cnbcv18economy.xml","NDTV Profit": "https://www.ndtvprofit.com/rss","NDTV Economy": "https://www.ndtvprofit.com/rss/economy","Zee Business": "https://zeenews.india.com/rss/business.xml","MC IPO": "https://www.moneycontrol.com/rss/ipo.xml",},"🌎 GLOBAL MARKET (20)": {"Reuters Business": "http://feeds.reuters.com/reuters/businessNews","Reuters Markets": "http://feeds.reuters.com/reuters/marketsNews","Reuters Top": "http://feeds.reuters.com/reuters/topNews","CNBC Top": "https://www.cnbc.com/id/100003114/device/rss/rss.html","CNBC Markets": "https://www.cnbc.com/id/10000664/device/rss/rss.html","CNBC Economy": "https://www.cnbc.com/id/10000113/device/rss/rss.html","Yahoo Finance": "https://finance.yahoo.com/news/rssindex","MarketWatch Top": "http://feeds.marketwatch.com/marketwatch/topstories/","MarketWatch Pulse": "http://feeds.marketwatch.com/marketwatch/marketpulse/","MarketWatch RealTime": "http://feeds.marketwatch.com/marketwatch/realtimeheadlines/","Investing News": "https://www.investing.com/rss/news.rss","Investing Overview": "https://www.investing.com/rss/market_overview.rss","BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml","BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml","NYT Business": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml","NYT Economy": "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml","FT Markets": "https://www.ft.com/markets?format=rss","Bloomberg Markets": "https://feeds.bloomberg.com/markets/news.rss","WSJ Markets": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml","WSJ Economy": "https://feeds.a.dj.com/rss/RSSWSJD.xml",},"🛢️ COMMODITY (15)": {"MC Commodity": "https://www.moneycontrol.com/rss/commodity.xml","ET Commodity": "https://economictimes.indiatimes.com/commodity/rssfeeds/1808152121.cms","OilPrice Main": "https://oilprice.com/rss/main","OilPrice Energy": "https://oilprice.com/rss/energy-news","Kitco News": "https://www.kitco.com/rss/KitcoNews.xml","Kitco Gold": "https://www.kitco.com/rss/gold.xml","Investing Commodity": "https://www.investing.com/rss/commodities_Feed.rss","Investing Gold": "https://www.investing.com/rss/commodities_Gold.rss","Investing Oil": "https://www.investing.com/rss/commodities_Oil.rss","GoldPrice": "https://goldprice.org/rss","ET Energy": "https://economictimes.indiatimes.com/industry/energy/rssfeeds/1783664934.cms","LiveMint Commodity": "https://www.livemint.com/rss/commodities","Commodity Online": "https://www.commodityonline.com/rss/","MCX India": "https://www.mcxindia.com/rss/mcx-news.xml","Investing Silver": "https://www.investing.com/rss/commodities_Silver.rss",},"₿ CRYPTO (10)": {"CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/","CoinDesk Markets": "https://www.coindesk.com/arc/outboundfeeds/rss/?collection=markets","CoinTelegraph": "https://cointelegraph.com/rss","CoinTelegraph Markets": "https://cointelegraph.com/rss-feeds/markets","Decrypt": "https://decrypt.co/feed","Investing Crypto": "https://www.investing.com/rss/news_301.rss","Bitcoin.com": "https://news.bitcoin.com/feed/","NewsBTC": "https://www.newsbtc.com/feed/","CryptoPanic": "https://cryptopanic.com/news/rss/","CoinJournal": "https://coinjournal.net/feed/",},"🏦 RBI / INDIA ECO (10)": {"RBI Press": "https://www.rbi.org.in/rss/RBI_PressRelease.xml","RBI Speech": "https://www.rbi.org.in/rss/RBI_Speeches.xml","RBI Notification": "https://www.rbi.org.in/rss/RBI_Notification.xml","RBI Circular": "https://www.rbi.org.in/rss/RBI_Circulars.xml","ET Economy": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms","ET RBI": "https://economictimes.indiatimes.com/topic/rbi/rss","LiveMint Economy": "https://www.livemint.com/rss/economy","BS Economy Policy": "https://www.business-standard.com/rss/economy-policy-105.rss","FE Economy 2": "https://www.financialexpress.com/economy/feed/","NDTV Eco": "https://www.ndtvprofit.com/rss/economy",},"🏛️ FED / US ECO (10)": {"Fed All Press": "https://www.federalreserve.gov/feeds/press_all.xml","Fed Monetary": "https://www.federalreserve.gov/feeds/press_monetary.xml","Fed Financial": "https://www.federalreserve.gov/feeds/press_financial.xml","Fed Supervision": "https://www.federalreserve.gov/feeds/press_supervision.xml","Fed Other": "https://www.federalreserve.gov/feeds/other.xml","US Treasury Press": "https://home.treasury.gov/rss/press-releases","ET Fed": "https://economictimes.indiatimes.com/topic/federal-reserve/rss","Investing US Eco": "https://www.investing.com/rss/news_14.rss","BLS News": "https://www.bls.gov/feed/bls_news.xml","BEA News": "https://www.bea.gov/rss/rss.xml",}}

@st.cache_data
def load_cash_symbols():
    try:
        df = pd.read_csv("EQUITY_L.csv")
        df.columns = [c.strip() for c in df.columns]
        if 'SERIES' in df.columns: df = df[df['SERIES'].astype(str).str.strip() == 'EQ']
        df['SYMBOL'] = df['SYMBOL'].astype(str).str.strip()
        return sorted(list(set([f"{s}.NS" for s in df['SYMBOL'] if s!='' and s.lower()!='nan'])))
    except: return []

def scan_fno():
    up, down = [], []; last_date = None
    bar = st.progress(0, text="FNO Scanning 200 stocks...")
    for i, sym in enumerate(FNO):
        try:
            d = yf.Ticker(f"{sym}.NS").history(period="5d", auto_adjust=True)
            if d.empty: continue
            d = d.dropna()
            if len(d)<1: continue
            last_date = d.index[-1].strftime("%d-%m-%Y")
            o=float(d['Open'].iloc[-1]); h=float(d['High'].iloc[-1]); l=float(d['Low'].iloc[-1]); c=float(d['Close'].iloc[-1])
            if l==0 or h==0: continue
            lu = (c-l)/l*100 if l!=0 else 0; hd = (h-c)/h*100 if h!=0 else 0
            if lu >= 1: up.append({"SYM":sym,"OPEN":round(o,2),"LOW":round(l,2),"LTP":round(c,2),"LOW_UP %":round(lu,2),"DATE":d.index[-1].strftime("%d-%m")})
            if hd >= 1: down.append({"SYM":sym,"OPEN":round(o,2),"HIGH":round(h,2),"LTP":round(c,2),"HIGH_DOWN %":round(hd,2),"DATE":d.index[-1].strftime("%d-%m")})
        except: pass
        bar.progress((i+1)/len(FNO))
    bar.empty()
    return pd.DataFrame(up), pd.DataFrame(down), last_date

def scan_cash_full():
    syms = load_cash_symbols()
    if not syms: return pd.DataFrame(), pd.DataFrame(), None
    up, down = [], []; last_date = None
    bar = st.progress(0, text=f"CASH Scanning {len(syms)} stocks...")
    for idx, s in enumerate(syms):
        try:
            d = yf.Ticker(s).history(period="5d", auto_adjust=True)
            if d.empty: continue
            d = d.dropna()
            if len(d)<1: continue
            last_date = d.index[-1].strftime("%d-%m-%Y")
            h,l,c,v = float(d['High'].iloc[-1]), float(d['Low'].iloc[-1]), float(d['Close'].iloc[-1]), float(d['Volume'].iloc[-1])
            if v < 10000000 or l==0 or h==0: continue
            lu = (c-l)/l*100 if l!=0 else 0; hd = (h-c)/h*100 if h!=0 else 0
            name = s.replace(".NS","")
            if lu >= 2.5: up.append({"SYMBOL":name,"LTP":round(c,2),"LOW":round(l,2),"VOL Cr":round(v/1e7,2),"LOW_UP %":round(lu,2),"DATE":d.index[-1].strftime("%d-%m")})
            if hd >= 3: down.append({"SYMBOL":name,"LTP":round(c,2),"HIGH":round(h,2),"VOL Cr":round(v/1e7,2),"HIGH_DOWN %":round(hd,2),"DATE":d.index[-1].strftime("%d-%m")})
        except: continue
        if idx%20==0: bar.progress((idx+1)/len(syms))
    bar.empty()
    return pd.DataFrame(up), pd.DataFrame(down), last_date

@st.cache_data(ttl=90)
def fetch_news():
    all_news={}
    for cat, feeds in RSS_FEEDS.items():
        lst=[]
        for src, url in feeds.items():
            try:
                f=feedparser.parse(url)
                for e in f.entries[:4]:
                    dt = datetime(*e.published_parsed[:6]) if hasattr(e,'published_parsed') and e.published_parsed else datetime.now()
                    lst.append({"DATE":dt.strftime("%d-%m"),"TIME":dt.strftime("%H:%M"),"SRC":src,"TITLE":e.title,"LINK":e.link,"DT":dt})
            except: continue
        lst=sorted(lst,key=lambda x:x['DT'],reverse=True)
        all_news[cat]=lst
    return all_news

with st.sidebar:
    st.markdown("## 🔷 TradingPro")
    st.markdown("<span style='color:#00d084; font-size:20px; font-weight:900'>● PREMIUM</span> <span style='background:#00d084;color:#000;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:900'>PRO PLAN • ACTIVE</span>", unsafe_allow_html=True)
    st.write("")
    menu = st.radio("Navigation", ["📊 Dashboard - All in One","📈 FNO - 1% Low UP + High DOWN","🔍 CASH - 2.5% (EQUITY_L.csv)","📊 Sector + Heatmap (Only FNO)","📰 NEWS Terminal - 87 Sources"], label_visibility="collapsed")
    st.divider()
    st.caption(f"📅 {datetime.now(IST).strftime('%d %b %Y %I:%M %p')} IST")

if menu == "📊 Dashboard - All in One":
    st.title("📊 TradingPro - All in One Dashboard")
    if st.button("🚀 FULL SCAN KARO - FNO + CASH", type="primary", use_container_width=True):
        df_u, df_d, last_dt = scan_fno()
        st.info(f"FNO Last Trading Date: {last_dt}")
        c1,c2 = st.columns(2)
        with c1: st.markdown(f"<div class='green-box'>↗ LOW 1% UP: {len(df_u)}</div>", unsafe_allow_html=True); render_hover_table(df_u.sort_values("LOW_UP %", ascending=False) if not df_u.empty else df_u, "SYM")
        with c2: st.markdown(f"<div class='red-box'>↘ HIGH 1% DOWN: {len(df_d)}</div>", unsafe_allow_html=True); render_hover_table(df_d.sort_values("HIGH_DOWN %", ascending=False) if not df_d.empty else df_d, "SYM")
        st.divider()
        df_cu, df_cd, last_dt_cash = scan_cash_full()
        st.info(f"CASH Last Trading Date: {last_dt_cash} | Total: {len(load_cash_symbols())} stocks")
        c3,c4 = st.columns(2)
        with c3: st.markdown(f"<div class='green-box'>↗ CASH LOW 2.5% UP: {len(df_cu)}</div>", unsafe_allow_html=True); render_hover_table(df_cu.sort_values("LOW_UP %", ascending=False) if not df_cu.empty else df_cu, "SYMBOL")
        with c4: st.markdown(f"<div class='red-box'>↘ CASH HIGH 3% DOWN: {len(df_cd)}</div>", unsafe_allow_html=True); render_hover_table(df_cd.sort_values("HIGH_DOWN %", ascending=False) if not df_cd.empty else df_cd, "SYMBOL")

elif menu == "📈 FNO - 1% Low UP + High DOWN":
    st.title("📈 FNO - 1% Low UP + High DOWN")
    if st.button("🚀 SCAN FNO - LOW 1% + HIGH 1%", type="primary", use_container_width=True):
        df_u, df_d, last_dt = scan_fno()
        st.info(f"Last Trading Date: {last_dt}")
        c1,c2 = st.columns(2)
        with c1: st.markdown(f"<div class='green-box'>↗ LOW se 1% UP: {len(df_u)}</div>", unsafe_allow_html=True); render_hover_table(df_u.sort_values("LOW_UP %", ascending=False) if not df_u.empty else df_u, "SYM")
        with c2: st.markdown(f"<div class='red-box'>↘ HIGH se 1% DOWN: {len(df_d)}</div>", unsafe_allow_html=True); render_hover_table(df_d.sort_values("HIGH_DOWN %", ascending=False) if not df_d.empty else df_d, "SYM")

elif menu == "🔍 CASH - 2.5% (EQUITY_L.csv)":
    st.title("🔍 CASH Screener - 2.5% UP / 3% DOWN")
    if st.button("🚀 SCAN FULL CASH", type="primary", use_container_width=True):
        df_u, df_d, last_dt = scan_cash_full(); st.info(f"Last Trading Date: {last_dt}")
        c1,c2 = st.columns(2)
        with c1: st.success(f"LOW 2.5% UP: {len(df_u)}"); render_hover_table(df_u.sort_values("LOW_UP %", ascending=False) if not df_u.empty else df_u, "SYMBOL")
        with c2: st.error(f"HIGH 3% DOWN: {len(df_d)}"); render_hover_table(df_d.sort_values("HIGH_DOWN %", ascending=False) if not df_d.empty else df_d, "SYMBOL")

elif menu == "📊 Sector + Heatmap (Only FNO)":
    st.title("📊 Heatmap + Sector Performance")
    if st.button("🔥 GENERATE NSE HEATMAP & SECTOR CHART", type="primary", use_container_width=True):
        with st.spinner("Fetching live data for 200 FNO..."):
            heat_data = []
            bar = st.progress(0, text="Heatmap data...")
            for i, sym in enumerate(FNO):
                try:
                    d = yf.Ticker(f"{sym}.NS").history(period="5d", auto_adjust=True)
                    if d.empty or len(d)<2: continue
                    c = float(d['Close'].iloc[-1]); prev = float(d['Close'].iloc[-2])
                    ch = (c-prev)/prev*100 if prev!=0 else 0
                    sector = SECTOR_MAP_FULL.get(sym, "Others")
                    heat_data.append({"SYM":sym,"SECTOR":sector,"CHANGE":round(ch,2),"LTP":round(c,2),"SIZE":1})
                except: continue
                bar.progress((i+1)/len(FNO))
            bar.empty()
            st.session_state['df_h'] = pd.DataFrame(heat_data)

    if 'df_h' in st.session_state and not st.session_state['df_h'].empty:
        df_h = st.session_state['df_h']

        # 1. HEATMAP - SIRF RED/GREEN
        st.subheader("Heatmap - Only Red & Green")
        fig_tree = px.treemap(df_h, path=['SECTOR','SYM'], values='SIZE', color='CHANGE',
                              color_continuous_scale=[(0, "#d50000"), (0.5, "#1a1a1a"), (1, "#00c853")],
                              color_continuous_midpoint=0, range_color=[-5,5])
        fig_tree.update_layout(height=650, template="plotly_dark")
        st.plotly_chart(fig_tree, use_container_width=True)

        # 2. SECTOR BAR - SIRF RED/GREEN
        st.subheader("Sector Performance - Green/Red Only")
        sec_perf = df_h.groupby("SECTOR")["CHANGE"].mean().reset_index().sort_values("CHANGE", ascending=False)
        colors = ['#00c853' if x>=0 else '#d50000' for x in sec_perf['CHANGE']]
        fig_bar = go.Figure(go.Bar(x=sec_perf['SECTOR'], y=sec_perf['CHANGE'], marker_color=colors,
                                   text=[f"{x:+.2f}%" for x in sec_perf['CHANGE']], textposition='outside'))
        fig_bar.update_layout(height=500, template="plotly_dark", yaxis_title="% Avg Change")
        st.plotly_chart(fig_bar, use_container_width=True)

        # 3. SECTOR PE CLICK = SARE STOCK DIKHE - NEW FEATURE
        st.divider()
        st.subheader("🔍 Sector pe click karke uske sare stock dekho")
        selected_sector = st.selectbox("Sector select karo:", ["All"] + sorted(df_h["SECTOR"].unique().tolist()))
        if selected_sector!= "All":
            filtered = df_h[df_h["SECTOR"] == selected_sector].sort_values("CHANGE", ascending=False)
        else:
            filtered = df_h.sort_values("CHANGE", ascending=False)

        st.dataframe(filtered[['SYM','SECTOR','LTP','CHANGE']].style.applymap(
            lambda x: 'color: #00c853; font-weight:bold' if isinstance(x, (int,float)) and x>0 else 'color: #d50000; font-weight:bold' if isinstance(x, (int,float)) and x<0 else '',
            subset=['CHANGE']
        ), use_container_width=True, height=500)

    else:
        st.info("👆 Pehle 'GENERATE NSE HEATMAP' dabao")

elif menu == "📰 NEWS Terminal - 87 Sources":
    st.title("📰 LIVE NEWS TERMINAL - 87 Sources")
    if st.button("🔄 REFRESH NEWS", type="primary"): st.cache_data.clear()
    news_data = fetch_news()
    total = sum(len(v) for v in news_data.values())
    st.success(f"Live • {total} headlines • {datetime.now(IST).strftime('%H:%M:%S')} IST")

    # AB 6 ki jagah 3 COLUMN - BADA DIKHEGA
    cats = list(RSS_FEEDS.keys())
    for i in range(0, len(cats), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(cats):
                cat = cats[i+j]
                with cols[j]:
                    st.markdown(f"### {cat}")
                    lst = news_data.get(cat, [])
                    with st.container(border=True, height=800):
                        for n in lst[:15]:
                            st.caption(f"{n['TIME']} | {n['SRC']}")
                            st.markdown(f"**[{n['TITLE']}]({n['LINK']})**")
                            st.divider()
    time.sleep(120); st.rerun()
