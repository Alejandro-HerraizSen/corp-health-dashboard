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