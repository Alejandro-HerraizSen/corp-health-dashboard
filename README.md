# Corporate Health Dashboard

[![Live demo](https://img.shields.io/badge/Live%20demo-Open%20app-green)](https://alexs-corp-health-dashboard.streamlit.app)
![Built with](https://img.shields.io/badge/Stack-Python%20%7C%20Streamlit%20%7C%20Pandas-blue)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A consulting-style tool that converts public company financials into decision-ready health scores and a ranked watchlist. It produces a clean Excel report pack and a CSV you can drop into Power BI. Built to look like something a consultant or PE analyst would actually use.

---

## TLDR for recruiters

- Audience: consulting teams, PE screens, strategy and FP&A
- Output: a ranked list with profitability, liquidity, leverage and cash generation metrics, plus a peer heatmap
- Value: fast triage of targets with a transparent scoring model you can tune to a client’s priorities
- Try it now: click the green Live demo badge above and choose Sample CSV in the sidebar

---



## Features

- CSV upload or live SEC fetch for US tickers
- Adjustable weights for profitability, liquidity, leverage, cash generation
- Peer ranking table with a compact metric set
- Heatmap to spot strengths and weaknesses at a glance
- One-click exports
  - `company_report_cards.xlsx` for email handoff
  - `metrics_long.csv` ready for Power BI

---

## Live demo

- Open the hosted app: **https://alexs-corp-health-dashboard.streamlit.app**
- In the sidebar pick **Sample CSV** to see results instantly
- Switch to **SEC fetch** to pull recent fundamentals for tickers like `AAPL, MSFT, NVDA`

---

## How to run locally

```bash
# clone your fork or local copy
git clone <YOUR_REPO_URL>
cd corp-health-dashboard

# create and activate a virtual environment
python -m venv .venv
# macOS or Linux
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

# install dependencies
pip install -r requirements.txt

# optional for live SEC fetch
# macOS or Linux
export SEC_USER_AGENT="corp-health-dashboard (you@example.com)"
# Windows PowerShell
# setx SEC_USER_AGENT "corp-health-dashboard (you@example.com)"

# run the app
# add repo root to PYTHONPATH so Streamlit can import src/
PYTHONPATH="$PWD" streamlit run app/streamlit_app.py
# Windows PowerShell:
# $env:PYTHONPATH = (Get-Location).Path; streamlit run app/streamlit_app.py

```
---
## Data, scoring and transparency
### Inputs
- Sample data at templates
- Live data pulled from the SEC Company Facts API for common us-gaap concepts
### Metrics
- Profitability: EBIT margin, EBITDA margin, ROA, ROE
- Liquidity: Current ratio, Quick ratio
- Leverage: Debt to Equity, Net debt to EBITDA
- Cash generation: Operating cash flow margin, Free cash flow margin
- Valuation helper: EV to EBITDA for context
### Scoring method
- Z-score metrics across the current peer set
- Combine into a composite score on a 0 to 100 scale with user-controlled weights
- For leverage, lower is better, so the model inverts that component
### Assumptions
- Latest full fiscal year per company is used when multiple years are available
- Missing values are handled conservatively and shown for review
- Educational project. Not investment advice
---
## Power BI handoff

- The app saves `outputs/metrics_long.csv`.
- Open Power BI Desktop, import that CSV, and build the one-pager using `dashboards/PowerBI_Readme.md`.
- Optional artifacts to include in a release:
  - `dashboards/CorporateHealth.pbix`
  - `dashboards/CorporateHealth.pdf`

---

## What this demonstrates

- Business framing that matches consulting and PE workflows
- Clean data ingestion, normalization, and transparent scoring
- Analyst-ready exports and an exec-friendly view
- Ability to blend data science and finance into a usable product

---

## Repo structure
corp-health-dashboard/
    app/
        streamlit_app.py
    src/
        init.py
        ingest_sec.py
        transform.py
        metrics.py
        scoring.py
        export.py
        viz.py
    templates/
        tickers_example.txt
        financials_example.csv
    outputs/
        .gitkeep
    dashboards/
        PowerBI_Readme.md
    tests/
        test_metrics.py
        test_scoring.py
    README.md
    requirements.txt
    .gitignore

## License

MIT. See `LICENSE`.

---

## Contact

If you want a quick tour or would like me to extend this for a specific sector or screening rule set, open an issue or reach out on LinkedIn.