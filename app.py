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
from streamlit_plotly_events import plotly_events
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

st.set_page_config(page_title="TradingPro FINAL - HALF CHART", layout="wide", initial_sidebar_state="expanded")
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
        df = pd.DataFrame()
        try:
            df_1m = yf.Ticker(f"{symbol}.NS").history(period="1d", interval="1m", auto_adjust=True)
            if not df_1m.empty and len(df_1m) > 10:
                df = df_1m.resample('5min').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
        except: pass
        if df.empty or len(df) < 10:
            try: df = yf.Ticker(f"{symbol}.NS").history(period="2d", interval="5m", auto_adjust=True)
            except: pass
        if df.empty or len(df) < 10:
            df = yf.Ticker(f"{symbol}.NS").history(period="5d", interval="15m", auto_adjust=True)
        if df.empty:
            st.error(f"{symbol} no data"); return
        df = df.tail(80)
        # HALF SIZE - pehle 22,12 tha, ab 11,5.5
        fig, ax = plt.subplots(figsize=(11, 5.5), facecolor='#0e121b')
        ax.set_facecolor('#0e121b')
        for i in range(len(df)):
            o,h,l,c = float(df['Open'].iloc[i]), float(df['High'].iloc[i]), float(df['Low'].iloc[i]), float(df['Close'].iloc[i])
            x = mdates.date2num(df.index[i])
            col = '#00d084' if c >= o else '#ff4d4d'
            ax.plot([x,x],[l,h], color=col, linewidth=1.8)
            bh = abs(c-o)
            if bh < (h-l)*0.1: bh = (h-l)*0.1
            rect = Rectangle((x-0.0007, min(o,c)), 0.0014, bh, facecolor=col, edgecolor=col)
            ax.add_patch(rect)
        ax.set_title(f"{symbol} {pct_info} - 5MIN", color='#00d084', fontsize=14, fontweight='bold', pad=10)
        ax.tick_params(colors='#aaa', labelsize=9)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        for spine in ax.spines.values(): spine.set_color('#1e2a3e')
        ax.grid(True, color='#1e2a3e', alpha=0.3)
        plt.xticks(rotation=15)
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
    menu = st.radio("Navigation", ["📈 FNO - HALF CHART SIDE-BY-SIDE","📋 CUSTOM LIST + HALF CHARTS","📊 Sector Heatmap","📰 NEWS - 87 Sources"], label_visibility="collapsed")
    st.caption(f"📅 {datetime.now(IST).strftime('%d %b %Y %I:%M %p')} IST")

if menu == "📈 FNO - HALF CHART SIDE-BY-SIDE":
    st.title("📈 FNO - Aadhe Charts - Side by Side")
    if st.button("🚀 SCAN FNO", type="primary", use_container_width=True):
        df_u, df_d, last_dt = scan_fno()
        st.info(f"Last Date: {last_dt} | BOX hata diya, niche aadhe size ke charts dono taraf")

        # Upar sirf table - BOX nahi
        c1,c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='green-box'>↗ LOW se 1% UP: {len(df_u)}</div>", unsafe_allow_html=True)
            st.dataframe(df_u.sort_values("LOW_UP %", ascending=False) if not df_u.empty else df_u, use_container_width=True, height=400)
        with c2:
            st.markdown(f"<div class='red-box'>↘ HIGH se 1% DOWN: {len(df_d)}</div>", unsafe_allow_html=True)
            st.dataframe(df_d.sort_values("HIGH_DOWN %", ascending=False) if not df_d.empty else df_d, use_container_width=True, height=400)

        st.divider()
        st.subheader("📊 Aadhe size charts - Left me LOW UP, Right me HIGH DOWN")

        # Dono ka chart ek saath
        col_left, col_right = st.columns(2)
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

elif menu == "📋 CUSTOM LIST + HALF CHARTS":
    st.title("📋 CUSTOM LIST - Half Charts")
    user_input = st.text_area("Stocks (comma se)", value="PATANJALI, MANKIND, LICHSGFIN, RELIANCE, TCS", height=100)
    if st.button("🔥 SHOW HALF CHARTS", type="primary", use_container_width=True):
        symbols = [s.strip().upper().replace(".NS","") for s in user_input.replace("\n",",").split(",") if s.strip()!=""]
        symbols = list(dict.fromkeys(symbols))
        cols = st.columns(2)
        for idx, sym in enumerate(symbols):
            with cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"**📈 {sym}**")
                    draw_half_chart(sym)

elif menu == "📊 Sector Heatmap":
    st.title("📊 Sector Heatmap")
    if st.button("🔥 GENERATE", type="primary", use_container_width=True):
        heat_data=[]
        bar=st.progress(0)
        for i,sym in enumerate(FNO):
            try:
                d=yf.Ticker(f"{sym}.NS").history(period="5d", auto_adjust=True)
                if d.empty or len(d)<2: continue
                c=float(d['Close'].iloc[-1]); prev=float(d['Close'].iloc[-2])
                ch=(c-prev)/prev*100
                heat_data.append({"SYM":sym,"SECTOR":SECTOR_MAP_FULL.get(sym,"Others"),"CHANGE":round(ch,2),"LTP":round(c,2),"SIZE":1})
            except: continue
            bar.progress((i+1)/len(FNO))
        bar.empty()
        st.session_state['df_h']=pd.DataFrame(heat_data)
    if 'df_h' in st.session_state and not st.session_state['df_h'].empty:
        df_h=st.session_state['df_h']
        sec_perf=df_h.groupby('SECTOR')['CHANGE'].mean().reset_index().sort_values('CHANGE',ascending=False)
        fig_bar=px.bar(sec_perf,x='SECTOR',y='CHANGE',color='CHANGE',color_continuous_scale=[(0,"#d50000"),(0.5,"#1e222d"),(1,"#00c853")],range_color=[-3,3])
        fig_bar.update_layout(paper_bgcolor="#0e121b",plot_bgcolor="#0e121b",font=dict(color="white"),height=500)
        st.plotly_chart(fig_bar, use_container_width=True)
        fig_tree = px.treemap(df_h, path=[px.Constant("NSE FNO"), 'SECTOR', 'SYM'], values='SIZE', color='CHANGE', color_continuous_scale=[(0, "#d50000"), (0.5, "#1e222d"), (1, "#00c853")], range_color=[-3, 3])
        fig_tree.update_layout(margin=dict(t=10,l=10,r=10,b=10), paper_bgcolor="#0e121b", height=700)
        st.plotly_chart(fig_tree, use_container_width=True)

elif menu == "📰 NEWS - 87 Sources":
    st.title("📰 LIVE NEWS - 87 Sources")
    if st.button("🔄 REFRESH NEWS", type="primary"): st.cache_data.clear()
    news_data = fetch_news(); total = sum(len(v) for v in news_data.values())
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
    time.sleep(120); st.rerun()
