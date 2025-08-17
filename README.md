# Corporate Health Dashboard

[![Live demo](https://img.shields.io/badge/Live%20demo-Open%20app-green)](https://alexs-corp-health-dashboard.streamlit.app)
![Built with](https://img.shields.io/badge/Stack-Python%20%7C%20Streamlit%20%7C%20Pandas-blue)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

 Corporate Health Dashboard is a consulting-style tool that converts public company financials into decision-ready health scores and a ranked watchlist. **Now with live updates—company values and metrics are fetched in real time from the SEC and Yahoo Finance whenever you run the app.** It produces a clean Excel report pack and a CSV you can drop into Power BI. Built to look like something a consultant or PE analyst would actually use.

---

## TLDR for recruiters

- Audience: consulting teams, PE screens, strategy and FP&A
- Output: a ranked list with profitability, liquidity, leverage and cash generation metrics, plus a peer heatmap
- Value: fast triage of targets with a transparent scoring model you can tune to a client’s priorities
Corporate Health Dashboard is a consulting-style app that instantly converts public company financials into decision-ready health scores and a ranked watchlist. **Now with live stock prices and fundamentals fetched in real time from the SEC and Yahoo Finance.**

The dashboard produces:
- A ranked peer table with key metrics and scores
- A heatmap for visual peer comparison
- One-click exports: Excel report cards and Power BI-ready CSV
- All data is fetched live for US tickers, or you can upload your own CSV




- Peer ranking table with a compact metric set
- One-click exports
  - `company_report_cards.xlsx` for email handoff
  - `metrics_long.csv` ready for Power BI
- Open the hosted app: **https://alexs-corp-health-dashboard.streamlit.app**
- In the sidebar pick **Sample CSV** to see results instantly
### App features
- **Live stocks:** Real-time SEC fundamentals and Yahoo Finance prices for US tickers
- **CSV upload:** Analyze your own company data
- **Adjustable scoring:** Tune weights for profitability, liquidity, leverage, and cash generation
- **Peer ranking:** Table with all key metrics and composite scores
- **Heatmap:** Visualize strengths and weaknesses across peers
- **Exports:**
    - `company_report_cards.xlsx` for email handoff
    - `metrics_long.csv` ready for Power BI
- **Streamlit UI:** Modern, interactive, and cloud-ready
- Switch to **SEC fetch** to pull recent fundamentals for tickers like `AAPL, MSFT, NVDA`
---

## How to run locally
The app is built for analysts, consultants, and anyone needing a fast, transparent view of corporate health. It:
- Accepts US tickers (AAPL, MSFT, etc.) or CSV uploads
- Fetches the latest annual fundamentals and market prices live
- Computes decision-ready metrics (profitability, liquidity, leverage, cash generation)
- Scores and ranks companies using a peer-normalized model
- Visualizes results in a ranking table and heatmap
- Exports results for further analysis or sharing

# clone your fork or local copy
git clone <YOUR_REPO_URL>
cd corp-health-dashboard
    - Enter tickers or upload a CSV to get live company data and scores
# macOS or Linux
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
- Combine into a composite score on a 0 to 100 scale with user-controlled weights
- For leverage, lower is better, so the model inverts that component
    - **Live data pulled from the SEC Company Facts API and Yahoo Finance for common us-gaap concepts and prices**
- Missing values are handled conservatively and shown for review
- Open Power BI Desktop, import that CSV, and build the one-pager using `dashboards/PowerBI_Readme.md`.

- Business framing that matches consulting and PE workflows
- Clean data ingestion, normalization, and transparent scoring
---

## Repo structure
    app/
If you want a quick tour or would like me to extend this for a specific sector or screening rule set, open an issue or reach out on LinkedIn.