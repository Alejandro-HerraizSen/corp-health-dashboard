# Corporate Health Dashboard

Consulting-style dashboard that ingests public financials and converts them into decision-ready scores:
- Liquidity, leverage, profitability, and growth metrics
- Peer benchmarking across a selected sector
- Company report cards and an exportable one-pager pack for stakeholders

## Quick start
```bash
git clone <your-repo-url>
cd corp-health-dashboard
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py

```

## Two Input Nodes
1. Sample CSV: runs instantly with templates/financials_example.csv
2. Live SEC (US): paste tickers and fetch recent fundamentals via the public SEC API

## Deliverables
- Streamlit dashboard with ranking and peer heatmap
- outputs/company_report_cards.xlsx ready for email
- outputs/metrics_long.csv for Power BI
- Optional: build a Power BI page using dashboards/PowerBI_Readme.md

## Disclaimer
Educational project. Not investment advice.