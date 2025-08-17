# src/ingest_sec.py
from __future__ import annotations

import os
from typing import Optional

import pandas as pd
import requests

SEC_BASE = "https://data.sec.gov/api"
UA = os.environ.get("SEC_USER_AGENT", "corp-health-dashboard (email@example.com)")


def _get(url: str, params: Optional[dict] = None) -> dict:
    resp = requests.get(url, params=params, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    resp.raise_for_status()
    return resp.json()


def fetch_company_concepts(ticker: str) -> pd.DataFrame:
    """
    Fetch a small set of standardized concepts from SEC for the given ticker.
    Returns a wide DataFrame at the annual level (latest FY per ticker is used later).
    """
    comp = _get(f"{SEC_BASE}/xbrl/companyfacts/CIK{_ticker_to_cik(ticker)}.json")
    facts = comp.get("facts", {}).get("us-gaap", {})
    want = {
        "Revenues": "revenue",
        "OperatingIncomeLoss": "ebit",
        "DepreciationAndAmortization": "da",
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
    rows = []
    for gaap, col in want.items():
        if gaap not in facts:
            continue
        series = facts[gaap].get("units", {})
        usd = series.get("USD", [])
        for item in usd:
            if item.get("form") in {"10-K", "10-K/A"} and item.get("fy"):
                rows.append(
                    {
                        "ticker": ticker.upper(),
                        "fy": int(item["fy"]),
                        "col": col,
                        "value": float(item["val"]),
                    }
                )
    if not rows:
        return pd.DataFrame()
    long_df = pd.DataFrame(rows)
    wide = long_df.pivot_table(index=["ticker", "fy"], columns="col", values="value", aggfunc="first").reset_index()
    if "da" in wide.columns:
        wide["ebitda"] = (wide.get("ebit", 0) + wide["da"]).fillna(pd.NA)
    else:
        wide["ebitda"] = pd.NA
    return wide


def _ticker_to_cik(ticker: str) -> str:
    """
    Resolve ticker to CIK number padded to 10 digits via SEC mapping.
    """
    url = "https://www.sec.gov/files/company_tickers.json"
    js = _get(url)
    for _, row in js.items():
        if row["ticker"].upper() == ticker.upper():
            return str(row["cik_str"]).zfill(10)
    raise ValueError(f"Could not resolve CIK for {ticker}")