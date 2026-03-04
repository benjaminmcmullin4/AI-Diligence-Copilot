"""Analysis View -- Tabbed display of a completed diligence analysis."""

import json

import streamlit as st

st.set_page_config(
    page_title="Analysis View | Meridian",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

from components.styles import inject_custom_css

inject_custom_css()

from core.config import get_settings
from core.database import get_analysis, init_db, parse_json_field

settings = get_settings()
init_db(settings.db_path)

from core.auth import require_auth
require_auth(settings)

# ── Get analysis_id ──
analysis_id = st.query_params.get("analysis_id")
if not analysis_id:
    st.warning("No analysis selected. Go to the dashboard and select an analysis.")
    if st.button("Back to Dashboard"):
        st.switch_page("app.py")
    st.stop()

# ── Load analysis from DB ──
record = get_analysis(settings.db_path, analysis_id)
if record is None:
    st.error(f"Analysis `{analysis_id}` not found.")
    if st.button("Back to Dashboard"):
        st.switch_page("app.py")
    st.stop()

# ── Header ──
st.markdown(
    f"""
    <div class="brand-header">
        <span class="brand-name">Meridian</span>
        <span class="tagline">{record['company_name']}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

status = record.get("status", "pending")
model_badge = "green" if record["business_model"] == "saas" else "yellow"
st.markdown(
    f'<span class="risk-badge {model_badge}">{record["business_model"].upper()}</span> '
    f'<span class="status-badge {status}">{status.capitalize()}</span>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Handle non-complete states ──
if status == "running":
    st.info("This analysis is still running. Refresh the page to check for updates.")
    st.stop()
elif status == "failed":
    st.error(f"This analysis failed: {record.get('error_message', 'Unknown error')}")
    st.stop()
elif status == "pending":
    st.warning("This analysis has not been started yet.")
    st.stop()

# ── Parse stored JSON ──
analysis_data = parse_json_field(record.get("analysis_json"))
memo_data = parse_json_field(record.get("memo_json"))

if analysis_data is None:
    st.warning("Analysis data is not yet available.")
    st.stop()

# ── Reconstruct Pydantic models (with graceful fallback) ──
try:
    from schemas.memo import ICMemo, MemoOutput
    from schemas.saas import SaaSAnalysis, BenchmarkRating, ARRBridge, CohortVintage
    from schemas.non_saas import NonSaaSAnalysis
    from schemas.common import Risk, Competitor, MarketAnalysis, ManagementAssessment, InvestmentThesis

    ic_memo = ICMemo(**analysis_data)
except Exception as e:
    ic_memo = None
    st.warning(f"Could not parse analysis into structured model: {e}")

memo_output = None
if memo_data:
    try:
        memo_output = MemoOutput(**memo_data)
    except Exception:
        memo_output = None

# ── Tabs ──
tab_exec, tab_market, tab_financial, tab_mgmt, tab_risks, tab_memo = st.tabs([
    "Executive Summary",
    "Market & Competition",
    "Financial Analysis",
    "Management & Thesis",
    "Risks & Diligence",
    "IC Memo & Export",
])

# ═══════════════════════════════════════════
# Tab 1: Executive Summary
# ═══════════════════════════════════════════
with tab_exec:
    if ic_memo:
        # Thesis one-liner callout
        if ic_memo.investment_thesis:
            st.markdown(
                f'<div class="callout-green"><strong>Investment Thesis:</strong> '
                f'{ic_memo.investment_thesis.thesis_one_liner}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("#### Executive Summary")
        st.markdown(ic_memo.executive_summary)

        # Key metrics grid
        st.markdown("#### Key Metrics")
        if ic_memo.saas_analysis:
            metrics = ic_memo.saas_analysis.metrics
            m_cols = st.columns(5)
            metric_items = [
                ("ARR", metrics.arr),
                ("ARR Growth", metrics.arr_growth_yoy),
                ("NRR", metrics.nrr),
                ("Gross Margin", metrics.gross_margin),
                ("Rule of 40", metrics.rule_of_40),
            ]
            for col, (label, br) in zip(m_cols, metric_items):
                with col:
                    delta_color = "normal" if br.rating == "green" else ("off" if br.rating == "yellow" else "inverse")
                    st.metric(label=label, value=br.value, delta=br.rating.upper())
        elif ic_memo.non_saas_analysis:
            metrics = ic_memo.non_saas_analysis.metrics
            m_cols = st.columns(5)
            metric_items = [
                ("Revenue", metrics.revenue),
                ("Revenue Growth", metrics.revenue_growth_yoy),
                ("Gross Margin", metrics.gross_margin),
                ("EBITDA Margin", metrics.ebitda_margin),
                ("FCF Conversion", metrics.fcf_conversion),
            ]
            for col, (label, br) in zip(m_cols, metric_items):
                with col:
                    st.metric(label=label, value=br.value, delta=br.rating.upper())

        # Company snapshot
        st.markdown("#### Company Snapshot")
        if ic_memo.company_overview:
            for claim in ic_memo.company_overview:
                st.markdown(f"- {claim.claim} _({claim.source.value}, {claim.confidence:.0%} confidence)_")
    else:
        st.info("Executive summary data is not available.")

# ═══════════════════════════════════════════
# Tab 2: Market & Competition
# ═══════════════════════════════════════════
with tab_market:
    if ic_memo:
        st.markdown("#### Market Sizing")
        market = ic_memo.market_analysis

        # TAM/SAM/SOM bar chart
        if market.tam_value_b or market.sam_value_b or market.som_value_b:
            try:
                import plotly.graph_objects as go

                tam_v = market.tam_value_b or 0
                sam_v = market.sam_value_b or 0
                som_v = market.som_value_b or 0

                fig = go.Figure(go.Bar(
                    x=["TAM", "SAM", "SOM"],
                    y=[tam_v, sam_v, som_v],
                    marker_color=["#353F3F", "#A8A8A8", "#FFFFFF"],
                    text=[f"${v:.1f}B" for v in [tam_v, sam_v, som_v]],
                    textposition="outside",
                ))
                fig.update_layout(
                    title="Market Sizing ($B)",
                    plot_bgcolor="#000000",
                    paper_bgcolor="#000000",
                    font=dict(color="#FFFFFF"),
                    yaxis=dict(title="$B", gridcolor="#353F3F", color="#A8A8A8"),
                    xaxis=dict(color="#A8A8A8"),
                    margin=dict(l=50, r=30, t=50, b=40),
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                pass

        st.markdown(f"**TAM:** {market.tam}")
        st.markdown(f"**SAM:** {market.sam}")
        st.markdown(f"**SOM:** {market.som}")
        st.caption(f"_Methodology: {market.methodology}_")

        # Why Now
        st.markdown("#### Why Now?")
        for claim in market.why_now:
            st.markdown(f"- {claim.claim}")

        # Competitors
        st.markdown("#### Competitive Landscape")
        try:
            from components.competitor_table import render_competitor_table
            render_competitor_table(ic_memo.competitive_positioning)
        except Exception as e:
            st.warning(f"Could not render competitor table: {e}")

        # Expansion paths
        if market.expansion_paths:
            st.markdown("#### Expansion Paths")
            for path in market.expansion_paths:
                st.markdown(f"- {path}")
    else:
        st.info("Market analysis data is not available.")

# ═══════════════════════════════════════════
# Tab 3: Financial Analysis
# ═══════════════════════════════════════════
with tab_financial:
    if ic_memo:
        try:
            from components.metrics_dashboard import render_metrics_dashboard
            from components.arr_bridge_chart import render_arr_bridge_chart
            from components.cohort_chart import render_cohort_chart
        except ImportError as e:
            st.error(f"Missing component: {e}")

        if ic_memo.saas_analysis:
            saas = ic_memo.saas_analysis
            st.markdown("#### SaaS Metrics Dashboard")

            metrics_dict = {
                "ARR": saas.metrics.arr,
                "ARR Growth YoY": saas.metrics.arr_growth_yoy,
                "Net Revenue Retention": saas.metrics.nrr,
                "Gross Revenue Retention": saas.metrics.grr,
                "Gross Margin": saas.metrics.gross_margin,
                "CAC Payback": saas.metrics.cac_payback,
                "LTV/CAC": saas.metrics.ltv_cac,
                "Rule of 40": saas.metrics.rule_of_40,
                "Magic Number": saas.metrics.magic_number,
                "Logo Retention": saas.metrics.logo_retention,
            }
            render_metrics_dashboard(metrics_dict)

            # ARR Bridge
            if saas.arr_bridge:
                st.markdown("#### ARR Bridge")
                render_arr_bridge_chart(saas.arr_bridge)

            # Cohort Retention
            if saas.cohort_vintages:
                st.markdown("#### Cohort Retention")
                render_cohort_chart(saas.cohort_vintages)

            # Revenue Quality
            if saas.revenue_quality_assessment:
                st.markdown("#### Revenue Quality Assessment")
                for claim in saas.revenue_quality_assessment:
                    st.markdown(f"- {claim.claim} _({claim.source.value})_")

        elif ic_memo.non_saas_analysis:
            nonsaas = ic_memo.non_saas_analysis
            st.markdown("#### Financial Metrics Dashboard")

            metrics_dict = {
                "Revenue": nonsaas.metrics.revenue,
                "Revenue Growth YoY": nonsaas.metrics.revenue_growth_yoy,
                "Gross Margin": nonsaas.metrics.gross_margin,
                "EBITDA Margin": nonsaas.metrics.ebitda_margin,
                "Adjusted EBITDA": nonsaas.metrics.adjusted_ebitda,
                "FCF Conversion": nonsaas.metrics.fcf_conversion,
                "Working Capital": nonsaas.metrics.working_capital,
                "Same-Store Growth": nonsaas.metrics.same_store_growth,
                "Customer Concentration": nonsaas.metrics.customer_concentration,
                "Unit Economics": nonsaas.metrics.unit_economics,
            }
            render_metrics_dashboard(metrics_dict)

            # Revenue Quality
            if nonsaas.revenue_quality_assessment:
                st.markdown("#### Revenue Quality Assessment")
                for claim in nonsaas.revenue_quality_assessment:
                    st.markdown(f"- {claim.claim} _({claim.source.value})_")
        else:
            st.info("No financial analysis data available.")
    else:
        st.info("Financial analysis data is not available.")

# ═══════════════════════════════════════════
# Tab 4: Management & Thesis
# ═══════════════════════════════════════════
with tab_mgmt:
    if ic_memo:
        # Management Assessment
        st.markdown("#### Management Assessment")
        mgmt = ic_memo.management_assessment

        if mgmt.strengths:
            st.markdown("**Strengths:**")
            for s in mgmt.strengths:
                st.markdown(f"- {s.claim} _({s.source.value})_")

        if mgmt.gaps:
            st.markdown("**Gaps:**")
            for g in mgmt.gaps:
                st.markdown(f"- {g}")

        st.markdown(f"**Scaling Readiness:** {mgmt.scaling_readiness}")
        st.markdown(f"**Key Person Risk:** {mgmt.key_person_risk}")

        st.markdown("---")

        # Bull / Bear Case
        st.markdown("#### Investment Thesis")
        thesis = ic_memo.investment_thesis

        col_bull, col_bear = st.columns(2)
        with col_bull:
            st.markdown("**Bull Case**")
            for claim in thesis.bull_case:
                st.markdown(
                    f'<div class="callout-green" style="padding: 0.5rem 0.75rem; margin: 0.3rem 0;">'
                    f'{claim.claim}</div>',
                    unsafe_allow_html=True,
                )
        with col_bear:
            st.markdown("**Bear Case**")
            for claim in thesis.bear_case:
                st.markdown(
                    f'<div class="callout-red" style="padding: 0.5rem 0.75rem; margin: 0.3rem 0;">'
                    f'{claim.claim}</div>',
                    unsafe_allow_html=True,
                )

        # Value Creation Levers
        if thesis.value_creation_levers:
            st.markdown("#### Value Creation Levers")
            for lever in thesis.value_creation_levers:
                st.markdown(f"- {lever}")

        # What Makes This a No
        st.markdown("#### What Makes This a No")
        st.markdown(
            f'<div class="callout-red"><strong>Key Risk:</strong> {thesis.what_makes_this_a_no}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Management and thesis data is not available.")

# ═══════════════════════════════════════════
# Tab 5: Risks & Diligence
# ═══════════════════════════════════════════
with tab_risks:
    if ic_memo:
        # Risk Heatmap
        st.markdown("#### Risk Heatmap")
        if ic_memo.risks:
            try:
                import plotly.graph_objects as go

                severities = [r.severity for r in ic_memo.risks]
                likelihoods = [r.likelihood for r in ic_memo.risks]
                labels = [r.category for r in ic_memo.risks]
                descriptions = [r.description[:60] + "..." if len(r.description) > 60 else r.description for r in ic_memo.risks]

                # Color by composite risk score
                scores = [s * l for s, l in zip(severities, likelihoods)]
                max_score = max(scores) if scores else 1

                fig = go.Figure(go.Scatter(
                    x=severities,
                    y=likelihoods,
                    mode="markers+text",
                    text=labels,
                    textposition="top center",
                    textfont=dict(size=10, color="#FFFFFF"),
                    marker=dict(
                        size=[max(12, s * 4) for s in scores],
                        color=scores,
                        colorscale=[[0, "#10b981"], [0.5, "#f59e0b"], [1, "#ef4444"]],
                        showscale=True,
                        colorbar=dict(title="Risk Score", tickfont=dict(color="#A8A8A8")),
                        line=dict(width=1, color="#353F3F"),
                    ),
                    hovertext=[f"{l}: {d}" for l, d in zip(labels, descriptions)],
                    hoverinfo="text",
                ))
                fig.update_layout(
                    xaxis=dict(title="Severity", range=[0.5, 5.5], dtick=1, color="#A8A8A8", gridcolor="#353F3F"),
                    yaxis=dict(title="Likelihood", range=[0.5, 5.5], dtick=1, color="#A8A8A8", gridcolor="#353F3F"),
                    plot_bgcolor="#000000",
                    paper_bgcolor="#000000",
                    font=dict(color="#FFFFFF"),
                    margin=dict(l=60, r=30, t=30, b=50),
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not render risk heatmap: {e}")

        # Risk Table
        st.markdown("#### Risk Register")
        try:
            from components.risk_table import render_risk_table
            render_risk_table(ic_memo.risks)
        except Exception as e:
            st.warning(f"Could not render risk table: {e}")

        # Next Steps
        if ic_memo.next_diligence_steps:
            st.markdown("#### Next Diligence Steps")
            for i, step in enumerate(ic_memo.next_diligence_steps, 1):
                st.checkbox(step, key=f"step_{i}")

        # Data Requests
        if ic_memo.suggested_data_requests:
            st.markdown("#### Suggested Data Requests")
            for req in ic_memo.suggested_data_requests:
                st.markdown(f"- {req}")
    else:
        st.info("Risk and diligence data is not available.")

# ═══════════════════════════════════════════
# Tab 6: IC Memo & Export
# ═══════════════════════════════════════════
with tab_memo:
    memo_markdown = record.get("memo_markdown", "")
    if memo_output and memo_output.memo_markdown:
        memo_markdown = memo_output.memo_markdown

    if memo_markdown:
        st.markdown("#### Investment Committee Memo")
        st.markdown(memo_markdown)
    else:
        st.info("IC memo has not been generated yet.")

    st.markdown("---")
    st.markdown("#### Export")

    col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)

    with col_dl1:
        if memo_markdown:
            st.download_button(
                label="Download Markdown",
                data=memo_markdown,
                file_name=f"{record['company_name']}_IC_Memo.md",
                mime="text/markdown",
            )
        else:
            st.button("Download Markdown", disabled=True)

    with col_dl2:
        # Try WeasyPrint PDF, fall back to HTML download
        if memo_output and memo_output.memo_html:
            try:
                from export.pdf import generate_memo_pdf
                pdf_bytes = generate_memo_pdf(
                    record["company_name"],
                    memo_output.memo_html,
                    record["business_model"],
                )
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=f"{record['company_name']}_IC_Memo.pdf",
                    mime="application/pdf",
                )
            except (ImportError, RuntimeError):
                st.download_button(
                    label="Download HTML (for PDF)",
                    data=memo_output.memo_html,
                    file_name=f"{record['company_name']}_IC_Memo.html",
                    mime="text/html",
                )
                st.caption("Use browser Print > Save as PDF")
        else:
            st.button("Download PDF", disabled=True)

    with col_dl3:
        if memo_output and memo_output.memo_html:
            st.download_button(
                label="Download HTML",
                data=memo_output.memo_html,
                file_name=f"{record['company_name']}_IC_Memo.html",
                mime="text/html",
            )
        else:
            st.button("Download HTML", disabled=True)

    with col_dl4:
        if analysis_data:
            st.download_button(
                label="Download JSON",
                data=json.dumps(analysis_data, indent=2),
                file_name=f"{record['company_name']}_Analysis.json",
                mime="application/json",
            )
        else:
            st.button("Download JSON", disabled=True)
