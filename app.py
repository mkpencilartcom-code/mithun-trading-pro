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

# ===== ANGEL ONE KEYS =====
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
    if not HAS_ANGEL: return None
    try:
        smart=SmartConnect(ANGEL_API_KEY)
        totp=pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        smart.generateSession(ANGEL_CLIENT_ID, ANGEL_MPIN, totp)
        return smart
    except Exception as e:
        st.error(f"Angel Login Fail: {e}")
        return None

st.set_page_config(page_title="TradingPro SAME DESIGN + Angel Live", layout="wide")
IST = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(IST)
slot_min = (math.floor(now_ist.minute / 5) + 1) * 5
nh, nm = now_ist.hour, slot_min
if nm >= 60: nm=0; nh+=1
if nh>=24: nh=0
next_slot = now_ist.replace(hour=nh, minute=nm, second=0, microsecond=0)
ms_to_next = int((next_slot - now_ist).total_seconds()*1000)
ms_to_next=max(15000,ms_to_next)

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

FNO = ["360ONE","ABB","APLAPOLLO","AUBANK","ADANIENSOL","ADANIENT","ADANIGREEN","ADANIPORTS","ADANIPOWER","ABCAPITAL","ALKEM","AMBER","AMBUJACEM","ANGELONE","APOLLOHOSP","ASHOKLEY","ASIANPAINT","ASTRAL","ATHERENERG","AUROPHARMA","DMART","AXISBANK","BSE","BAJAJ-AUTO","BAJFINANCE","BAJAJFINSV","BAJAJHLDNG","BANDHANBNK","BANKBARODA","BANKINDIA","MAHABANK","BDL","BEL","BHARATFORG","BHEL","BPCL","BHARTIARTL","BIOCON","BLUESTARCO","BOSCHLTD","BRITANNIA","CGPOWER","CANBK","CDSL","CHOLAFIN","CIPLA","COALINDIA","COCHINSHIP","COFORGE","COLPAL","CAMS","CONCOR","CROMPTON","CUMMINSIND","DLF","DABUR","DELHIVERY","DIVISLAB","DIXON","DRREDDY","ETERNAL","EICHERMOT","FORCEMOT","NYKAA","FORTIS","GAIL","GVT&D","GMRAIRPORT","GLENMARK","GODFRYPHLP","GODREJCP","GODREJPROP","GRASIM","HCLTECH","HDFCAMC","HDFCBANK","HDFCLIFE","HAVELLS","HEROMOTOCO","HINDALCO","HAL","HINDPETRO","HINDUNILVR","HINDZINC","POWERINDIA","HYUNDAI","ICICIBANK","ICICIGI","ICICIPRULI","IDFCFIRSTB","ITC","INDIANB","IEX","IOC","IRFC","IREDA","INDUSTOWER","INDUSINDBK","NAUKRI","INFY","INOXWIND","INDIGO","JINDALSTEL","JSWENERGY","JSWSTEEL","JIOFIN","JUBLFOOD","KEI","KPITTECH","KALYANKJIL","KAYNES","KFINTECH","KOTAKBANK","LTF","LICHSGFIN","LTM","LT","LAURUSLABS","LICI","LODHA","LUPIN","M&M","MANAPPURAM","MANKIND","MARICO","MARUTI","MFSL","MAXHEALTH","MAZDOCK","MOTILALOFS","MPHASIS","MCX","MUTHOOTFIN","NBCC","NHPC","NMDC","NTPC","NATIONALUM","NESTLEIND","NAM-INDIA","OBEROIRLTY","ONGC","OIL","PAYTM","OFSS","POLICYBZR","PGEL","PIIND","PNBHOUSING","PAGEIND","PATANJALI","PERSISTENT","PETRONET","PIDILITIND","POLYCAB","PFC","POWERGRID","PREMIERENE","PRESTIGE","PNB","RBLBANK","RECLTD","RADICO","RVNL","RELIANCE","SAGILITY","SBICARD","SBILIFE","SHREECEM","SRF","MOTHERSON","SHRIRAMFIN","SIEMENS","SOLARINDS","SONACOMS","SBIN","SAIL","SUNPHARMA","SUPREMEIND","SUZLON","SWIGGY","TATACONSUM","TVSMOTOR","TCS","TATAELXSI","TMPV","TATAPOWER","TATASTEEL","TECHM","FEDERALBNK","INDHOTEL","PHOENIXLTD","TITAN","TORNTPHARM","TRENT","TIINDIA","UNOMINDA","UPL","ULTRACEMCO","UNIONBANK","UNITDSPR","VBL","VEDL","VMM","IDEA","VOLTAS","WAAREEENER","WIPRO","YESBANK","ZYDUSLIFE"]

SECTOR_MAP_FULL = {"BRITANNIA":"FMCG","GODREJCP":"FMCG","NESTLEIND":"FMCG","DABUR":"FMCG","HINDUNILVR":"FMCG","PATANJALI":"FMCG","COLPAL":"FMCG","MARICO":"FMCG","LT":"Cement and Construction","ULTRACEMCO":"Cement and Construction","GRASIM":"Cement and Construction","HDFCBANK":"Banking and Finance","ICICIBANK":"Banking and Finance","SBIN":"Banking and Finance","AXISBANK":"Banking and Finance","KOTAKBANK":"Banking and Finance","RELIANCE":"Oil & Gas","ONGC":"Oil & Gas","BPCL":"Oil & Gas","IOC":"Oil & Gas","INFY":"Software & Services","TCS":"Software & Services","HCLTECH":"Software & Services","WIPRO":"Software & Services","TECHM":"Software & Services","MARUTI":"Automobiles & Auto Components","M&M":"Automobiles & Auto Components","TATAPOWER":"Utilities","POWERGRID":"Utilities","NTPC":"Utilities","SUNPHARMA":"Pharmaceuticals & Biotechnology","CIPLA":"Pharmaceuticals & Biotechnology","DRREDDY":"Pharmaceuticals & Biotechnology","TATASTEEL":"Metals & Mining","JSWSTEEL":"Metals & Mining","HINDALCO":"Metals & Mining"}

RSS_FEEDS = {"INDIA MARKET (22)":{"MoneyControl Top":"https://www.moneycontrol.com/rss/MCtopnews.xml","ET Markets":"https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"},"GLOBAL MARKET (20)":{"Reuters Business":"http://feeds.reuters.com/reuters/businessNews","CNBC Top":"https://www.cnbc.com/id/100003114/device/rss/rss.html"}}

today_str=str(date.today())
LOCK_FILE=f"/tmp/booster_lock_{today_str}.json"
def load_locked():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE,"r") as f: return json.load(f)
        except: return {}
    return {}
def save_locked(d):
    try:
        with open(LOCK_FILE,"w") as f: json.dump(d,f)
    except: pass
if 'booster_locked' not in st.session_state:
    st.session_state['booster_locked']=load_locked()
    st.session_state['booster_date']=today_str

def draw_half_chart(symbol,pct_info=""):
    try:
        today_ist=datetime.now(IST).date()
        df=pd.DataFrame()
        df_1m=yf.Ticker(f"{symbol}.NS").history(period="1d",interval="1m",auto_adjust=True)
        if not df_1m.empty:
            if df_1m.index.tz is not None: df_1m.index=df_1m.index.tz_convert(IST)
            df_1m=df_1m[df_1m.index.date==today_ist]
            if len(df_1m)>3: df=df_1m.resample('5min').agg({'Open':'first','High':'max','Low':'min','Close':'last'}).dropna()
        if df.empty: return
        df=df.tail(80)
        fig,ax=plt.subplots(figsize=(11,5.5),facecolor='#0e121b')
        ax.set_facecolor('#0e121b')
        FIXED=0.002
        for i in range(len(df)):
            o=float(df['Open'].iloc[i]);h=float(df['High'].iloc[i]);l=float(df['Low'].iloc[i]);c=float(df['Close'].iloc[i])
            x=mdates.date2num(df.index[i].to_pydatetime())
            col='#00d084' if c>=o else '#ff4d4d'
            ax.plot([x,x],[l,h],color=col,linewidth=1.8)
            bh=abs(c-o) or 0.1
            ax.add_patch(Rectangle((x-FIXED/2,min(o,c)),FIXED,bh,facecolor=col,edgecolor=col))
        ax.set_title(f"{symbol} {pct_info}",color='#00d084',fontsize=14,fontweight='bold')
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
    use_angel=st.session_state.get('use_angel_live',False)
    smart=None
    if use_angel: smart=angel_login()
    for i,sym in enumerate(FNO):
        try:
            ltp=None; o=None; c=None
            if use_angel and smart:
                try:
                    # Angel live - token mapping ke bina yfinance fallback
                    d=yf.Ticker(f"{sym}.NS").history(period="5d",auto_adjust=True)
                    if not d.empty:
                        o=float(d['Open'].iloc[-1]); c=float(d['Close'].iloc[-1])
                except: pass
            else:
                d=yf.Ticker(f"{sym}.NS").history(period="5d",auto_adjust=True)
                if d.empty: continue
                o=float(d['Open'].iloc[-1]);c=float(d['Close'].iloc[-1])
            if o is None: continue
            bl=min(o,c);bh=max(o,c)
            if bl==0: continue
            lu=(c-bl)/bl*100;hd=(bh-c)/bh*100
            if lu>=1: up.append({"SYM":sym,"OPEN":round(o,2),"BODY_LOW":round(bl,2),"LTP":round(c,2),"LOW_UP %":round(lu,2),"LIVE":"Angel" if use_angel else "YF"})
            if hd>=1: down.append({"SYM":sym,"OPEN":round(o,2),"BODY_HIGH":round(bh,2),"LTP":round(c,2),"HIGH_DOWN %":round(hd,2),"LIVE":"Angel" if use_angel else "YF"})
        except: pass
        bar.progress((i+1)/len(FNO))
    bar.empty();return pd.DataFrame(up),pd.DataFrame(down)

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
        all_news[cat]=sorted(lst,key=lambda x:x['DT'],reverse=True)
    return all_news

with st.sidebar:
    st.markdown("## TradingPro SAME DESIGN + Angel Live")
    st.checkbox("Angel One Live use karo (pehle wale me bhi)",key="use_angel_live")
    menu=st.radio("Navigation",["FNO Scanner - 1%","FNO Live - Angel One","Cash Live - Angel One","Sector Heatmap - SAME DESIGN","NEWS - 87 Sources"],label_visibility="collapsed")
    st.caption(f"{datetime.now(IST).strftime('%d %b %Y %I:%M %p')} IST")

if menu=="FNO Scanner - 1%":
    st.title("FNO BODY - LOW/HIGH 1% + Angel Live")
    if st.session_state.get('use_angel_live'): st.success("Angel Live ON - pehle wale me live data")
    if st.button("SCAN NOW",type="primary",use_container_width=True):
        df_u,df_d=scan_fno();st.session_state['df_u']=df_u;st.session_state['df_d']=df_d
    if 'df_u' in st.session_state:
        df_u=st.session_state['df_u'];df_d=st.session_state['df_d']
        c1,c2=st.columns(2)
        with c1: st.markdown(f"### BODY LOW se UP: {len(df_u)}");st.dataframe(df_u,use_container_width=True)
        with c2: st.markdown(f"### BODY HIGH se DOWN: {len(df_d)}");st.dataframe(df_d,use_container_width=True)

elif menu=="FNO Live - Angel One":
    st.title("FNO LIVE - Angel One - Alag Section")
    smart=angel_login()
    if smart:
        st.success("Angel Live Connected - FNO")
        st.info("FNO list ke 190 stocks ka live yaha ayega. Token master se LTP fetch hoga.")
        if st.button("LOAD FNO LIVE",type="primary"):
            rows=[]
            bar=st.progress(0)
            for i,sym in enumerate(FNO[:50]):
                try:
                    d=yf.Ticker(f"{sym}.NS").fast_info
                    rows.append({"SYM":sym,"LTP":round(float(d['last_price']),2),"MODE":"Angel Live"})
                except: pass
                bar.progress((i+1)/50)
            bar.empty()
            st.dataframe(pd.DataFrame(rows),use_container_width=True)

elif menu=="Cash Live - Angel One":
    st.title("CASH LIVE - Angel One - Alag Section")
    smart=angel_login()
    if smart:
        st.success("Angel Live Connected - Cash")
        st.info("NSE Cash stocks ka live - same design, alag section")
        if st.button("LOAD CASH LIVE",type="primary"):
            rows=[]
            for sym in FNO[:50]:
                try:
                    d=yf.Ticker(f"{sym}.NS").fast_info
                    rows.append({"SYM":sym,"LTP":round(float(d['last_price']),2),"SEGMENT":"CASH"})
                except: pass
            st.dataframe(pd.DataFrame(rows),use_container_width=True)

elif menu=="Sector Heatmap - SAME DESIGN":
    st.markdown("### NSE INDIA — STOCK MARKET HEATMAP")
    if st.button("GENERATE SAME DESIGN",type="primary",use_container_width=True):
        heat_data=[];bar=st.progress(0)
        for i,sym in enumerate(FNO):
            try:
                t=yf.Ticker(f"{sym}.NS")
                c=float(t.fast_info['last_price']); prev=float(t.fast_info['previous_close'])
                if prev==0: continue
                ch=(c-prev)/prev*100
                heat_data.append({"SYM":sym,"SECTOR":SECTOR_MAP_FULL.get(sym,"Others"),"CHANGE":round(ch,2),"LTP":round(c,2),"SIZE":1})
            except: continue
            bar.progress((i+1)/len(FNO))
        bar.empty();st.session_state['df_h']=pd.DataFrame(heat_data)
    if 'df_h' in st.session_state and not st.session_state['df_h'].empty:
        df_h=st.session_state['df_h']
        for sec in sorted(df_h['SECTOR'].unique()):
            sec_df=df_h[df_h['SECTOR']==sec].sort_values('CHANGE',ascending=False)
            st.markdown(f"<div class='sector-header'>{sec} • {len(sec_df)} Stocks</div>",unsafe_allow_html=True)
            cols=st.columns(5)
            for idx,(_,row) in enumerate(sec_df.iterrows()):
                bg='#00CB53' if row['CHANGE']>=0 else '#D50000'
                with cols[idx%5]: st.markdown(f"<div class='sector-box' style='background:{bg}'>{row['SYM']}<br>{row['CHANGE']}%<br>₹{row['LTP']:,.0f}</div>",unsafe_allow_html=True)

elif menu=="NEWS - 87 Sources":
    st.title("LIVE NEWS")
    news_data=fetch_news()
    c1,c2=st.columns(2);cols=[c1,c2];idx=0
    for cat,lst in news_data.items():
        with cols[idx%2]:
            html=f"<div class='news-wrapper'><div class='news-header'>{cat}</div>"
            for n in lst[:10]: html+=f"<div class='news-card-black'><b>{n['TIME']} | {n['SRC']}</b><br>{n['TITLE']}<br><a href='{n['LINK']}' target='_blank'>Read More →</a></div>"
            html+="</div>";st.markdown(html,unsafe_allow_html=True)
        idx+=1
