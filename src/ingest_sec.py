# src/ingest_sec.py
from __future__ import annotations

import os
from functools import lru_cache
from typing import Dict, Iterable, Optional, Tuple

import pandas as pd
import requests
import yfinance as yf

SEC_BASE = "https://data.sec.gov/api"
UA = os.environ.get("SEC_USER_AGENT", "corp-health-dashboard (email@example.com)")


def _get_json(url: str, params: Optional[dict] = None) -> dict:
    resp = requests.get(
        url,
        params=params,
        headers={"User-Agent": UA, "Accept-Encoding": "gzip"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


@lru_cache(maxsize=1)
def _ticker_map() -> Dict[str, str]:
    """Return {TICKER: CIK_str_padded} using SEC's public mapping."""
    js = _get_json("https://www.sec.gov/files/company_tickers.json")
    out: Dict[str, str] = {}
    for _, row in js.items():
        t = str(row.get("ticker", "")).upper().strip()
        cik_str = str(row.get("cik_str", "")).strip()
        if t and cik_str:
            out[t] = cik_str.zfill(10)
    return out


def _normalize_ticker_for_yf(t: str) -> str:
    # yfinance uses "-" for class shares (e.g., BRK-B), while SEC uses "."
    return t.replace(".", "-").upper().strip()


def _normalize_ticker_for_sec(t: str) -> str:
    return t.replace("-", ".").upper().strip()


def _resolve_cik(ticker: str) -> str:
    t = _normalize_ticker_for_sec(ticker)
    m = _ticker_map()
    if t in m:
        return m[t]
    # Fallback: some tickers exist with/without class letter
    if t.endswith(".A") or t.endswith(".B"):
        base = t.split(".")[0]
        if base in m:
            return m[base]
    raise ValueError(f"SEC CIK not found for ticker '{ticker}'")


def _extract_latest_annual_value(facts: dict, gaap: str, units: Iterable[str]) -> Optional[Tuple[int, float]]:
    """Return (fy, value) for latest annual 10-K value of a concept, preferring given units."""
    node = facts.get("us-gaap", {}).get(gaap)
    if not node:
        return None
    series = node.get("units", {})
    rows = []
    for u in units:
        for item in series.get(u, []):
            if item.get("form") in {"10-K", "10-K/A"} and item.get("fy"):
                try:
                    fy = int(item["fy"])
                    val = float(item["val"])
                    rows.append((fy, val))
                except Exception:
                    continue
    if not rows:
        return None
    rows.sort(key=lambda r: r[0])  # by fiscal year
    return rows[-1]  # latest FY


def _extract_latest_instant_shares(facts: dict) -> Optional[Tuple[int, float]]:
    """Pick best shares concept (instant) for latest year."""
    candidates = [
        ("CommonStockSharesOutstanding", ["shares"]),
        ("EntityCommonStockSharesOutstanding", ["shares"]),
    ]
    best: Optional[Tuple[int, float]] = None
    for gaap, units in candidates:
        got = _extract_latest_annual_value(facts, gaap, units)
        if got:
            if best is None or got[0] > best[0]:
                best = got
    return best


def _extract_latest_duration_shares(facts: dict) -> Optional[Tuple[int, float]]:
    """Fallback: duration-based weighted average shares (basic)."""
    candidates = [
        ("WeightedAverageNumberOfSharesOutstandingBasic", ["shares"]),
        ("WeightedAverageNumberOfDilutedSharesOutstanding", ["shares"]),
    ]
    best: Optional[Tuple[int, float]] = None
    for gaap, units in candidates:
        got = _extract_latest_annual_value(facts, gaap, units)
        if got:
            if best is None or got[0] > best[0]:
                best = got
    return best


def _yf_latest_close(ticker: str) -> Tuple[float, Optional[str]]:
    t = _normalize_ticker_for_yf(ticker)
    try:
        hist = yf.Ticker(t).history(period="5d", auto_adjust=False)
        if not hist.empty and "Close" in hist:
            close = float(hist["Close"].dropna().iloc[-1])
            asof = str(hist.index[-1].date())
            return close, asof
    except Exception:
        pass
    return 1.0, None  # safe fallback


def fetch_fundamentals_and_price(ticker: str) -> pd.DataFrame:
    """
    For a single ticker, return a 1-row DataFrame with latest FY fundamentals,
    best-effort shares_basic, and a recent price.
    """
    cik = _resolve_cik(ticker)
    comp = _get_json(f"{SEC_BASE}/xbrl/companyfacts/CIK{cik}.json")
    facts = comp.get("facts", {})

    # Annual fundamentals (USD)
    items = {
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

    row: Dict[str, float | int | str | None] = {"ticker": _normalize_ticker_for_sec(ticker)}
    latest_fy = -1
    for gaap, col in items.items():
        got = _extract_latest_annual_value(facts, gaap, ["USD"])
        if got:
            fy, val = got
            row[col] = val
            if fy > latest_fy:
                latest_fy = fy

    # EBITDA if DA present
    if "ebit" in row and "da" in row:
        row["ebitda"] = float(row["ebit"]) + float(row["da"])
    # Shares (instant preferred, else duration WA)
    shares = _extract_latest_instant_shares(comp)
    if not shares:
        shares = _extract_latest_duration_shares(comp)
    if shares:
        row["shares_basic"] = float(shares[1])

    # Price
    price, asof = _yf_latest_close(ticker)
    row["price"] = price
    row["price_asof"] = asof

    if latest_fy > 0:
        row["fy"] = latest_fy

    return pd.DataFrame([row])


def fetch_bulk(tickers: Iterable[str]) -> pd.DataFrame:
    frames = []
    seen = set()
    for t in tickers:
        t = t.strip()
        if not t or t.upper() in seen:
            continue
        try:
            frames.append(fetch_fundamentals_and_price(t))
            seen.add(t.upper())
        except Exception as e:
            # Return a row with at least the ticker and error note
            frames.append(pd.DataFrame([{"ticker": t.upper(), "error": str(e)}]))
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    # Ensure required fields even if missing
    for c in ["shares_basic", "price"]:
        if c not in df.columns:
            df[c] = 1.0
    return df