
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT)
)

from io import StringIO

import pandas as pd
import streamlit as st

from src.ingest_sec import fetch_company_concepts
from src.transform import prepare_financials
from src.metrics import compute_metrics
from src.scoring import score_companies, DEFAULT_WEIGHTS
from src.export import export_report_cards
from src.viz import plot_peer_heatmap

st.set_page_config(page_title="Alex's Corporate Health Dashboard", layout="wide")
st.title("Alex's Corporate Health Dashboard")

st.markdown(
    "Upload a CSV with financials or fetch from SEC for US tickers. "
    "Get an objective health score and peer benchmarking."
)

with st.sidebar:
    st.header("Data input")
    mode = st.radio("Input mode", ["Sample CSV", "Upload CSV", "SEC fetch (US tickers)"])

    tickers_text = ""
    if mode == "SEC fetch (US tickers)":
        default = "AAPL, MSFT, NVDA, AMZN, GOOGL, META"
        tickers_text = st.text_area("Tickers (comma separated)", default)
        st.caption("Tip: set env var SEC_USER_AGENT to your email to be polite to the SEC API.")

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


def fetch_sec_bulk(tickers: list[str]) -> pd.DataFrame:
    frames = []
    for t in tickers:
        try:
            frames.append(fetch_company_concepts(t))
        except Exception as e:
            st.warning(f"Failed {t}: {e}")
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    # minimal placeholders if not provided by SEC facts
    if "shares_basic" not in df.columns:
        df["shares_basic"] = 1.0
    if "price" not in df.columns:
        df["price"] = 1.0
    return df


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
        fin = fetch_sec_bulk(tickers)

    if fin.empty:
        st.error("No financial data found")
        st.stop()

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
    ]
    st.dataframe(scored[display_cols].round(3), use_container_width=True)

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