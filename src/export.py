# src/export.py
from __future__ import annotations

import pandas as pd


def export_report_cards(scored: pd.DataFrame, path_xlsx: str) -> None:
    """
    Export a compact Excel with the main KPIs and scores.
    """
    cols = [
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
        "market_cap",
        "enterprise_value",
    ]
    present = [c for c in cols if c in scored.columns]
    with pd.ExcelWriter(path_xlsx) as xw:
        scored[present].to_excel(xw, sheet_name="Scores", index=False)