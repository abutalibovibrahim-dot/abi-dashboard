<<<<<<< HEAD
# 📊 Global Beverages Trading Comparables Dashboard
### ABI Short Thesis — Live Equity Research Tool

> **Part 1 of 5** in a finance & data analytics portfolio  
> Built with Python · Streamlit · yfinance · Plotly  
> Deployable free on Streamlit Cloud

---

## Table of Contents
1. [What This Dashboard Does](#what-this-dashboard-does)
2. [Why It Was Built This Way](#why-it-was-built-this-way)
3. [The Investment Thesis](#the-investment-thesis)
4. [File Structure](#file-structure)
5. [How to Run Locally](#how-to-run-locally)
6. [How to Deploy on Streamlit Cloud (Free)](#how-to-deploy-on-streamlit-cloud-free)
7. [Code Walkthrough — Line by Line](#code-walkthrough--line-by-line)
8. [The Metrics Explained](#the-metrics-explained)
9. [Design Decisions](#design-decisions)
10. [Limitations & Known Constraints](#limitations--known-constraints)
11. [How to Use This in Interviews](#how-to-use-this-in-interviews)
12. [Extending the Dashboard](#extending-the-dashboard)

---

## What This Dashboard Does

This is a **live equity research dashboard** that displays a professional trading comparables ("comps") table for a user-selected peer group of global beverages companies, with Anheuser-Busch InBev (NYSE: BUD) as the focus company for a short investment thesis.

It pulls **real-time market data** from Yahoo Finance every 60 minutes and displays:

- A **trading comps table** with LTM (Last Twelve Months) valuation multiples, profitability metrics, leverage ratios, and market data — one row per company
- **Peer comparison bar charts** for EV/EBITDA, EBITDA margins, revenue growth, and leverage
- An **indexed price performance chart** showing all peers rebased to 100 at the start of the selected period
- A **valuation vs growth scatter plot** showing whether companies trade at a premium or discount relative to their growth profile
- A **BUD candlestick chart** with 50-day and 200-day moving averages and volume bars
- A **KPI strip** showing BUD's key metrics at a glance
- An **investment thesis summary box** explaining the short case

---

## Why It Was Built This Way

**Trading comps rather than standalone company tracker**

A short thesis on ABI is not just "ABI looks expensive." It is "ABI looks expensive *relative to peers* while having *worse fundamental trends* than those peers." That relative argument requires a comparison set. This is how professional analysts at hedge funds, investment banks, and private equity firms actually think about valuation.

**LTM multiples only (no forward estimates)**

Forward estimates (NTM EV/EBITDA, consensus price targets) require Bloomberg or FactSet — paid data services. This dashboard uses only LTM (Last Twelve Months) reported financials, which are fully accurate, freely available via Yahoo Finance, and analytically robust. This is noted clearly in the UI so interviewers understand the constraint is deliberate, not accidental.

**User-selectable peer group**

The dashboard is not hardcoded to beverages. You can type any Yahoo Finance ticker into the sidebar and it joins the comps table. This means the same tool works for tech, healthcare, energy, or any sector — making it a general-purpose research tool, not a single-use demonstration.

**Dark terminal aesthetic**

Finance professionals use Bloomberg terminals, dark trading screens, and dense analytical interfaces. The IBM Plex Mono font, dark background (#0a0e14), and red/teal colour scheme deliberately evokes that professional environment rather than generic data science dashboard aesthetics.

---

## The Investment Thesis

**SHORT: Anheuser-Busch InBev (NYSE: BUD)**

ABI trades at a premium EV/EBITDA multiple relative to its peer group despite three converging structural headwinds:

**1. GLP-1 Drug Adoption**  
Glucagon-like peptide-1 receptor agonists (semaglutide / Ozempic, tirzepatide / Mounjaro) reduce appetite, caloric intake, and — critically — alcohol tolerance and desire. US GLP-1 prescriptions have grown exponentially since 2022. Early consumer survey data suggests GLP-1 users are consuming significantly less alcohol. ABI's US business (~25% of revenue) faces a structurally shrinking addressable market as adoption scales.

**2. Gen Z Secular Consumption Decline**  
Gallup and IWSR data show that adults under 35 in the US and Western Europe drink significantly less alcohol than equivalent age cohorts did in previous decades. This is not a cyclical dip — it is a documented, persistent generational shift. As Gen Z moves into peak consumption age (25–40), the historical volume tailwind that supported beverages companies' growth assumptions no longer applies.

**3. Bud Light Brand Damage**  
The 2023 Bud Light controversy caused a persistent decline in US volume that has not fully recovered. Bud Light was the #1 selling beer in the US for decades. Shelf space and consumer habits lost to Coors Light and Miller Lite are structurally difficult to recapture.

**Structural Leverage Problem**  
ABI took on ~$100B in debt to acquire SABMiller in 2016. While they have deleveraged since, Net Debt/EBITDA remains elevated relative to peers, constraining their ability to invest aggressively through volume headwinds or pursue M&A.

**The Bull Case (and why it's insufficient)**  
Bulls point to emerging market volume growth (Brazil, Africa, China) and strong FCF conversion. The dashboard tracks these — specifically the FCF yield and Net Debt/EBITDA trend — to monitor whether the bull case is materialising. The thesis is that EM growth is insufficient to offset developed market structural decline at the current premium multiple.

**What Would Break the Thesis**  
- Sustained, accelerating EM volume growth outpacing developed market decline
- Multiple compression normalising relative to peers (the short becomes less interesting)
- GLP-1 adoption plateauing at lower-than-expected penetration rates
- Successful Bud Light brand recovery showing in US volume data

---

## File Structure

```
abi_dashboard/
│
├── app.py                    ← Main Streamlit application (all logic here)
├── requirements.txt          ← Python package dependencies
├── README.md                 ← This file
│
└── .streamlit/
    └── config.toml           ← Streamlit theme configuration (dark mode)
```

---

## How to Run Locally

**Prerequisites:** Python 3.10 or higher, pip

**Step 1 — Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/abi-dashboard.git
cd abi-dashboard
```

**Step 2 — Create a virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows
```

**Step 3 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 4 — Run the app**
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## How to Deploy on Streamlit Cloud (Free)

Streamlit Community Cloud is free for public repositories and gives you a permanent shareable URL.

**Step 1 — Push to GitHub**
```bash
git init
git add .
git commit -m "initial commit — ABI beverages comps dashboard"
git remote add origin https://github.com/YOUR_USERNAME/abi-dashboard.git
git push -u origin main
```

**Step 2 — Deploy**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your repository, branch (`main`), and file (`app.py`)
5. Click **"Deploy"**

**Step 3 — Your URL**  
Streamlit generates a URL like `https://your-username-abi-dashboard-app-xxxxxx.streamlit.app`  
This is what you put on your CV, LinkedIn, and personal website.

---

## Code Walkthrough — Line by Line

This section explains every major block of `app.py` so you can understand, modify, and explain the code in interviews.

---

### 1. Imports and Page Configuration

```python
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
```

- **`streamlit`** — the web framework. It converts Python scripts into interactive web apps. Every `st.` function renders something in the browser.
- **`yfinance`** — an unofficial Python wrapper around Yahoo Finance's API. It lets you download stock prices, financial statements, and company info with a single function call.
- **`pandas`** — the standard Python library for working with tabular data (DataFrames). Think of it as Excel in Python.
- **`plotly`** — an interactive charting library. `graph_objects` gives you fine-grained control over every element of a chart. `express` is a simpler interface for standard chart types.

```python
st.set_page_config(
    page_title="Beverages Comps | ABI Short Thesis",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

This must be the **first Streamlit command** in your script. It sets the browser tab title, uses the full browser width (`layout="wide"`), and opens the sidebar by default.

---

### 2. Custom CSS

```python
st.markdown("""<style> ... </style>""", unsafe_allow_html=True)
```

Streamlit has a default light theme. We override it entirely with custom CSS injected via `st.markdown`. `unsafe_allow_html=True` allows HTML and CSS — it's safe here because we control the content.

Key CSS decisions:
- `font-family: 'IBM Plex Mono'` — the monospace font used on Bloomberg terminals, giving a professional finance aesthetic
- `background-color: #0a0e14` — very dark navy, not pure black, which is easier on the eyes
- `#e63946` — the red accent colour used for ABI (the short) and all alert/danger indicators
- `#2dd4bf` — teal used for positive indicators and peer companies
- `.header-strip`, `.kpi-card`, `.thesis-box` — custom HTML component classes defined here and used throughout

---

### 3. Constants — DEFAULT_PEERS and COLORS

```python
DEFAULT_PEERS = {
    "BUD":    "Anheuser-Busch InBev",
    "HEINY":  "Heineken",
    ...
}

COLORS = {
    "BUD":   "#e63946",   # red — focus / short
    "HEINY": "#2dd4bf",
    ...
}
```

- `DEFAULT_PEERS` — a Python dictionary mapping Yahoo Finance ticker symbols to full company names. This is the default peer group loaded when the app starts.
- `COLORS` — a second dictionary mapping each ticker to its chart colour. BUD always renders in red to visually anchor the short thesis. Each peer has a distinct colour for the indexed price chart.

**Why a dictionary and not a list?**  
Dictionaries allow O(1) lookup — `DEFAULT_PEERS.get("BUD")` instantly returns "Anheuser-Busch InBev" without scanning through a list. This matters when you're iterating over many tickers.

---

### 4. The Data Layer — `fetch_fundamentals()`

```python
@st.cache_data(ttl=3600)
def fetch_fundamentals(tickers: list[str]) -> pd.DataFrame:
```

**`@st.cache_data(ttl=3600)`** — This is a Streamlit decorator that caches the function's return value. The first time this function runs, it fetches data from Yahoo Finance and stores the result. Every subsequent call within 3600 seconds (1 hour) returns the cached result without making a new API call. This is critical for performance — without caching, the app would re-fetch every metric every time any user interaction occurs.

```python
t = yf.Ticker(tkr)
info = t.info
```

`yf.Ticker(tkr)` creates a Ticker object for a given symbol. `.info` returns a Python dictionary with ~150 data fields: prices, multiples, balance sheet items, analyst estimates, and more.

```python
def g(key, default=None):
    v = info.get(key)
    return v if v not in (None, "N/A", 0) else default
```

A helper function (named `g` for "get") that safely extracts values from the `info` dictionary. Yahoo Finance sometimes returns `None`, `"N/A"`, or `0` for unavailable fields — this function treats all three as missing and returns the `default` value instead. This prevents crashes when a company doesn't report a particular metric.

```python
net_debt = (total_debt - cash) if (total_debt and cash is not None) else None
```

Net debt is not directly reported by Yahoo Finance — it must be calculated. This line subtracts total cash from total debt. The conditional `if (total_debt and cash is not None)` prevents errors when either value is missing.

```python
net_debt_ebitda = (net_debt / ebitda) if (net_debt and ebitda and ebitda > 0) else None
```

Net Debt/EBITDA is a key leverage ratio — it tells you how many years of operating earnings (before interest, taxes, depreciation, amortisation) would be needed to repay all debt. The `ebitda > 0` check prevents division by zero for loss-making companies.

---

### 5. `fetch_price_history()` — Indexed Performance

```python
@st.cache_data(ttl=3600)
def fetch_price_history(tickers: list[str], period: str = "2y") -> pd.DataFrame:
    raw = yf.download(tickers, period=period, auto_adjust=True, progress=False)["Close"]
    normalised = raw.div(raw.iloc[0]).mul(100)
    return normalised
```

- `yf.download()` fetches OHLCV data for multiple tickers simultaneously — more efficient than calling `yf.Ticker()` for each one separately
- `auto_adjust=True` adjusts prices for dividends and stock splits, ensuring the performance comparison reflects total return
- `raw.div(raw.iloc[0]).mul(100)` — this is the **index normalisation**. `raw.iloc[0]` is the first row (first date). Dividing every value by the first value then multiplying by 100 sets every series to 100 at the start. This allows you to compare performance regardless of absolute price level — a $10 stock and a $500 stock both start at 100 and diverge based on returns.

---

### 6. Chart Functions

All chart functions follow the same pattern:

```python
def bar_chart(df_col, title, fmt=""):
    fig = go.Figure(go.Bar(...))
    fig.update_layout(**CHART_LAYOUT, ...)
    return fig
```

They return a Plotly `Figure` object, which is then rendered with `st.plotly_chart()`. The `**CHART_LAYOUT` unpacking applies the dark theme settings (background colour, font, grid colour) consistently to every chart.

**The scatter plot (`scatter_multiple_vs_growth`)**  
This is analytically the most important chart. It plots:
- X axis: Revenue Growth YoY (%)
- Y axis: EV/EBITDA multiple
- Bubble size: Market capitalisation

The logic: companies with higher growth should trade at higher multiples. If ABI is in the top-left quadrant (high multiple, low growth), that's evidence of overvaluation relative to the peer group. The median horizontal line shows where the "fair" multiple is for an average-growth company in the peer group.

**The candlestick chart**
```python
hist["MA50"]  = hist["Close"].rolling(50).mean()
hist["MA200"] = hist["Close"].rolling(200).mean()
```
Moving averages smooth out daily noise. The 50-day MA shows medium-term trend; the 200-day MA shows the long-term trend. A stock trading below its 200-day MA is in a long-term downtrend — relevant for the short thesis.

---

### 7. The Sidebar

```python
selected_tickers = st.multiselect(
    "Active peer group",
    options=all_tickers,
    default=all_tickers,
)
```

`st.multiselect` renders a dropdown where the user can select multiple options. When the selection changes, Streamlit automatically reruns the entire script with the new values — this is how Streamlit's reactive model works. There is no explicit event handler needed.

```python
if FOCUS_TICKER not in selected_tickers:
    selected_tickers = [FOCUS_TICKER] + selected_tickers
```

This guard ensures BUD is always in the peer group even if the user accidentally deselects it. The short thesis requires BUD to always be present for comparison.

---

### 8. Styled DataFrame

```python
def style_row(row):
    if row["Ticker"] == FOCUS_TICKER:
        return ["background-color: rgba(230,57,70,0.08); ..."] * len(row)
    return [""] * len(row)

styled = df_display.set_index("Ticker").style.apply(style_row, axis=1)
```

Pandas `.style` allows conditional formatting of DataFrames — similar to conditional formatting in Excel. `apply(style_row, axis=1)` applies the function to each **row** (axis=1). For ABI, it returns a red-tinted background. For other rows, it returns empty strings (no special formatting).

`.format({...})` applies display formatting to each column — numbers are shown as `$12.3B`, `8.5x`, `24.1%` rather than raw floats. The `lambda x: f"..." if pd.notna(x) else "—"` pattern handles missing values by showing a dash rather than `NaN`.

---

## The Metrics Explained

| Metric | What it measures | Why it matters for ABI |
|--------|-----------------|------------------------|
| **EV/EBITDA** | Enterprise Value divided by EBITDA. How many years of operating earnings does the market price represent? | Core valuation metric for beverages. If BUD trades at a premium here vs peers with better growth, that's the short argument. |
| **EV/Revenue** | Enterprise Value divided by total revenue | Useful when EBITDA margins differ significantly across peers |
| **P/E** | Share price divided by earnings per share | Less useful for highly leveraged companies — use EV/EBITDA instead |
| **Net Debt/EBITDA** | Net debt (debt minus cash) divided by EBITDA | Leverage ratio. Above 3x is considered elevated for consumer staples. ABI inherited high debt from the SABMiller acquisition. |
| **EBITDA Margin** | EBITDA as a % of revenue | Operating efficiency. Premium brands typically have higher margins. |
| **Rev Growth YoY** | Year-on-year revenue change | Forward multiple compression requires either multiple re-rating or growth improvement |
| **Div Yield** | Annual dividend as % of share price | Bulls argue ABI's yield is attractive. Bears argue the payout is constrained by leverage. |
| **Short % Float** | % of shares outstanding currently sold short | Indicates institutional conviction in the bear case. Rising short interest can cause short squeezes — a key risk to monitor. |
| **Beta** | Sensitivity to broader market moves | A beta > 1 means the stock amplifies market moves. Relevant for portfolio construction. |

---

## Design Decisions

**Why IBM Plex Mono?**  
It's the typeface used in IBM's developer and financial tools. Monospace fonts make numerical alignment easier to read in dense tables — the same reason Bloomberg uses a monospace font. It signals professional intent without looking like a coding project.

**Why #e63946 (red) for ABI?**  
Red traditionally signals a short position, danger, or alert in financial interfaces. Using it consistently for ABI — in the header badge, KPI card borders, thesis box, chart bars, and scatter bubble — creates visual coherence. Anyone opening the dashboard immediately understands BUD is the focus of concern.

**Why cache for 1 hour?**  
Streamlit apps rerun the entire Python script on every user interaction. Without caching, every sidebar toggle or slider change would trigger new Yahoo Finance API calls for all tickers — slow and potentially rate-limited. Caching means data is fetched once per hour and reused for all interactions within that window.

**Why no `st.plotly_chart` sidebar layout?**  
Plotly charts are wide and information-dense. The sidebar is reserved for controls only. Charts always render in the main body at full width for maximum readability.

---

## Limitations & Known Constraints

1. **LTM only, no forward estimates** — Forward consensus (NTM multiples) requires Bloomberg or FactSet. This dashboard uses only trailing financials. For interviews, frame this as a deliberate choice: "I wanted to use only hard reported data rather than consensus estimates that can be revised or manipulated."

2. **Yahoo Finance data quality** — yfinance is an unofficial wrapper. Occasionally fields are missing, stale, or incorrectly reported for non-US tickers (e.g., CBRL.L for Carlsberg in GBp). Always sanity-check displayed figures against a primary source before an interview.

3. **No volume data by geography** — The ABI short thesis ideally tracks beer volume by region (US vs EM). Yahoo Finance doesn't provide this granularity. For the full thesis, supplement with ABI's quarterly earnings calls and investor presentations (available at bud.com/investors).

4. **Rate limiting** — Yahoo Finance has unofficial rate limits. If you add more than ~15 tickers simultaneously, some may time out. The `try/except` block handles this gracefully by skipping failed tickers with a warning.

5. **Currency** — Non-USD tickers (DEO in GBp, CBRL.L in DKKr) are displayed in their local currency. Market cap and EV figures may appear in different denominations. Always note this when discussing with interviewers.

---

## How to Use This in Interviews

**Opening the conversation**  
"I built a live trading comps dashboard for the global beverages sector, focused on a short thesis I've developed on Anheuser-Busch InBev. Would you like me to walk you through it?"

**For Hedge Fund interviews**  
Start with the thesis summary box — explain the three structural drivers (GLP-1, Gen Z, brand damage). Then open the comps table and show where BUD sits on EV/EBITDA relative to peers. Then show the scatter plot — if BUD is in the top-left quadrant (high multiple, low growth), that's your visual short argument. Finish with the candlestick and show the 200-day MA relationship.

**For Investment Banking interviews**  
Start with the comps table — explain what each column measures and why you chose those metrics. Walk through the methodology: "I used LTM multiples from reported financials via Yahoo Finance — deliberately avoiding forward estimates given the noise in consensus." Show the leverage chart — "ABI's Net Debt/EBITDA is meaningfully higher than peers, which is a legacy of the SABMiller acquisition."

**For Private Equity interviews**  
Focus on FCF yield and leverage. "The question for a PE buyer would be: can you buy this business, reduce leverage, and exit at a higher multiple? My view is no — because the volume decline is structural, not cyclical, which means EBITDA will compress over the hold period regardless of financial engineering."

**Questions you'll likely get asked**  
- "What's your price target?" — Answer: explain you'd need a DCF with explicit volume decline assumptions (see Tool 3 in this portfolio)
- "What's your catalyst?" — US beer volume data (next quarterly earnings), GLP-1 prescription data (monthly), Bud Light market share data
- "What would make you wrong?" — See the thesis box: EM volume acceleration, multiple compression normalising, GLP-1 adoption plateau

---

## Extending the Dashboard

Things you could add as your finance knowledge deepens:

- **Quarterly volume data** — scrape ABI's quarterly earnings press releases to build a volume trend chart by geography
- **GLP-1 overlay** — add a secondary axis to the price chart showing US semaglutide prescription volumes over time
- **DCF integration** — link to Tool 3 (the DCF modelling tool) with pre-populated ABI assumptions
- **News feed** — use a news API (NewsAPI.org, free tier) to display recent ABI headlines in a sidebar panel
- **Export to PDF** — add a download button that generates a one-page investment memo PDF from the live data

---

## About This Project

This dashboard is Part 1 of a 5-part finance portfolio built to demonstrate quantitative research, data engineering, and investment analysis capabilities for roles in hedge funds, investment banking, and private equity in Geneva.

The full portfolio includes:
1. **Equity Research Dashboard** (this tool) — live trading comps
2. **AI Financial Research Assistant** — Claude API-powered company analysis
3. **Interactive DCF Modelling Tool** — scenario-based valuation
4. **Commodity Price Tracker** — live commodity supply/demand visualisation
5. **Personal Website** — portfolio hub with links to all tools

---

*Data sourced from Yahoo Finance via yfinance. For informational and portfolio demonstration purposes only. Not investment advice.*
=======
# abi-dashboard
>>>>>>> c5b4db76f0acb8814953f09fad9c2cca9645782e
