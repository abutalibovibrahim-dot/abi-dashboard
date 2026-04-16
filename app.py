"""
═══════════════════════════════════════════════════════════════════
  GLOBAL BEVERAGES TRADING COMPARABLES DASHBOARD
  Focus: Anheuser-Busch InBev Short Thesis
  Stack: Python · Streamlit · yfinance · plotly
═══════════════════════════════════════════════════════════════════
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
import json
import os
import warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────
# PERSISTENT CACHE — last known good data
# Streamlit Cloud gives each app a writable /tmp directory.
# We save the last successful fetch here as JSON so if Yahoo
# Finance is rate-limiting, the dashboard can show stale data
# rather than going blank. The timestamp tells the user how
# old the data is so they know it may not be live.
# ──────────────────────────────────────────────
CACHE_FILE = "/tmp/abi_dashboard_cache.json"

def save_cache(df: pd.DataFrame, prices: pd.DataFrame, fetched_at: str):
    """
    Save last known good data to TWO places:
    1. st.session_state  — survives page interactions, lost on app restart
    2. /tmp on disk      — survives Streamlit TTL expiry but lost on container restart
    Using both maximises the chance of having fallback data available.
    """
    payload = {
        "fetched_at": fetched_at,
        "fundamentals": df.to_json(orient="records"),
        "prices": prices.to_json(orient="split") if not prices.empty else None,
    }
    # Save to session state (always works)
    st.session_state["_data_cache"] = payload
    # Save to disk (best effort)
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(payload, f)
    except Exception:
        pass


def load_cache() -> tuple:
    """
    Load last known good data. Tries session_state first (fastest),
    then disk. Returns (df, prices, fetched_at) or (None, None, None).
    """
    # Try session state first
    payload = st.session_state.get("_data_cache")
    # Fall back to disk
    if not payload:
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, "r") as f:
                    payload = json.load(f)
        except Exception:
            pass
    if not payload:
        return None, None, None
    try:
        df     = pd.read_json(payload["fundamentals"], orient="records")
        prices = pd.read_json(payload["prices"], orient="split") if payload.get("prices") else pd.DataFrame()
        return df, prices, payload.get("fetched_at", "unknown")
    except Exception:
        return None, None, None

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Beverages Comps | ABI Short Thesis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# CUSTOM CSS — Finance-grade dark theme
# ──────────────────────────────────────────────
# ──────────────────────────────────────────────
# DARK THEME CONSTANTS
# Always dark — no switching logic needed.
# All colours defined once here as a dict so they can be
# referenced in both CSS (via f-string injection) and
# Python components like Plotly and pandas styler.
# ──────────────────────────────────────────────
_T = {
    "bg_page":      "#0a0e14",
    "bg_card":      "#0d1117",
    "bg_card2":     "#111827",
    "border":       "#1e2530",
    "text_primary": "#f0f4ff",
    "text_muted":   "#9aa3b8",
    "text_faint":   "#6b7a99",
    "text_ghost":   "#2a3550",
    "chart_grid":   "rgba(100,120,150,0.12)",
    "chart_line":   "rgba(100,120,150,0.22)",
    "chart_font":   "#6b7a99",
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

/* Force dark on every element — overrides Streamlit light mode, system preference,
   and browser defaults. Using !important throughout ensures nothing leaks through. */
html, body, [class*="css"], .stApp, section[data-testid="stSidebar"],
div[data-testid="stAppViewContainer"], div[data-testid="stHeader"],
div[data-testid="stToolbar"], .main, .block-container {{
    background-color: {_T["bg_page"]} !important;
    color: {_T["text_muted"]} !important;
}}

.main .block-container {{
    padding: 1.5rem 2rem;
    max-width: 1400px;
    background-color: {_T["bg_page"]} !important;
}}

[data-testid="stSidebar"] {{
    background-color: {_T["bg_card"]} !important;
    border-right: 1px solid {_T["border"]} !important;
}}
[data-testid="stSidebar"] .block-container {{ padding: 1.5rem 1rem; }}

/* ── Header ── */
.header-strip {{
    background: linear-gradient(90deg, {_T["bg_card"]} 0%, {_T["bg_card2"]} 100%);
    border: 1px solid {_T["border"]};
    border-left: 3px solid #e63946;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
.header-title {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    color: {_T["text_primary"]};
    letter-spacing: 0.05em;
    text-transform: uppercase;
}}
.header-sub {{
    font-size: 0.75rem;
    color: {_T["text_faint"]};
    font-family: 'IBM Plex Mono', monospace;
    margin-top: 0.2rem;
}}
.header-badge {{
    background: #e63946;
    color: white;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.25rem 0.6rem;
    letter-spacing: 0.08em;
}}

/* ── Section labels ── */
.section-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: {_T["text_faint"]};
    letter-spacing: 0.15em;
    text-transform: uppercase;
    border-bottom: 1px solid {_T["border"]};
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
    margin-top: 1.5rem;
}}

/* ── KPI cards ── */
.kpi-card {{
    background: {_T["bg_card"]};
    border: 1px solid {_T["border"]};
    padding: 1rem 1.2rem;
}}
.kpi-card.focus {{ border-left: 3px solid #e63946; }}
.kpi-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: {_T["text_faint"]};
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}}
.kpi-value {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.4rem;
    font-weight: 600;
    color: {_T["text_primary"]};
}}

/* ── Pills ── */
.pill {{
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    padding: 0.15rem 0.5rem;
    margin: 0.15rem;
    border: 1px solid;
}}
.pill-red   {{ border-color:#e63946; color:#e63946; background:rgba(230,57,70,0.08); }}
.pill-teal  {{ border-color:#2dd4bf; color:#2dd4bf; background:rgba(45,212,191,0.08); }}
.pill-amber {{ border-color:#f59e0b; color:#f59e0b; background:rgba(245,158,11,0.08); }}

/* ── Inputs & controls ── */
.stTextInput input, .stSelectbox > div > div,
input, select, textarea {{
    background: {_T["bg_card"]} !important;
    border: 1px solid {_T["border"]} !important;
    color: {_T["text_primary"]} !important;
    font-family: 'IBM Plex Mono', monospace !important;
}}
label, .stSelectbox label, .stMultiselect label,
.stSlider label, .stTextInput label {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    color: {_T["text_faint"]} !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}}
.stButton > button {{
    background: {_T["bg_card"]} !important;
    border: 1px solid {_T["border"]} !important;
    color: {_T["text_muted"]} !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
}}
.stButton > button:hover {{
    border-color: #e63946 !important;
    color: #e63946 !important;
}}

/* ── Expander ── */
div[data-testid="stExpander"] {{
    background: {_T["bg_card"]} !important;
    border: 1px solid {_T["border"]} !important;
}}

/* ── DataFrame ── */
.stDataFrame, [data-testid="stDataFrame"] {{
    background: {_T["bg_card"]} !important;
}}
.stDataFrame tbody tr td, .stDataFrame thead tr th {{
    background-color: {_T["bg_card"]} !important;
    color: {_T["text_muted"]} !important;
    border-color: {_T["border"]} !important;
}}

/* ── Alerts / warnings ── */
.stAlert {{
    background: {_T["bg_card"]} !important;
    border: 1px solid {_T["border"]} !important;
    color: {_T["text_muted"]} !important;
}}

/* ── Misc ── */
h1, h2, h3 {{
    font-family: 'IBM Plex Mono', monospace !important;
    color: {_T["text_primary"]} !important;
}}
hr {{ border-color: {_T["border"]} !important; opacity: 1 !important; }}
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {_T["bg_page"]}; }}
::-webkit-scrollbar-thumb {{ background: {_T["border"]}; border-radius: 2px; }}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# CONSTANTS — DEFAULT PEER GROUP
# ──────────────────────────────────────────────
DEFAULT_PEERS = {
    "BUD":      "Anheuser-Busch InBev",
    "HEINY":    "Heineken",
    "CBRL.L":   "Carlsberg",
    "TAP":      "Molson Coors",
    "STZ":      "Constellation Brands",
    "DEO":      "Diageo",
    "ABEV":     "Ambev",
}

FOCUS_TICKER = "BUD"

COLORS = {
    "BUD":    "#e63946",   # red  — focus / short
    "HEINY":  "#2dd4bf",
    "CBRL.L": "#60a5fa",
    "TAP":    "#f59e0b",
    "STZ":    "#a78bfa",
    "DEO":    "#34d399",
    "ABEV":   "#fb923c",
    "default":"#6b7a99",
}


# ──────────────────────────────────────────────
# DATA LAYER
# Strategy: use fast_info + financials endpoints instead of .info
# .info is the most rate-limited Yahoo Finance endpoint.
# fast_info, .financials, and .balance_sheet use separate endpoints
# that are significantly more reliable on shared cloud IPs.
# ──────────────────────────────────────────────

def _safe(val, default=None):
    """Return val if it is a real non-zero number, else default."""
    try:
        if val is None or (isinstance(val, float) and (val != val)):  # NaN check
            return default
        return val if val != 0 else default
    except Exception:
        return default


def _parse_yield(raw) -> float | None:
    """
    Yahoo Finance returns dividendYield inconsistently:
    - Most tickers: decimal form  e.g. 0.0142  → means 1.42%
    - Some tickers: already as %  e.g. 1.42    → means 1.42%
    - Zero dividend payers: 0.0   → should show 0.00%, not None
    - No dividend data: None      → show dash

    Rule: if value exists (including 0), treat as decimal and multiply by 100.
    Cap sanity check at 30% — anything above is almost certainly already
    in percentage form, so we use it as-is.
    """
    if raw is None:
        return None
    try:
        val = float(raw)
        if val > 0.30:
            # Already in percentage form (e.g. 1.42 meaning 1.42%)
            return round(val, 2)
        else:
            # Decimal form (e.g. 0.0142 meaning 1.42%)
            return round(val * 100, 2)
    except (TypeError, ValueError):
        return None


def _get_ticker_data(tkr: str) -> dict:
    """
    Fetch all available data for one ticker as fast as possible.
    Strategy: fire all requests with minimal delay, no long retry loops.
    If a request fails we skip it and use what we got — partial data
    is better than waiting 45 seconds for complete data.
    The 4-hour cache means we only hit Yahoo once every 4 hours per ticker.
    """
    result = {"ticker": tkr}
    t = yf.Ticker(tkr)

    # ── fast_info: price and market cap — most reliable endpoint ──
    # Separate try block so a failure here doesn't block anything else
    try:
        fi = t.fast_info
        p = fi.last_price
        m = fi.market_cap
        # Explicit None checks — do not use _safe() here because
        # _safe() converts 0 to None which would hide $0 price edge cases
        result["price"]       = float(p) if p is not None else None
        result["mktcap"]      = float(m) if m is not None else None
        result["week52_high"] = float(fi.fifty_two_week_high) if fi.fifty_two_week_high else None
        result["week52_low"]  = float(fi.fifty_two_week_low)  if fi.fifty_two_week_low  else None
    except Exception:
        pass

    # ── .info: multiples and ratios ──
    try:
        info = t.info
        if info and len(info) > 5:
            def g(k): return _safe(info.get(k))
            result["name"]        = info.get("shortName") or tkr
            result["ev"]          = g("enterpriseValue")
            result["ev_ebitda"]   = g("enterpriseToEbitda")
            result["ev_revenue"]  = g("enterpriseToRevenue")
            result["pe"]          = g("trailingPE")
            result["pb"]          = g("priceToBook")
            result["div_yield"]   = g("dividendYield")
            result["payout"]      = g("payoutRatio")
            result["beta"]        = g("beta")
            result["short_pct"]   = g("shortPercentOfFloat")
            result["net_margin"]  = g("profitMargins")
            result["rev_growth"]  = g("revenueGrowth")
            result["total_debt"]  = g("totalDebt")
            result["cash"]        = g("totalCash")
            result["ebitda_info"] = g("ebitda")
            result["revenue_info"]= g("totalRevenue")
    except Exception:
        pass

    # ── financials: income statement ──
    try:
        fs = t.financials
        if fs is not None and not fs.empty:
            col = fs.iloc[:, 0]
            def frow(lbl):
                m = [i for i in col.index if lbl.lower() in str(i).lower()]
                return float(col[m[0]]) if m else None
            result["revenue_fs"] = _safe(frow("Total Revenue"))
            result["ebitda_fs"]  = _safe(frow("EBITDA"))
    except Exception:
        pass

    # ── balance sheet: debt and cash ──
    try:
        bs = t.balance_sheet
        if bs is not None and not bs.empty:
            col = bs.iloc[:, 0]
            def brow(lbl):
                m = [i for i in col.index if lbl.lower() in str(i).lower()]
                return float(col[m[0]]) if m else None
            result["debt_bs"] = _safe(brow("Total Debt"))
            result["cash_bs"] = _safe(brow("Cash And Cash Equivalents"))
    except Exception:
        pass

    return result


@st.cache_data(ttl=14400, show_spinner=False)
def fetch_fundamentals(tickers: list[str]) -> pd.DataFrame:
    """
    Build comps table. One request per ticker, no long retry waits.
    ttl=14400 = 4 hour cache so we fetch as infrequently as possible.
    """
    rows = []
    progress = st.progress(0, text="Fetching market data...")

    for i, tkr in enumerate(tickers):
        progress.progress(i / len(tickers), text=f"Fetching {tkr}... ({i+1}/{len(tickers)})")
        time.sleep(0.8)   # small stagger — avoids burst hitting Yahoo
        try:
            d = _get_ticker_data(tkr)

            # Prefer filing data, fall back to .info data
            revenue = d.get("revenue_fs")  or d.get("revenue_info")
            ebitda  = d.get("ebitda_fs")   or d.get("ebitda_info")
            debt    = d.get("debt_bs")     or d.get("total_debt")
            cash    = d.get("cash_bs")     or d.get("cash")
            price   = d.get("price")
            mktcap  = d.get("mktcap")

            net_debt        = (debt - cash)        if (debt is not None and cash is not None) else None
            ebitda_margin   = (ebitda / revenue)   if (ebitda and revenue)                    else None
            net_debt_ebitda = (net_debt / ebitda)  if (net_debt is not None and ebitda and ebitda > 0) else None

            ev = d.get("ev")
            if not ev and mktcap and net_debt is not None:
                ev = mktcap + net_debt

            ev_ebitda  = d.get("ev_ebitda")  or (round(ev/ebitda,1)   if (ev and ebitda and ebitda>0)   else None)
            ev_revenue = d.get("ev_revenue") or (round(ev/revenue,2)  if (ev and revenue and revenue>0) else None)

            rows.append({
                "Ticker":          tkr,
                "Company":         d.get("name", DEFAULT_PEERS.get(tkr, tkr)),
                "Price":           round(price,2)         if price  is not None else None,
                "Mkt Cap ($B)":    round(mktcap/1e9,1)   if mktcap is not None else None,
                "EV ($B)":         round(ev/1e9,1)        if ev     is not None else None,
                "52W High":        round(d["week52_high"],2) if d.get("week52_high") else None,
                "52W Low":         round(d["week52_low"],2)  if d.get("week52_low")  else None,
                "EV/EBITDA":       ev_ebitda,
                "EV/Revenue":      ev_revenue,
                "P/E":             round(d["pe"],1)       if d.get("pe")         else None,
                "P/B":             round(d["pb"],2)       if d.get("pb")         else None,
                "EBITDA Margin":   round(ebitda_margin*100,1)        if ebitda_margin       else None,
                "Net Margin":      round(d["net_margin"]*100,1)      if d.get("net_margin") else None,
                "Rev Growth YoY":  round(d["rev_growth"]*100,1)      if d.get("rev_growth") else None,
                "Net Debt/EBITDA": round(net_debt_ebitda,1)          if net_debt_ebitda is not None else None,
                "Div Yield":       _parse_yield(d.get("div_yield")),
                "Payout Ratio":    round(d["payout"]*100,1)          if d.get("payout")     else None,
                "Beta":            round(d["beta"],2)                 if d.get("beta")       else None,
                "Short % Float":   round(d["short_pct"]*100,2)       if d.get("short_pct")  else None,
                "Revenue ($B)":    round(revenue/1e9,2)  if revenue  else None,
                "EBITDA ($B)":     round(ebitda/1e9,2)   if ebitda   else None,
                "Net Debt ($B)":   round(net_debt/1e9,2) if net_debt is not None else None,
            })
        except Exception as e:
            st.warning(f"Could not process {tkr}: {e}")

    progress.progress(1.0, text="Done.")
    time.sleep(0.3)
    progress.empty()
    return pd.DataFrame(rows)


@st.cache_data(ttl=7200)
def fetch_price_history(tickers: list[str], period: str = "2y") -> pd.DataFrame:
    """
    Download adjusted close prices for all tickers.
    yf.download() uses a different endpoint to .info — much more reliable.
    threads=False sends requests sequentially to avoid rate limiting.
    Indexed to 100 at start so all series are comparable regardless of price level.
    """
    for attempt in range(3):
        try:
            time.sleep(2)
            raw = yf.download(
                tickers, period=period,
                auto_adjust=True, progress=False, threads=False
            )
            # yf.download returns MultiIndex columns when multiple tickers
            if isinstance(raw.columns, pd.MultiIndex):
                raw = raw["Close"]
            else:
                raw = raw[["Close"]] if "Close" in raw.columns else raw

            if isinstance(raw, pd.Series):
                raw = raw.to_frame(name=tickers[0])

            raw.dropna(how="all", inplace=True)
            if not raw.empty:
                return raw.div(raw.iloc[0]).mul(100)
        except Exception:
            time.sleep(3 * (attempt + 1))
    return pd.DataFrame()


@st.cache_data(ttl=7200)
def fetch_single_price_history(ticker: str, period: str = "3y") -> pd.DataFrame:
    """OHLCV for the focus ticker candlestick chart."""
    for attempt in range(3):
        try:
            time.sleep(2)
            t = yf.Ticker(ticker)
            hist = t.history(period=period, auto_adjust=True)
            if not hist.empty:
                return hist
        except Exception:
            pass
        time.sleep(3 * (attempt + 1))
    return pd.DataFrame()


# ──────────────────────────────────────────────
# CHART HELPERS
# ──────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Mono, monospace", color=_T["chart_font"], size=11),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=_T["chart_line"],
                borderwidth=1, font=dict(size=10)),
    xaxis=dict(gridcolor=_T["chart_grid"], linecolor=_T["chart_line"],
               zerolinecolor=_T["chart_line"]),
    yaxis=dict(gridcolor=_T["chart_grid"], linecolor=_T["chart_line"],
               zerolinecolor=_T["chart_line"]),
)


def bar_chart(df_col: pd.Series, title: str, fmt: str = "", color_ticker=FOCUS_TICKER):
    """Horizontal bar chart for comps comparison of a single metric."""
    df_s = df_col.dropna().sort_values()
    colours = [COLORS.get(t, COLORS["default"]) for t in df_s.index]
    fig = go.Figure(go.Bar(
        x=df_s.values, y=df_s.index,
        orientation="h",
        marker_color=colours,
        text=[f"{v:.1f}{fmt}" for v in df_s.values],
        textposition="outside",
        textfont=dict(size=10, family="IBM Plex Mono, monospace"),
    ))
    fig.update_layout(**CHART_LAYOUT, title=dict(text=title, font=dict(size=12), x=0),
                      height=280, showlegend=False)
    fig.update_xaxes(showgrid=False)
    return fig


def indexed_price_chart(norm_df: pd.DataFrame, selected: list[str]) -> go.Figure:
    """Indexed total return chart — all series start at 100."""
    fig = go.Figure()
    for tkr in selected:
        if tkr not in norm_df.columns:
            continue
        is_focus = tkr == FOCUS_TICKER
        fig.add_trace(go.Scatter(
            x=norm_df.index, y=norm_df[tkr],
            name=DEFAULT_PEERS.get(tkr, tkr),
            line=dict(color=COLORS.get(tkr, COLORS["default"]),
                      width=2.5 if is_focus else 1.5,
                      dash="solid" if is_focus else "solid"),
        ))
    fig.update_layout(**CHART_LAYOUT,
                      title=dict(text="Indexed Price Performance (Base = 100)", font=dict(size=12), x=0),
                      height=380,
                      yaxis_title="Indexed (100 = start)",
                      hovermode="x unified")
    return fig


def candlestick_chart(hist: pd.DataFrame, ticker: str) -> go.Figure:
    """OHLCV candlestick with 50-day and 200-day moving averages."""
    hist = hist.copy()
    hist["MA50"]  = hist["Close"].rolling(50).mean()
    hist["MA200"] = hist["Close"].rolling(200).mean()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.75, 0.25], vertical_spacing=0.03)

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=hist.index, open=hist["Open"], high=hist["High"],
        low=hist["Low"], close=hist["Close"],
        increasing_line_color="#2dd4bf", decreasing_line_color="#e63946",
        name="OHLC"
    ), row=1, col=1)

    # Moving averages
    for ma, col, lbl in [("MA50","#f59e0b","MA 50"), ("MA200","#a78bfa","MA 200")]:
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist[ma], name=lbl,
            line=dict(color=col, width=1.2, dash="dot")
        ), row=1, col=1)

    # Volume bars
    colours = ["#e63946" if c < o else "#2dd4bf"
               for c, o in zip(hist["Close"], hist["Open"])]
    fig.add_trace(go.Bar(
        x=hist.index, y=hist["Volume"],
        marker_color=colours, name="Volume", showlegend=False
    ), row=2, col=1)

    fig.update_layout(**CHART_LAYOUT, height=480,
                      title=dict(text=f"{ticker} — Price & Volume", font=dict(size=12), x=0),
                      xaxis_rangeslider_visible=False)
    fig.update_yaxes(gridcolor="#1e2530", row=1, col=1)
    fig.update_yaxes(gridcolor="#1e2530", row=2, col=1, title_text="Volume")
    return fig


def scatter_multiple_vs_growth(df: pd.DataFrame) -> go.Figure:
    """
    Bubble chart: EV/EBITDA (y) vs Revenue Growth (x), sized by Market Cap.
    Highlights overvaluation vs growth — the core of the short argument.
    Defensive: resets index if Ticker was accidentally set as index upstream.
    """
    df = df.copy()
    if df.index.name == "Ticker":
        df = df.reset_index()   # move Ticker back to a regular column
    if "Ticker" not in df.columns:
        df["Ticker"] = df.index.astype(str)
    df_s = df.dropna(subset=["EV/EBITDA", "Rev Growth YoY", "Mkt Cap ($B)"])
    fig = go.Figure()
    if df_s.empty:
        fig.update_layout(**CHART_LAYOUT, height=380,
                          title=dict(text="EV/EBITDA vs Revenue Growth — Peer Scatter",
                                     font=dict(size=12), x=0))
        fig.add_annotation(text="Insufficient data — EV/EBITDA or Rev Growth not available for peers",
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
                           font=dict(color=_T["text_faint"], size=11,
                                     family="IBM Plex Mono, monospace"))
        return fig
    for _, row in df_s.iterrows():
        is_focus = row["Ticker"] == FOCUS_TICKER
        fig.add_trace(go.Scatter(
            x=[row["Rev Growth YoY"]],
            y=[row["EV/EBITDA"]],
            mode="markers+text",
            marker=dict(
                size=max(row["Mkt Cap ($B)"] ** 0.45 * 6, 12),
                color=COLORS.get(row["Ticker"], COLORS["default"]),
                line=dict(width=2 if is_focus else 0,
                          color="#ffffff" if is_focus else "rgba(0,0,0,0)"),
                opacity=0.9,
            ),
            text=[row["Ticker"]],
            textposition="top center",
            textfont=dict(size=10, family="IBM Plex Mono, monospace",
                          color=COLORS.get(row["Ticker"], COLORS["default"])),
            name=row["Company"],
            hovertemplate=(
                f"<b>{row['Company']}</b><br>"
                f"EV/EBITDA: {row['EV/EBITDA']}x<br>"
                f"Rev Growth: {row['Rev Growth YoY']}%<br>"
                f"Mkt Cap: ${row['Mkt Cap ($B)']}B<extra></extra>"
            )
        ))
    fig.update_layout(**CHART_LAYOUT, height=380, showlegend=False,
                      title=dict(text="EV/EBITDA vs Revenue Growth — Peer Scatter", font=dict(size=12), x=0),
                      xaxis_title="Revenue Growth YoY (%)",
                      yaxis_title="EV/EBITDA (x)")
    fig.add_hline(y=df_s["EV/EBITDA"].median(), line_dash="dash",
                  line_color="#6b7a99", annotation_text="Peer Median", annotation_font_size=9)
    return fig


def leverage_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of Net Debt/EBITDA for all peers."""
    d = df.set_index("Ticker")["Net Debt/EBITDA"].dropna().sort_values(ascending=False)
    colours = [COLORS.get(t, COLORS["default"]) for t in d.index]
    fig = go.Figure(go.Bar(
        x=d.index, y=d.values,
        marker_color=colours,
        text=[f"{v:.1f}x" for v in d.values],
        textposition="outside",
        textfont=dict(size=10, family="IBM Plex Mono, monospace"),
    ))
    fig.update_layout(**CHART_LAYOUT, height=300,
                      title=dict(text="Net Debt / EBITDA — Leverage Comparison", font=dict(size=12), x=0),
                      yaxis_title="Net Debt / EBITDA (x)")
    fig.add_hline(y=3.0, line_dash="dash", line_color="#e63946",
                  annotation_text="3.0x Danger Zone", annotation_font_size=9,
                  annotation_font_color="#e63946")
    return fig


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">📌 Focus Company</div>', unsafe_allow_html=True)
    

    st.markdown('<div class="section-label">🔍 Peer Group</div>', unsafe_allow_html=True)
    st.caption("Add tickers (Yahoo Finance format — e.g. HEINY, DEO, 2503.T)")

    custom_input = st.text_input("Add ticker", placeholder="e.g. 2503.T", label_visibility="collapsed")

    all_tickers = list(DEFAULT_PEERS.keys())
    if custom_input.strip():
        t_clean = custom_input.strip().upper()
        if t_clean not in all_tickers:
            all_tickers.append(t_clean)

    selected_tickers = st.multiselect(
        "Active peer group",
        options=all_tickers,
        default=all_tickers,
        label_visibility="collapsed"
    )

    if FOCUS_TICKER not in selected_tickers:
        selected_tickers = [FOCUS_TICKER] + selected_tickers

    st.markdown('<div class="section-label">📅 Price History</div>', unsafe_allow_html=True)
    period_map = {"6 months": "6mo", "1 year": "1y", "2 years": "2y", "3 years": "3y", "5 years": "5y"}
    period_label = st.select_slider("Lookback period", options=list(period_map.keys()), value="2 years")
    period = period_map[period_label]

    st.markdown('<div class="section-label">⚙️ Display</div>', unsafe_allow_html=True)
    show_comps     = st.toggle("Show comps table",       value=True)
    show_charts    = st.toggle("Show peer charts",       value=True)
    show_candle    = st.toggle("Show BUD candlestick",   value=True)

    st.markdown("---")
    st.markdown('<div class="section-label">🔄 Data</div>', unsafe_allow_html=True)
    if st.button("Refresh data", use_container_width=True, key="sidebar_refresh"):
        fetch_fundamentals.clear()
        fetch_price_history.clear()
        fetch_single_price_history.clear()
        st.rerun()
    st.markdown(f"""
    <div style='font-family:IBM Plex Mono,monospace;font-size:0.62rem;
    color:{_T["text_ghost"]};line-height:1.8;margin-top:0.5rem;'>
    Source: Yahoo Finance · yfinance<br>
    Cache: 2h in-memory + disk fallback<br>
    Last run: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC<br><br>
    ⚠ LTM multiples only.<br>Not investment advice.
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
st.markdown(f"""
<div class="header-strip">
  <div>
    <div class="header-title">Global Beverages — Trading Comparables</div>
    <div class="header-sub">
      {len(selected_tickers)} companies · LTM multiples · 
      {datetime.now().strftime('%d %b %Y %H:%M')} UTC
    </div>
  </div>

</div>
""", unsafe_allow_html=True)



# ──────────────────────────────────────────────
# THESIS SUMMARY BOX
# ──────────────────────────────────────────────


# ──────────────────────────────────────────────
# DATA FETCH
# ──────────────────────────────────────────────
# ── Attempt live fetch ──
# If Yahoo Finance is rate-limiting, the functions return empty DataFrames.
# In that case we fall back to the last known good data saved on disk.
_data_status = "live"   # track whether we're showing live or cached data

with st.spinner("Fetching market data..."):
    df_fund      = fetch_fundamentals(selected_tickers)
    norm_prices  = fetch_price_history(selected_tickers, period=period)

if not df_fund.empty:
    # Good fetch — save to disk so this becomes the new fallback
    _now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    save_cache(df_fund, norm_prices, _now)
    _fetched_at = _now
else:
    # Live fetch failed — try loading last known good data from disk
    _cached_df, _cached_prices, _fetched_at = load_cache()
    if _cached_df is not None and not _cached_df.empty:
        df_fund     = _cached_df
        norm_prices = _cached_prices if _cached_prices is not None else pd.DataFrame()
        _data_status = "cached"
    else:
        # No live data AND no cache — nothing to show
        st.error(
            "⚠️ Unable to fetch market data and no cached data available. "
            "Yahoo Finance may be rate-limiting this server. Please try again in a few minutes."
        )
        st.stop()

# ── Data status banner + refresh button ──
# Rendered AFTER the fetch so _data_status and _fetched_at are guaranteed to exist.
_hcol1, _hcol2 = st.columns([5, 1])
with _hcol1:
    if _data_status == "live":
        st.markdown(
            f'''<div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;
            color:{_T["text_faint"]};padding:0.2rem 0 0.6rem;">
            <span style="color:#2dd4bf;">●</span>&nbsp; LIVE DATA &nbsp;·&nbsp;
            Last fetched: {_fetched_at}
            </div>''',
            unsafe_allow_html=True
        )
    else:
        st.warning(
            f"⚠️ Showing cached data from **{_fetched_at}**. "
            "Yahoo Finance is rate-limiting this server. Click **Refresh data** to retry.",
            icon="🕐"
        )
with _hcol2:
    if st.button("🔄 Refresh", use_container_width=True):
        fetch_fundamentals.clear()
        fetch_price_history.clear()
        fetch_single_price_history.clear()
        st.rerun()

# ── BUD row for KPIs ──
bud_row = df_fund[df_fund["Ticker"] == FOCUS_TICKER]
bud = bud_row.iloc[0] if not bud_row.empty else None

# ──────────────────────────────────────────────
# KPI STRIP — BUD ONLY
# ──────────────────────────────────────────────
if bud is not None:
    st.markdown('<div class="section-label">BUD KEY METRICS — LIVE</div>', unsafe_allow_html=True)

    def fmt(val, suffix="", prefix=""):
        return f"{prefix}{val}{suffix}" if val is not None else "—"

    def delta_class(val, inverse=False):
        if val is None: return ""
        if inverse:
            return "neg" if val > 0 else "pos"
        return "pos" if val > 0 else "neg"

    cols = st.columns(8)
    metrics = [
        ("Price",          fmt(bud["Price"], prefix="$"),        None,                      False),
        ("Mkt Cap",        fmt(bud["Mkt Cap ($B)"], suffix="B",  prefix="$"), None,         False),
        ("EV/EBITDA",      fmt(bud["EV/EBITDA"], suffix="x"),    "Peer comp key",           False),
        ("Net Debt/EBITDA",fmt(bud["Net Debt/EBITDA"],suffix="x"),"Leverage",               True),
        ("EBITDA Margin",  fmt(bud["EBITDA Margin"], suffix="%"), None,                     False),
        ("Rev Growth",     fmt(bud["Rev Growth YoY"], suffix="%"),None,                     False),
        ("Div Yield",      fmt(bud["Div Yield"], suffix="%"),     None,                     False),
        ("Short % Float",  fmt(bud["Short % Float"], suffix="%"), "Smart money positioning",False),
    ]
    for col, (label, value, note, inv) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="kpi-card {'focus' if label in ['EV/EBITDA','Net Debt/EBITDA'] else ''}">
              <div class="kpi-label">{label}</div>
              <div class="kpi-value">{value}</div>
              {"<div class='kpi-label' style='margin-top:0.25rem;'>"+note+"</div>" if note else ""}
            </div>
            """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# COMPS TABLE
# ──────────────────────────────────────────────
if show_comps:
    st.markdown('<div class="section-label">📊 TRADING COMPARABLES TABLE — LTM</div>', unsafe_allow_html=True)

    display_cols = [
        "Ticker", "Company",
        "Price", "Mkt Cap ($B)", "EV ($B)",
        "EV/EBITDA", "EV/Revenue", "P/E", "P/B",
        "EBITDA Margin", "Net Margin", "Rev Growth YoY",
        "Net Debt/EBITDA", "Div Yield", "Beta", "Short % Float"
    ]
    df_display = df_fund[display_cols].copy()

    # ── Colour ABI row differently via styling ──
    def style_row(row):
        if row.name == FOCUS_TICKER:   # row.name is the index value after set_index("Ticker")
            return [f"background-color:rgba(230,57,70,0.10);color:{_T['text_primary']};font-weight:600"] * len(row)
        return [f"color:{_T['text_muted']}"] * len(row)

    def highlight_extremes(s):
        """Highlight highest/lowest values in each numeric column."""
        styles = [""] * len(s)
        numeric = pd.to_numeric(s, errors="coerce")
        if numeric.notna().sum() < 2:
            return styles
        max_idx = numeric.idxmax()
        min_idx = numeric.idxmin()
        for i, idx in enumerate(s.index):
            if idx == max_idx:
                styles[i] = "color: #2dd4bf"
            elif idx == min_idx:
                styles[i] = "color: #e63946"
        return styles

    styled = (
        df_display.set_index("Ticker")
        .style
        .apply(style_row, axis=1)
        .apply(highlight_extremes, axis=0, subset=[
            "EV/EBITDA","EV/Revenue","P/E","EBITDA Margin",
            "Rev Growth YoY","Net Debt/EBITDA","Short % Float"
        ])
        .format({
            "Price":           lambda x: f"${x:.2f}" if pd.notna(x) else "—",
            "Mkt Cap ($B)":    lambda x: f"${x:.1f}B" if pd.notna(x) else "—",
            "EV ($B)":         lambda x: f"${x:.1f}B" if pd.notna(x) else "—",
            "EV/EBITDA":       lambda x: f"{x:.1f}x"  if pd.notna(x) else "—",
            "EV/Revenue":      lambda x: f"{x:.2f}x"  if pd.notna(x) else "—",
            "P/E":             lambda x: f"{x:.1f}x"  if pd.notna(x) else "—",
            "P/B":             lambda x: f"{x:.2f}x"  if pd.notna(x) else "—",
            "EBITDA Margin":   lambda x: f"{x:.1f}%"  if pd.notna(x) else "—",
            "Net Margin":      lambda x: f"{x:.1f}%"  if pd.notna(x) else "—",
            "Rev Growth YoY":  lambda x: f"{x:.1f}%"  if pd.notna(x) else "—",
            "Net Debt/EBITDA": lambda x: f"{x:.1f}x"  if pd.notna(x) else "—",
            "Div Yield":       lambda x: f"{x:.2f}%"  if pd.notna(x) else "—",
            "Beta":            lambda x: f"{x:.2f}"   if pd.notna(x) else "—",
            "Short % Float":   lambda x: f"{x:.2f}%"  if pd.notna(x) else "—",
        })
        .set_table_styles([{
            "selector": "th",
            "props": [("background-color",_T["bg_card"]),("color",_T["text_faint"]),
                      ("font-size","0.7rem"),("font-family","IBM Plex Mono, monospace"),
                      ("border-bottom","1px solid "+_T["border"]),("text-align","right")]
        },{
            "selector": "td",
            "props": [("font-family","IBM Plex Mono, monospace"),("font-size","0.78rem"),
                      ("border-bottom","1px solid "+_T["border"]),("text-align","right")]
        }])
    )

    st.dataframe(styled, use_container_width=True, height=320)

    # ── Median / Mean footer ──
    num_cols = ["EV/EBITDA","EV/Revenue","P/E","EBITDA Margin","Net Debt/EBITDA","Div Yield"]
    numeric_df = df_fund[num_cols].apply(pd.to_numeric, errors="coerce")
    median_row = numeric_df.median().rename("Peer Median").to_frame().T
    mean_row   = numeric_df.mean().rename("Peer Mean").to_frame().T
    summary    = pd.concat([median_row, mean_row]).round(2)

    with st.expander("📐 Peer median / mean summary"):
        st.dataframe(summary, use_container_width=True)


# ──────────────────────────────────────────────
# PEER CHARTS
# ──────────────────────────────────────────────
if show_charts:
    st.markdown('<div class="section-label">📈 PEER COMPARISON CHARTS</div>', unsafe_allow_html=True)

    # Row 1: Indexed performance + scatter
    c1, c2 = st.columns([3, 2])
    with c1:
        st.plotly_chart(indexed_price_chart(norm_prices, selected_tickers),
                        use_container_width=True, config={"displayModeBar": False})
    with c2:
        # Pass df_fund directly — Ticker must be a column, not the index
        st.plotly_chart(scatter_multiple_vs_growth(df_fund),
                        use_container_width=True, config={"displayModeBar": False})

    # Row 2: EV/EBITDA + Leverage
    c3, c4 = st.columns(2)
    df_bars = df_fund.set_index("Ticker")
    with c3:
        st.plotly_chart(bar_chart(df_bars["EV/EBITDA"], "EV/EBITDA (x) — Peer Comparison", "x"),
                        use_container_width=True, config={"displayModeBar": False})
    with c4:
        st.plotly_chart(leverage_chart(df_fund),
                        use_container_width=True, config={"displayModeBar": False})

    # Row 3: EBITDA Margin + Rev Growth
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(bar_chart(df_bars["EBITDA Margin"], "EBITDA Margin (%) — Peer Comparison", "%"),
                        use_container_width=True, config={"displayModeBar": False})
    with c6:
        st.plotly_chart(bar_chart(df_bars["Rev Growth YoY"], "Revenue Growth YoY (%) — Peer Comparison", "%"),
                        use_container_width=True, config={"displayModeBar": False})


# ──────────────────────────────────────────────
# BUD CANDLESTICK
# ──────────────────────────────────────────────
if show_candle:
    st.markdown('<div class="section-label">🕯 BUD — PRICE & VOLUME DETAIL</div>', unsafe_allow_html=True)
    with st.spinner("Loading BUD price history..."):
        bud_hist = fetch_single_price_history(FOCUS_TICKER, period=period)
    if not bud_hist.empty:
        st.plotly_chart(candlestick_chart(bud_hist, FOCUS_TICKER),
                        use_container_width=True, config={"displayModeBar": True})


# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style='font-family:IBM Plex Mono,monospace;font-size:0.65rem;
color:{_T["text_ghost"]};text-align:center;padding:0.5rem 0 1rem;line-height:1.8;'>
  Data sourced from Yahoo Finance via yfinance · LTM multiples only · Not investment advice ·
  Built for portfolio demonstration purposes ·
  {datetime.now().strftime('%Y')}
</div>
""", unsafe_allow_html=True)
