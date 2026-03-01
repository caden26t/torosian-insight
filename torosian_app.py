"""
╔══════════════════════════════════════════════════════════╗
║         TOROSIAN STOCK INSIGHTS  —  Web App v2           ║
║                                                          ║
║  SETUP (run once):                                       ║
║    pip install streamlit yfinance pandas numpy plotly    ║
║                                                          ║
║  RUN:                                                    ║
║    python -m streamlit run torosian_app.py               ║
╚══════════════════════════════════════════════════════════╝
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import math
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Torosian Stock Insights",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,300&family=DM+Mono:wght@300;400;500&display=swap');
:root {
    --ink:#0b0a09;--surface:#111210;--surface2:#181917;--surface3:#1f2020;
    --border:#2a2c2b;--gold:#c8953a;--gold-light:#e8c97a;--cream:#e8e4dc;
    --muted:#6b6e6c;--green:#4caf7d;--red:#e05c5c;--cyan:#5bc8c8;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--surface)!important;color:var(--cream)!important;font-family:'DM Mono',monospace!important;}
[data-testid="stSidebar"]{background:var(--ink)!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebar"] *{font-family:'DM Mono',monospace!important;color:var(--cream)!important;}
h1,h2,h3{font-family:'Fraunces',serif!important;font-weight:300!important;}
[data-testid="stTabs"] button{font-family:'DM Mono',monospace!important;font-size:11px!important;letter-spacing:.12em!important;text-transform:uppercase!important;color:var(--muted)!important;background:transparent!important;border:none!important;border-bottom:2px solid transparent!important;padding:8px 20px!important;}
[data-testid="stTabs"] button[aria-selected="true"]{color:var(--gold)!important;border-bottom:2px solid var(--gold)!important;}
[data-testid="stTabsContent"]{border:none!important;padding-top:24px!important;}
[data-testid="stSelectbox"]>div>div,[data-testid="stMultiSelect"]>div>div{background:var(--surface3)!important;border:1px solid #353836!important;border-radius:3px!important;color:var(--cream)!important;font-family:'DM Mono',monospace!important;font-size:12px!important;}
[data-testid="stButton"]>button{background:var(--gold)!important;color:var(--ink)!important;border:none!important;font-family:'DM Mono',monospace!important;font-size:11px!important;font-weight:500!important;letter-spacing:.1em!important;text-transform:uppercase!important;border-radius:2px!important;padding:10px 24px!important;}
[data-testid="stButton"]>button:hover{background:var(--gold-light)!important;}
[data-testid="stExpander"]{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:3px!important;}
hr{border-color:var(--border)!important;}
#MainMenu,footer,header{visibility:hidden!important;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "learn"

# ─────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────
STOCK_UNIVERSE = [
    ("AAPL","Apple","Technology","Large"),("MSFT","Microsoft","Technology","Large"),
    ("NVDA","Nvidia","Technology","Large"),("GOOGL","Alphabet","Technology","Large"),
    ("META","Meta","Technology","Large"),("INTC","Intel","Technology","Large"),
    ("CSCO","Cisco","Technology","Large"),("IBM","IBM","Technology","Large"),
    ("ORCL","Oracle","Technology","Large"),("ADBE","Adobe","Technology","Large"),
    ("PLTR","Palantir","Technology","Mid"),("DDOG","Datadog","Technology","Mid"),
    ("CRWD","CrowdStrike","Technology","Large"),("SMCI","Super Micro","Technology","Mid"),
    ("IONQ","IonQ","Technology","Small"),("SOUN","SoundHound AI","Technology","Small"),
    ("JNJ","Johnson & Johnson","Healthcare","Large"),("UNH","UnitedHealth","Healthcare","Large"),
    ("PFE","Pfizer","Healthcare","Large"),("ABBV","AbbVie","Healthcare","Large"),
    ("MRK","Merck","Healthcare","Large"),("LLY","Eli Lilly","Healthcare","Large"),
    ("TMO","Thermo Fisher","Healthcare","Large"),("GEHC","GE HealthCare","Healthcare","Mid"),
    ("ACAD","Acadia Pharma","Healthcare","Small"),
    ("JPM","JPMorgan Chase","Finance","Large"),("BAC","Bank of America","Finance","Large"),
    ("GS","Goldman Sachs","Finance","Large"),("MS","Morgan Stanley","Finance","Large"),
    ("V","Visa","Finance","Large"),("BRK-B","Berkshire Hathaway","Finance","Large"),
    ("AXP","American Express","Finance","Large"),("WFC","Wells Fargo","Finance","Large"),
    ("HOOD","Robinhood","Finance","Mid"),("SOFI","SoFi Technologies","Finance","Small"),
    ("AMZN","Amazon","Consumer","Large"),("TSLA","Tesla","Consumer","Large"),
    ("WMT","Walmart","Consumer","Large"),("MCD","McDonald's","Consumer","Large"),
    ("NKE","Nike","Consumer","Large"),("SBUX","Starbucks","Consumer","Large"),
    ("HD","Home Depot","Consumer","Large"),("TGT","Target","Consumer","Large"),
    ("XOM","ExxonMobil","Energy","Large"),("CVX","Chevron","Energy","Large"),
    ("COP","ConocoPhillips","Energy","Large"),("NEE","NextEra Energy","Energy","Large"),
    ("SLB","Schlumberger","Energy","Large"),("RIG","Transocean","Energy","Small"),
    ("AMT","American Tower","Real Estate","Large"),("PLD","Prologis","Real Estate","Large"),
    ("EQIX","Equinix","Real Estate","Large"),("SPG","Simon Property","Real Estate","Large"),
    ("BA","Boeing","Industrials","Large"),("CAT","Caterpillar","Industrials","Large"),
    ("GE","GE Aerospace","Industrials","Large"),("HON","Honeywell","Industrials","Large"),
    ("UPS","UPS","Industrials","Large"),("MMM","3M","Industrials","Large"),
]

RISK_RANGES = {
    "Low (β < 0.8)":      (0.0, 0.8),
    "Medium (β 0.8–1.3)": (0.8, 1.3),
    "High (β > 1.3)":     (1.3, 99.0),
}

MA_NAMES  = ["EMA 10","SMA 10","EMA 20","SMA 20","EMA 30","SMA 30",
             "EMA 50","SMA 50","EMA 100","SMA 100","EMA 200","SMA 200",
             "Ichimoku","VWMA 20","HMA 9"]
OSC_NAMES = ["RSI 14","Stoch %K","CCI 20","ADX 14","Awe. Osc.",
             "Momentum","MACD","Stoch RSI","Williams %R","Bull/Bear","Ult. Osc."]
ALL_INDICATORS = MA_NAMES + OSC_NAMES

# ─────────────────────────────────────────────────────────
#  SECTOR-ADJUSTED THRESHOLDS
# ─────────────────────────────────────────────────────────
SECTOR_THRESHOLDS = {
    "Technology":  {"rsi_os":35,"rsi_ob":73,"cci_os":-110,"cci_ob":110,"wpr_os":-82,"wpr_ob":-18},
    "Healthcare":  {"rsi_os":30,"rsi_ob":68,"cci_os":-100,"cci_ob":100,"wpr_os":-80,"wpr_ob":-20},
    "Finance":     {"rsi_os":30,"rsi_ob":68,"cci_os":-100,"cci_ob":105,"wpr_os":-80,"wpr_ob":-20},
    "Consumer":    {"rsi_os":32,"rsi_ob":70,"cci_os":-105,"cci_ob":105,"wpr_os":-80,"wpr_ob":-20},
    "Energy":      {"rsi_os":28,"rsi_ob":72,"cci_os":-115,"cci_ob":115,"wpr_os":-82,"wpr_ob":-18},
    "Real Estate": {"rsi_os":30,"rsi_ob":65,"cci_os": -95,"cci_ob": 95,"wpr_os":-78,"wpr_ob":-22},
    "Industrials": {"rsi_os":30,"rsi_ob":68,"cci_os":-100,"cci_ob":108,"wpr_os":-80,"wpr_ob":-20},
}
DEFAULT_THRESH = {"rsi_os":30,"rsi_ob":70,"cci_os":-100,"cci_ob":100,"wpr_os":-80,"wpr_ob":-20}

def get_thresh(sector): return SECTOR_THRESHOLDS.get(sector, DEFAULT_THRESH)

# ─────────────────────────────────────────────────────────
#  INDICATORS
# ─────────────────────────────────────────────────────────
def sma(s,n): return s.rolling(n,min_periods=n).mean()
def ema(s,n): return s.ewm(span=n,adjust=False,min_periods=n).mean()
def wma(s,n):
    w=np.arange(1,n+1)
    return s.rolling(n).apply(lambda x:np.dot(x,w)/w.sum(),raw=True)
def hma(s,n): return wma(2*wma(s,n//2)-wma(s,n),int(math.sqrt(n)))
def vwma(c,v,n): return (c*v).rolling(n).sum()/v.rolling(n).sum()
def ichimoku_base(h,l,n=26): return (h.rolling(n).max()+l.rolling(n).min())/2
def rsi(c,n=14):
    d=c.diff();g=d.clip(lower=0);lo=-d.clip(upper=0)
    ag=g.ewm(alpha=1/n,min_periods=n,adjust=False).mean()
    al=lo.ewm(alpha=1/n,min_periods=n,adjust=False).mean()
    return 100-100/(1+ag/al.replace(0,np.nan))
def stoch_k(h,l,c,n=14,sm=3):
    ll=l.rolling(n).min();hh=h.rolling(n).max()
    return (100*(c-ll)/(hh-ll).replace(0,np.nan)).rolling(sm).mean()
def cci(h,l,c,n=20):
    tp=(h+l+c)/3;s=tp.rolling(n).mean()
    md=tp.rolling(n).apply(lambda x:np.mean(np.abs(x-x.mean())),raw=True)
    return (tp-s)/(0.015*md.replace(0,np.nan))
def adx_calc(h,l,c,n=14):
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    pdm=h.diff().clip(lower=0);mdm=(-l.diff()).clip(lower=0)
    pdm=pdm.where(pdm>(-l.diff()).clip(lower=0),0.0)
    mdm=mdm.where(mdm>h.diff().clip(lower=0),0.0)
    atr=tr.ewm(alpha=1/n,min_periods=n,adjust=False).mean()
    pdi=100*pdm.ewm(alpha=1/n,min_periods=n,adjust=False).mean()/atr.replace(0,np.nan)
    mdi=100*mdm.ewm(alpha=1/n,min_periods=n,adjust=False).mean()/atr.replace(0,np.nan)
    dx=100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan)
    return dx.ewm(alpha=1/n,min_periods=n,adjust=False).mean(),pdi,mdi
def awesome_osc(h,l): mid=(h+l)/2; return sma(mid,5)-sma(mid,34)
def momentum_ind(c,n=10): return c-c.shift(n)
def macd_calc(c,f=12,sl=26,sg=9): ml=ema(c,f)-ema(c,sl); return ml,ema(ml,sg)
def stoch_rsi(c,rn=14,sn=14,k=3):
    rv=rsi(c,rn);mn=rv.rolling(sn).min();mx=rv.rolling(sn).max()
    return ((rv-mn)/(mx-mn).replace(0,np.nan)).rolling(k).mean()
def williams_r(h,l,c,n=14):
    hh=h.rolling(n).max();ll=l.rolling(n).min()
    return -100*(hh-c)/(hh-ll).replace(0,np.nan)
def bbpower(h,l,c,n=13): e=ema(c,n); return (h-e)+(l-e)
def ult_osc(h,l,c,s=7,m=14,lg=28):
    bp=c-pd.concat([l,c.shift()],axis=1).min(axis=1)
    tr=pd.concat([h,c.shift()],axis=1).max(axis=1)-pd.concat([l,c.shift()],axis=1).min(axis=1)
    a=lambda p:bp.rolling(p).sum()/tr.rolling(p).sum().replace(0,np.nan)
    return 100*(4*a(s)+2*a(m)+a(lg))/7

# ─────────────────────────────────────────────────────────
#  SCORING ENGINE  (sector-aware)
# ─────────────────────────────────────────────────────────
def compute_score(hist, sector=""):
    if hist is None or len(hist)<210: return None,{}
    c,h,l,v=hist["Close"],hist["High"],hist["Low"],hist["Volume"]
    price=c.iloc[-1]; th=get_thresh(sector)
    signals,raw,mx={},0,0
    def sig_ma(val): return 0 if pd.isna(val) or val==0 else (1 if price>val else -1)
    for name,series in [
        ("EMA 10",ema(c,10)),("SMA 10",sma(c,10)),("EMA 20",ema(c,20)),("SMA 20",sma(c,20)),
        ("EMA 30",ema(c,30)),("SMA 30",sma(c,30)),("EMA 50",ema(c,50)),("SMA 50",sma(c,50)),
        ("EMA 100",ema(c,100)),("SMA 100",sma(c,100)),("EMA 200",ema(c,200)),("SMA 200",sma(c,200)),
        ("Ichimoku",ichimoku_base(h,l,26)),("VWMA 20",vwma(c,v,20)),("HMA 9",hma(c,9))]:
        s=sig_ma(series.iloc[-1]); signals[name]=s; raw+=s; mx+=1
    def s_rsi(x):  return 1 if x<th["rsi_os"] else(-1 if x>th["rsi_ob"] else 0)
    def s_stoch(x):return 1 if x<20 else(-1 if x>80 else 0)
    def s_cci(x):  return 1 if x<th["cci_os"] else(-1 if x>th["cci_ob"] else 0)
    def s_wpr(x):  return 1 if x<th["wpr_os"] else(-1 if x>th["wpr_ob"] else 0)
    def s_srsi(x): return 1 if x<0.2 else(-1 if x>0.8 else 0)
    def s_uo(x):   return 1 if x<30 else(-1 if x>70 else 0)
    def s_sign(x): return 0 if pd.isna(x) else(1 if x>0 else(-1 if x<0 else 0))
    adxv,pdi,mdi=adx_calc(h,l,c,14)
    ml,sig_l=macd_calc(c); w=1.5
    for name,s in [
        ("RSI 14",    s_rsi(rsi(c,14).iloc[-1])),
        ("Stoch %K",  s_stoch(stoch_k(h,l,c).iloc[-1])),
        ("CCI 20",    s_cci(cci(h,l,c).iloc[-1])),
        ("ADX 14",    (1 if pdi.iloc[-1]>mdi.iloc[-1] else -1) if adxv.iloc[-1]>25 else 0),
        ("Awe. Osc.", s_sign(awesome_osc(h,l).iloc[-1])),
        ("Momentum",  s_sign(momentum_ind(c).iloc[-1])),
        ("MACD",      s_sign(ml.iloc[-1]-sig_l.iloc[-1])),
        ("Stoch RSI", s_srsi(stoch_rsi(c).iloc[-1])),
        ("Williams %R",s_wpr(williams_r(h,l,c).iloc[-1])),
        ("Bull/Bear", s_sign(bbpower(h,l,c).iloc[-1])),
        ("Ult. Osc.", s_uo(ult_osc(h,l,c).iloc[-1])),
    ]:
        signals[name]=s; raw+=s*w; mx+=w
    return round(max(0,min(100,((raw+mx)/(2*mx))*100)),1), signals

# ─────────────────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────────────────
@st.cache_data(ttl=300,show_spinner=False)
def get_info(t):
    try: return yf.Ticker(t).info
    except: return {}
@st.cache_data(ttl=300,show_spinner=False)
def get_hist(t):
    try: h=yf.Ticker(t).history(period="1y"); return h if len(h)>50 else None
    except: return None
def fmt_cap(mc):
    if not mc: return "—"
    if mc>=1e12: return f"${mc/1e12:.1f}T"
    if mc>=1e9:  return f"${mc/1e9:.1f}B"
    return f"${mc/1e6:.0f}M"
def score_color(s):
    if s is None: return "#6b6e6c"
    if s>=70: return "#4caf7d"
    if s>=55: return "#8bc98b"
    if s>=45: return "#5bc8c8"
    if s>=30: return "#e07b5c"
    return "#e05c5c"
def score_label(s):
    if s is None: return "N/A"
    if s>=70: return "Strong Buy"
    if s>=55: return "Buy"
    if s>=45: return "Neutral"
    if s>=30: return "Sell"
    return "Strong Sell"
def analyst_label(rec):
    return {"strong_buy":"Strong Buy","buy":"Buy","hold":"Hold",
            "underperform":"Underperform","sell":"Sell"}.get((rec or "").lower().replace(" ","_"),rec or "—")

# ─────────────────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────────────────
def metric_card(label,value,sub="",color="#c8953a"):
    st.markdown(f"""<div style="background:#181917;border:1px solid #2a2c2b;border-left:3px solid {color};
    border-radius:3px;padding:16px 20px;margin-bottom:4px;">
    <div style="font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#6b6e6c;margin-bottom:6px;">{label}</div>
    <div style="font-family:'Fraunces',serif;font-size:1.5rem;font-weight:300;color:#e8e4dc;">{value}</div>
    <div style="font-size:11px;color:#6b6e6c;margin-top:4px;">{sub}</div></div>""",unsafe_allow_html=True)

def score_gauge(score,ticker):
    color=score_color(score); label=score_label(score)
    fig=go.Figure(go.Indicator(mode="gauge+number",value=score or 0,
        number={"suffix":"/100","font":{"size":28,"color":"#e8e4dc","family":"Fraunces, serif"}},
        gauge={"axis":{"range":[0,100],"tickcolor":"#2a2c2b","tickfont":{"color":"#6b6e6c","size":10}},
               "bar":{"color":color,"thickness":0.3},"bgcolor":"#181917","bordercolor":"#2a2c2b",
               "steps":[{"range":[0,30],"color":"#1a1210"},{"range":[30,45],"color":"#1a1512"},
                        {"range":[45,55],"color":"#141a1a"},{"range":[55,70],"color":"#121a12"},
                        {"range":[70,100],"color":"#101810"}],
               "threshold":{"line":{"color":color,"width":3},"thickness":0.8,"value":score or 0}},
        title={"text":f"<b>{ticker}</b><br><span style='font-size:12px;color:{color}'>{label}</span>",
               "font":{"color":"#e8e4dc","family":"Fraunces, serif","size":16}}))
    fig.update_layout(height=240,margin=dict(l=20,r=20,t=40,b=10),paper_bgcolor="#111210",font_color="#e8e4dc")
    return fig

def price_chart(hist,ticker):
    if hist is None: return None
    c=hist["Close"]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=hist.index,y=c,name="Price",line=dict(color="#c8953a",width=2)))
    fig.add_trace(go.Scatter(x=hist.index,y=ema(c,20),name="EMA 20",line=dict(color="#5bc8c8",width=1,dash="dot"),opacity=0.7))
    fig.add_trace(go.Scatter(x=hist.index,y=ema(c,50),name="EMA 50",line=dict(color="#8b7ed8",width=1,dash="dot"),opacity=0.7))
    fig.add_trace(go.Scatter(x=hist.index,y=ema(c,200),name="EMA 200",line=dict(color="#e05c5c",width=1,dash="dot"),opacity=0.7))
    fig.update_layout(height=280,margin=dict(l=0,r=0,t=24,b=0),paper_bgcolor="#111210",plot_bgcolor="#111210",
        font=dict(color="#6b6e6c",family="DM Mono"),
        legend=dict(bgcolor="#181917",bordercolor="#2a2c2b",font=dict(size=10,color="#a0a8a4")),
        xaxis=dict(showgrid=False,color="#6b6e6c",tickfont=dict(size=10)),
        yaxis=dict(showgrid=True,gridcolor="#1f2020",color="#6b6e6c",tickformat="$.2f",tickfont=dict(size=10)),
        title=dict(text=f"{ticker} — 1 Year Price + Key MAs",font=dict(size=13,color="#e8e4dc",family="Fraunces, serif"),x=0),
        hovermode="x unified",hoverlabel=dict(bgcolor="#181917",bordercolor="#2a2c2b",font=dict(color="#e8e4dc",family="DM Mono",size=11)))
    return fig

def signals_chart(signals):
    vals=[signals.get(n,0) for n in ALL_INDICATORS]
    colors=["#4caf7d" if v==1 else("#e05c5c" if v==-1 else "#2a2c2b") for v in vals]
    labels=["BUY" if v==1 else("SELL" if v==-1 else "NEU") for v in vals]
    fig=go.Figure(go.Bar(x=ALL_INDICATORS,y=[1]*26,marker_color=colors,text=labels,textposition="inside",
        textfont=dict(size=9,color="#0b0a09",family="DM Mono"),hovertemplate="%{x}: %{text}<extra></extra>"))
    fig.add_vline(x=14.5,line_color="#2a2c2b",line_width=1,line_dash="dot")
    fig.add_annotation(x=7,y=1.05,text="MOVING AVERAGES",showarrow=False,font=dict(size=9,color="#6b6e6c",family="DM Mono"),yref="paper")
    fig.add_annotation(x=20,y=1.05,text="OSCILLATORS",showarrow=False,font=dict(size=9,color="#6b6e6c",family="DM Mono"),yref="paper")
    fig.update_layout(height=180,margin=dict(l=0,r=0,t=30,b=40),paper_bgcolor="#111210",plot_bgcolor="#111210",showlegend=False,
        xaxis=dict(showgrid=False,tickfont=dict(size=8,color="#6b6e6c",family="DM Mono"),tickangle=-45),yaxis=dict(visible=False))
    return fig

def style_df(df):
    def c_score(v):
        try: return f"color:{score_color(float(str(v)))};font-weight:500"
        except: return ""
    def c_up(v):
        if v=="—": return ""
        try: n=float(str(v).replace("%","").replace("+","")); return "color:#4caf7d" if n>=0 else "color:#e05c5c"
        except: return ""
    def c_con(v):
        return {"Strong Buy":"color:#4caf7d","Buy":"color:#8bc98b","Hold":"color:#5bc8c8",
                "Underperform":"color:#e07b5c","Sell":"color:#e05c5c"}.get(v,"")
    styled=df.style
    for col,fn in [("Score",c_score),("Upside",c_up),("Consensus",c_con),("Signal",c_con)]:
        if col in df.columns: styled=styled.applymap(fn,subset=[col])
    return styled.set_properties(**{"background-color":"#111210","color":"#e8e4dc","border-color":"#1f2020",
        "font-family":"DM Mono, monospace","font-size":"12px"}).set_table_styles([
        {"selector":"th","props":[("background-color","#0b0a09"),("color","#6b6e6c"),("font-size","9px"),
         ("letter-spacing","0.15em"),("text-transform","uppercase"),("font-family","DM Mono, monospace"),
         ("border-color","#1f2020"),("padding","10px 12px")]},
        {"selector":"td","props":[("padding","10px 12px"),("border-color","#1f2020")]},
        {"selector":"tr:hover td","props":[("background-color","#181917")]},
    ])

# ─────────────────────────────────────────────────────────
#  LEARN PAGE
# ─────────────────────────────────────────────────────────
INDICATOR_DOCS = {
    "Moving Averages": [
        {"name":"Simple Moving Average (SMA)","variants":"SMA 10, 20, 30, 50, 100, 200","difficulty":"Beginner",
         "what":"The plain average of closing prices over N days. Every day gets equal weight.",
         "how":"Price above SMA = bullish trend. Below = bearish. Longer SMAs (200) show the big picture; shorter ones (10) react to recent moves quickly.",
         "buy":"Price crosses above the SMA","sell":"Price crosses below the SMA",
         "note":"The SMA 200 is one of Wall Street's most watched levels. Institutional funds often use it as a key support/resistance line."},
        {"name":"Exponential Moving Average (EMA)","variants":"EMA 10, 20, 30, 50, 100, 200","difficulty":"Beginner",
         "what":"Like the SMA but recent prices carry more weight, making it faster to react.",
         "how":"Signals trend changes earlier than SMA but also produces more false signals. Traders often use EMA for timing and SMA for trend confirmation.",
         "buy":"Price above EMA and EMA sloping upward","sell":"Price drops below EMA or EMA slopes downward",
         "note":"The Golden Cross (EMA 50 crossing above EMA 200) is one of the most famous bullish signals in technical analysis."},
        {"name":"Hull Moving Average (HMA 9)","variants":"HMA 9","difficulty":"Intermediate",
         "what":"Designed by Alan Hull to reduce lag without sacrificing smoothness, using weighted MAs in a two-step formula.",
         "how":"Far more responsive than SMA or EMA. Popular for short-term trading where identifying current momentum quickly matters.",
         "buy":"HMA slopes upward and price is above it","sell":"HMA slopes downward and price is below it",
         "note":"The square root step in HMA's formula is what gives it its unique lag-reduction property."},
        {"name":"Volume Weighted Moving Average (VWMA 20)","variants":"VWMA 20","difficulty":"Intermediate",
         "what":"Like the SMA but each price is weighted by volume on that day — high-volume days matter more.",
         "how":"Reflects the true average price investors actually paid. Deviations between VWMA and SMA reveal whether price moves happened on high or low conviction.",
         "buy":"Price is above VWMA (demand is strong)","sell":"Price falls below VWMA (sellers dominating)",
         "note":"Institutional traders reference the intraday version (VWAP) as a benchmark for executing large orders efficiently."},
        {"name":"Ichimoku Base Line","variants":"Ichimoku (9, 26, 52, 26)","difficulty":"Advanced",
         "what":"Part of the Ichimoku Cloud system. The Base Line (Kijun-sen) is the midpoint of the 26-period high-low range — the equilibrium price.",
         "how":"Price above the Base Line = medium-term bullish trend. The full Ichimoku system has five components; we use the Base Line as a standalone trend filter.",
         "buy":"Price is above the Base Line","sell":"Price is below the Base Line",
         "note":"Developed by Japanese journalist Goichi Hosoda in the 1930s. The name means 'one glance equilibrium chart'."},
    ],
    "Oscillators": [
        {"name":"Relative Strength Index (RSI)","variants":"RSI 14","difficulty":"Beginner",
         "what":"Measures the speed and size of recent price changes on a 0–100 scale. Reveals if a stock is overbought or oversold relative to its own history.",
         "how":"Standard thresholds: 30 = oversold (buy zone), 70 = overbought (sell zone). Torosian adjusts these by sector — tech stocks can sustain higher RSI longer than REITs.",
         "buy":"RSI drops below sector-adjusted oversold level (30–35 depending on sector)","sell":"RSI rises above sector-adjusted overbought level (65–73 depending on sector)",
         "note":"Developed by J. Welles Wilder in 1978. One of the most widely used indicators globally. Sector adjustment is what separates professional from amateur analysis."},
        {"name":"MACD","variants":"MACD Level (12, 26)","difficulty":"Beginner",
         "what":"Measures the relationship between a 12-day and 26-day EMA. When the faster EMA diverges from the slower, it signals momentum.",
         "how":"MACD Line = EMA(12) minus EMA(26). Signal Line = 9-day EMA of MACD. Crossovers between these two lines generate signals.",
         "buy":"MACD Line crosses above the Signal Line","sell":"MACD Line crosses below the Signal Line",
         "note":"Developed by Gerald Appel in the 1970s. The 12-26-9 parameters are the universal standard used by virtually every charting platform."},
        {"name":"Stochastic %K","variants":"Stochastic %K (14, 3, 3)","difficulty":"Beginner",
         "what":"Compares closing price to the 14-day high-low range on a 0–100 scale. Shows where the current price sits within its recent range.",
         "how":"Near 100 = closing near period highs (strong momentum). Near 0 = closing near period lows (weak). Extreme readings signal potential reversals.",
         "buy":"Stochastic drops below 20","sell":"Stochastic rises above 80",
         "note":"Developed by George Lane in the 1950s. The smoothing parameter reduces noise — raw %K without smoothing generates far more false signals."},
        {"name":"Stochastic RSI Fast","variants":"Stoch RSI Fast (3, 3, 14, 14)","difficulty":"Intermediate",
         "what":"Applies the Stochastic formula to RSI values instead of price — an indicator of an indicator, making it more sensitive to short-term shifts.",
         "how":"Ranges from 0 to 1. Below 0.2 means RSI is near its lowest recent point (potential bounce). Above 0.8 = RSI near recent high (potential pullback).",
         "buy":"Stoch RSI drops below 0.2","sell":"Stoch RSI rises above 0.8",
         "note":"More volatile than standard RSI — generates more signals but also more false positives. Best used alongside slower indicators for confirmation."},
        {"name":"Commodity Channel Index (CCI)","variants":"CCI (20)","difficulty":"Intermediate",
         "what":"Measures how far price is from its 20-day average, normalised by typical volatility. Despite the name, it works well on stocks.",
         "how":"Oscillates around zero with no fixed bounds. Readings beyond ±100 are significant — they suggest the stock has moved unusually far from average.",
         "buy":"CCI drops below sector-adjusted oversold level (~-100)","sell":"CCI rises above sector-adjusted overbought level (~+100)",
         "note":"Developed by Donald Lambert in 1980. Unique because it has no fixed ceiling or floor — extreme readings of ±200 do occur."},
        {"name":"Williams %R","variants":"Williams %R (14)","difficulty":"Beginner",
         "what":"Nearly identical to Stochastic %K but inverted. Measures where the close sits within the 14-day range, on a scale from -100 to 0.",
         "how":"Readings near 0 = closing near period highs (strong). Near -100 = closing near lows (weak). Think of it as an upside-down Stochastic.",
         "buy":"Williams %R drops below sector-adjusted level (~-80)","sell":"Williams %R rises above sector-adjusted level (~-20)",
         "note":"Developed by Larry Williams. The negative scale confuses beginners — remember -10 is overbought and -90 is oversold."},
        {"name":"Average Directional Index (ADX)","variants":"ADX (14)","difficulty":"Intermediate",
         "what":"Measures trend strength, not direction. Combines +DI and -DI lines to show how powerful the prevailing trend is.",
         "how":"ADX above 25 = strong trend present. Direction is determined by +DI vs -DI: if +DI leads, trend is up. If -DI leads, trend is down.",
         "buy":"ADX > 25 and +DI is above -DI","sell":"ADX > 25 and -DI is above +DI",
         "note":"ADX below 20 means the market is ranging with no clear trend — signals from other indicators become less reliable in this condition."},
        {"name":"Awesome Oscillator","variants":"Awesome Oscillator","difficulty":"Beginner",
         "what":"Measures momentum by comparing a 5-period and 34-period SMA of the midpoint price ((high+low)/2).",
         "how":"Positive = fast average above slow average (bullish momentum). Negative = bearish momentum. No overbought/oversold levels — purely directional.",
         "buy":"Awesome Oscillator crosses above zero","sell":"Awesome Oscillator crosses below zero",
         "note":"Created by Bill Williams. One of the simplest momentum indicators — its simplicity can be a strength as it is less prone to over-optimisation."},
        {"name":"Momentum (10)","variants":"Momentum (10)","difficulty":"Beginner",
         "what":"The simplest momentum indicator: today's price minus the price 10 days ago. Positive = risen, negative = fallen.",
         "how":"Pure rate of change. Positive and rising = trend accelerating. Positive but falling = trend may be losing steam even if price is still up.",
         "buy":"Momentum is positive (price higher than 10 days ago)","sell":"Momentum is negative (price lower than 10 days ago)",
         "note":"In economics terms, this is a first-difference of price — the same concept as measuring GDP growth rate rather than GDP level."},
        {"name":"Bull Bear Power","variants":"Bull Bear Power","difficulty":"Intermediate",
         "what":"Measures the distance between high/low prices and a 13-period EMA. Bull Power = High minus EMA. Bear Power = Low minus EMA.",
         "how":"Positive combined value = bulls controlling price action. Negative = bears in control. Developed by Dr. Alexander Elder.",
         "buy":"Combined Bull+Bear Power is positive","sell":"Combined Bull+Bear Power is negative",
         "note":"Elder recommended pairing this with a trend filter (like EMA direction) to avoid trading counter-trend."},
        {"name":"Ultimate Oscillator","variants":"Ultimate Oscillator (7, 14, 28)","difficulty":"Advanced",
         "what":"Combines three timeframes (7, 14, 28 days) into one oscillator with weighted averaging to reduce false signals.",
         "how":"Ranges 0–100. Shorter period gets 4x weight, medium 2x, long 1x. Multi-period design makes it more robust than single-period oscillators.",
         "buy":"Ultimate Oscillator drops below 30","sell":"Ultimate Oscillator rises above 70",
         "note":"Also developed by Larry Williams. The multi-timeframe approach was his answer to the problem of single-period oscillators being too sensitive to the chosen lookback."},
    ]
}

DIFF_COLOR = {"Beginner":"#4caf7d","Intermediate":"#c8953a","Advanced":"#e05c5c"}

def render_learn():
    st.markdown("""
    <div style="padding:60px 0 48px;text-align:center;border-bottom:1px solid #1f2020;margin-bottom:48px;">
        <div style="font-size:10px;letter-spacing:.3em;text-transform:uppercase;color:#c8953a;margin-bottom:16px;">Torosian Stock Insights</div>
        <h1 style="font-family:'Fraunces',serif;font-size:clamp(2rem,5vw,3.2rem);font-weight:300;color:#e8e4dc;margin:0 0 16px;line-height:1.1;">
            Understand every indicator.<br><em style="color:#c8953a;">Make better decisions.</em></h1>
        <p style="font-size:13px;color:#6b6e6c;max-width:520px;margin:0 auto 32px;line-height:1.8;">
            A plain-English guide to all 26 technical indicators used in this platform — what they measure, how to read them, and why they matter.</p>
    </div>""", unsafe_allow_html=True)

    _,col_c,_ = st.columns([1,2,1])
    with col_c:
        if st.button("Enter the App  →", use_container_width=True):
            st.session_state.page = "app"; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Sector thresholds explainer
    rows = [[s,f"RSI: {t['rsi_os']}/{t['rsi_ob']}",f"CCI: {t['cci_os']}/{t['cci_ob']}",f"W%R: {t['wpr_os']}/{t['wpr_ob']}"]
            for s,t in SECTOR_THRESHOLDS.items()]
    df_thresh = pd.DataFrame(rows, columns=["Sector","RSI (OS/OB)","CCI (OS/OB)","W%R (OS/OB)"])
    st.markdown("""
    <div style="background:#181917;border:1px solid #2a2c2b;border-left:3px solid #c8953a;
                padding:20px 24px;border-radius:3px;margin-bottom:12px;">
        <div style="font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#c8953a;margin-bottom:8px;">Sector-Adjusted Thresholds</div>
        <p style="font-size:12px;color:#a0a8a4;line-height:1.8;margin:0 0 16px;">
            Most platforms apply the same RSI, CCI, and Williams %R thresholds to every stock.
            Torosian adjusts these by sector — because a Technology stock at RSI 71 is normal,
            while a Real Estate stock at RSI 66 is already overbought. The table below shows the exact thresholds used.</p>
    </div>""", unsafe_allow_html=True)
    st.dataframe(style_df(df_thresh), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    for group, inds in INDICATOR_DOCS.items():
        st.markdown(f"""<div style="font-size:9px;letter-spacing:.2em;text-transform:uppercase;
                    color:#6b6e6c;margin-bottom:20px;padding-top:16px;border-top:1px solid #1f2020;">{group}</div>""",
                    unsafe_allow_html=True)
        for ind in inds:
            dc = DIFF_COLOR.get(ind["difficulty"],"#6b6e6c")
            with st.expander(f"  {ind['name']}  —  {ind['variants']}"):
                st.markdown(f"""
                <div style="margin-bottom:14px;">
                    <span style="font-size:9px;letter-spacing:.15em;text-transform:uppercase;
                                 background:{dc}22;color:{dc};padding:3px 8px;border-radius:2px;">{ind['difficulty']}</span>
                </div>
                <div style="font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#6b6e6c;margin-bottom:6px;">What it measures</div>
                <p style="font-size:12px;color:#a0a8a4;line-height:1.8;margin-bottom:14px;">{ind['what']}</p>
                <div style="font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#6b6e6c;margin-bottom:6px;">How to read it</div>
                <p style="font-size:12px;color:#a0a8a4;line-height:1.8;margin-bottom:14px;">{ind['how']}</p>
                <div style="display:flex;gap:12px;margin-bottom:14px;">
                    <div style="background:#4caf7d11;border:1px solid #4caf7d33;padding:10px 14px;border-radius:3px;flex:1;">
                        <div style="font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#4caf7d;margin-bottom:4px;">Buy signal</div>
                        <div style="font-size:11px;color:#a0a8a4;">{ind['buy']}</div>
                    </div>
                    <div style="background:#e05c5c11;border:1px solid #e05c5c33;padding:10px 14px;border-radius:3px;flex:1;">
                        <div style="font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#e05c5c;margin-bottom:4px;">Sell signal</div>
                        <div style="font-size:11px;color:#a0a8a4;">{ind['sell']}</div>
                    </div>
                </div>
                <div style="background:#111210;border:1px solid #1f2020;padding:10px 14px;border-radius:3px;">
                    <span style="font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#c8953a;">Did you know · </span>
                    <span style="font-size:11px;color:#6b6e6c;">{ind['note']}</span>
                </div>""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    _,col_c,_ = st.columns([1,2,1])
    with col_c:
        if st.button("Enter the App  →", key="bottom_enter", use_container_width=True):
            st.session_state.page = "app"; st.rerun()

# ─────────────────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────────────────
def render_app():

    # ── Sidebar ──────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="padding:20px 0 20px;">
            <div style="font-size:9px;letter-spacing:.25em;text-transform:uppercase;color:#c8953a;margin-bottom:6px;">Equity Research Platform</div>
            <div style="font-family:'Fraunces',serif;font-size:1.4rem;font-weight:300;color:#e8e4dc;line-height:1.2;">
                Torosian<br><em style="color:#c8953a;">Stock Insights</em></div>
        </div>
        <hr style="border-color:#1f2020;margin:0 0 16px;">
        <div style="font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:#6b6e6c;margin-bottom:10px;">Core Filters</div>
        """, unsafe_allow_html=True)

        all_sectors = sorted(set(s for _,_,s,_ in STOCK_UNIVERSE))
        sector      = st.selectbox("Sector", ["ALL"]+all_sectors)
        cap         = st.selectbox("Market Cap", ["All","Large (>$10B)","Mid ($2B–$10B)","Small (<$2B)"])
        cap_filter  = {"All":"All","Large (>$10B)":"Large","Mid ($2B–$10B)":"Mid","Small (<$2B)":"Small"}[cap]
        risk_key    = st.selectbox("Risk Tolerance", list(RISK_RANGES.keys()))
        beta_min,beta_max = RISK_RANGES[risk_key]
        horizon     = st.radio("Horizon", ["Short Term","Long Term"])
        min_score   = st.slider("Min Technical Score", 0, 90, 0, 5)
        top_n       = st.slider("Results to Show", 3, 20, 8)

        # ── Advanced Filters ──────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("⚙  Advanced Filters"):
            st.markdown("""<div style="font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#c8953a;margin-bottom:10px;">Indicator Filter</div>""",unsafe_allow_html=True)
            use_ind_filter  = st.checkbox("Filter by specific indicators")
            req_indicators  = []
            req_direction   = "Bullish"
            if use_ind_filter:
                req_indicators = st.multiselect("Required indicators", ALL_INDICATORS,
                    help="Only show stocks where ALL selected indicators match the chosen direction")
                req_direction  = st.radio("Signal direction", ["Bullish","Bearish"],
                    help="Bullish = long plays. Bearish = short plays (stock is signalling downside).")

            st.markdown("""<div style="font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#c8953a;margin:14px 0 10px;">Sort Mode</div>""",unsafe_allow_html=True)
            sort_mode      = st.radio("Sort results by", ["Composite Score","Single Indicator"])
            sort_indicator = None
            sort_dir       = "Most Bullish First"
            if sort_mode == "Single Indicator":
                sort_indicator = st.selectbox("Choose indicator", ALL_INDICATORS)
                sort_dir       = st.radio("Rank direction", ["Most Bullish First","Most Bearish First"],
                    help="'Most Bearish First' surfaces short candidates at the top.")

        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("Run Screener →", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to Learn", use_container_width=True):
            st.session_state.page = "learn"; st.rerun()
        st.markdown("""<hr style="border-color:#1f2020;margin:16px 0 10px;">
        <div style="font-size:9px;color:#3a3c3b;line-height:1.8;">Data via Yahoo Finance · Not financial advice</div>""",
        unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────
    st.markdown("""
    <div style="padding:28px 0 20px;border-bottom:1px solid #1f2020;margin-bottom:28px;">
        <div style="font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:#c8953a;margin-bottom:6px;">Torosian Stock Insights</div>
        <h1 style="font-family:'Fraunces',serif;font-size:2rem;font-weight:300;color:#e8e4dc;margin:0;">
            Your personal <em style="color:#c8953a;">equity research</em> dashboard</h1>
        <p style="color:#6b6e6c;font-size:11px;margin-top:8px;">
            26 indicators · Sector-adjusted thresholds · Live from Yahoo Finance</p>
    </div>""", unsafe_allow_html=True)

    tab_screen, tab_deep, tab_compare = st.tabs(["📋  Screener","🔍  Deep Dive","⚔  Compare"])

    # ════════════════════════════════════════════════════
    #  SCREENER
    # ════════════════════════════════════════════════════
    with tab_screen:
        if not run:
            st.markdown("""<div style="text-align:center;padding:64px 0;">
                <div style="font-size:3rem;margin-bottom:16px;">📈</div>
                <div style="font-family:'Fraunces',serif;font-size:1.2rem;color:#6b6e6c;font-weight:300;">
                    Configure your filters in the sidebar and press <em>Run Screener</em></div>
            </div>""", unsafe_allow_html=True)
        else:
            candidates=[(t,n,s,c) for t,n,s,c in STOCK_UNIVERSE
                        if (sector=="ALL" or s==sector) and (cap_filter=="All" or c==cap_filter)]
            if not candidates: st.error("No stocks match your filters."); st.stop()

            results=[]; prog=st.progress(0,text="Fetching live data…")
            for i,(ticker,name,sec,cap_size) in enumerate(candidates):
                prog.progress((i+1)/len(candidates),text=f"Analysing {ticker}…")
                info=get_info(ticker); beta=info.get("beta")
                if beta is None or not (beta_min<=beta<beta_max): continue
                hist=get_hist(ticker); score,signals=compute_score(hist,sec)
                if score is None or score<min_score: continue
                # Advanced indicator filter
                if use_ind_filter and req_indicators:
                    req_val=1 if req_direction=="Bullish" else -1
                    if not all(signals.get(ind,0)==req_val for ind in req_indicators): continue
                price=info.get("currentPrice") or info.get("regularMarketPrice")
                pe=info.get("trailingPE"); div=(info.get("dividendYield") or 0)*100
                mcap=info.get("marketCap"); target=info.get("targetMeanPrice")
                upside=((target-price)/price*100) if price and target else None
                results.append({"ticker":ticker,"name":name,"sector":sec,"cap":cap_size,
                    "price":price,"beta":beta,"pe":pe,"div":div,"mcap":mcap,"target":target,
                    "upside":upside,"rec":analyst_label(info.get("recommendationKey","")),
                    "n_analysts":info.get("numberOfAnalystOpinions"),
                    "score":score,"signals":signals,"hist":hist,"info":info})
            prog.empty()
            if not results: st.error("No stocks passed all filters."); st.stop()

            # Sorting
            if sort_mode=="Single Indicator" and sort_indicator:
                rev=(sort_dir=="Most Bullish First")
                results.sort(key=lambda x:x["signals"].get(sort_indicator,0),reverse=rev)
                sort_note=f"Sorted by {sort_indicator} — {'bullish' if rev else 'bearish'} first"
            elif horizon=="Long Term":
                results.sort(key=lambda x:(x["score"],x["div"]),reverse=True)
                sort_note="Sorted by score + dividend yield"
            else:
                results.sort(key=lambda x:x["score"],reverse=True)
                sort_note="Sorted by composite technical score"
            top=results[:top_n]

            # Metrics
            avg_sc=round(sum(r["score"] for r in top)/len(top),1)
            buys=sum(1 for r in top if r["score"]>=55)
            sells=sum(1 for r in top if r["score"]<45)
            c1,c2,c3,c4=st.columns(4)
            with c1: metric_card("Stocks Found",str(len(top)),f"of {len(results)} passed","#c8953a")
            with c2: metric_card("Avg Score",f"{avg_sc}/100",score_label(avg_sc),score_color(avg_sc))
            with c3: metric_card("Buy Signals",str(buys),f"{len(top)-buys-sells} neutral · {sells} sell","#4caf7d")
            with c4: metric_card("Sort Mode","Indicator" if sort_mode=="Single Indicator" else horizon,sort_note,"#5bc8c8")

            # Advanced filter badge
            if use_ind_filter and req_indicators:
                badges=" &nbsp;".join([f'<span style="background:#c8953a22;color:#c8953a;font-size:10px;padding:2px 8px;border-radius:2px;">{i}</span>' for i in req_indicators])
                st.markdown(f'<div style="margin:12px 0 4px;font-size:11px;color:#6b6e6c;">Filtered: {req_direction} on &nbsp;{badges}</div>',unsafe_allow_html=True)

            # Table
            st.markdown("<br>",unsafe_allow_html=True)
            rows=[{"Ticker":r["ticker"],"Company":r["name"],"Cap":r["cap"],
                   "Price":f"${r['price']:.2f}" if r["price"] else "—",
                   "Beta":f"{r['beta']:.2f}","P/E":f"{r['pe']:.1f}" if r["pe"] else "—",
                   "Div %":f"{r['div']:.2f}%","Upside":f"{r['upside']:+.1f}%" if r["upside"] else "—",
                   "Consensus":r["rec"],"Score":r["score"],"Signal":score_label(r["score"])} for r in top]
            st.dataframe(style_df(pd.DataFrame(rows)),use_container_width=True,hide_index=True,height=380)

            # Signal breakdown
            top_r=top[0]
            st.markdown("<br>",unsafe_allow_html=True)
            th=get_thresh(top_r["sector"])
            st.markdown(f"""<div style="font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#6b6e6c;margin-bottom:12px;">
                Signal Breakdown — {top_r['ticker']} (Top Pick)
                &nbsp;<span style="color:#c8953a;font-size:9px;">· {top_r['sector']} thresholds: RSI {th['rsi_os']}/{th['rsi_ob']}</span></div>""",
                unsafe_allow_html=True)
            col_chart,col_summary=st.columns([2,1])
            with col_chart:
                st.plotly_chart(signals_chart(top_r["signals"]),use_container_width=True,config={"displayModeBar":False})
            with col_summary:
                sigs=top_r["signals"]
                ma_b=sum(1 for n in MA_NAMES if sigs.get(n,0)==1)
                ma_s=sum(1 for n in MA_NAMES if sigs.get(n,0)==-1)
                osc_b=sum(1 for n in OSC_NAMES if sigs.get(n,0)==1)
                osc_s=sum(1 for n in OSC_NAMES if sigs.get(n,0)==-1)
                tb=ma_b+osc_b; ts=ma_s+osc_s; pct=tb/26*100
                interp=("Strong bullish consensus" if pct>=65 else "Mildly bullish lean" if pct>=50
                        else "Bearish lean" if ts>tb else "Mixed signals")
                ic=("#4caf7d" if pct>=65 else "#8bc98b" if pct>=50 else "#e05c5c" if ts>tb else "#5bc8c8")
                st.markdown(f"""
                <div style="background:#181917;border:1px solid #2a2c2b;padding:20px;border-radius:3px;">
                    <div style="font-family:'Fraunces',serif;font-size:1.1rem;color:{ic};margin-bottom:12px;">{interp}</div>
                    <div style="font-size:11px;color:#a0a8a4;line-height:2.2;">
                        <span style="color:#4caf7d">▲ {tb} Buy</span> &nbsp;
                        <span style="color:#e05c5c">▼ {ts} Sell</span> &nbsp;
                        <span style="color:#6b6e6c">● {26-tb-ts} Neutral</span><br>
                        MAs: <span style="color:#4caf7d">{ma_b}↑</span>/<span style="color:#e05c5c">{ma_s}↓</span>
                        &nbsp; Oscs: <span style="color:#4caf7d">{osc_b}↑</span>/<span style="color:#e05c5c">{osc_s}↓</span>
                    </div>
                    <hr style="border-color:#2a2c2b;margin:12px 0;">
                    <div style="font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#6b6e6c;margin-bottom:4px;">Sector Thresholds</div>
                    <div style="font-size:10px;color:#6b6e6c;line-height:1.9;">
                        RSI: {th['rsi_os']} / {th['rsi_ob']}<br>
                        CCI: {th['cci_os']} / {th['cci_ob']}<br>
                        W%R: {th['wpr_os']} / {th['wpr_ob']}
                    </div>
                    <hr style="border-color:#2a2c2b;margin:12px 0;">
                    <div style="font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#6b6e6c;margin-bottom:4px;">Analyst Consensus</div>
                    <div style="font-size:12px;color:#e8e4dc;">{top_r['rec']}</div>
                    <div style="font-size:11px;color:#6b6e6c;">
                        {f"{top_r['n_analysts']} analysts" if top_r['n_analysts'] else ""}
                        {f" · Target {top_r['upside']:+.1f}%" if top_r['upside'] else ""}
                    </div>
                </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    #  DEEP DIVE
    # ════════════════════════════════════════════════════
    with tab_deep:
        ci,cb=st.columns([3,1])
        with ci: dive_ticker=st.text_input("",placeholder="Enter ticker e.g. NVDA, AAPL, TSLA",label_visibility="collapsed").strip().upper()
        with cb: dive_run=st.button("Analyse →",key="dive_btn",use_container_width=True)
        if dive_run and dive_ticker:
            with st.spinner(f"Loading {dive_ticker}…"):
                info=get_info(dive_ticker); hist=get_hist(dive_ticker)
                sec=info.get("sector",""); score,signals=compute_score(hist,sec); th=get_thresh(sec)
            if not info: st.error(f"Could not find {dive_ticker}."); st.stop()
            name=info.get("longName",dive_ticker); price=info.get("currentPrice") or info.get("regularMarketPrice")
            beta=info.get("beta"); pe=info.get("trailingPE"); div=(info.get("dividendYield") or 0)*100
            mcap=info.get("marketCap"); target=info.get("targetMeanPrice")
            rec=analyst_label(info.get("recommendationKey","")); n_ana=info.get("numberOfAnalystOpinions")
            rec_mean=info.get("recommendationMean"); upside=((target-price)/price*100) if price and target else None
            desc=info.get("longBusinessSummary","")
            st.markdown(f"""
            <div style="margin-bottom:20px;">
                <div style="font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:#c8953a;margin-bottom:4px;">{sec}</div>
                <h2 style="font-family:'Fraunces',serif;font-size:1.8rem;font-weight:300;color:#e8e4dc;margin:0;">
                    {name} <span style="color:#6b6e6c;font-size:1rem;">({dive_ticker})</span></h2>
                <div style="font-size:10px;color:#6b6e6c;margin-top:6px;">
                    Sector thresholds — RSI: {th['rsi_os']}/{th['rsi_ob']} · CCI: {th['cci_os']}/{th['cci_ob']} · W%%R: {th['wpr_os']}/{th['wpr_ob']}
                </div>
            </div>""", unsafe_allow_html=True)
            cols=st.columns(6)
            for col,(lbl,val,sub) in zip(cols,[
                ("Price",f"${price:.2f}" if price else "—",""),
                ("Market Cap",fmt_cap(mcap),""),("Beta",f"{beta:.2f}" if beta else "—","vs market"),
                ("P/E Ratio",f"{pe:.1f}" if pe else "—",""),("Div Yield",f"{div:.2f}%",""),
                ("Analyst Target",f"${target:.2f}" if target else "—",f"{upside:+.1f}% upside" if upside else ""),
            ]):
                with col: metric_card(lbl,val,sub)
            st.markdown("<br>",unsafe_allow_html=True)
            cg,cc=st.columns([1,2])
            with cg:
                if score: st.plotly_chart(score_gauge(score,dive_ticker),use_container_width=True,config={"displayModeBar":False})
                rc=("#4caf7d" if rec in("Strong Buy","Buy") else "#5bc8c8" if rec=="Hold" else "#e05c5c")
                st.markdown(f"""<div style="background:#181917;border:1px solid #2a2c2b;padding:16px;border-radius:3px;margin-top:4px;">
                    <div style="font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:#6b6e6c;margin-bottom:8px;">Analyst Sentiment</div>
                    <div style="font-family:'Fraunces',serif;font-size:1.1rem;color:{rc};">{rec}</div>
                    <div style="font-size:11px;color:#6b6e6c;margin-top:4px;">
                        {f"{n_ana} analysts" if n_ana else ""}{f"<br>Mean: {rec_mean:.1f}/5" if rec_mean else ""}
                    </div></div>""",unsafe_allow_html=True)
            with cc:
                fp=price_chart(hist,dive_ticker)
                if fp: st.plotly_chart(fp,use_container_width=True,config={"displayModeBar":False})
            if signals:
                st.markdown("<br>",unsafe_allow_html=True)
                st.markdown("""<div style="font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#6b6e6c;margin-bottom:12px;">All 26 Indicators</div>""",unsafe_allow_html=True)
                st.plotly_chart(signals_chart(signals),use_container_width=True,config={"displayModeBar":False})
            if desc:
                st.markdown(f"""<div style="background:#181917;border:1px solid #2a2c2b;padding:20px;border-radius:3px;margin-top:8px;">
                    <div style="font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:#6b6e6c;margin-bottom:10px;">About</div>
                    <div style="font-size:12px;color:#a0a8a4;line-height:1.8;">{desc[:400]}{'…' if len(desc)>400 else ''}</div>
                </div>""",unsafe_allow_html=True)
        else:
            st.markdown("""<div style="text-align:center;padding:64px 0;">
                <div style="font-size:3rem;margin-bottom:16px;">🔍</div>
                <div style="font-family:'Fraunces',serif;font-size:1.2rem;color:#6b6e6c;font-weight:300;">
                    Enter any ticker symbol to get a full technical + fundamental analysis</div>
            </div>""",unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    #  COMPARE
    # ════════════════════════════════════════════════════
    with tab_compare:
        c1,c2,c3=st.columns([2,2,1])
        with c1: t1=st.text_input("",placeholder="First ticker e.g. AAPL",label_visibility="collapsed",key="t1").strip().upper()
        with c2: t2=st.text_input("",placeholder="Second ticker e.g. MSFT",label_visibility="collapsed",key="t2").strip().upper()
        with c3: cmp_run=st.button("Compare →",key="cmp_btn",use_container_width=True)
        if cmp_run and t1 and t2:
            with st.spinner(f"Loading {t1} and {t2}…"):
                data={}
                for tk in [t1,t2]:
                    info=get_info(tk); hist=get_hist(tk); sec=info.get("sector","")
                    score,sigs=compute_score(hist,sec); data[tk]={"info":info,"hist":hist,"score":score,"signals":sigs,"sector":sec}
            st.markdown(f"""<div style="font-family:'Fraunces',serif;font-size:1.5rem;font-weight:300;color:#e8e4dc;margin-bottom:24px;">
                {t1} <span style="color:#c8953a;">vs</span> {t2}</div>""",unsafe_allow_html=True)
            g1,g2=st.columns(2)
            with g1: st.plotly_chart(score_gauge(data[t1]["score"],t1),use_container_width=True,config={"displayModeBar":False})
            with g2: st.plotly_chart(score_gauge(data[t2]["score"],t2),use_container_width=True,config={"displayModeBar":False})
            s1,s2=data[t1]["score"] or 0,data[t2]["score"] or 0
            winner=t1 if s1>s2 else t2
            st.markdown(f"""<div style="background:#181917;border:1px solid #c8953a33;padding:14px 24px;
                border-radius:3px;margin-bottom:16px;text-align:center;">
                <span style="font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:#6b6e6c;">Technical Edge &nbsp;→&nbsp; </span>
                <span style="font-family:'Fraunces',serif;font-size:1.1rem;color:#c8953a;">{winner}</span>
                <span style="font-size:11px;color:#6b6e6c;"> by {abs(s1-s2):.1f} points</span>
            </div>""",unsafe_allow_html=True)
            sec1,sec2=data[t1]["sector"],data[t2]["sector"]
            if sec1!=sec2:
                st.markdown(f"""<div style="background:#181917;border:1px solid #2a2c2b;padding:10px 16px;
                    border-radius:3px;margin-bottom:14px;font-size:11px;color:#6b6e6c;">
                    ⚠ Different sectors — sector-adjusted thresholds applied independently:
                    <span style="color:#c8953a">{t1} ({sec1})</span> and <span style="color:#c8953a">{t2} ({sec2})</span>
                </div>""",unsafe_allow_html=True)

            # Fundamentals
            st.markdown("""<div style="font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#6b6e6c;margin-bottom:12px;">Fundamentals</div>""",unsafe_allow_html=True)
            def gv(tk,key): return data[tk]["info"].get(key)
            rows_c=[]
            for lbl,fn in [
                ("Price",     lambda tk:f"${gv(tk,'currentPrice'):.2f}" if gv(tk,'currentPrice') else "—"),
                ("Market Cap",lambda tk:fmt_cap(gv(tk,'marketCap'))),
                ("Beta",      lambda tk:f"{gv(tk,'beta'):.2f}" if gv(tk,'beta') else "—"),
                ("P/E Ratio", lambda tk:f"{gv(tk,'trailingPE'):.1f}" if gv(tk,'trailingPE') else "—"),
                ("Div Yield", lambda tk:f"{(gv(tk,'dividendYield') or 0)*100:.2f}%"),
                ("Analyst Target",lambda tk:f"${gv(tk,'targetMeanPrice'):.2f}" if gv(tk,'targetMeanPrice') else "—"),
                ("Consensus", lambda tk:analyst_label(gv(tk,'recommendationKey') or "")),
                ("Sector",    lambda tk:gv(tk,'sector') or "—"),
            ]:
                rows_c.append({"Metric":lbl,t1:fn(t1),t2:fn(t2)})
            df_c=pd.DataFrame(rows_c).set_index("Metric")
            st.dataframe(df_c.style.set_properties(**{"background-color":"#111210","color":"#e8e4dc",
                "border-color":"#1f2020","font-family":"DM Mono, monospace","font-size":"12px"}).set_table_styles([
                {"selector":"th","props":[("background-color","#0b0a09"),("color","#6b6e6c"),("font-size","9px"),
                 ("letter-spacing","0.15em"),("text-transform","uppercase"),("border-color","#1f2020"),("padding","10px 14px")]},
                {"selector":"td","props":[("padding","10px 14px"),("border-color","#1f2020")]}]),use_container_width=True)

            # Analyst sentiment side by side
            st.markdown("<br>",unsafe_allow_html=True)
            a1,a2=st.columns(2)
            for col,tk in [(a1,t1),(a2,t2)]:
                with col:
                    rec=analyst_label(data[tk]["info"].get("recommendationKey",""))
                    rc=("#4caf7d" if rec in("Strong Buy","Buy") else "#5bc8c8" if rec=="Hold" else "#e05c5c")
                    n=data[tk]["info"].get("numberOfAnalystOpinions")
                    tgt=data[tk]["info"].get("targetMeanPrice"); prc=data[tk]["info"].get("currentPrice")
                    up=f"{((tgt-prc)/prc*100):+.1f}%" if tgt and prc else "—"
                    st.markdown(f"""<div style="background:#181917;border:1px solid #2a2c2b;padding:16px;border-radius:3px;">
                        <div style="font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:#6b6e6c;margin-bottom:6px;">{tk} · Analyst Consensus</div>
                        <div style="font-family:'Fraunces',serif;font-size:1.1rem;color:{rc};">{rec}</div>
                        <div style="font-size:11px;color:#6b6e6c;margin-top:4px;">{f"{n} analysts · " if n else ""}Target: {up}</div>
                    </div>""",unsafe_allow_html=True)

            # Where they disagree
            sig1,sig2=data[t1]["signals"],data[t2]["signals"]
            if sig1 and sig2:
                disagree={k for k in sig1 if sig1.get(k,0)!=sig2.get(k,0)}
                if disagree:
                    st.markdown("<br>",unsafe_allow_html=True)
                    st.markdown("""<div style="font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#6b6e6c;margin-bottom:12px;">Where They Disagree</div>""",unsafe_allow_html=True)
                    d1,d2=st.columns(2)
                    for col,tk,smap in [(d1,t1,sig1),(d2,t2,sig2)]:
                        with col:
                            bull=[k for k in disagree if smap.get(k,0)==1]
                            bear=[k for k in disagree if smap.get(k,0)==-1]
                            st.markdown(f"""<div style="background:#181917;border:1px solid #2a2c2b;padding:16px;border-radius:3px;">
                                <div style="font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:#6b6e6c;margin-bottom:10px;">{tk}</div>
                                {f'<div style="font-size:10px;color:#4caf7d;margin-bottom:4px;">▲ Bullish on</div><div style="font-size:11px;color:#a0a8a4;margin-bottom:10px;">{", ".join(bull)}</div>' if bull else ""}
                                {f'<div style="font-size:10px;color:#e05c5c;margin-bottom:4px;">▼ Bearish on</div><div style="font-size:11px;color:#a0a8a4;">{", ".join(bear)}</div>' if bear else ""}
                            </div>""",unsafe_allow_html=True)

            # Normalised price chart
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown("""<div style="font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#6b6e6c;margin-bottom:12px;">Normalised 1-Year Price Performance</div>""",unsafe_allow_html=True)
            fig_c=go.Figure()
            for tk,color in [(t1,"#c8953a"),(t2,"#5bc8c8")]:
                h=data[tk]["hist"]
                if h is not None:
                    norm=h["Close"]/h["Close"].iloc[0]*100
                    fig_c.add_trace(go.Scatter(x=h.index,y=norm,name=tk,line=dict(color=color,width=2)))
            fig_c.update_layout(height=260,margin=dict(l=0,r=0,t=10,b=0),paper_bgcolor="#111210",plot_bgcolor="#111210",
                font=dict(color="#6b6e6c",family="DM Mono"),
                legend=dict(bgcolor="#181917",bordercolor="#2a2c2b",font=dict(size=11,color="#e8e4dc")),
                xaxis=dict(showgrid=False,color="#6b6e6c",tickfont=dict(size=10)),
                yaxis=dict(showgrid=True,gridcolor="#1f2020",color="#6b6e6c",ticksuffix="%",tickfont=dict(size=10)),
                hovermode="x unified",hoverlabel=dict(bgcolor="#181917",bordercolor="#2a2c2b",font=dict(color="#e8e4dc",family="DM Mono",size=11)))
            st.plotly_chart(fig_c,use_container_width=True,config={"displayModeBar":False})
        else:
            st.markdown("""<div style="text-align:center;padding:64px 0;">
                <div style="font-size:3rem;margin-bottom:16px;">⚔</div>
                <div style="font-family:'Fraunces',serif;font-size:1.2rem;color:#6b6e6c;font-weight:300;">
                    Enter two ticker symbols to compare them head-to-head</div>
            </div>""",unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────────────────
if st.session_state.page == "learn":
    render_learn()
else:
    render_app()
