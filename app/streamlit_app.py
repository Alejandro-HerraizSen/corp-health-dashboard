# app/streamlit_app.py
from __future__ import annotations

# Ensure imports work on Streamlit Cloud
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from io import StringIO
from typing import List

import pandas as pd
import streamlit as st

from src.ingest_sec import fetch_bulk
from src.transform import prepare_financials
from src.metrics import compute_metrics
from src.scoring import score_companies, DEFAULT_WEIGHTS
from src.export import export_report_cards
from src.viz import plot_peer_heatmap

st.set_page_config(page_title="Corporate Health Dashboard", layout="wide")
st.title("Corporate Health Dashboard")

st.markdown(
    "Upload a CSV or paste US tickers and the app will fetch the latest annual fundamentals "
    "from the SEC plus the most recent market price from Yahoo Finance."
)

with st.sidebar:
    st.header("Data input")
    mode = st.radio("Input mode", ["Sample CSV", "Upload CSV", "SEC fetch (US tickers)"])

    tickers_text = ""
    if mode == "SEC fetch (US tickers)":
        default = "AAPL, MSFT, NVDA, AMZN, GOOGL, META"
        tickers_text = st.text_area("Tickers (comma separated)", default)
        st.caption("Set secret SEC_USER_AGENT to your email on Streamlit Cloud for polite SEC requests.")

    uploaded = None
    if mode == "Upload CSV":
        uploaded = st.file_uploader("Upload financials CSV", type=["csv"])

    st.header("Weights")
    p = st.slider("Profitability", 0.0, 1.0, float(DEFAULT_WEIGHTS["profitability"]), 0.05)
    lq = st.slider("Liquidity", 0.0, 1.0, float(DEFAULT_WEIGHTS["liquidity"]), 0.05)
    lev = st.slider("Leverage", 0.0, 1.0, float(DEFAULT_WEIGHTS["leverage"]), 0.05)
    cg = st.slider("Cash generation", 0.0, 1.0, float(DEFAULT_WEIGHTS["cash_gen"]), 0.05)
    total = p + lq + lev + cg
    if total == 0:
        st.warning("Increase at least one weight")
    else:
        p, lq, lev, cg = [w / total for w in [p, lq, lev, cg]]

go = st.button("Run", type="primary")


def load_sample() -> pd.DataFrame:
    return pd.read_csv("templates/financials_example.csv")


def parse_uploaded(file) -> pd.DataFrame:
    content = file.read().decode("utf-8")
    return pd.read_csv(StringIO(content))


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_sec_cached(_tickers: List[str]) -> pd.DataFrame:
    return fetch_bulk(_tickers)


if go:
    if mode == "Sample CSV":
        fin = load_sample()
    elif mode == "Upload CSV":
        if uploaded is None:
            st.error("Upload a CSV first")
            st.stop()
        fin = parse_uploaded(uploaded)
    else:
        tickers = [t.strip().upper() for t in tickers_text.split(",") if t.strip()]
        if len(tickers) == 0:
            st.error("Provide at least one ticker")
            st.stop()
        with st.spinner("Fetching SEC fundamentals and latest prices..."):
            fin = fetch_sec_cached(tickers)

    if fin.empty:
        st.error("No financial data found")
        st.stop()

    # Display info about price as-of date if present
    if "price_asof" in fin.columns:
        asof_vals = sorted({v for v in fin["price_asof"].dropna().unique().tolist()})
        if asof_vals:
            st.caption(f"Price data as of: {', '.join(asof_vals)}")

    fin_norm = prepare_financials(fin)
    metrics = compute_metrics(fin_norm)
    weights = {"profitability": p, "liquidity": lq, "leverage": lev, "cash_gen": cg}
    scored = score_companies(metrics, weights)

    st.subheader("Ranking")
    display_cols = [
        "ticker",
        "score_0_100",
        "ebit_margin",
        "ebitda_margin",
        "roa",
        "roe",
        "current_ratio",
        "quick_ratio",
        "debt_to_equity",
        "net_debt_to_ebitda",
        "ocf_margin",
        "fcf_margin",
        "ev_ebitda",
        "price",
    ]
    existing = [c for c in display_cols if c in scored.columns]
    st.dataframe(scored[existing].round(3), use_container_width=True)

    st.subheader("Peer heatmap")
    st.image(plot_peer_heatmap(scored), caption="Relative positioning across key metrics")

    st.subheader("Exports")
    export_report_cards(scored, "outputs/company_report_cards.xlsx")
    scored.to_csv("outputs/metrics_long.csv", index=False)
    st.success("Saved Excel report and CSV to outputs/")
    st.download_button(
        "Download report cards (Excel)",
        data=open("outputs/company_report_cards.xlsx", "rb").read(),
        file_name="company_report_cards.xlsx",
    )
    st.download_button(
        "Download metrics (CSV)",
        data=open("outputs/metrics_long.csv", "rb").read(),
        file_name="metrics_long.csv",
    )