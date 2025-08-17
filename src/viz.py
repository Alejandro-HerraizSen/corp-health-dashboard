# src/viz.py
from __future__ import annotations

import io

import matplotlib.pyplot as plt
import pandas as pd


def plot_peer_heatmap(scored: pd.DataFrame) -> bytes:
    cols = [
        "ebit_margin",
        "ebitda_margin",
        "roa",
        "roe",
        "current_ratio",
        "quick_ratio",
        "debt_to_equity",
        "ocf_margin",
        "fcf_margin",
        "ev_ebitda",
    ]
    df = scored.set_index("ticker")[cols].copy()
    fig, ax = plt.subplots(figsize=(9, 5))
    im = ax.imshow(df.fillna(0).values, aspect="auto")
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels(df.index)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha="right")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.04)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    return buf.getvalue()