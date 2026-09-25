import streamlit as st
import yfinance as yf
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="FNO Scanner Pro", layout="wide")

FNO = ["RELIANCE","HDFCBANK","ICICIBANK","INFY","TCS","SBIN","TATAMOTORS","TATASTEEL","ITC","LT","AXISBANK","KOTAKBANK","BAJFINANCE","MARUTI","ONGC","NTPC","POWERGRID","COALINDIA","ULTRACEMCO","TITAN","ADANIENT","ADANIPORTS","ADANIGREEN","ADANIPOWER","AMBUJACEM","ACC","APOLLOHOSP","ASHOKLEY","ASIANPAINT","AUBANK","ABB","AARTIIND","ATUL","AMARAJABAT","ANGELONE","BALKRISIND","BANDHANBNK","BANKBARODA","BEL","BERGEPAINT","BHARATFORG","BHEL","BIOCON","BPCL","BRITANNIA","CANBK","CHOLAFIN","CIPLA","COFORGE","CONCOR","CUMMINSIND","DABUR","DALBHARAT","DIVISLAB","DIXON","DLF","DRREDDY","EICHERMOTORS","FEDERALBNK","GAIL","GMRINFRA","GODREJCP","GODREJPROP","GRASIM","HAL","HAVELLS","HCLTECH","HEROMOTOCO","HINDALCO","HINDUNILVR","ICICIGI","IDFCFIRSTB","IGL","INDIGO","INDUSINDBK","INDUSTOWER","IOC","IRCTC","IRFC","JSWSTEEL","KOTAKBANK","KPITTECH","LTTS","LTIM","LUPIN","M&M","MARICO","MGL","MPHASIS","MUTHOOTFIN","NAUKRI","NESTLEIND","OIL","PETRONET","PFC","PIDILITEIND","PIIND","PNB","POLYCAB","RECLTD","SAIL","SBILIFE","SRF","SHREECEM","SHRIRAMFIN","SIEMENS","SONACOMS","SUNPHARMA","TATACHEM","TATACONSUM","TATAELXSI","TATAPOWER","TATATECH","TECHM","TITAN","TRENT","TVSMOTOR","UPL","VEDL","VOLTAS","WIPRO","YESBANK","ZYDUSLIFE","SUZLON","PERSISTENT","TATACOMM","JUBLFOOD","SBICARD"]

SECTORS = {
    "BANKING": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK","BANDHANBNK","BANKBARODA","CANBK","PNB","IDFCFIRSTB","FEDERALBNK","INDUSINDBK","AUBANK","YESBANK","RBLBANK"],
    "IT": ["INFY","TCS","TECHM","WIPRO","HCLTECH","COFORGE","MPHASIS","LTTS","KPITTECH","PERSISTENT","TATATECH","TATAELXSI"],
    "AUTO": ["TATAMOTORS","MARUTI","M&M","BAJAJ-AUTO","HEROMOTOCO","EICHERMOTORS","ASHOKLEY","TVSMOTOR","BALKRISIND","MRF","SONACOMS","MOTHERSON","BHARATFORG"],
    "PHARMA": ["SUNPHARMA","DRREDDY","CIPLA","DIVISLAB","LUPIN","BIOCON","ZYDUSLIFE","TORNTPHARM","IPCALAB","GRANULES"],
    "ENERGY_OIL": ["RELIANCE","ONGC","NTPC","POWERGRID","COALINDIA","ADANIPOWER","ADANIGREEN","TATAPOWER","BPCL","HPCL","IOC","GAIL","PETRONET","IGL","MGL","OIL"],
    "METALS": ["TATASTEEL","JSWSTEEL","HINDALCO","VEDL","COALINDIA","SAIL","NMDC","NATIONALUM"],
    "FMCG": ["ITC","BRITANNIA","NESTLEIND","HINDUNILVR","DABUR","GODREJCP","MARICO","COLPAL","TATACONSUM","PAGEIND"],
    "CEMENT": ["ULTRACEMCO","AMBUJACEM","ACC","SHREECEM","JKCEMENT","DALBHARAT","RAMCOCEM"],
    "FINANCE": ["BAJFINANCE","BAJAJFINSV","SHRIRAMFIN","CHOLAFIN","MUTHOOTFIN","LICHSGFIN","SBICARD","SBILIFE","HDFCLIFE","ICICIPRULI","ICICIGI"],
    "INFRA": ["LT","ADANIPORTS","ADANIENT","GMRINFRA","CONCOR","RVNL","IRFC","BEL","HAL","BHEL","SIEMENS","ABB"],
    "CHEMICALS": ["UPL","SRF","PIIND","AARTIIND","ATUL","DEEPAKNTR","NAVINFLUOR","TATACHEM","COROMANDEL","CHAMBLFERT"],
    "CONSUMER_DURABLE": ["TITAN","HAVELLS","VOLTAS","DIXON","BLUESTARCO","CROMPTON","POLYCAB","AMBER"],
    "REALTY": ["DLF","GODREJPROP","OBEROIRLTY","PRESTIGE","BRIGADE","SOBHA","PHOENIXLTD"],
}

menu = st.sidebar.selectbox("Menu", ["FNO Scanner - 1%", "Booster Scanner", "FNO Live - Angel One", "Cash Live - Angel One", "Sector Heatmap", "NEWS - 87 Sources"])

def get_score(sym):
    try:
        df = yf.download(sym+".NS", period="6mo", interval="1d", progress=False)
        if len(df)<50: return 0,0,0,0,0,0
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        c = df['Close']
        rsi = 100 - (100/(1+ c.diff().where(c.diff()>0,0).rolling(14).mean() / -c.diff().where(c.diff()<0,0).rolling(14).mean()))
        rsi_v = float(rsi.iloc[-1])
        sma20 = c.rolling(20).mean().iloc[-1]
        sma50 = c.rolling(50).mean().iloc[-1]
        price = float(c.iloc[-1])
        low = float(df['Low'].tail(20).min())
        high = float(df['High'].tail(20).max())
        score=0
        if price>sma20: score+=20
        if price>sma50: score+=20
        if 55<rsi_v<75: score+=30
        elif rsi_v>=75: score+=10
        vol_surge = float(df['Volume'].iloc[-1]/df['Volume'].rolling(20).mean().iloc[-1])
        if vol_surge>1.5: score+=30
        return score, price, round(price*1.01,2), low, high, rsi_v
    except: return 0,0,0,0,0,0

if menu=="FNO Scanner - 1%":
    st.title("FNO Scanner - 1% Target")
    if st.button("SCAN 190 FNO STOCKS"):
        results=[]; all_scores={}; bar=st.progress(0)
        for i,sym in enumerate(FNO):
            score,price,target,low,high,rsi = get_score(sym)
            all_scores[sym]=score
            if score>=60: results.append({"Stock":sym,"Price":round(price,2),"Target 1%":target,"Score":score})
            bar.progress((i+1)/len(FNO))
        if results:
            df=pd.DataFrame(results).sort_values("Score",ascending=False)
            st.dataframe(df,use_container_width=True)
            st.subheader("Top 30 Score Chart - 1% Scanner")
            chart_df=pd.DataFrame(list(all_scores.items()),columns=["Stock","Score"]).sort_values("Score",ascending=False).head(30).set_index("Stock")
            st.bar_chart(chart_df)

elif menu=="Booster Scanner":
    st.title("Booster Scanner - High Momentum")
    if st.button("RUN BOOSTER SCAN"):
        results=[]; all_scores={}; bar=st.progress(0)
        for i,sym in enumerate(FNO):
            try:
                df=yf.download(sym+".NS",period="3mo",interval="1d",progress=False)
                if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
                c=df['Close']; pct=float((c.iloc[-1]-c.iloc[-5])/c.iloc[-5]*100); vol=float(df['Volume'].iloc[-1]/df['Volume'].rolling(20).mean().iloc[-1])
                score=0
                if pct>5: score+=40
                if pct>10: score+=30
                if vol>2: score+=30
                all_scores[sym]=score
                if score>=50: results.append({"Stock":sym,"Price":round(float(c.iloc[-1]),2),"5D %":round(pct,2),"Vol x":round(vol,2),"Booster Score":score})
            except: all_scores[sym]=0
            bar.progress((i+1)/len(FNO))
        if results:
            df=pd.DataFrame(results).sort_values("Booster Score",ascending=False)
            st.dataframe(df,use_container_width=True)
            st.subheader("Top 30 Booster Chart")
            chart_df=pd.DataFrame(list(all_scores.items()),columns=["Stock","Score"]).sort_values("Score",ascending=False).head(30).set_index("Stock")
            st.bar_chart(chart_df)
            fig=go.Figure(data=[go.Bar(x=df["Stock"].head(15),y=df["Booster Score"].head(15),marker_color='orange')])
            st.plotly_chart(fig,use_container_width=True)

elif menu=="Sector Heatmap":
    st.title("Sector Heatmap - Click Sector")
    # Sector avg performance for heatmap
    sector_perf=[]
    for sec, stocks in SECTORS.items():
        vals=[]
        for s in stocks[:8]:
            try:
                df=yf.download(s+".NS",period="5d",interval="1d",progress=False)
                if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
                chg=float((df['Close'].iloc[-1]-df['Close'].iloc[-2])/df['Close'].iloc[-2]*100)
                vals.append(chg)
            except: pass
        avg=round(sum(vals)/len(vals),2) if vals else 0
        sector_perf.append({"Sector":sec,"Avg %":avg,"Count":len(stocks)})
    perf_df=pd.DataFrame(sector_perf)
    fig=px.treemap(perf_df, path=['Sector'], values='Count', color='Avg %', color_continuous_scale='RdYlGn', title="Sector Performance")
    st.plotly_chart(fig,use_container_width=True)

    sel_sector = st.selectbox("Sector select karo", list(SECTORS.keys()))
    stocks = SECTORS[sel_sector]
    st.subheader(f"{sel_sector} - {len(stocks)} Stocks")

    if st.button(f"SCAN {sel_sector}"):
        low_results=[]; high_results=[]; all_scores={}
        bar=st.progress(0)
        for i,sym in enumerate(stocks):
            score,price,target,low,high,rsi = get_score(sym)
            all_scores[sym]=score
            if low>0:
                up_from_low = (price-low)/low*100
                down_from_high = (high-price)/high*100
                if 0 <= up_from_low <= 1.2:
                    low_results.append({"Stock":sym,"Price":round(price,2),"Low":round(low,2),"Up from Low %":round(up_from_low,2),"Target 1%":target,"Score":score})
                if 0 <= down_from_high <= 1.2:
                    high_results.append({"Stock":sym,"Price":round(price,2),"High":round(high,2),"Down from High %":round(down_from_high,2),"Score":score})
            bar.progress((i+1)/len(stocks))
            time.sleep(0.05)

        c1,c2 = st.columns(2)
        with c1:
            st.markdown("### 🟢 Low se 1% Up")
            if low_results:
                st.dataframe(pd.DataFrame(low_results).sort_values("Up from Low %"), use_container_width=True)
            else: st.warning("Koi stock low ke paas nahi")
        with c2:
            st.markdown("### 🔴 High se 1% Down")
            if high_results:
                st.dataframe(pd.DataFrame(high_results).sort_values("Down from High %"), use_container_width=True)
            else: st.warning("Koi stock high ke paas nahi")

        st.subheader(f"Top 30 Score Chart - {sel_sector} (Pehle jaisa fix chart)")
        if all_scores:
            chart_df=pd.DataFrame(list(all_scores.items()),columns=["Stock","Score"]).sort_values("Score",ascending=False).head(30).set_index("Stock")
            st.bar_chart(chart_df)
            fig2=go.Figure(data=[go.Bar(x=list(all_scores.keys())[:15], y=list(all_scores.values())[:15], marker_color='lightblue')])
            st.plotly_chart(fig2,use_container_width=True)

elif menu=="NEWS - 87 Sources":
    st.title("NEWS - 6 Category")
    tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs(["🇮🇳 Indian","🌍 Global","🛢️ Commodity","₿ Crypto","🏦 RBI","🇺🇸 Fed"])
    INDIAN = [("Moneycontrol","https://www.moneycontrol.com/rss/latestnews.xml"),("ET Markets","https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),("Business Standard","https://www.business-standard.com/rss/markets-106.rss"),("LiveMint","https://www.livemint.com/rss/markets"),("CNBC TV18","https://www.cnbctv18.com/rss/market.xml"),("Zee Business","https://www.zeebiz.com/rss.xml"),("NDTV Profit","https://www.ndtvprofit.com/rss")]
    GLOBAL = [("Reuters","https://www.reuters.com/rssFeed/businessNews"),("Investing Global","https://in.investing.com/rss/news_25.xml"),("CNBC Global","https://www.cnbc.com/id/100003114/device/rss/rss.html"),("MarketWatch","https://www.marketwatch.com/rss/topstories")]
    COMMODITY = [("Moneycontrol Comm","https://www.moneycontrol.com/rss/commodities.xml"),("ET Comm","https://economictimes.indiatimes.com/markets/commodities/rssfeeds/1808152121.cms"),("Kitco","https://www.kitco.com/rss/")]
    CRYPTO = [("CoinDesk","https://www.coindesk.com/arc/outboundfeeds/rss/"),("CoinTelegraph","https://cointelegraph.com/rss"),("Decrypt","https://decrypt.co/feed")]
    RBI_SOURCES = [("RBI","https://www.rbi.org.in/rss.xml"),("ET Economy","https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms"),("BS Economy","https://www.business-standard.com/rss/economy-105.rss")]
    FED_SOURCES = [("Fed","https://www.federalreserve.gov/feeds/press_all.xml"),("CNBC Fed","https://www.cnbc.com/id/10000664/device/rss/rss.html"),("WSJ","https://www.wsj.com/xml/rss/3_7085.xml")]
    def show_news(sources):
        for name,url in sources:
            try:
                r=requests.get(url,timeout=6,headers={"User-Agent":"Mozilla/5.0"})
                soup=BeautifulSoup(r.content,"xml")
                items=soup.find_all("item")[:3]
                if items:
                    with st.expander(name):
                        for it in items:
                            title=it.title.text if it.title else "No title"
                            link=it.link.text.strip() if it.link else "#"
                            st.markdown(f"- [{title}]({link})")
            except: continue
    with tab1: show_news(INDIAN)
    with tab2: show_news(GLOBAL)
    with tab3: show_news(COMMODITY)
    with tab4: show_news(CRYPTO)
    with tab5: show_news(RBI_SOURCES)
    with tab6: show_news(FED_SOURCES)

else:
    st.info("Angel Live section")
