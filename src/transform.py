# src/transform.py
from __future__ import annotations

import pandas as pd


def prepare_financials(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names, fill safe NaNs, and keep the latest FY per ticker if present.
    Works for either the sample CSV or SEC-ingested data.
    """
    rename_map = {
        "Revenues": "revenue",
        "OperatingIncomeLoss": "ebit",
        "NetIncomeLoss": "net_income",
        "Assets": "total_assets",
        "Liabilities": "total_liabilities",
        "AssetsCurrent": "current_assets",
        "LiabilitiesCurrent": "current_liabilities",
        "InventoryNet": "inventory",
        "CashAndCashEquivalentsAtCarryingValue": "cash",
        "NetCashProvidedByUsedInOperatingActivities": "operating_cf",
        "PaymentsToAcquirePropertyPlantAndEquipment": "capex",
        "LongTermDebtNoncurrent": "long_term_debt",
        "LongTermDebtCurrent": "short_term_debt",
        "StockholdersEquity": "shareholders_equity",
    }
    df = df.rename(columns=rename_map).copy()

    numeric_cols = [c for c in df.columns if c not in {"ticker", "period"}]
    for c in numeric_cols:
        if pd.api.types.is_numeric_dtype(df[c]):
            df[c] = df[c].fillna(0)

    if "fy" in df.columns:
        df = df.sort_values(["ticker", "fy"]).groupby("ticker", as_index=False).tail(1)

    return df