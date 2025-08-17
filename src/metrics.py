# src/metrics.py
from __future__ import annotations

import numpy as np
import pandas as pd

def safe_div(a, b):
    """
    Robust elementwise division that never raises ZeroDivisionError.
    Returns np.ndarray with NaN where denominator is ~0.
    """
    a_arr = np.asarray(pd.to_numeric(a, errors="coerce"), dtype=float)
    b_arr = np.asarray(pd.to_numeric(b, errors="coerce"), dtype=float)
    out = np.full_like(a_arr, np.nan, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        np.divide(a_arr, b_arr, out=out, where=np.abs(b_arr) > 1e-12)
    return out

def compute_metrics(fin: pd.DataFrame, price_col: str = "price", shares_col: str = "shares_basic") -> pd.DataFrame:
    """
    Compute decision-ready finance metrics from normalized financials.
    Safely coerces inputs to numeric and avoids zero-division.
    """
    df = fin.copy()

    # Coerce expected numeric fields; create if missing
    num_cols = [
        "revenue","ebit","ebitda","net_income","total_assets","shareholders_equity",
        "current_assets","current_liabilities","inventory","operating_cf","capex",
        "short_term_debt","long_term_debt","cash", price_col, shares_col
    ]
    for c in num_cols:
        if c not in df.columns:
            df[c] = 0.0
        df[c] = pd.to_numeric(df[c], errors="coerce").astype(float).fillna(0.0)

    # Size & capital structure
    df["market_cap"] = df[price_col] * df[shares_col]
    df["net_debt"] = (df["short_term_debt"] + df["long_term_debt"]) - df["cash"]
    df["enterprise_value"] = df["market_cap"] + df["net_debt"]

    # Profitability
    df["ebit_margin"] = safe_div(df["ebit"], df["revenue"])
    df["ebitda_margin"] = safe_div(df["ebitda"], df["revenue"])
    df["roa"] = safe_div(df["net_income"], df["total_assets"])
    df["roe"] = safe_div(df["net_income"], df["shareholders_equity"])

    # Liquidity & working capital
    df["current_ratio"] = safe_div(df["current_assets"], df["current_liabilities"])
    df["quick_ratio"] = safe_div(df["current_assets"] - df["inventory"], df["current_liabilities"])

    # Leverage
    df["debt_to_equity"] = safe_div(df["short_term_debt"] + df["long_term_debt"], df["shareholders_equity"])
    df["net_debt_to_ebitda"] = safe_div(df["net_debt"], df["ebitda"])

    # Cash generation & valuation helper
    df["ocf_margin"] = safe_div(df["operating_cf"], df["revenue"])
    df["fcf"] = df["operating_cf"] - np.abs(df["capex"])
    df["fcf_margin"] = safe_div(df["fcf"], df["revenue"])
    df["ev_ebitda"] = safe_div(df["enterprise_value"], df["ebitda"])

    return df