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
thead tr th:first-child{display:none} tbody th{display:none}
</style>
""", unsafe_allow_html=True)

def draw_half_chart(symbol, pct_info=""):
    try:
        today_ist = datetime.now(IST).date()
        df = pd.DataFrame()
        is_today = True
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
                df_5 = yf.Ticker(f"{symbol}.NS").history(period="5d", interval="5m", auto_adjust=True)
                if not df_5.empty:
                    if df_5.index.tz is not None:
                        df_5.index = df_5.index.tz_convert(IST)
                    last_date = df_5.index[-1].date()
                    df_last = df_5[df_5.index.date == last_date]
                    if len(df_last) >= 2:
                        df = df_last
                        is_today = False
                        today_ist = last_date
            except: pass
        if df.empty:
            st.caption(f"{symbol} - Data nahi")
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
        title_tag = "TODAY LIVE" if is_today else f"{today_ist.strftime('%d %b')} LAST"
        color_tag = '#00d084' if is_today else '#ffaa00'
        ax.set_title(f"{symbol} {pct_info} - {title_tag}", color=color_tag, fontsize=14, fontweight='bold', pad=10)
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

FNO = ["360ONE","ABB","APLAPOLLO","AUBANK","ADANIENSOL","ADANIENT","ADANIGREEN","ADANIPORTS","ADANIPOWER","ABCAPITAL","ALKEM","AMBER","AMBUJACEM","ANGELONE","APOLLOHOSP","ASHOKLEY","ASIANPAINT","ASTRAL","ATHERENERG","AUROPHARMA","DMART","AXISBANK","BSE","BAJAJ-AUTO","BAJFINANCE","BAJAJFINSV","BAJAJHLDNG","BANDHANBNK","BANKBARODA","BANKINDIA","MAHABANK","BDL","BEL","BHARATFORG","BHEL","BPCL","BHARTIARTL","BIOCON","BLUESTARCO","BOSCHLTD","BRITANNIA","CGPOWER","CANBK","CDSL","CHOLAFIN","CIPLA","COALINDIA","COCHINSHIP","COFORGE","COLPAL","CAMS","CONCOR","CROMPTON","CUMMINSIND","DLF","DABUR","DELHIVERY","DIVISLAB","DIXON","DRREDDY","ETERNAL","EICHERMOT","FORCEMOT","NYKAA","FORTIS","GAIL","GVT&D","GMRAIRPORT","GLENMARK","GODFRYPHLP","GODREJCP","GODREJPROP","GRASIM","HCLTECH","HDFCAMC","HDFCBANK","HDFCLIFE","HAVELLS","HEROMOTOCO","HINDALCO","HAL","HINDPETRO","HINDUNILVR","HINDZINC","POWERINDIA","HYUNDAI","ICICIBANK","ICICIGI","ICICIPRULI","IDFCFIRSTB","ITC","INDIANB","IEX","IOC","IRFC","IREDA","INDUSTOWER","INDUSINDBK","NAUKRI","INFY","INOXWIND","INDIGO","JINDALSTEL","JSWENERGY","JSWSTEEL","JIOFIN","JUBLFOOD","KEI","KPITTECH","KALYANKJIL","KAYNES","KFINTECH","KOTAKBANK","LTF","LICHSGFIN","LTM","LT","LAURUSLABS","LICI","LODHA","LUPIN","M&M","MANAPPURAM","MANKIND","MARICO","MARUTI","MFSL","MAXHEALTH","MAZDOCK","MOTILALOFS","MPHASIS","MCX","MUTHOOTFIN","NBCC","NHPC","NMDC","NTPC","NATIONALUM","NESTLEIND","NAM-INDIA","OBEROIRLTY","ONGC","OIL","PAYTM","OFSS","POLICYBZR","PGEL","PIIND","PNBHOUSING","PAGEIND","PATANJALI","PERSISTENT","PETRONET","PIDILITIND","POLYCAB","PFC","POWERGRID","PREMIERENE","PRESTIGE","PNB","RBLBANK","RECLTD","RADICO","RVNL","RELIANCE","SAGILITY","SBICARD","SBILIFE","SHREECEM","SRF","MOTHERSON","SHRIRAMFIN","SIEMENS","SOLARINDS","SONACOMS","SBIN","SAIL","SUNPHARMA","SUPREMEIND","SUZLON","SWIGGY","TATACONSUM","TVSMOTOR","TCS","TATAELXSI","TMPV","TATAPOWER","TATASTEEL","TECHM","FEDERALBNK","INDHOTEL","PHOENIXLTD","TITAN","TORNTPHARM","TRENT","TIINDIA","UNOMINDA","UPL","ULTRACEMCO","UNIONBANK","UNITDSPR","VBL","VEDL","VMM","IDEA","VOLTAS","WAAREEENER","WIPRO","YESBANK","ZYDUSLIFE"]

SECTOR_MAP_FULL = {"HDFCBANK":"Banking","ICICIBANK":"Banking","SBIN":"Banking","AXISBANK":"Banking","KOTAKBANK":"Banking","INDUSINDBK":"Banking","BANDHANBNK":"Banking","BANKBARODA":"Banking","BANKINDIA":"Banking","FEDERALBNK":"Banking","IDFCFIRSTB":"Banking","RBLBANK":"Banking","PNB":"Banking","INDIANB":"Banking","CANBK":"Banking","UNIONBANK":"Banking","MAHABANK":"Banking","YESBANK":"Banking","BAJFINANCE":"Finance","BAJAJFINSV":"Finance","SBILIFE":"Finance","HDFCLIFE":"Finance","ICICIPRULI":"Finance","ICICIGI":"Finance","SBICARD":"Finance","CHOLAFIN":"Finance","MUTHOOTFIN":"Finance","SHRIRAMFIN":"Finance","LICHSGFIN":"Finance","LTF":"Finance","RECLTD":"Finance","PFC":"Finance","BSE":"Finance","CDSL":"Finance","CAMS":"Finance","KFINTECH":"Finance","JIOFIN":"Finance","ABCAPITAL":"Finance","360ONE":"Finance","ANGELONE":"Finance","MOTILALOFS":"Finance","MANAPPURAM":"Finance","PNBHOUSING":"Finance","NAM-INDIA":"Finance","HDFCAMC":"Finance","MCX":"Finance","RELIANCE":"Energy","ONGC":"Energy","BPCL":"Energy","IOC":"Energy","HINDPETRO":"Energy","GAIL":"Energy","OIL":"Energy","NTPC":"Energy","POWERGRID":"Energy","JSWENERGY":"Energy","ADANIPOWER":"Energy","ADANIGREEN":"Energy","TATAPOWER":"Energy","NHPC":"Energy","ADANIENSOL":"Energy","INFY":"IT","TCS":"IT","HCLTECH":"IT","WIPRO":"IT","TECHM":"IT","COFORGE":"IT","MPHASIS":"IT","PERSISTENT":"IT","LTM":"IT","KPITTECH":"IT","OFSS":"IT","MARUTI":"Auto","M&M":"Auto","TMPV":"Auto","BAJAJ-AUTO":"Auto","EICHERMOT":"Auto","TVSMOTOR":"Auto","ASHOKLEY":"Auto","BHARATFORG":"Auto","BOSCHLTD":"Auto","MOTHERSON":"Auto","UNOMINDA":"Auto","SONACOMS":"Auto","TIINDIA":"Auto","SUNPHARMA":"Pharma","DRREDDY":"Pharma","CIPLA":"Pharma","DIVISLAB":"Pharma","LUPIN":"Pharma","AUROPHARMA":"Pharma","ALKEM":"Pharma","TORNTPHARM":"Pharma","ZYDUSLIFE":"Pharma","LAURUSLABS":"Pharma","BIOCON":"Pharma","MANKIND":"Pharma","ITC":"FMCG","HINDUNILVR":"FMCG","NESTLEIND":"FMCG","BRITANNIA":"FMCG","TATACONSUM":"FMCG","DABUR":"FMCG","GODREJCP":"FMCG","MARICO":"FMCG","COLPAL":"FMCG","VBL":"FMCG","GODFRYPHLP":"FMCG","RADICO":"FMCG","UNITDSPR":"FMCG","LT":"Capital Goods","BEL":"Capital Goods","BHEL":"Capital Goods","SIEMENS":"Capital Goods","ABB":"Capital Goods","CGPOWER":"Capital Goods","CUMMINSIND":"Capital Goods","POLYCAB":"Capital Goods","KEI":"Capital Goods","HAVELLS":"Capital Goods","POWERINDIA":"Capital Goods","GVT&D":"Capital Goods","VOLTAS":"Capital Goods","CROMPTON":"Capital Goods","BLUESTARCO":"Capital Goods","ASTRAL":"Capital Goods","DIXON":"Capital Goods","KAYNES":"Capital Goods","AMBER":"Capital Goods","PGEL":"Capital Goods","BDL":"Capital Goods","HAL":"Capital Goods","MAZDOCK":"Capital Goods","COCHINSHIP":"Capital Goods","JSWSTEEL":"Metals","TATASTEEL":"Metals","HINDALCO":"Metals","VEDL":"Metals","NMDC":"Metals","SAIL":"Metals","JINDALSTEL":"Metals","HINDZINC":"Metals","NATIONALUM":"Metals","ULTRACEMCO":"Cement","SHREECEM":"Cement","AMBUJACEM":"Cement","GRASIM":"Cement","DLF":"Realty","GODREJPROP":"Realty","OBEROIRLTY":"Realty","LODHA":"Realty","PRESTIGE":"Realty","PHOENIXLTD":"Realty","ADANIENT":"Adani","ADANIPORTS":"Adani","GMRAIRPORT":"Adani"}

RSS_FEEDS = {"🇮🇳 INDIA MARKET (22)": {"MoneyControl Top": "https://www.moneycontrol.com/rss/MCtopnews.xml","MoneyControl Market": "https://www.moneycontrol.com/rss/marketreports.xml","MoneyControl Business": "https://www.moneycontrol.com/rss/business.xml","MoneyControl Economy": "https://www.moneycontrol.com/rss/economy.xml","ET Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms","ET Stocks": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms","ET Sensex": "https://economictimes.indiatimes.com/markets/sensex/rssfeeds/477580.cms","ET Nifty": "https://economictimes.indiatimes.com/markets/nse-nifty/rssfeeds/1793823366.cms","LiveMint Markets": "https://www.livemint.com/rss/markets","LiveMint Companies": "https://www.livemint.com/rss/companies","BS Markets": "https://www.business-standard.com/rss/markets-106.rss","BS Economy": "https://www.business-standard.com/rss/economy-105.rss","BS Finance": "https://www.business-standard.com/rss/finance-103.rss","FE Market": "https://www.financialexpress.com/market/feed/","FE Economy": "https://www.financialexpress.com/economy/feed/","CNBC TV18 All": "https://www.cnbctv18.com/commonfeeds/v1/cnbcv18all.xml","CNBC TV18 Market": "https://www.cnbctv18.com/commonfeeds/v1/cnbcv18market.xml","CNBC TV18 Economy": "https://www.cnbctv18.com/commonfeeds/v1/cnbcv18economy.xml","NDTV Profit": "https://www.ndtvprofit.com/rss","NDTV Economy": "https://www.ndtvprofit.com/rss/economy","Zee Business": "https://zeenews.india.com/rss/business.xml","MC IPO": "https://www.moneycontrol.com/rss/ipo.xml",},"🌎 GLOBAL MARKET (20)": {"Reuters Business": "http://feeds.reuters.com/reuters/businessNews","Reuters Markets": "http://feeds.reuters.com/reuters/marketsNews","Reuters Top": "http://feeds.reuters.com/reuters/topNews","CNBC Top": "https://www.cnbc.com/id/100003114/device/rss/rss.html","CNBC Markets": "https://www.cnbc.com/id/10000664/device/rss/rss.html","CNBC Economy": "https://www.cnbc.com/id/10000113/device/rss/rss.html","Yahoo Finance": "https://finance.yahoo.com/news/rssindex","MarketWatch Top": "http://feeds.marketwatch.com/marketwatch/topstories/","MarketWatch Pulse": "http://feeds.marketwatch.com/marketwatch/marketpulse/","MarketWatch RealTime": "http://feeds.marketwatch.com/marketwatch/realtimeheadlines/","Investing News": "https://www.investing.com/rss/news.rss","Investing Overview": "https://www.investing.com/rss/market_overview.rss","BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml","BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml","NYT Business": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml","NYT Economy": "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml","FT Markets": "https://www.ft.com/markets?format=rss","Bloomberg Markets": "https://feeds.bloomberg.com/markets/news.rss","WSJ Markets": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml","WSJ Economy": "https://feeds.a.dj.com/rss/RSSWSJD.xml",},"🛢️ COMMODITY (15)": {"MC Commodity": "https://www.moneycontrol.com/rss/commodity.xml","ET Commodity": "https://economictimes.indiatimes.com/commodity/rssfeeds/1808152121.cms","OilPrice Main": "https://oilprice.com/rss/main","OilPrice Energy": "https://oilprice.com/rss/energy-news","Kitco News": "https://www.kitco.com/rss/KitcoNews.xml","Kitco Gold": "https://www.kitco.com/rss/gold.xml","Investing Commodity": "https://www.investing.com/rss/commodities_Feed.rss","Investing Gold": "https://www.investing.com/rss/commodities_Gold.rss","Investing Oil": "https://www.investing.com/rss/commodities_Oil.rss","GoldPrice": "https://goldprice.org/rss","ET Energy": "https://economictimes.indiatimes.com/industry/energy/rssfeeds/1783664934.cms","LiveMint Commodity": "https://www.livemint.com/rss/commodities","Commodity Online": "https://www.commodityonline.com/rss/","MCX India": "https://www.mcxindia.com/rss/mcx-news.xml","Investing Silver": "https://www.investing.com/rss/commodities_Silver.rss",},"₿ CRYPTO (10)": {"CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/","CoinDesk Markets": "https://www.coindesk.com/arc/outboundfeeds/rss/?collection=markets","CoinTelegraph": "https://cointelegraph.com/rss","CoinTelegraph Markets": "https://cointelegraph.com/rss-feeds/markets","Decrypt": "https://decrypt.co/feed","Investing Crypto": "https://www.investing.com/rss/news_301.rss","Bitcoin.com": "https://news.bitcoin.com/feed/","NewsBTC": "https://www.newsbtc.com/feed/","CryptoPanic": "https://cryptopanic.com/news/rss/","CoinJournal": "https://coinjournal.net/feed/",},"🏦 RBI / INDIA ECO (10)": {"RBI Press": "https://www.rbi.org.in/rss/RBI_PressRelease.xml","RBI Speech": "https://www.rbi.org.in/rss/RBI_Speeches.xml","RBI Notification": "https://www.rbi.org.in/rss/RBI_Notification.xml","RBI Circular": "https://www.rbi.org.in/rss/RBI_Circulars.xml","ET Economy": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms","ET RBI": "https://economictimes.indiatimes.com/topic/rbi/rss","LiveMint Economy": "https://www.livemint.com/rss/economy","BS Economy Policy": "https://www.business-standard.com/rss/economy-policy-105.rss","FE Economy 2": "https://www.financialexpress.com/economy/feed/","NDTV Eco": "https://www.ndtvprofit.com/rss/economy",},"🏛️ FED / US ECO (10)": {"Fed All Press": "https://www.federalreserve.gov/feeds/press_all.xml","Fed Monetary": "https://www.federalreserve.gov/feeds/press_monetary.xml","Fed Financial": "https://www.federalreserve.gov/feeds/press_financial.xml","Fed Supervision": "https://www.federalreserve.gov/feeds/press_supervision.xml","Fed Other": "https://www.federalreserve.gov/feeds/other.xml","US Treasury Press": "https://home.treasury.gov/rss/press-releases","ET Fed": "https://economictimes.indiatimes.com/topic/federal-reserve/rss","Investing US Eco": "https://www.investing.com/rss/news_14.rss","BLS News": "https://www.bls.gov/feed/bls_news.xml","BEA News": "https://www.bea.gov/rss/rss.xml",}}

def scan_fno():
    up, down = [], []; last_date = None
    bar = st.progress(0, text="Scanning FNO...")
    for i, sym in enumerate(FNO):
        try:
            d = yf.Ticker(f"{sym}.NS").history(period="5d", auto_adjust=True)
            if d.empty: continue
            last_date = d.index[-1].strftime("%d-%m-%Y")
            o,h,l,c = float(d['Open'].iloc[-1]), float(d['High'].iloc[-1]), float(d['Low'].iloc[-1]), float(d['Close'].iloc[-1])
            if l==0 or h==0: continue
            lu = (c-l)/l*100; hd = (h-c)/h*100
            if lu >= 1: up.append({"SYM":sym,"OPEN":round(o,2),"LOW":round(l,2),"LTP":round(c,2),"LOW_UP %":round(lu,2),"DATE":d.index[-1].strftime("%d-%m")})
            if hd >= 1: down.append({"SYM":sym,"OPEN":round(o,2),"HIGH":round(h,2),"LTP":round(c,2),"HIGH_DOWN %":round(hd,2),"DATE":d.index[-1].strftime("%d-%m")})
        except: pass
        bar.progress((i+1)/len(FNO))
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
                    lst.append({"TIME":dt.strftime("%H:%M"),"SRC":src,"TITLE":e.title,"LINK":e.link,"DT":dt})
            except: continue
        all_news[cat]=sorted(lst,key=lambda x:x['DT'],reverse=True)
    return all_news

with st.sidebar:
    st.markdown("## 🔷 TradingPro")
    menu = st.radio("Navigation", ["📈 FNO - HALF CHART SIDE-BY-SIDE","📊 Sector Heatmap","📰 NEWS - 87 Sources"], label_visibility="collapsed")
    st.caption(f"📅 {datetime.now(IST).strftime('%d %b %Y %I:%M %p')} IST")

if menu == "📈 FNO - HALF CHART SIDE-BY-SIDE":
    st.title("📈 FNO - Kal ka data + Live")
    col_a, col_b = st.columns([1,1])
    with col_a:
        auto_on = st.checkbox("🔁 Auto Scan ON (Har 5 min)", value=False)
    with col_b:
        if st.button("🚀 SCAN NOW", type="primary", use_container_width=True):
            df_u, df_d, last_dt = scan_fno()
            st.session_state['df_u'] = df_u
            st.session_state['df_d'] = df_d
            st.session_state['last_dt'] = last_dt
            st.session_state['last_scan_time'] = datetime.now(IST)
    if auto_on:
        now_tmp = datetime.now(IST)
        last_scan = st.session_state.get('last_scan_time')
        if last_scan is None or (now_tmp - last_scan).total_seconds() >= 300:
            df_u, df_d, last_dt = scan_fno()
            st.session_state['df_u'] = df_u
            st.session_state['df_d'] = df_d
            st.session_state['last_dt'] = last_dt
            st.session_state['last_scan_time'] = now_tmp
            st.toast(f"Auto Scan: {now_tmp.strftime('%H:%M:%S')}")
    if 'df_u' in st.session_state:
        df_u = st.session_state['df_u']
        df_d = st.session_state['df_d']
        last_dt = st.session_state.get('last_dt','')
        last_scan_time = st.session_state.get('last_scan_time')
        scan_time_str = last_scan_time.strftime('%H:%M:%S') if last_scan_time else ''
        st.info(f"Last Date: {last_dt} | Last Scan: {scan_time_str} | Mode: {'Auto 5min ON' if auto_on else 'Manual'}")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='green-box'>↗ LOW se 1% UP: {len(df_u)}</div>", unsafe_allow_html=True)
            st.dataframe(df_u.sort_values("LOW_UP %", ascending=False).reset_index(drop=True) if not df_u.empty else df_u, use_container_width=True, height=500, hide_index=True)
        with c2:
            st.markdown(f"<div class='red-box'>↘ HIGH se 1% DOWN: {len(df_d)}</div>", unsafe_allow_html=True)
            st.dataframe(df_d.sort_values("HIGH_DOWN %", ascending=False).reset_index(drop=True) if not df_d.empty else df_d, use_container_width=True, height=500, hide_index=True)
        st.divider()
        st.subheader("📊 Charts - Kal ka dikhega, Market khulega to Live")
        up_syms = df_u.sort_values("LOW_UP %", ascending=False)['SYM'].tolist() if not df_u.empty else []
        down_syms = df_d.sort_values("HIGH_DOWN %", ascending=False)['SYM'].tolist() if not df_d.empty else []
        max_len = max(len(up_syms), len(down_syms))
        for i in range(max_len):
            cl, cr = st.columns(2)
            if i < len(up_syms):
                sym = up_syms[i]
                pct = df_u[df_u['SYM']==sym]['LOW_UP %'].values[0]
                with cl:
                    with st.container(border=True):
                        st.markdown(f"**↗ {sym} - LOW se {pct}% UP**")
                        draw_half_chart(sym, f"LOW+{pct}%")
            if i < len(down_syms):
                sym = down_syms[i]
                pct = df_d[df_d['SYM']==sym]['HIGH_DOWN %'].values[0]
                with cr:
                    with st.container(border=True):
                        st.markdown(f"**↘ {sym} - HIGH se {pct}% DOWN**")
                        draw_half_chart(sym, f"HIGH-{pct}%")

elif menu == "📊 Sector Heatmap":
    st.title("📊 Sector Heatmap")
    if st.button("🔥 GENERATE", type="primary", use_container_width=True):
        heat_data=[]
        bar=st.progress(0, text="Fetching...")
        for i,sym in enumerate(FNO):
            try:
                d = yf.Ticker(f"{sym}.NS").history(period="5d", auto_adjust=True)
                if d.empty or len(d)<2:
                    d = yf.Ticker(f"{sym}.NS").history(period="1mo", auto_adjust=True)
                if d.empty or len(d)<2:
                    continue
                c = float(d['Close'].iloc[-1]); prev = float(d['Close'].iloc[-2])
                if pd.isna(c) or pd.isna(prev) or prev==0:
                    continue
                ch = (c-prev)/prev*100
                if pd.isna(ch):
                    continue
                heat_data.append({"SYM":sym,"SECTOR":SECTOR_MAP_FULL.get(sym,"Others"),"CHANGE":round(float(ch),2),"LTP":round(float(c),2),"SIZE":1})
            except:
                continue
            bar.progress((i+1)/len(FNO))
        bar.empty()
        if heat_data:
            st.session_state['df_h']=pd.DataFrame(heat_data).dropna()
            st.session_state['selected_sector']=None
            st.toast(f"{len(heat_data)} stocks loaded")

    if 'df_h' in st.session_state and not st.session_state['df_h'].empty:
        df_h = st.session_state['df_h'].dropna(subset=['CHANGE','LTP'])
        df_h = df_h[pd.notna(df_h['CHANGE']) & pd.notna(df_h['LTP'])]
        st.markdown("### 📈 Sector Performance")
        sec_perf = df_h.groupby('SECTOR')['CHANGE'].mean().reset_index().sort_values('CHANGE',ascending=False)
        sec_perf['COLOR_LABEL'] = sec_perf['CHANGE'].apply(lambda x: 'Profit' if x >=0 else 'Loss')
        fig_bar = px.bar(sec_perf, x='SECTOR', y='CHANGE', color='COLOR_LABEL', color_discrete_map={'Profit':'#00e676', 'Loss':'#ff1744'}, text=sec_perf['CHANGE'].apply(lambda x: f"{x:+.2f}%"))
        fig_bar.update_traces(marker=dict(cornerradius=8), textposition='outside', textfont=dict(size=13, color='white'))
        fig_bar.update_layout(paper_bgcolor="#0e121b", plot_bgcolor="#0e121b", font=dict(color="white"), height=550, showlegend=False, xaxis=dict(tickangle=-30, gridcolor='#1e2a3e'), yaxis=dict(gridcolor='#1e2a3e'))
        st.markdown("👇 Sector bar pe click karo")
        clicked = plotly_events(fig_bar, click_event=True, hover_event=False, override_height=550, override_width="100%")
        if clicked:
            st.session_state['selected_sector'] = clicked[0]['x']
        if st.session_state.get('selected_sector'):
            sel = st.session_state['selected_sector']
            sdf_all = df_h[df_h['SECTOR']==sel].dropna()
            if not sdf_all.empty:
                sel_avg = sdf_all['CHANGE'].mean()
                if sel_avg >= 0:
                    sdf = sdf_all.sort_values('CHANGE', ascending=False).reset_index(drop=True)
                    st.success(f"👉 {sel} GREEN ({sel_avg:+.2f}%) - Gaining High to Low: {len(sdf)}")
                else:
                    sdf = sdf_all.sort_values('CHANGE', ascending=True).reset_index(drop=True)
                    st.error(f"👉 {sel} RED ({sel_avg:+.2f}%) - Most Loss First: {len(sdf)}")
                st.dataframe(sdf[['SYM','CHANGE','LTP']], use_container_width=True, height=400, hide_index=True)
            if st.button("❌ Clear Selection"):
                st.session_state['selected_sector'] = None
                st.rerun()
        st.divider()
        st.subheader("🔥 Treemap Heatmap")
        try:
            df_t = df_h.copy().dropna(subset=['SYM','SECTOR','CHANGE','LTP','SIZE'])
            df_t['LABEL'] = df_t['SYM'] + '<br>' + df_t['CHANGE'].astype(str) + '%<br>₹' + df_t['LTP'].astype(str)
            fig_tree = px.treemap(df_t, path=[px.Constant("NSE FNO"), 'SECTOR', 'LABEL'], values='SIZE', color='CHANGE', color_continuous_scale=[(0, "#d50000"), (0.5, "#1e222d"), (1, "#00c853")], range_color=[-3, 3])
            fig_tree.update_traces(textinfo="label", textfont=dict(size=12, color="white"))
            fig_tree.update_layout(margin=dict(t=10,l=10,r=10,b=10), paper_bgcolor="#0e121b", height=800)
            st.plotly_chart(fig_tree, use_container_width=True)
        except Exception as e:
            st.warning(f"Treemap skip: {e}")

elif menu == "📰 NEWS - 87 Sources":
    st.title("📰 LIVE NEWS - 87 Sources")
    if st.button("🔄 REFRESH NEWS", type="primary"):
        st.cache_data.clear()
        st.rerun()
    news_data = fetch_news()
    total = sum(len(v) for v in news_data.values())
    st.success(f"Live • {total} headlines • {datetime.now(IST).strftime('%H:%M:%S')} IST")
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
                        for n in lst[:20]:
                            st.caption(f"{n['TIME']} | {n['SRC']}")
                            st.markdown(f"[{n['TITLE']}]({n['LINK']})")
                            st.divider()

now = datetime.now(IST)
is_market_hours = 9 <= now.hour < 16 and now.weekday() < 5 and not (now.hour == 15 and now.minute > 30)
if is_market_hours:
    next_min = ((now.minute // 5) + 1) * 5
    next_time = now.replace(second=0, microsecond=0)
    if next_min >= 60:
        next_time = next_time.replace(minute=0) + timedelta(hours=1)
    else:
        next_time = next_time.replace(minute=next_min)
    remaining = (next_time - now).total_seconds()
    st.markdown(f"<p style='text-align:center;color:#00d084;font-size:13px;margin-top:25px'>⏰ Next: {next_time.strftime('%H:%M')} ({int(remaining)}s) | Last: {now.strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    if st.session_state.get('df_u') is not None:
        time.sleep(max(1, min(remaining, 30)))
        st.rerun()
else:
    st.markdown(f"<p style='text-align:center;color:gray;font-size:12px;margin-top:20px'>Market Closed - Kal ka data dikh raha hai | {now.strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
