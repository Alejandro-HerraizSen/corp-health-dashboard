import pandas as pd

from src.scoring import score_companies


def test_scores_exist():
    df = pd.DataFrame(
        {
            "ticker": ["A", "B", "C"],
            "ebit_margin": [0.1, 0.2, 0.15],
            "ebitda_margin": [0.2, 0.25, 0.22],
            "roa": [0.05, 0.08, 0.06],
            "roe": [0.10, 0.15, 0.12],
            "current_ratio": [1.5, 1.2, 2.0],
            "quick_ratio": [1.2, 1.1, 1.8],
            "debt_to_equity": [0.8, 1.5, 0.4],
            "ocf_margin": [0.12, 0.10, 0.15],
            "fcf_margin": [0.08, 0.05, 0.10],
            "market_cap": [1, 2, 3],
            "enterprise_value": [1, 2, 3],
        }
    )
    scored = score_companies(df)
    assert "score_0_100" in scored.columns
    assert len(scored) == 3