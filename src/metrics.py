# src/metrics.py
from __future__ import annotations

import numpy as np
import pandas as pd


def safe_div(a, b):
    return np.where(np.abs(b) > 1e-12, a / b, np.nan)


def compute_metrics(fin: pd.DataFrame, price_col: str = "price", shares_col: str = "shares_basic") -> pd.DataFrame:
    """
    Compute decision-ready finance metrics from normalized financials.
    """
    df = fin.copy()

    # Size and capital structure
    df["market_cap"] = df.get(price_col, 0) * df.get(shares_col, 0)
    df["net_debt"] = (df.get("short_term_debt", 0) + df.get("long_term_debt", 0)) - df.get("cash", 0)
    df["enterprise_value"] = df["market_cap"] + df["net_debt"]

    # Profitability
    df["ebit_margin"] = safe_div(df.get("ebit", 0), df.get("revenue", 0))
    df["ebitda_margin"] = safe_div(df.get("ebitda", 0), df.get("revenue", 0))
    df["roa"] = safe_div(df.get("net_income", 0), df.get("total_assets", 0))
    df["roe"] = safe_div(df.get("net_income", 0), df.get("shareholders_equity", 0))

    # Liquidity and working capital
    df["current_ratio"] = safe_div(df.get("current_assets", 0), df.get("current_liabilities", 0))
    df["quick_ratio"] = safe_div(df.get("current_assets", 0) - df.get("inventory", 0), df.get("current_liabilities", 0))

    # Leverage
    df["debt_to_equity"] = safe_div(
        df.get("short_term_debt", 0) + df.get("long_term_debt", 0),
        df.get("shareholders_equity", 0),
    )
    df["net_debt_to_ebitda"] = safe_div(df["net_debt"], df.get("ebitda", 0))

    # Cash generation
    df["ocf_margin"] = safe_div(df.get("operating_cf", 0), df.get("revenue", 0))
    df["fcf"] = df.get("operating_cf", 0) - np.abs(df.get("capex", 0))
    df["fcf_margin"] = safe_div(df["fcf"], df.get("revenue", 0))
    df["ev_ebitda"] = safe_div(df["enterprise_value"], df.get("ebitda", 0))

    return df