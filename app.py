import streamlit as st
import os, tempfile, json
import yfinance as yf
yf.set_tz_cache_location(os.path.join(tempfile.gettempdir(), "yf_tz_cache"))
import pandas as pd
import feedparser
from datetime import datetime, date
import pytz
import plotly.express as px
from streamlit_plotly_events import plotly_events
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import math
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="TradingPro SAME DESIGN + Auto 5min", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

now_ist = datetime.now(IST)
slot_min = (math.floor(now_ist.minute / 5) + 1) * 5
nh, nm = now_ist.hour, slot_min
if nm >= 60:
    nm = 0; nh += 1
    if nh >= 24: nh = 0
next_slot = now_ist.replace(hour=nh, minute=nm, second=0, microsecond=0)
ms_to_next = int((next_slot - now_ist).total_seconds() * 1000)
ms_to_next = max(15000, ms_to_next)

st.markdown("""
<style>
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

FNO = ["360ONE","ABB","APLAPOLLO","AUBANK","ADANIENSOL","ADANIENT","ADANIGREEN","ADANIPORTS","ADANIPOWER","ABCAPITAL","ALKEM","AMBER","AMBUJACEM","ANGELONE","APOLLOHOSP","ASHOKLEY","ASIANPAINT","ASTRAL","ATHERENERG","AUROPHARMA","DMART","AXISBANK","BSE","BAJAJ-AUTO","BAJFINANCE","BAJAJFINSV","BAJAJHLDNG","BANDHANBNK","BANKBARODA","BANKINDIA","MAHABANK","BDL","BEL","BHARATFORG","BHEL","BPCL","BHARTIARTL","BIOCON","BLUESTARCO","BOSCHLTD","BRITANNIA","CGPOWER","CANBK","CDSL","CHOLAFIN","CIPLA","COALINDIA","COCHINSHIP","COFORGE","COLPAL","CAMS","CONCOR","CROMPTON","CUMMINSIND","DLF","DABUR","DELHIVERY","DIVISLAB","DIXON","DRREDDY","ETERNAL","EICHERMOT","FORCEMOT","NYKAA","FORTIS","GAIL","GVT&D","GMRAIRPORT","GLENMARK","GODFRYPHLP","GODREJCP","GODREJPROP","GRASIM","HCLTECH","HDFCAMC","HDFCBANK","HDFCLIFE","HAVELLS","HEROMOTOCO","HINDALCO","HAL","HINDPETRO","HINDUNILVR","HINDZINC","POWERINDIA","HYUNDAI","ICICIBANK","ICICIGI","ICICIPRULI","IDFCFIRSTB","ITC","INDIANB","IEX","IOC","IRFC","IREDA","INDUSTOWER","INDUSINDBK","NAUKRI","INFY","INOXWIND","INDIGO","JINDALSTEL","JSWENERGY","JSWSTEEL","JIOFIN","JUBLFOOD","KEI","KPITTECH","KALYANKJIL","KAYNES","KFINTECH","KOTAKBANK","LTF","LICHSGFIN","LTM","LT","LAURUSLABS","LICI","LODHA","LUPIN","M&M","MANAPPURAM","MANKIND","MARICO","MARUTI","MFSL","MAXHEALTH","MAZDOCK","MOTILALOFS","MPHASIS","MCX","MUTHOOTFIN","NBCC","NHPC","NMDC","NTPC","NATIONALUM","NESTLEIND","NAM-INDIA","OBEROIRLTY","ONGC","OIL","PAYTM","OFSS","POLICYBZR","PGEL","PIIND","PNBHOUSING","PAGEIND","PATANJALI","PERSISTENT","PETRONET","PIDILITIND","POLYCAB","PFC","POWERGRID","PREMIERENE","PRESTIGE","PNB","RBLBANK","RECLTD","RADICO","RVNL","RELIANCE","SAGILITY","SBICARD","SBILIFE","SHREECEM","SRF","MOTHERSON","SHRIRAMFIN","SIEMENS","SOLARINDS","SONACOMS","SBIN","SAIL","SUNPHARMA","SUPREMEIND","SUZLON","SWIGGY","TATACONSUM","TVSMOTOR","TCS","TATAELXSI","TMPV","TATAPOWER","TATASTEEL","TECHM","FEDERALBNK","INDHOTEL","PHOENIXLTD","TITAN","TORNTPHARM","TRENT","TIINDIA","UNOMINDA","UPL","ULTRACEMCO","UNIONBANK","UNITDSPR","VBL","VEDL","VMM","IDEA","VOLTAS","WAAREEENER","WIPRO","YESBANK","ZYDUSLIFE"]

SECTOR_MAP_FULL = {
"BRITANNIA":"FMCG","GODREJCP":"FMCG","NESTLEIND":"FMCG","DABUR":"FMCG","HINDUNILVR":"FMCG","PATANJALI":"FMCG","COLPAL":"FMCG","MARICO":"FMCG",
"INOXWIND":"General Industrials","SUPREMEIND":"General Industrials","SOLARINDS":"General Industrials","POWERINDIA":"General Industrials","ASTRAL":"General Industrials","CGPOWER":"General Industrials","MAZDOCK":"General Industrials","SIEMENS":"General Industrials","HAL":"General Industrials","BHARATFORG":"General Industrials","BEL":"General Industrials","SUZLON":"General Industrials","BDL":"General Industrials","ABB":"General Industrials","BHEL":"General Industrials","CUMMINSIND":"General Industrials","GVT&D":"General Industrials",
"GODREJPROP":"Realty","DLF":"Realty","PHOENIXLTD":"Realty","OBEROIRLTY":"Realty","LODHA":"Realty","PRESTIGE":"Realty",
"ADANIENT":"Commercial Services & Supplies",
"COCHINSHIP":"Transportation","ADANIPORTS":"Transportation","INDIGO":"Transportation","CONCOR":"Transportation","DELHIVERY":"Transportation",
"RVNL":"Cement and Construction","NBCC":"Cement and Construction","AMBUJACEM":"Cement and Construction","GRASIM":"Cement and Construction","ULTRACEMCO":"Cement and Construction","GMRAIRPORT":"Cement and Construction","SHREECEM":"Cement and Construction","LT":"Cement and Construction",
"IREDA":"Banking and Finance","MFSL":"Banking and Finance","MANAPPURAM":"Banking and Finance","MAHABANK":"Banking and Finance","AXISBANK":"Banking and Finance","MOTILALOFS":"Banking and Finance","360ONE":"Banking and Finance","RECLTD":"Banking and Finance","CDSL":"Banking and Finance","IEX":"Banking and Finance","UNIONBANK":"Banking and Finance","AUBANK":"Banking and Finance","KFINTECH":"Banking and Finance","HDFCBANK":"Banking and Finance","BANDHANBNK":"Banking and Finance","LICI":"Banking and Finance","JIOFIN":"Banking and Finance","FEDERALBNK":"Banking and Finance","INDIANB":"Banking and Finance","SHRIRAMFIN":"Banking and Finance","IDFCFIRSTB":"Banking and Finance","BANKBARODA":"Banking and Finance","LTF":"Banking and Finance","RBLBANK":"Banking and Finance","BANKINDIA":"Banking and Finance","SBICARD":"Banking and Finance","BAJFINANCE":"Banking and Finance","KOTAKBANK":"Banking and Finance","HDFCLIFE":"Banking and Finance","ICICIPRULI":"Banking and Finance","HDFCAMC":"Banking and Finance","LICHSGFIN":"Banking and Finance","SBIN":"Banking and Finance","MUTHOOTFIN":"Banking and Finance","PFC":"Banking and Finance","NAM-INDIA":"Banking and Finance","PNBHOUSING":"Banking and Finance","YESBANK":"Banking and Finance","BSE":"Banking and Finance","IRFC":"Banking and Finance","ICICIGI":"Banking and Finance","PNB":"Banking and Finance","CANBK":"Banking and Finance","ICICIBANK":"Banking and Finance","SBILIFE":"Banking and Finance","INDUSINDBK":"Banking and Finance","ANGELONE":"Banking and Finance","CHOLAFIN":"Banking and Finance","MCX":"Banking and Finance",
"HYUNDAI":"Automobiles & Auto Components","SONACOMS":"Automobiles & Auto Components","FORCEMOT":"Automobiles & Auto Components","M&M":"Automobiles & Auto Components","BOSCHLTD":"Automobiles & Auto Components","MARUTI":"Automobiles & Auto Components","ASHOKLEY":"Automobiles & Auto Components","BAJAJ-AUTO":"Automobiles & Auto Components","HEROMOTOCO":"Automobiles & Auto Components","TVSMOTOR":"Automobiles & Auto Components","TIINDIA":"Automobiles & Auto Components","EICHERMOT":"Automobiles & Auto Components","UNOMINDA":"Automobiles & Auto Components","MOTHERSON":"Automobiles & Auto Components","ATHERENERG":"Automobiles & Auto Components","TMPV":"Automobiles & Auto Components",
"KAYNES":"Consumer Durables","BLUESTARCO":"Consumer Durables","DIXON":"Consumer Durables","ASIANPAINT":"Consumer Durables","WAAREEENER":"Consumer Durables","PGEL":"Consumer Durables","VOLTAS":"Consumer Durables","HAVELLS":"Consumer Durables","KEI":"Consumer Durables","POLYCAB":"Consumer Durables","AMBER":"Consumer Durables","PREMIERENE":"Consumer Durables","CROMPTON":"Consumer Durables",
"ADANIPOWER":"Utilities","ADANIGREEN":"Utilities","TATAPOWER":"Utilities","POWERGRID":"Utilities","JSWENERGY":"Utilities","ADANIENSOL":"Utilities","NHPC":"Utilities","NTPC":"Utilities","GAIL":"Utilities",
"PAGEIND":"Textiles Apparels & Accessories","TITAN":"Textiles Apparels & Accessories","KALYANKJIL":"Textiles Apparels & Accessories",
"APLAPOLLO":"Metals & Mining","NATIONALUM":"Metals & Mining","COALINDIA":"Metals & Mining","VEDL":"Metals & Mining","TATASTEEL":"Metals & Mining","JINDALSTEL":"Metals & Mining","HINDZINC":"Metals & Mining","JSWSTEEL":"Metals & Mining","HINDALCO":"Metals & Mining","NMDC":"Metals & Mining","SAIL":"Metals & Mining",
"ZYDUSLIFE":"Pharmaceuticals & Biotechnology","TORNTPHARM":"Pharmaceuticals & Biotechnology","CIPLA":"Pharmaceuticals & Biotechnology","MANKIND":"Pharmaceuticals & Biotechnology","AUROPHARMA":"Pharmaceuticals & Biotechnology","SUNPHARMA":"Pharmaceuticals & Biotechnology","DRREDDY":"Pharmaceuticals & Biotechnology","DIVISLAB":"Pharmaceuticals & Biotechnology","BIOCON":"Pharmaceuticals & Biotechnology","LUPIN":"Pharmaceuticals & Biotechnology","ALKEM":"Pharmaceuticals & Biotechnology","GLENMARK":"Pharmaceuticals & Biotechnology","LAURUSLABS":"Pharmaceuticals & Biotechnology",
"BAJAJFINSV":"Diversified","BAJAJHLDNG":"Diversified","ABCAPITAL":"Diversified",
"HCLTECH":"Software & Services","PERSISTENT":"Software & Services","LTM":"Software & Services","TATAELXSI":"Software & Services","TCS":"Software & Services","KPITTECH":"Software & Services","TECHM":"Software & Services","WIPRO":"Software & Services","COFORGE":"Software & Services","CAMS":"Software & Services","INFY":"Software & Services","MPHASIS":"Software & Services","OFSS":"Software & Services","PAYTM":"Software & Services","POLICYBZR":"Software & Services",
"IDEA":"Telecom Services","BHARTIARTL":"Telecom Services","INDUSTOWER":"Telecom Services",
"HINDPETRO":"Oil & Gas","BPCL":"Oil & Gas","IOC":"Oil & Gas","PETRONET":"Oil & Gas","RELIANCE":"Oil & Gas","ONGC":"Oil & Gas","OIL":"Oil & Gas",
"RADICO":"Food, Beverages & Tobacco","GODFRYPHLP":"Food, Beverages & Tobacco","VBL":"Food, Beverages & Tobacco","UNITDSPR":"Food, Beverages & Tobacco","ITC":"Food, Beverages & Tobacco","TATACONSUM":"Food, Beverages & Tobacco",
"JUBLFOOD":"Hotels Restaurants & Tourism","INDHOTEL":"Hotels Restaurants & Tourism",
"APOLLOHOSP":"Healthcare","SAGILITY":"Healthcare","MAXHEALTH":"Healthcare","FORTIS":"Healthcare",
"NAUKRI":"Retailing","DMART":"Retailing","NYKAA":"Retailing","TRENT":"Retailing","ETERNAL":"Retailing","VMM":"Retailing","SWIGGY":"Retailing",
"PIIND":"Chemicals & Petrochemicals","UPL":"Chemicals & Petrochemicals","PIDILITIND":"Chemicals & Petrochemicals","SRF":"Chemicals & Petrochemicals",
}

RSS_FEEDS = {
    "INDIA MARKET (22)": {"MoneyControl Top": "https://www.moneycontrol.com/rss/MCtopnews.xml","MoneyControl Market": "https://www.moneycontrol.com/rss/marketreports.xml","MoneyControl Economy": "https://www.moneycontrol.com/rss/economy.xml","MoneyControl MF": "https://www.moneycontrol.com/rss/mfnews.xml","ET Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms","ET Stocks": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms","ET MF": "https://economictimes.indiatimes.com/mf/rssfeeds/20320306.cms","ET Economy": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms","LiveMint Markets": "https://www.livemint.com/rss/markets","LiveMint Companies": "https://www.livemint.com/rss/companies","LiveMint Money": "https://www.livemint.com/rss/money","CNBC TV18 All": "https://www.cnbctv18.com/commonfeeds/v1/cnbcv18all.xml","CNBC TV18 Market": "https://www.cnbctv18.com/commonfeeds/v1/cnbcv18market.xml","CNBC TV18 Economy": "https://www.cnbctv18.com/commonfeeds/v1/cnbcv18economy.xml","NDTV Profit": "https://www.ndtvprofit.com/rss","NDTV Profit Market": "https://www.ndtvprofit.com/rss/markets","BS Markets": "https://www.business-standard.com/rss/markets-106.rss","BS Economy": "https://www.business-standard.com/rss/economy-103.rss","Zee Business": "https://www.zeebiz.com/rss/markets.xml","Financial Express Market": "https://www.financialexpress.com/market/rss","Financial Express Economy": "https://www.financialexpress.com/economy/rss","Hindu BusinessLine Market": "https://www.thehindubusinessline.com/markets/feeder/default.rss"},
    "GLOBAL MARKET (20)": {"Reuters Business": "http://feeds.reuters.com/reuters/businessNews","Reuters Markets": "http://feeds.reuters.com/reuters/marketsNews","CNBC Top": "https://www.cnbc.com/id/100003114/device/rss/rss.html","CNBC World Market": "https://www.cnbc.com/id/100727362/device/rss/rss.html","CNBC Economy": "https://www.cnbc.com/id/10000113/device/rss/rss.html","Yahoo Finance": "https://finance.yahoo.com/news/rssindex","Yahoo World": "https://finance.yahoo.com/rss/topstories","BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml","BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml","FT Markets": "https://www.ft.com/markets?format=rss","WSJ Markets": "https://www.wsj.com/xml/rss/3_7031.xml","WSJ Economy": "https://www.wsj.com/xml/rss/3_7085.xml","Bloomberg Markets": "https://feeds.bloomberg.com/markets/news.rss","Bloomberg Economy": "https://feeds.bloomberg.com/economics/news.rss","MarketWatch Top": "http://feeds.marketwatch.com/marketwatch/topstories/","MarketWatch MarketPulse": "http://feeds.marketwatch.com/marketwatch/marketpulse/","Investing Global": "https://www.investing.com/rss/news_25.rss","Investing Market": "https://www.investing.com/rss/news_1065.rss","The Guardian Business": "https://www.theguardian.com/business/rss","NYT Business": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml"},
    "COMMODITY (15)": {"MC Commodity": "https://www.moneycontrol.com/rss/commodity.xml","ET Commodity": "https://economictimes.indiatimes.com/commodity/rssfeeds/1808152121.cms","OilPrice Main": "https://oilprice.com/rss/main","OilPrice News": "https://oilprice.com/rss/news","Kitco News": "https://www.kitco.com/rss/KitcoNews.xml","Kitco Gold": "https://www.kitco.com/rss/gold.xml","GoldPrice": "https://www.goldprice.org/rss","Investing Commodity": "https://www.investing.com/rss/news_1065.rss","Commodity Online": "https://www.commodityonline.com/rss/news.xml","MCX India": "https://www.mcxindia.com/rss/market-news","TradingEconomics Commodity": "https://tradingeconomics.com/rss/commodities","Barchart Commodity": "https://www.barchart.com/rss/commodities","Reuters Commodity": "http://feeds.reuters.com/reuters/commodityNews","Economic Times Gold": "https://economictimes.indiatimes.com/topic/gold/rss","LiveMint Commodity": "https://www.livemint.com/rss/commodities"},
    "CRYPTO (10)": {"CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/","CoinTelegraph": "https://cointelegraph.com/rss","CoinMarketCap News": "https://coinmarketcap.com/headlines/rss/","CryptoNews": "https://cryptonews.com/news/feed/","Decrypt": "https://decrypt.co/feed","Bitcoin.com": "https://news.bitcoin.com/feed/","NewsBTC": "https://www.newsbtc.com/feed/","CryptoPotato": "https://cryptopotato.com/feed/","CoinJournal": "https://coinjournal.net/feed/","CryptoSlate": "https://cryptoslate.com/feed/"},
    "RBI ECO (10)": {"RBI Press": "https://www.rbi.org.in/rss/RBI_PressRelease.xml","RBI Speeches": "https://www.rbi.org.in/rss/RBI_Speeches.xml","ET Economy": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms","ET Policy": "https://economictimes.indiatimes.com/news/economy/policy/rssfeeds/3879630.cms","LiveMint Economy": "https://www.livemint.com/rss/economy","Business Standard Economy": "https://www.business-standard.com/rss/economy-103.rss","Financial Express Economy": "https://www.financialexpress.com/economy/rss","MoneyControl Economy 2": "https://www.moneycontrol.com/rss/economy.xml","PIB Economy": "https://pib.gov.in/RssMain.aspx?ModId=3&Lang=1&Regid=3","Investing India Eco": "https://www.investing.com/rss/news_456.rss"},
    "FED US ECO (10)": {"Fed All Press": "https://www.federalreserve.gov/feeds/press_all.xml","Fed Monetary": "https://www.federalreserve.gov/feeds/press_monetary.xml","Investing US Eco": "https://www.investing.com/rss/news_14.rss","Investing Fed": "https://www.investing.com/rss/news_175.rss","Reuters US Economy": "http://feeds.reuters.com/reuters/USPersonalFinanceNews","Yahoo US Economy": "https://finance.yahoo.com/news/rssindex","MarketWatch Economy": "http://feeds.marketwatch.com/marketwatch/economy/","CNBC US Economy": "https://www.cnbc.com/id/10000113/device/rss/rss.html","BLS News": "https://www.bls.gov/feed/bls_news_release.rss","BEA News": "https://www.bea.gov/rss/rss.xml"}
}

today_str = str(date.today())
LOCK_FILE = f"/tmp/booster_lock_{today_str}.json"
def load_locked():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}
def save_locked(d):
    try:
        with open(LOCK_FILE, "w") as f: json.dump(d, f)
    except: pass
if 'booster_locked' not in st.session_state:
    st.session_state['booster_locked'] = load_locked()
    st.session_state['booster_date'] = today_str
if st.session_state.get('booster_date')!= today_str:
    st.session_state['booster_date'] = today_str
    st.session_state['booster_locked'] = {}

def draw_half_chart(symbol, pct_info=""):
    try:
        today_ist = datetime.now(IST).date()
        df = pd.DataFrame()
        try:
            df_1m = yf.Ticker(f"{symbol}.NS").history(period="1d", interval="1m", auto_adjust=True)
            if not df_1m.empty:
                if df_1m.index.tz is not None: df_1m.index = df_1m.index.tz_convert(IST)
                else: df_1m.index = df_1m.index.tz_localize('UTC').tz_convert(IST)
                df_1m = df_1m[df_1m.index.date == today_ist]
                if len(df_1m) > 3:
                    df = df_1m.resample('5min').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
        except: pass
        if df.empty or len(df) < 3:
            try:
                df_5 = yf.Ticker(f"{symbol}.NS").history(period="5d", interval="5m", auto_adjust=True)
                if not df_5.empty:
                    if df_5.index.tz is not None: df_5.index = df_5.index.tz_convert(IST)
                    last_date = df_5.index[-1].date()
                    df_last = df_5[df_5.index.date == last_date]
                    if len(df_last) >= 2: df = df_last; today_ist = last_date
            except: pass
        if df.empty: return
        df = df.tail(80)
        fig, ax = plt.subplots(figsize=(11, 5.5), facecolor='#0e121b')
        ax.set_facecolor('#0e121b')
        FIXED = 0.002
        for i in range(len(df)):
            o=float(df['Open'].iloc[i]);h=float(df['High'].iloc[i]);l=float(df['Low'].iloc[i]);c=float(df['Close'].iloc[i])
            x=mdates.date2num(df.index[i].to_pydatetime())
            col='#00d084' if c>=o else '#ff4d4d'
            ax.plot([x,x],[l,h],color=col,linewidth=1.8)
            bh=abs(c-o)
            if bh < (h-l)*0.08: bh=(h-l)*0.08
            if bh==0: bh=(h-l)*0.1 if h!=l else 0.1
            ax.add_patch(Rectangle((x-FIXED/2,min(o,c)),FIXED,bh,facecolor=col,edgecolor=col,linewidth=0))
        ms=IST.localize(datetime.combine(today_ist,datetime.min.time().replace(hour=9,minute=15)))
        me=IST.localize(datetime.combine(today_ist,datetime.min.time().replace(hour=15,minute=30)))
        ax.set_xlim(mdates.date2num(ms),mdates.date2num(me))
        ax.set_title(f"{symbol} {pct_info}",color='#00d084',fontsize=14,fontweight='bold',pad=10)
        ax.tick_params(colors='#aaa',labelsize=9)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M',tz=IST))
        for spine in ax.spines.values(): spine.set_color('#1e2a3e')
        ax.grid(True,color='#1e2a3e',alpha=0.3)
        plt.xticks(rotation=30);plt.tight_layout()
        st.pyplot(fig,use_container_width=True);plt.close(fig)
    except Exception as e: st.error(f"{symbol}: {e}")

def scan_fno():
    up,down=[],[]
    bar=st.progress(0,text="Scanning FNO BODY...")
    for i,sym in enumerate(FNO):
        try:
            d=yf.Ticker(f"{sym}.NS").history(period="5d",auto_adjust=True)
            if d.empty: continue
            o=float(d['Open'].iloc[-1]);c=float(d['Close'].iloc[-1])
            bl=min(o,c);bh=max(o,c)
            if bl==0 or bh==0: continue
            lu=(c-bl)/bl*100;hd=(bh-c)/bh*100
            if lu>=1: up.append({"SYM":sym,"OPEN":round(o,2),"BODY_LOW":round(bl,2),"LTP":round(c,2),"LOW_UP %":round(lu,2)})
            if hd>=1: down.append({"SYM":sym,"OPEN":round(o,2),"BODY_HIGH":round(bh,2),"LTP":round(c,2),"HIGH_DOWN %":round(hd,2)})
        except: pass
        bar.progress((i+1)/len(FNO))
    bar.empty();return pd.DataFrame(up),pd.DataFrame(down)

def get_sector_perf():
    tmp=[]
    for sym in FNO:
        try:
            t=yf.Ticker(f"{sym}.NS")
            c=float(t.fast_info['last_price']); prev=float(t.fast_info['previous_close'])
            if prev==0: continue
            ch=(c-prev)/prev*100
            tmp.append({"SYM":sym,"SECTOR":SECTOR_MAP_FULL.get(sym,"Others"),"CHANGE":ch})
        except: continue
    if tmp:
        df=pd.DataFrame(tmp)
        return df.groupby('SECTOR')['CHANGE'].mean().to_dict()
    return {}

def scan_booster_fno():
    cards=[]
    sector_perf=get_sector_perf()
    bar=st.progress(0,text="Booster BODY Scanning...")
    for i,sym in enumerate(FNO):
        try:
            df=yf.Ticker(f"{sym}.NS").history(period="2d",interval="5m",auto_adjust=True)
            if df.empty or len(df)<20: bar.progress((i+1)/len(FNO));continue
            if df.index.tz is not None: df.index=df.index.tz_convert(IST)
            last_day=df.index[-1].date()
            day_df=df[df.index.date==last_day]
            if len(day_df)<10: bar.progress((i+1)/len(FNO));continue
            or_df=day_df.between_time("09:15","09:45")
            if len(or_df)<3: bar.progress((i+1)/len(FNO));continue
            or_df['BodyHigh']=or_df[['Open','Close']].max(axis=1)
            or_df['BodyLow']=or_df[['Open','Close']].min(axis=1)
            or_h=float(or_df['BodyHigh'].max());or_l=float(or_df['BodyLow'].min())
            or_range=or_h-or_l
            if or_range==0: bar.progress((i+1)/len(FNO));continue
            ltp=float(day_df['Close'].iloc[-1]);range_pct=or_range/or_l*100
            if not (0.5 < range_pct < 2.0): bar.progress((i+1)/len(FNO));continue
            is_long=ltp>or_h*1.002;is_short=ltp<or_l*0.998
            if not (is_long or is_short): bar.progress((i+1)/len(FNO));continue
            sec=SECTOR_MAP_FULL.get(sym,"Others")
            sec_avg=sector_perf.get(sec,0)
            if sec_avg>0 and not is_long: bar.progress((i+1)/len(FNO));continue
            if sec_avg<0 and not is_short: bar.progress((i+1)/len(FNO));continue
            if sec_avg==0: bar.progress((i+1)/len(FNO));continue
            # PHOTO FORMULA
            if is_long:
                entry=or_h
                sl=or_l*0.999
                t1=entry+or_range*0.40
                t2=entry+or_range*0.90
            else:
                entry=or_l
                sl=or_h*1.001
                t1=entry-or_range*0.40
                t2=entry-or_range*0.90
            cards.append({"SYM":sym,"LTP":ltp,"ENTRY":entry,"SL":sl,"T1":t1,"T2":t2,"RANGE":range_pct,"TYPE":"Long Breakout" if is_long else "Short Breakdown","SECTOR":sec,"SEC_AVG":round(sec_avg,2)})
        except: pass
        bar.progress((i+1)/len(FNO))
    bar.empty();return cards

@st.cache_data(ttl=90)
def fetch_news():
    all_news={}
    for cat,feeds in RSS_FEEDS.items():
        lst=[]
        for src,url in feeds.items():
            try:
                f=feedparser.parse(url)
                for e in f.entries[:4]:
                    dt=datetime(*e.published_parsed[:6]) if hasattr(e,'published_parsed') and e.published_parsed else datetime.now()
                    lst.append({"TIME":dt.strftime("%H:%M"),"SRC":src,"TITLE":e.title,"LINK":e.link,"DT":dt})
            except: continue
        all_news[cat]=sorted(lst,key=lambda x: x['DT'],reverse=True)
    return all_news

with st.sidebar:
    st.markdown("## TradingPro SAME DESIGN")
    menu=st.radio("Navigation",["FNO Scanner - 1%","Sector Heatmap - SAME DESIGN","Booster Scanner - FNO Only","NEWS - 87 Sources"],label_visibility="collapsed")
    st.caption(f"{datetime.now(IST).strftime('%d %b %Y %I:%M %p')} IST")
    st.info(f"Abhi: {now_ist.strftime('%H:%M:%S')} Agla auto: {next_slot.strftime('%H:%M')}")

if menu=="FNO Scanner - 1%":
    st.title("FNO BODY - LOW/HIGH 1%")
    auto_fno=st.checkbox("Auto Scan har 5 minute me (FIX 9:15,9:20,9:25)",value=False,key="auto_fno")
    if auto_fno:
        st_autorefresh(interval=ms_to_next,key="fno_autorefresh_fix")
        df_u,df_d=scan_fno();st.session_state['df_u']=df_u;st.session_state['df_d']=df_d
        st.caption(f"Last Auto Scan: {now_ist.strftime('%H:%M:%S')} | Agla: {next_slot.strftime('%H:%M')}")
    if st.button("SCAN NOW",type="primary",use_container_width=True):
        df_u,df_d=scan_fno();st.session_state['df_u']=df_u;st.session_state['df_d']=df_d
    if 'df_u' in st.session_state:
        df_u=st.session_state['df_u'];df_d=st.session_state['df_d']
        c1,c2=st.columns(2)
        with c1: st.markdown(f"### BODY LOW se UP: {len(df_u)}");st.dataframe(df_u.sort_values("LOW_UP %",ascending=False),use_container_width=True)
        with c2: st.markdown(f"### BODY HIGH se DOWN: {len(df_d)}");st.dataframe(df_d.sort_values("HIGH_DOWN %",ascending=False),use_container_width=True)
        up_syms=df_u.sort_values("LOW_UP %",ascending=False)['SYM'].tolist() if not df_u.empty else []
        down_syms=df_d.sort_values("HIGH_DOWN %",ascending=False)['SYM'].tolist() if not df_d.empty else []
        max_len=max(len(up_syms),len(down_syms))
        for i in range(max_len):
            cl,cr=st.columns(2)
            if i < len(up_syms):
                sym=up_syms[i];pct=df_u[df_u['SYM']==sym]['LOW_UP %'].values[0]
                with cl: st.markdown(f"**{sym} BODY LOW +{pct}%**");draw_half_chart(sym,f"BODY LOW +{pct}%")
            if i < len(down_syms):
                sym=down_syms[i];pct=df_d[df_d['SYM']==sym]['HIGH_DOWN %'].values[0]
                with cr: st.markdown(f"**{sym} BODY HIGH -{pct}%**");draw_half_chart(sym,f"BODY HIGH -{pct}%")

elif menu=="Sector Heatmap - SAME DESIGN":
    st.markdown("### NSE INDIA — STOCK MARKET HEATMAP")
    st.caption(f"NSE • {datetime.now(IST).strftime('%d %b %Y • %H:%M IST')} • Day Change (%) - fast_info")
    if st.button("GENERATE SAME DESIGN",type="primary",use_container_width=True):
        heat_data=[];bar=st.progress(0,text="Heatmap loading...")
        for i,sym in enumerate(FNO):
            try:
                t=yf.Ticker(f"{sym}.NS")
                try:
                    c=float(t.fast_info['last_price']); prev=float(t.fast_info['previous_close'])
                except:
                    d=t.history(period="2d",auto_adjust=False)
                    if len(d)<2: continue
                    c=float(d['Close'].iloc[-1]); prev=float(d['Close'].iloc[-2])
                if prev==0: continue
                ch=(c-prev)/prev*100
                heat_data.append({"SYM":sym,"SECTOR":SECTOR_MAP_FULL.get(sym,"Others"),"CHANGE":round(ch,2),"LTP":round(c,2),"SIZE":1})
            except: continue
            bar.progress((i+1)/len(FNO))
        bar.empty();st.session_state['df_h']=pd.DataFrame(heat_data);st.success(f"{len(heat_data)} loaded")
    if 'df_h' in st.session_state and not st.session_state['df_h'].empty:
        df_h=st.session_state['df_h']
        sec_perf=df_h.groupby('SECTOR')['CHANGE'].mean().reset_index().sort_values('CHANGE',ascending=False)
        sec_perf['LABEL']=sec_perf['CHANGE'].apply(lambda x: f"{'+' if x>=0 else ''}{x:.2f}%")
        sec_perf['COLOR']=sec_perf['CHANGE'].apply(lambda x: '#00CB53' if x>=0 else '#D50000')
        fig=px.bar(sec_perf,x='SECTOR',y='CHANGE',text='LABEL',color='COLOR',color_discrete_map={'#00CB53':'#00CB53','#D50000':'#D50000'})
        fig.update_traces(textposition='outside',textfont=dict(size=13,color='white',family='Arial Black'),marker_line_width=0)
        fig.update_layout(plot_bgcolor='#0e121b',paper_bgcolor='#0e121b',font=dict(color='white'),showlegend=False,height=450,margin=dict(t=30,b=30),yaxis=dict(gridcolor='#1e2a3e',title='Change (%)'),xaxis=dict(title=''))
        fig.add_hline(y=0,line_color='white',line_width=1)
        st.markdown("**Sector Performance - Bar pe click karo**")
        clicked=plotly_events(fig,click_event=True,hover_event=False,key="bar_same")
        selected_sector=None
        if clicked: selected_sector=clicked[0].get('x');st.success(f"Selected Sector: {selected_sector}")
        st.divider()
        df_show=df_h.copy()
        if selected_sector: df_show=df_show[df_show['SECTOR']==selected_sector]
        for sec in sorted(df_show['SECTOR'].unique()):
            sec_df=df_show[df_show['SECTOR']==sec].sort_values('CHANGE',ascending=False)
            avg=sec_df['CHANGE'].mean()
            st.markdown(f"<div class='sector-header'>🏦 {sec} • {len(sec_df)} Stocks • Avg {'+' if avg>=0 else ''}{avg:.1f}%</div>",unsafe_allow_html=True)
            cols=st.columns(5)
            for idx,(_,row) in enumerate(sec_df.iterrows()):
                bg='#00CB53' if row['CHANGE']>=0 else '#D50000'
                with cols[idx % 5]: st.markdown(f"<div class='sector-box' style='background:{bg}'>{row['SYM']}<br>{row['CHANGE']}%<br>₹{row['LTP']:,.0f}</div>",unsafe_allow_html=True)

elif menu=="Booster Scanner - FNO Only":
    st.title("Booster BODY - LONG vs SHORT + Sector Filter + CHART")
    st.caption(f"Long=Green Sector Only | Short=Red Sector Only | Date: {today_str}")
    auto_boost=st.checkbox("Auto Scan har 5 minute me (FIX 9:15,9:20,9:25)",value=False,key="auto_boost")
    def do_booster_scan():
        fresh=scan_booster_fno();locked=st.session_state['booster_locked'];cur_t=datetime.now(IST).strftime("%H:%M")
        for c in fresh:
            sym=c['SYM']
            if sym not in locked: c['SCANNER_TIME']=cur_t;locked[sym]=c
        st.session_state['booster_locked']=locked;save_locked(locked)
    if auto_boost:
        st_autorefresh(interval=ms_to_next,key="boost_autorefresh_fix");do_booster_scan()
        st.caption(f"Last Scan: {now_ist.strftime('%H:%M:%S')} | Agla: {next_slot.strftime('%H:%M')}")
    if st.button("SCAN BOOSTER - FNO BODY",type="primary",use_container_width=True): do_booster_scan()
    if st.sidebar.button("Booster Reset"):
        st.session_state['booster_locked']={}
        try: os.remove(LOCK_FILE)
        except: pass
        st.rerun()
    cards=list(st.session_state['booster_locked'].values())
    if cards:
        def sort_key(c):
            try: h,m=map(int,str(c.get('SCANNER_TIME','15:30')).split(':'));return h*60+m
            except: return 9999
        cards_sorted=sorted(cards,key=sort_key)
        long_cards=[x for x in cards_sorted if "Long" in x['TYPE']]
        short_cards=[x for x in cards_sorted if "Short" in x['TYPE']]
        st.success(f"Total: {len(cards_sorted)} | LONG (Green Sec): {len(long_cards)} | SHORT (Red Sec): {len(short_cards)}")
        cL,cS=st.columns(2)
        with cL:
            st.markdown(f"### LONG BODY - Green Sector - {len(long_cards)}")
            for c in long_cards:
                st.markdown(f"<div style='background:white;color:black;padding:12px;border-radius:12px;margin:8px 0;border-left:6px solid #00c853'><b>{c['SYM']} LONG ⏰ {c.get('SCANNER_TIME')}</b><br>Sector {c['SECTOR']} ({c.get('SEC_AVG',0)}%) | LTP {c['LTP']:.2f} ENTRY {c['ENTRY']:.2f} SL {c['SL']:.2f} T1 {c['T1']:.2f} T2 {c['T2']:.2f}</div>",unsafe_allow_html=True)
                draw_half_chart(c['SYM'],f"SCANNER {c.get('SCANNER_TIME')} {c['TYPE']}")
        with cS:
            st.markdown(f"### SHORT BODY - Red Sector - {len(short_cards)}")
            for c in short_cards:
                st.markdown(f"<div style='background:white;color:black;padding:12px;border-radius:12px;margin:8px 0;border-left:6px solid #d50000'><b>{c['SYM']} SHORT ⏰ {c.get('SCANNER_TIME')}</b><br>Sector {c['SECTOR']} ({c.get('SEC_AVG',0)}%) | LTP {c['LTP']:.2f} ENTRY {c['ENTRY']:.2f} SL {c['SL']:.2f} T1 {c['T1']:.2f} T2 {c['T2']:.2f}</div>",unsafe_allow_html=True)
                draw_half_chart(c['SYM'],f"SCANNER {c.get('SCANNER_TIME')} {c['TYPE']}")
    else: st.info("SCAN dabao")

elif menu=="NEWS - 87 Sources":
    st.title("LIVE NEWS - 87 Sources - 3 Column Black + Scroll")
    if st.button("REFRESH NEWS",type="primary"): st.cache_data.clear();st.rerun()
    news_data=fetch_news()
    c1,c2,c3=st.columns(3);cols=[c1,c2,c3];idx=0
    for cat,lst in news_data.items():
        with cols[idx%3]:
            html=f"<div class='news-wrapper'><div class='news-header'>{cat} - {datetime.now(IST).strftime('%H:%M:%S')}</div>"
            for n in lst[:15]: html+=f"<div class='news-card-black'><b>{n['TIME']} | {n['SRC']}</b><br>{n['TITLE']}<br><a href='{n['LINK']}' target='_blank'>Read More →</a></div>"
            html+="</div>";st.markdown(html,unsafe_allow_html=True)
        idx+=1
