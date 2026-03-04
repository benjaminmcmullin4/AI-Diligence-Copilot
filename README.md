# Meridian | Diligence Copilot

**AI-powered commercial due diligence for growth equity investors.**

Meridian takes company inputs (financials, website, notes, transcripts) and produces a full IC-style investment memo with structured analysis, source attribution, risk scoring, cohort charts, and professional export.

## Features

- **Dual Business Model Support** — SaaS and Non-SaaS analysis with appropriate metric frameworks
- **Source Attribution** — Every claim cites its evidence source with confidence scores
- **3-Stage LLM Pipeline** — Condense > Analyze > Memo, powered by Claude
- **SaaS Metrics Dashboard** — NRR, GRR, ARR Bridge, Cohort Retention, Rule of 40, LTV/CAC
- **Non-SaaS Metrics** — EBITDA margins, FCF conversion, same-store growth, customer concentration
- **Risk Heatmap** — Severity x likelihood visualization with actionable mitigants
- **Competitive Analysis** — Auto-generated competitor landscape with threat scoring
- **PDF / HTML Export** — IC-quality memo with cover page, headers, and print CSS
- **Email OTP Authentication** — Lightweight email verification gate (optional)
- **Demo Mode** — 3 pre-built sample analyses to explore without an API key

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure (optional — demo mode works without API key)
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run
streamlit run app.py
```

## Streamlit Cloud Deployment

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set main file to `app.py`
4. Add secrets in Advanced Settings (see `.streamlit/secrets.toml.example`)
5. Deploy

## Docker

```bash
docker-compose up
# Open http://localhost:8501
```

## Authentication

Set `AUTH_ENABLED=true` and configure SMTP credentials to enable email OTP login. See `.env.example` for all auth settings. When disabled, all pages are accessible without login.

## Project Structure

```
app.py                    # Main dashboard
pages/                    # Streamlit multi-page app
  1_New_Analysis.py       # Input form
  2_Analysis_View.py      # 6-tab analysis display
  3_History.py            # Past analyses
core/                     # Config, database, auth, extraction
schemas/                  # Pydantic v2 data models
pipeline/                 # 3-stage LLM pipeline
components/               # Reusable Streamlit UI components
export/                   # PDF and Markdown export
demo/                     # Pre-computed sample analyses
```

## Sample Analyses (Demo Mode)

| Company | Type | Key Story |
|---------|------|-----------|
| **AcmeSaaS** | B2B Vertical SaaS | $15M ARR, 125% NRR, strong unit economics |
| **PeakHealth** | Healthcare SaaS | $8M ARR, 105% NRR, elevated churn, missing VP Sales |
| **SummitRetail** | Specialty Retail | $45M revenue, 18% EBITDA margins, private label growth |

## Tech Stack

- **Streamlit** — UI framework with custom dark theme
- **Anthropic Claude** — LLM via Instructor for structured output
- **Pydantic v2** — Type-safe data models
- **Plotly** — Interactive charts (cohort curves, ARR bridge, risk heatmap)
- **SQLite** — Zero-config database
- **WeasyPrint** — PDF generation (Docker only; HTML fallback on Streamlit Cloud)
