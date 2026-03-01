"""
╔══════════════════════════════════════════════════════════╗
║         TOROSIAN STOCK INSIGHTS  —  Web App              ║
║                                                          ║
║  SETUP (run once):                                       ║
║    pip install streamlit yfinance pandas numpy plotly    ║
║                                                          ║
║  RUN:                                                    ║
║    streamlit run torosian_app.py                         ║
╚══════════════════════════════════════════════════════════╝
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import math
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ─────────────────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Torosian Stock Insights",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
#  CUSTOM CSS  —  Dark Financial Terminal Aesthetic
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,300&family=DM+Mono:wght@300;400;500&display=swap');

/* ── Root variables ── */
:root {
    --ink:        #0b0a09;
    --surface:    #111210;
    --surface2:   #181917;
    --surface3:   #1f2020;
    --border:     #2a2c2b;
    --border2:    #353836;
    --gold:       #c8953a;
    --gold-light: #e8c97a;
    --gold-dim:   #7a5820;
    --cream:      #e8e4dc;
    --muted:      #6b6e6c;
    --green:      #4caf7d;
    --red:        #e05c5c;
    --cyan:       #5bc8c8;
}

/* ── Global reset ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--surface) !important;
    color: var(--cream) !important;
    font-family: 'DM Mono', monospace !important;
}

[data-testid="stSidebar"] {
    background: var(--ink) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    font-family: 'DM Mono', monospace !important;
    color: var(--cream) !important;
}

/* ── Headings ── */
h1, h2, h3 { font-family: 'Fraunces', serif !important; font-weight: 300 !important; }

/* ── Tabs ── */
[data-testid="stTabs"] button {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 8px 20px !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
}
[data-testid="stTabsContent"] {
    border: none !important;
    padding-top: 24px !important;
}

/* ── Inputs & selects ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div,
[data-testid="stSlider"] {
    background: var(--surface3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 3px !important;
    color: var(--cream) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}

/* ── Buttons ── */
[data-testid="stButton"] > button {
    background: var(--gold) !important;
    color: var(--ink) !important;
    border: none !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    padding: 10px 24px !important;
    transition: all 0.2s !important;
}
[data-testid="stButton"] > button:hover {
    background: var(--gold-light) !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 10px !important; letter-spacing: 0.15em !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { color: var(--cream) !important; font-family: 'Fraunces', serif !important; font-size: 1.6rem !important; }
[data-testid="stMetricDelta"] { font-size: 11px !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 3px !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Spinner ── */
[data-testid="stSpinner"] { color: var(--gold) !important; }

/* ── Sidebar labels ── */
[data-testid="stSidebar"] label {
    font-size: 10px !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

/* ── Remove Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  STOCK UNIVERSE
# ─────────────────────────────────────────────────────────
STOCK_UNIVERSE = [
    ("AAPL","Apple","Technology","Large"),
    ("MSFT","Microsoft","Technology","Large"),
    ("NVDA","Nvidia","Technology","Large"),
    ("GOOGL","Alphabet","Technology","Large"),
    ("META","Meta","Technology","Large"),
    ("INTC","Intel","Technology","Large"),
    ("CSCO","Cisco","Technology","Large"),
    ("IBM","IBM","Technology","Large"),
    ("ORCL","Oracle","Technology","Large"),
    ("ADBE","Adobe","Technology","Large"),
    ("PLTR","Palantir","Technology","Mid"),
    ("DDOG","Datadog","Technology","Mid"),
    ("CRWD","CrowdStrike","Technology","Large"),
    ("SMCI","Super Micro","Technology","Mid"),
    ("IONQ","IonQ","Technology","Small"),
    ("SOUN","SoundHound AI","Technology","Small"),
    ("JNJ","Johnson & Johnson","Healthcare","Large"),
    ("UNH","UnitedHealth","Healthcare","Large"),
    ("PFE","Pfizer","Healthcare","Large"),
    ("ABBV","AbbVie","Healthcare","Large"),
    ("MRK","Merck","Healthcare","Large"),
    ("LLY","Eli Lilly","Healthcare","Large"),
    ("TMO","Thermo Fisher","Healthcare","Large"),
    ("GEHC","GE HealthCare","Healthcare","Mid"),
    ("ACAD","Acadia Pharma","Healthcare","Small"),
    ("JPM","JPMorgan Chase","Finance","Large"),
    ("BAC","Bank of America","Finance","Large"),
    ("GS","Goldman Sachs","Finance","Large"),
    ("MS","Morgan Stanley","Finance","Large"),
    ("V","Visa","Finance","Large"),
    ("BRK-B","Berkshire Hathaway","Finance","Large"),
    ("AXP","American Express","Finance","Large"),
    ("WFC","Wells Fargo","Finance","Large"),
    ("HOOD","Robinhood","Finance","Mid"),
    ("SOFI","SoFi Technologies","Finance","Small"),
    ("AMZN","Amazon","Consumer","Large"),
    ("TSLA","Tesla","Consumer","Large"),
    ("WMT","Walmart","Consumer","Large"),
    ("MCD","McDonald's","Consumer","Large"),
    ("NKE","Nike","Consumer","Large"),
    ("SBUX","Starbucks","Consumer","Large"),
    ("HD","Home Depot","Consumer","Large"),
    ("TGT","Target","Consumer","Large"),
    ("XOM","ExxonMobil","Energy","Large"),
    ("CVX","Chevron","Energy","Large"),
    ("COP","ConocoPhillips","Energy","Large"),
    ("NEE","NextEra Energy","Energy","Large"),
    ("SLB","Schlumberger","Energy","Large"),
    ("RIG","Transocean","Energy","Small"),
    ("AMT","American Tower","Real Estate","Large"),
    ("PLD","Prologis","Real Estate","Large"),
    ("EQIX","Equinix","Real Estate","Large"),
    ("SPG","Simon Property","Real Estate","Large"),
    ("BA","Boeing","Industrials","Large"),
    ("CAT","Caterpillar","Industrials","Large"),
    ("GE","GE Aerospace","Industrials","Large"),
    ("HON","Honeywell","Industrials","Large"),
    ("UPS","UPS","Industrials","Large"),
    ("MMM","3M","Industrials","Large"),
]

RISK_RANGES = {
    "Low (β < 0.8)":      (0.0, 0.8),
    "Medium (β 0.8–1.3)": (0.8, 1.3),
    "High (β > 1.3)":     (1.3, 99.0),
}

# ─────────────────────────────────────────────────────────
#  TECHNICAL INDICATORS
# ─────────────────────────────────────────────────────────
def sma(s, n):   return s.rolling(n, min_periods=n).mean()
def ema(s, n):   return s.ewm(span=n, adjust=False, min_periods=n).mean()
def wma(s, n):
    w = np.arange(1, n+1)
    return s.rolling(n).apply(lambda x: np.dot(x,w)/w.sum(), raw=True)
def hma(s, n):
    return wma(2*wma(s,n//2) - wma(s,n), int(math.sqrt(n)))
def vwma(c, v, n): return (c*v).rolling(n).sum() / v.rolling(n).sum()
def ichimoku_base(h, l, n=26): return (h.rolling(n).max()+l.rolling(n).min())/2

def rsi(c, n=14):
    d = c.diff(); g = d.clip(lower=0); lo = -d.clip(upper=0)
    ag = g.ewm(alpha=1/n, min_periods=n, adjust=False).mean()
    al = lo.ewm(alpha=1/n, min_periods=n, adjust=False).mean()
    return 100 - 100/(1 + ag/al.replace(0, np.nan))

def stoch_k(h, l, c, n=14, sm=3):
    ll = l.rolling(n).min(); hh = h.rolling(n).max()
    k = 100*(c-ll)/(hh-ll).replace(0,np.nan)
    return k.rolling(sm).mean()

def cci(h, l, c, n=20):
    tp = (h+l+c)/3; s = tp.rolling(n).mean()
    md = tp.rolling(n).apply(lambda x: np.mean(np.abs(x-x.mean())), raw=True)
    return (tp-s)/(0.015*md.replace(0,np.nan))

def adx_calc(h, l, c, n=14):
    tr = pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    pdm = h.diff().clip(lower=0); mdm = (-l.diff()).clip(lower=0)
    pdm = pdm.where(pdm > (-l.diff()).clip(lower=0), 0.0)
    mdm = mdm.where(mdm > h.diff().clip(lower=0), 0.0)
    atr = tr.ewm(alpha=1/n, min_periods=n, adjust=False).mean()
    pdi = 100*pdm.ewm(alpha=1/n, min_periods=n, adjust=False).mean()/atr.replace(0,np.nan)
    mdi = 100*mdm.ewm(alpha=1/n, min_periods=n, adjust=False).mean()/atr.replace(0,np.nan)
    dx  = 100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan)
    return dx.ewm(alpha=1/n, min_periods=n, adjust=False).mean(), pdi, mdi

def awesome_osc(h, l): mid=(h+l)/2; return sma(mid,5)-sma(mid,34)
def momentum_ind(c, n=10): return c - c.shift(n)
def macd_calc(c, f=12, sl=26, sg=9):
    ml = ema(c,f)-ema(c,sl); sig = ema(ml,sg); return ml, sig
def stoch_rsi(c, rn=14, sn=14, k=3):
    rv = rsi(c,rn); mn=rv.rolling(sn).min(); mx=rv.rolling(sn).max()
    return ((rv-mn)/(mx-mn).replace(0,np.nan)).rolling(k).mean()
def williams_r(h, l, c, n=14):
    hh=h.rolling(n).max(); ll=l.rolling(n).min()
    return -100*(hh-c)/(hh-ll).replace(0,np.nan)
def bbpower(h, l, c, n=13): e=ema(c,n); return (h-e)+(l-e)
def ult_osc(h, l, c, s=7, m=14, lg=28):
    bp = c - pd.concat([l,c.shift()],axis=1).min(axis=1)
    tr = pd.concat([h,c.shift()],axis=1).max(axis=1) - pd.concat([l,c.shift()],axis=1).min(axis=1)
    a  = lambda p: bp.rolling(p).sum()/tr.rolling(p).sum().replace(0,np.nan)
    return 100*(4*a(s)+2*a(m)+a(lg))/7

# ─────────────────────────────────────────────────────────
#  SCORING ENGINE
# ─────────────────────────────────────────────────────────
def sig_ma(price, val):
    if pd.isna(val) or val==0: return 0
    return 1 if price>val else -1

def compute_score(hist):
    if hist is None or len(hist) < 210: return None, {}
    c, h, l, v = hist["Close"], hist["High"], hist["Low"], hist["Volume"]
    price = c.iloc[-1]
    signals, raw, mx = {}, 0, 0

    mas = [("EMA 10",ema(c,10)),("SMA 10",sma(c,10)),("EMA 20",ema(c,20)),
           ("SMA 20",sma(c,20)),("EMA 30",ema(c,30)),("SMA 30",sma(c,30)),
           ("EMA 50",ema(c,50)),("SMA 50",sma(c,50)),("EMA 100",ema(c,100)),
           ("SMA 100",sma(c,100)),("EMA 200",ema(c,200)),("SMA 200",sma(c,200)),
           ("Ichimoku",ichimoku_base(h,l,26)),("VWMA 20",vwma(c,v,20)),("HMA 9",hma(c,9))]
    for name, series in mas:
        s = sig_ma(price, series.iloc[-1])
        signals[name]=s; raw+=s; mx+=1

    def s_rsi(x):  return 1 if x<30 else (-1 if x>70 else 0)
    def s_stoch(x):return 1 if x<20 else (-1 if x>80 else 0)
    def s_cci(x):  return 1 if x<-100 else (-1 if x>100 else 0)
    def s_wpr(x):  return 1 if x<-80 else (-1 if x>-20 else 0)
    def s_srsi(x): return 1 if x<0.2 else (-1 if x>0.8 else 0)
    def s_uo(x):   return 1 if x<30 else (-1 if x>70 else 0)
    def s_sign(x): return 1 if x>0 else (-1 if x<0 else 0)

    adxv, pdi, mdi = adx_calc(h,l,c,14)
    def s_adx(a,p,m): return (1 if p>m else -1) if a>25 else 0

    ml, sig_l = macd_calc(c)
    w = 1.5
    oscs = [
        ("RSI 14",     s_rsi(rsi(c,14).iloc[-1])),
        ("Stoch %K",   s_stoch(stoch_k(h,l,c).iloc[-1])),
        ("CCI 20",     s_cci(cci(h,l,c).iloc[-1])),
        ("ADX 14",     s_adx(adxv.iloc[-1], pdi.iloc[-1], mdi.iloc[-1])),
        ("Awe. Osc.",  s_sign(awesome_osc(h,l).iloc[-1])),
        ("Momentum",   s_sign(momentum_ind(c).iloc[-1])),
        ("MACD",       s_sign(ml.iloc[-1]-sig_l.iloc[-1])),
        ("Stoch RSI",  s_srsi(stoch_rsi(c).iloc[-1])),
        ("Williams %R",s_wpr(williams_r(h,l,c).iloc[-1])),
        ("Bull/Bear",  s_sign(bbpower(h,l,c).iloc[-1])),
        ("Ult. Osc.",  s_uo(ult_osc(h,l,c).iloc[-1])),
    ]
    for name, s in oscs:
        if not pd.isna(s): signals[name]=s; raw+=s*w; mx+=w

    score = ((raw+mx)/(2*mx))*100
    return round(max(0, min(100, score)), 1), signals

# ─────────────────────────────────────────────────────────
#  DATA FETCHING  (cached)
# ─────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def get_info(ticker):
    try: return yf.Ticker(ticker).info
    except: return {}

@st.cache_data(ttl=300, show_spinner=False)
def get_hist(ticker):
    try:
        h = yf.Ticker(ticker).history(period="1y")
        return h if len(h)>50 else None
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
    m = {"strong_buy":"Strong Buy","buy":"Buy","hold":"Hold",
         "underperform":"Underperform","sell":"Sell"}
    return m.get((rec or "").lower().replace(" ","_"), rec or "—")

# ─────────────────────────────────────────────────────────
#  CUSTOM COMPONENTS
# ─────────────────────────────────────────────────────────
def metric_card(label, value, sub="", color="#c8953a"):
    st.markdown(f"""
    <div style="background:#181917;border:1px solid #2a2c2b;border-left:3px solid {color};
                border-radius:3px;padding:16px 20px;margin-bottom:4px;">
        <div style="font-size:9px;letter-spacing:0.18em;text-transform:uppercase;
                    color:#6b6e6c;margin-bottom:6px;">{label}</div>
        <div style="font-family:'Fraunces',serif;font-size:1.5rem;font-weight:300;
                    color:#e8e4dc;">{value}</div>
        <div style="font-size:11px;color:#6b6e6c;margin-top:4px;">{sub}</div>
    </div>""", unsafe_allow_html=True)

def signal_badge(s):
    if s==1:  return '<span style="color:#4caf7d;font-size:11px;">▲ BUY</span>'
    if s==-1: return '<span style="color:#e05c5c;font-size:11px;">▼ SELL</span>'
    return '<span style="color:#6b6e6c;font-size:11px;">● NEU</span>'

def score_gauge(score, ticker):
    color = score_color(score)
    label = score_label(score)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score or 0,
        number={"suffix":"/100","font":{"size":28,"color":"#e8e4dc","family":"Fraunces, serif"}},
        gauge={
            "axis":{"range":[0,100],"tickcolor":"#2a2c2b","tickfont":{"color":"#6b6e6c","size":10}},
            "bar":{"color":color,"thickness":0.3},
            "bgcolor":"#181917",
            "bordercolor":"#2a2c2b",
            "steps":[
                {"range":[0,30],"color":"#1a1210"},
                {"range":[30,45],"color":"#1a1512"},
                {"range":[45,55],"color":"#141a1a"},
                {"range":[55,70],"color":"#121a12"},
                {"range":[70,100],"color":"#101810"},
            ],
            "threshold":{"line":{"color":color,"width":3},"thickness":0.8,"value":score or 0}
        },
        title={"text":f"<b>{ticker}</b><br><span style='font-size:12px;color:{color}'>{label}</span>",
               "font":{"color":"#e8e4dc","family":"Fraunces, serif","size":16}}
    ))
    fig.update_layout(
        height=240, margin=dict(l=20,r=20,t=40,b=10),
        paper_bgcolor="#111210", font_color="#e8e4dc"
    )
    return fig

def price_chart(hist, ticker):
    if hist is None: return None
    c = hist["Close"]
    e20 = ema(c,20); e50 = ema(c,50); e200 = ema(c,200)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=c, name="Price",
        line=dict(color="#c8953a", width=2)))
    fig.add_trace(go.Scatter(x=hist.index, y=e20, name="EMA 20",
        line=dict(color="#5bc8c8", width=1, dash="dot"), opacity=0.7))
    fig.add_trace(go.Scatter(x=hist.index, y=e50, name="EMA 50",
        line=dict(color="#8b7ed8", width=1, dash="dot"), opacity=0.7))
    fig.add_trace(go.Scatter(x=hist.index, y=e200, name="EMA 200",
        line=dict(color="#e05c5c", width=1, dash="dot"), opacity=0.7))
    fig.update_layout(
        height=280, margin=dict(l=0,r=0,t=24,b=0),
        paper_bgcolor="#111210", plot_bgcolor="#111210",
        font=dict(color="#6b6e6c", family="DM Mono"),
        legend=dict(bgcolor="#181917", bordercolor="#2a2c2b",
                    font=dict(size=10, color="#a0a8a4")),
        xaxis=dict(showgrid=False, color="#6b6e6c", tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="#1f2020", color="#6b6e6c",
                   tickformat="$.2f", tickfont=dict(size=10)),
        title=dict(text=f"{ticker} — 1 Year Price + Key MAs",
                   font=dict(size=13, color="#e8e4dc", family="Fraunces, serif"),
                   x=0, xanchor="left", pad=dict(l=4)),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#181917", bordercolor="#2a2c2b",
                        font=dict(color="#e8e4dc", family="DM Mono", size=11))
    )
    return fig

def signals_chart(signals):
    ma_names  = ["EMA 10","SMA 10","EMA 20","SMA 20","EMA 30","SMA 30",
                 "EMA 50","SMA 50","EMA 100","SMA 100","EMA 200","SMA 200",
                 "Ichimoku","VWMA 20","HMA 9"]
    osc_names = ["RSI 14","Stoch %K","CCI 20","ADX 14","Awe. Osc.",
                 "Momentum","MACD","Stoch RSI","Williams %R","Bull/Bear","Ult. Osc."]
    all_names = ma_names + osc_names
    vals = [signals.get(n,0) for n in all_names]
    colors = ["#4caf7d" if v==1 else ("#e05c5c" if v==-1 else "#2a2c2b") for v in vals]
    labels = ["BUY" if v==1 else ("SELL" if v==-1 else "NEU") for v in vals]
    cats   = ["MA"]*15 + ["OSC"]*11

    fig = go.Figure(go.Bar(
        x=all_names, y=[1]*26, marker_color=colors,
        text=labels, textposition="inside",
        textfont=dict(size=9, color="#0b0a09", family="DM Mono"),
        hovertemplate="%{x}: %{text}<extra></extra>"
    ))
    fig.add_vline(x=14.5, line_color="#2a2c2b", line_width=1, line_dash="dot")
    fig.add_annotation(x=7, y=1.05, text="MOVING AVERAGES", showarrow=False,
        font=dict(size=9, color="#6b6e6c", family="DM Mono"), yref="paper")
    fig.add_annotation(x=20, y=1.05, text="OSCILLATORS", showarrow=False,
        font=dict(size=9, color="#6b6e6c", family="DM Mono"), yref="paper")
    fig.update_layout(
        height=180, margin=dict(l=0,r=0,t=30,b=40),
        paper_bgcolor="#111210", plot_bgcolor="#111210",
        xaxis=dict(showgrid=False, color="#6b6e6c",
                   tickfont=dict(size=8, color="#6b6e6c", family="DM Mono"),
                   tickangle=-45),
        yaxis=dict(visible=False),
        showlegend=False
    )
    return fig

# ─────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 0 24px;">
        <div style="font-size:9px;letter-spacing:0.25em;text-transform:uppercase;
                    color:#c8953a;margin-bottom:6px;">Equity Research Platform</div>
        <div style="font-family:'Fraunces',serif;font-size:1.5rem;font-weight:300;
                    color:#e8e4dc;line-height:1.2;">Torosian<br><em style="color:#c8953a;">Stock Insights</em></div>
        <div style="font-size:10px;color:#6b6e6c;margin-top:8px;">
            26 indicators · Live data · Free
        </div>
    </div>
    <hr style="border-color:#1f2020;margin:0 0 20px;">
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:9px;letter-spacing:0.15em;text-transform:uppercase;color:#6b6e6c;margin-bottom:8px;">Screener Filters</div>', unsafe_allow_html=True)

    all_sectors = sorted(set(s for _,_,s,_ in STOCK_UNIVERSE))
    sector = st.selectbox("Sector", ["ALL"] + all_sectors)

    cap = st.selectbox("Market Cap", ["All", "Large (>$10B)", "Mid ($2B–$10B)", "Small (<$2B)"])
    cap_map = {"All":"All","Large (>$10B)":"Large","Mid ($2B–$10B)":"Mid","Small (<$2B)":"Small"}
    cap_filter = cap_map[cap]

    risk_key = st.selectbox("Risk Tolerance", list(RISK_RANGES.keys()))
    beta_min, beta_max = RISK_RANGES[risk_key]

    horizon = st.radio("Investment Horizon", ["Short Term", "Long Term"])

    min_score = st.slider("Min Technical Score", 0, 90, 0, 5)
    top_n = st.slider("Results to Show", 3, 20, 8)

    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("Run Screener →", use_container_width=True)

    st.markdown("""
    <hr style="border-color:#1f2020;margin:20px 0 12px;">
    <div style="font-size:9px;color:#3a3c3b;line-height:1.8;">
        Data via Yahoo Finance<br>
        Refreshes every 5 min<br>
        Not financial advice
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:32px 0 24px;border-bottom:1px solid #1f2020;margin-bottom:32px;">
    <div style="font-size:10px;letter-spacing:0.2em;text-transform:uppercase;
                color:#c8953a;margin-bottom:8px;">Torosian Stock Insights</div>
    <h1 style="font-family:'Fraunces',serif;font-size:2.2rem;font-weight:300;
               color:#e8e4dc;margin:0;line-height:1.1;">
        Your personal <em style="color:#c8953a;">equity research</em> dashboard
    </h1>
    <p style="color:#6b6e6c;font-size:12px;margin-top:10px;">
        26 technical indicators · Moving averages · Oscillators · Analyst sentiment · Live from Yahoo Finance
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────
tab_screen, tab_deep, tab_compare = st.tabs([
    "📋  Screener", "🔍  Deep Dive", "⚔  Compare"
])

# ══════════════════════════════════════════════════════════
#  TAB 1 — SCREENER
# ══════════════════════════════════════════════════════════
with tab_screen:
    if not run:
        st.markdown("""
        <div style="text-align:center;padding:64px 0;color:#3a3c3b;">
            <div style="font-size:3rem;margin-bottom:16px;">📈</div>
            <div style="font-family:'Fraunces',serif;font-size:1.3rem;color:#6b6e6c;font-weight:300;">
                Configure your filters in the sidebar and press <em>Run Screener</em>
            </div>
            <div style="font-size:11px;color:#2a2c2b;margin-top:8px;">
                Analysing up to 58 stocks across 7 sectors
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        # Filter universe
        candidates = [
            (t,n,s,c) for t,n,s,c in STOCK_UNIVERSE
            if (sector=="ALL" or s==sector)
            and (cap_filter=="All" or c==cap_filter)
        ]

        if not candidates:
            st.error("No stocks match your filters. Try broadening the sector or cap size.")
            st.stop()

        results = []
        progress = st.progress(0, text="Fetching live data…")

        for i, (ticker, name, sec, cap_size) in enumerate(candidates):
            progress.progress((i+1)/len(candidates), text=f"Analysing {ticker}…")
            info = get_info(ticker)
            beta = info.get("beta")
            if beta is None or not (beta_min <= beta < beta_max):
                continue
            hist  = get_hist(ticker)
            score, signals = compute_score(hist)
            if score is None or score < min_score:
                continue

            price  = info.get("currentPrice") or info.get("regularMarketPrice")
            pe     = info.get("trailingPE")
            div    = (info.get("dividendYield") or 0)*100
            mcap   = info.get("marketCap")
            target = info.get("targetMeanPrice")
            upside = ((target-price)/price*100) if price and target else None
            rec    = analyst_label(info.get("recommendationKey",""))
            n_ana  = info.get("numberOfAnalystOpinions")

            results.append({
                "ticker": ticker, "name": name, "sector": sec, "cap": cap_size,
                "price": price, "beta": beta, "pe": pe, "div": div,
                "mcap": mcap, "target": target, "upside": upside,
                "rec": rec, "n_analysts": n_ana,
                "score": score, "signals": signals, "hist": hist, "info": info,
                "_div": div, "_score": score or 0,
            })

        progress.empty()

        if not results:
            st.error("No stocks passed all filters. Try loosening the minimum score or risk tolerance.")
            st.stop()

        # Sort
        if horizon == "Long Term":
            results.sort(key=lambda x: (x["_score"], x["_div"]), reverse=True)
        else:
            results.sort(key=lambda x: x["_score"], reverse=True)
        top = results[:top_n]

        # ── Summary bar ────────────────────────────────
        buys    = sum(1 for r in top if r["score"] and r["score"]>=55)
        neutral = sum(1 for r in top if r["score"] and 45<=r["score"]<55)
        sells   = sum(1 for r in top if r["score"] and r["score"]<45)
        avg_sc  = round(sum(r["score"] for r in top if r["score"])/len(top),1)

        c1,c2,c3,c4 = st.columns(4)
        with c1: metric_card("Stocks Found", str(len(top)), f"of {len(results)} matched", "#c8953a")
        with c2: metric_card("Avg Score", f"{avg_sc}/100", score_label(avg_sc), score_color(avg_sc))
        with c3: metric_card("Buy Signals", str(buys), f"{neutral} neutral · {sells} sell", "#4caf7d")
        with c4: metric_card("Sorted By", "Score" if horizon=="Short Term" else "Score + Div Yield", horizon, "#5bc8c8")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Results table ───────────────────────────────
        st.markdown("""<div style="font-size:9px;letter-spacing:0.18em;text-transform:uppercase;
                    color:#6b6e6c;margin-bottom:12px;">Results</div>""", unsafe_allow_html=True)

        rows = []
        for r in top:
            rows.append({
                "Ticker":   r["ticker"],
                "Company":  r["name"],
                "Cap":      r["cap"],
                "Price":    f"${r['price']:.2f}" if r["price"] else "—",
                "Beta":     f"{r['beta']:.2f}" if r["beta"] else "—",
                "P/E":      f"{r['pe']:.1f}" if r["pe"] else "—",
                "Div %":    f"{r['div']:.2f}%",
                "Mkt Cap":  fmt_cap(r["mcap"]),
                "Upside":   f"{r['upside']:+.1f}%" if r["upside"] else "—",
                "Consensus":r["rec"],
                "Score":    r["score"],
                "Signal":   score_label(r["score"]),
            })

        df = pd.DataFrame(rows)

        def style_table(df):
            def color_score(val):
                try: v=float(str(val).replace("/100",""))
                except: return ""
                if v>=70: return "color:#4caf7d;font-weight:500"
                if v>=55: return "color:#8bc98b"
                if v>=45: return "color:#5bc8c8"
                if v>=30: return "color:#e07b5c"
                return "color:#e05c5c"

            def color_upside(val):
                if val=="—": return ""
                try: v=float(str(val).replace("%","").replace("+",""))
                except: return ""
                return "color:#4caf7d" if v>=0 else "color:#e05c5c"

            def color_consensus(val):
                m = {"Strong Buy":"color:#4caf7d","Buy":"color:#8bc98b",
                     "Hold":"color:#5bc8c8","Underperform":"color:#e07b5c","Sell":"color:#e05c5c"}
                return m.get(val,"")

            styled = df.style\
                .applymap(color_score, subset=["Score"])\
                .applymap(color_upside, subset=["Upside"])\
                .applymap(color_consensus, subset=["Consensus","Signal"])\
                .set_properties(**{
                    "background-color":"#111210",
                    "color":"#e8e4dc",
                    "border-color":"#1f2020",
                    "font-family":"DM Mono, monospace",
                    "font-size":"12px",
                })\
                .set_table_styles([
                    {"selector":"th","props":[
                        ("background-color","#0b0a09"),("color","#6b6e6c"),
                        ("font-size","9px"),("letter-spacing","0.15em"),
                        ("text-transform","uppercase"),("font-family","DM Mono, monospace"),
                        ("border-color","#1f2020"),("padding","10px 12px"),
                    ]},
                    {"selector":"td","props":[("padding","10px 12px"),("border-color","#1f2020")]},
                    {"selector":"tr:hover td","props":[("background-color","#181917")]},
                ])
            return styled

        st.dataframe(style_table(df), use_container_width=True, hide_index=True, height=380)

        # ── Signal breakdown for top stock ─────────────
        top_r = top[0]
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""<div style="font-size:9px;letter-spacing:0.18em;text-transform:uppercase;
                    color:#6b6e6c;margin-bottom:12px;">Signal Breakdown — {top_r['ticker']} (Top Pick)</div>""",
                    unsafe_allow_html=True)

        col_chart, col_summary = st.columns([2,1])
        with col_chart:
            fig_sig = signals_chart(top_r["signals"])
            st.plotly_chart(fig_sig, use_container_width=True, config={"displayModeBar":False})

        with col_summary:
            sigs = top_r["signals"]
            ma_names = ["EMA 10","SMA 10","EMA 20","SMA 20","EMA 30","SMA 30",
                        "EMA 50","SMA 50","EMA 100","SMA 100","EMA 200","SMA 200",
                        "Ichimoku","VWMA 20","HMA 9"]
            osc_names= ["RSI 14","Stoch %K","CCI 20","ADX 14","Awe. Osc.",
                        "Momentum","MACD","Stoch RSI","Williams %R","Bull/Bear","Ult. Osc."]
            ma_b  = sum(1 for n in ma_names  if sigs.get(n,0)==1)
            ma_s  = sum(1 for n in ma_names  if sigs.get(n,0)==-1)
            osc_b = sum(1 for n in osc_names if sigs.get(n,0)==1)
            osc_s = sum(1 for n in osc_names if sigs.get(n,0)==-1)
            total_b = ma_b+osc_b; total_s = ma_s+osc_s
            pct_b = total_b/26*100

            interp = ("Strong bullish consensus" if pct_b>=65
                      else "Mildly bullish lean" if pct_b>=50
                      else "Bearish lean" if total_s>total_b
                      else "Mixed signals")
            interp_color = ("#4caf7d" if pct_b>=65 else "#8bc98b" if pct_b>=50
                            else "#e05c5c" if total_s>total_b else "#5bc8c8")

            st.markdown(f"""
            <div style="background:#181917;border:1px solid #2a2c2b;padding:20px;border-radius:3px;">
                <div style="font-size:9px;letter-spacing:0.15em;text-transform:uppercase;
                            color:#6b6e6c;margin-bottom:12px;">Reading</div>
                <div style="font-family:'Fraunces',serif;font-size:1.1rem;color:{interp_color};
                            margin-bottom:16px;">{interp}</div>
                <div style="font-size:11px;color:#a0a8a4;line-height:2;">
                    <span style="color:#4caf7d">▲ {total_b} Buy</span> &nbsp;
                    <span style="color:#e05c5c">▼ {total_s} Sell</span> &nbsp;
                    <span style="color:#6b6e6c">● {26-total_b-total_s} Neutral</span><br>
                    MAs: <span style="color:#4caf7d">{ma_b}↑</span> / <span style="color:#e05c5c">{ma_s}↓</span><br>
                    Oscs: <span style="color:#4caf7d">{osc_b}↑</span> / <span style="color:#e05c5c">{osc_s}↓</span>
                </div>
                <hr style="border-color:#2a2c2b;margin:12px 0;">
                <div style="font-size:9px;letter-spacing:0.12em;text-transform:uppercase;
                            color:#6b6e6c;margin-bottom:6px;">Analyst Consensus</div>
                <div style="font-size:12px;color:#e8e4dc;">{top_r['rec']}</div>
                <div style="font-size:11px;color:#6b6e6c;">
                    {f"{top_r['n_analysts']} analysts" if top_r['n_analysts'] else ""}
                    {f" · Target {top_r['upside']:+.1f}%" if top_r['upside'] else ""}
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  TAB 2 — DEEP DIVE
# ══════════════════════════════════════════════════════════
with tab_deep:
    col_in, col_btn = st.columns([3,1])
    with col_in:
        dive_ticker = st.text_input("", placeholder="Enter ticker e.g. NVDA, AAPL, TSLA",
                                    label_visibility="collapsed").strip().upper()
    with col_btn:
        dive_run = st.button("Analyse →", key="dive_btn", use_container_width=True)

    if dive_run and dive_ticker:
        with st.spinner(f"Loading {dive_ticker}…"):
            info  = get_info(dive_ticker)
            hist  = get_hist(dive_ticker)
            score, signals = compute_score(hist)

        if not info:
            st.error(f"Could not find data for {dive_ticker}. Check the ticker symbol.")
            st.stop()

        name   = info.get("longName", dive_ticker)
        price  = info.get("currentPrice") or info.get("regularMarketPrice")
        beta   = info.get("beta")
        pe     = info.get("trailingPE")
        div    = (info.get("dividendYield") or 0)*100
        mcap   = info.get("marketCap")
        target = info.get("targetMeanPrice")
        sec    = info.get("sector","—")
        rec    = analyst_label(info.get("recommendationKey",""))
        n_ana  = info.get("numberOfAnalystOpinions")
        rec_mean=info.get("recommendationMean")
        upside = ((target-price)/price*100) if price and target else None
        desc   = info.get("longBusinessSummary","")

        st.markdown(f"""
        <div style="margin-bottom:24px;">
            <div style="font-size:9px;letter-spacing:0.2em;text-transform:uppercase;
                        color:#c8953a;margin-bottom:4px;">{sec}</div>
            <h2 style="font-family:'Fraunces',serif;font-size:1.8rem;font-weight:300;
                       color:#e8e4dc;margin:0;">{name}
                <span style="color:#6b6e6c;font-size:1rem;"> ({dive_ticker})</span>
            </h2>
        </div>""", unsafe_allow_html=True)

        # Fundamentals row
        cols = st.columns(6)
        fundamentals = [
            ("Price", f"${price:.2f}" if price else "—", ""),
            ("Market Cap", fmt_cap(mcap), ""),
            ("Beta", f"{beta:.2f}" if beta else "—", "volatility vs market"),
            ("P/E Ratio", f"{pe:.1f}" if pe else "—", ""),
            ("Div Yield", f"{div:.2f}%", ""),
            ("Analyst Target", f"${target:.2f}" if target else "—",
             f"{upside:+.1f}% upside" if upside else ""),
        ]
        for col, (lbl, val, sub) in zip(cols, fundamentals):
            with col: metric_card(lbl, val, sub)

        st.markdown("<br>", unsafe_allow_html=True)

        # Score gauge + price chart
        col_gauge, col_chart = st.columns([1,2])
        with col_gauge:
            if score:
                st.plotly_chart(score_gauge(score, dive_ticker),
                                use_container_width=True, config={"displayModeBar":False})
            # Analyst block
            rec_color = ("#4caf7d" if rec in ("Strong Buy","Buy")
                         else "#5bc8c8" if rec=="Hold"
                         else "#e05c5c")
            st.markdown(f"""
            <div style="background:#181917;border:1px solid #2a2c2b;padding:16px;
                        border-radius:3px;margin-top:4px;">
                <div style="font-size:9px;letter-spacing:0.15em;text-transform:uppercase;
                            color:#6b6e6c;margin-bottom:8px;">Analyst Sentiment</div>
                <div style="font-family:'Fraunces',serif;font-size:1.1rem;
                            color:{rec_color};">{rec}</div>
                <div style="font-size:11px;color:#6b6e6c;margin-top:4px;">
                    {f"{n_ana} analysts covering" if n_ana else ""}
                    {f"<br>Mean rating: {rec_mean:.1f}/5" if rec_mean else ""}
                </div>
            </div>""", unsafe_allow_html=True)

        with col_chart:
            fig_price = price_chart(hist, dive_ticker)
            if fig_price:
                st.plotly_chart(fig_price, use_container_width=True,
                                config={"displayModeBar":False})

        # Signal breakdown
        if signals:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""<div style="font-size:9px;letter-spacing:0.18em;text-transform:uppercase;
                        color:#6b6e6c;margin-bottom:12px;">All 26 Indicators</div>""",
                        unsafe_allow_html=True)
            fig_sig = signals_chart(signals)
            st.plotly_chart(fig_sig, use_container_width=True, config={"displayModeBar":False})

        # Description
        if desc:
            st.markdown(f"""
            <div style="background:#181917;border:1px solid #2a2c2b;padding:20px;
                        border-radius:3px;margin-top:8px;">
                <div style="font-size:9px;letter-spacing:0.15em;text-transform:uppercase;
                            color:#6b6e6c;margin-bottom:10px;">About</div>
                <div style="font-size:12px;color:#a0a8a4;line-height:1.8;">
                    {desc[:400]}{'…' if len(desc)>400 else ''}
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:64px 0;color:#3a3c3b;">
            <div style="font-size:3rem;margin-bottom:16px;">🔍</div>
            <div style="font-family:'Fraunces',serif;font-size:1.3rem;color:#6b6e6c;font-weight:300;">
                Enter any ticker symbol above to get a full technical + fundamental deep dive
            </div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  TAB 3 — COMPARE
# ══════════════════════════════════════════════════════════
with tab_compare:
    c1, c2, c3 = st.columns([2,2,1])
    with c1: t1 = st.text_input("", placeholder="First ticker e.g. AAPL",
                                  label_visibility="collapsed", key="t1").strip().upper()
    with c2: t2 = st.text_input("", placeholder="Second ticker e.g. MSFT",
                                  label_visibility="collapsed", key="t2").strip().upper()
    with c3: cmp_run = st.button("Compare →", key="cmp_btn", use_container_width=True)

    if cmp_run and t1 and t2:
        with st.spinner(f"Loading {t1} and {t2}…"):
            data = {}
            for tk in [t1, t2]:
                info  = get_info(tk)
                hist  = get_hist(tk)
                score, sigs = compute_score(hist)
                data[tk] = {"info":info,"hist":hist,"score":score,"signals":sigs}

        st.markdown(f"""
        <div style="font-family:'Fraunces',serif;font-size:1.5rem;font-weight:300;
                    color:#e8e4dc;margin-bottom:24px;">
            {t1} <span style="color:#c8953a;">vs</span> {t2}
        </div>""", unsafe_allow_html=True)

        # Score gauges
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(score_gauge(data[t1]["score"], t1),
                            use_container_width=True, config={"displayModeBar":False})
        with g2:
            st.plotly_chart(score_gauge(data[t2]["score"], t2),
                            use_container_width=True, config={"displayModeBar":False})

        # Winner callout
        s1, s2 = data[t1]["score"] or 0, data[t2]["score"] or 0
        winner = t1 if s1>s2 else t2
        margin = abs(s1-s2)
        st.markdown(f"""
        <div style="background:#181917;border:1px solid #c8953a33;padding:16px 24px;
                    border-radius:3px;margin-bottom:24px;text-align:center;">
            <span style="font-size:10px;letter-spacing:0.15em;text-transform:uppercase;
                         color:#6b6e6c;">Technical Edge &nbsp;→&nbsp; </span>
            <span style="font-family:'Fraunces',serif;font-size:1.1rem;
                         color:#c8953a;">{winner}</span>
            <span style="font-size:11px;color:#6b6e6c;"> by {margin:.1f} points</span>
        </div>""", unsafe_allow_html=True)

        # Fundamentals comparison
        st.markdown("""<div style="font-size:9px;letter-spacing:0.18em;text-transform:uppercase;
                    color:#6b6e6c;margin-bottom:12px;">Fundamentals</div>""", unsafe_allow_html=True)

        def gv(tk, key):
            v = data[tk]["info"].get(key)
            return v

        rows_cmp = []
        metrics = [
            ("Price",       lambda tk: f"${gv(tk,'currentPrice'):.2f}" if gv(tk,'currentPrice') else "—"),
            ("Market Cap",  lambda tk: fmt_cap(gv(tk,'marketCap'))),
            ("Beta",        lambda tk: f"{gv(tk,'beta'):.2f}" if gv(tk,'beta') else "—"),
            ("P/E Ratio",   lambda tk: f"{gv(tk,'trailingPE'):.1f}" if gv(tk,'trailingPE') else "—"),
            ("Div Yield",   lambda tk: f"{(gv(tk,'dividendYield') or 0)*100:.2f}%"),
            ("Analyst Target", lambda tk: f"${gv(tk,'targetMeanPrice'):.2f}" if gv(tk,'targetMeanPrice') else "—"),
            ("Consensus",   lambda tk: analyst_label(gv(tk,'recommendationKey') or "")),
            ("Sector",      lambda tk: gv(tk,'sector') or "—"),
        ]
        for label, fn in metrics:
            rows_cmp.append({"Metric": label, t1: fn(t1), t2: fn(t2)})

        df_cmp = pd.DataFrame(rows_cmp).set_index("Metric")
        st.dataframe(df_cmp.style.set_properties(**{
            "background-color":"#111210","color":"#e8e4dc",
            "border-color":"#1f2020","font-family":"DM Mono, monospace","font-size":"12px"
        }).set_table_styles([{
            "selector":"th","props":[("background-color","#0b0a09"),("color","#6b6e6c"),
            ("font-size","9px"),("letter-spacing","0.15em"),("text-transform","uppercase"),
            ("border-color","#1f2020"),("padding","10px 14px")]
        },{"selector":"td","props":[("padding","10px 14px"),("border-color","#1f2020")]}]),
        use_container_width=True)

        # Indicator disagreements
        sig1, sig2 = data[t1]["signals"], data[t2]["signals"]
        if sig1 and sig2:
            disagree = {k for k in sig1 if sig1.get(k,0)!=sig2.get(k,0)}
            if disagree:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("""<div style="font-size:9px;letter-spacing:0.18em;text-transform:uppercase;
                            color:#6b6e6c;margin-bottom:12px;">Where They Disagree</div>""",
                            unsafe_allow_html=True)
                fa = [k for k in disagree if sig1.get(k,0)==1]
                fb = [k for k in disagree if sig2.get(k,0)==1]
                da, db = st.columns(2)
                with da:
                    st.markdown(f"""
                    <div style="background:#181917;border:1px solid #2a2c2b;padding:16px;border-radius:3px;">
                        <div style="font-size:9px;letter-spacing:0.15em;text-transform:uppercase;
                                    color:#4caf7d;margin-bottom:10px;">{t1} bullish on</div>
                        <div style="font-size:11px;color:#a0a8a4;line-height:2;">
                            {', '.join(fa) if fa else 'None'}
                        </div>
                    </div>""", unsafe_allow_html=True)
                with db:
                    st.markdown(f"""
                    <div style="background:#181917;border:1px solid #2a2c2b;padding:16px;border-radius:3px;">
                        <div style="font-size:9px;letter-spacing:0.15em;text-transform:uppercase;
                                    color:#4caf7d;margin-bottom:10px;">{t2} bullish on</div>
                        <div style="font-size:11px;color:#a0a8a4;line-height:2;">
                            {', '.join(fb) if fb else 'None'}
                        </div>
                    </div>""", unsafe_allow_html=True)

        # Overlaid price chart
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div style="font-size:9px;letter-spacing:0.18em;text-transform:uppercase;
                    color:#6b6e6c;margin-bottom:12px;">Normalised Price Performance (1 Year)</div>""",
                    unsafe_allow_html=True)
        fig_cmp = go.Figure()
        for tk, color in [(t1,"#c8953a"),(t2,"#5bc8c8")]:
            h = data[tk]["hist"]
            if h is not None:
                norm = h["Close"]/h["Close"].iloc[0]*100
                fig_cmp.add_trace(go.Scatter(x=h.index, y=norm, name=tk,
                    line=dict(color=color, width=2)))
        fig_cmp.update_layout(
            height=260, margin=dict(l=0,r=0,t=10,b=0),
            paper_bgcolor="#111210", plot_bgcolor="#111210",
            font=dict(color="#6b6e6c", family="DM Mono"),
            legend=dict(bgcolor="#181917", bordercolor="#2a2c2b",
                        font=dict(size=11, color="#e8e4dc")),
            xaxis=dict(showgrid=False, color="#6b6e6c", tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor="#1f2020", color="#6b6e6c",
                       ticksuffix="%", tickfont=dict(size=10)),
            hovermode="x unified",
            hoverlabel=dict(bgcolor="#181917", bordercolor="#2a2c2b",
                            font=dict(color="#e8e4dc", family="DM Mono", size=11))
        )
        st.plotly_chart(fig_cmp, use_container_width=True, config={"displayModeBar":False})

    else:
        st.markdown("""
        <div style="text-align:center;padding:64px 0;color:#3a3c3b;">
            <div style="font-size:3rem;margin-bottom:16px;">⚔</div>
            <div style="font-family:'Fraunces',serif;font-size:1.3rem;color:#6b6e6c;font-weight:300;">
                Enter two ticker symbols above to compare them head-to-head
            </div>
        </div>""", unsafe_allow_html=True)
