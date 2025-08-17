import numpy as np
import pandas as pd

from src.metrics import compute_metrics


def test_basic_metrics():
    fin = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB"],
            "revenue": [100, 200],
            "ebit": [10, 30],
            "ebitda": [20, 40],
            "net_income": [8, 18],
            "total_assets": [80, 300],
            "shareholders_equity": [40, 150],
            "current_assets": [30, 60],
            "current_liabilities": [20, 50],
            "inventory": [5, 10],
            "operating_cf": [12, 36],
            "capex": [-5, -10],
            "short_term_debt": [2, 5],
            "long_term_debt": [8, 20],
            "cash": [3, 4],
            "shares_basic": [10, 20],
            "price": [5, 10],
        }
    )
    m = compute_metrics(fin)
    assert "current_ratio" in m.columns
    assert "debt_to_equity" in m.columns
    assert np.isfinite(m["market_cap"]).all()