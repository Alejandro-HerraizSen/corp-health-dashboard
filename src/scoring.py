# src/scoring.py
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_WEIGHTS = {
    "profitability": 0.35,
    "liquidity": 0.20,
    "leverage": 0.20,
    "cash_gen": 0.25,
}


def _zscore(col: pd.Series) -> pd.Series:
    mu = np.nanmean(col.values)
    sd = np.nanstd(col.values)
    if sd < 1e-12:
        return pd.Series(np.zeros_like(col.values), index=col.index)
    return (col - mu) / sd


def score_companies(metrics: pd.DataFrame, weights: dict | None = None) -> pd.DataFrame:
    """
    Peer-normalized composite score on 0–100 scale with adjustable component weights.
    """
    w = weights or DEFAULT_WEIGHTS
    df = metrics.copy()

    profit_cols = ["ebit_margin", "ebitda_margin", "roa", "roe"]
    liqu_cols = ["current_ratio", "quick_ratio"]
    cash_cols = ["ocf_margin", "fcf_margin"]

    for c in profit_cols + liqu_cols + cash_cols:
        df[f"z_{c}"] = _zscore(df[c])

    # For leverage a lower debt_to_equity is better
    df["z_debt_to_equity"] = -_zscore(df["debt_to_equity"])

    df["score_profitability"] = df[[f"z_{c}" for c in profit_cols]].mean(axis=1)
    df["score_liquidity"] = df[[f"z_{c}" for c in liqu_cols]].mean(axis=1)
    df["score_leverage"] = df["z_debt_to_equity"]
    df["score_cash"] = df[[f"z_{c}" for c in cash_cols]].mean(axis=1)

    df["score_total"] = (
        w["profitability"] * df["score_profitability"]
        + w["liquidity"] * df["score_liquidity"]
        + w["leverage"] * df["score_leverage"]
        + w["cash_gen"] * df["score_cash"]
    )

    z = _zscore(df["score_total"])
    df["score_0_100"] = (z - z.min()) / (z.max() - z.min() + 1e-9) * 100.0

    return df.sort_values("score_0_100", ascending=False)