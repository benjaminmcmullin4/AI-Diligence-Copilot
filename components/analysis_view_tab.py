"""Analysis View tab -- Tabbed display of a completed diligence analysis."""

from __future__ import annotations

import json

import streamlit as st

from config import DB_PATH, get_api_key, COLORS
from db import get_analysis, parse_json_field


def render_analysis_view(analysis_id: str) -> None:
    """Render the full analysis view for a given analysis_id."""

    # ── Load analysis from DB ──
    record = get_analysis(analysis_id)
    if record is None:
        st.error(f"Analysis `{analysis_id}` not found.")
        return

    # ── Header ──
    st.markdown(
        f'<div class="section-header">{record["company_name"]}</div>',
        unsafe_allow_html=True,
    )

    status = record.get("status", "pending")
    model_type = record.get("business_model", "unknown")
    badge_color = COLORS["teal"] if model_type == "saas" else COLORS["gold_accent"]
    status_colors = {
        "completed": COLORS["teal"],
        "running": COLORS["gold_accent"],
        "failed": COLORS["red_accent"],
        "pending": COLORS["muted"],
    }
    status_color = status_colors.get(status, COLORS["muted"])

    st.markdown(
        f'<span style="background: {badge_color}; color: white; padding: 0.2rem 0.6rem; '
        f'border-radius: 4px; font-size: 0.8rem; font-weight: 600;">{model_type.upper()}</span> '
        f'<span style="background: {status_color}; color: white; padding: 0.2rem 0.6rem; '
        f'border-radius: 4px; font-size: 0.8rem; font-weight: 600;">{status.capitalize()}</span>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Handle non-complete states ──
    if status == "running":
        st.info("This analysis is still running. Refresh the page to check for updates.")
        return
    elif status == "failed":
        st.error(f"This analysis failed: {record.get('error_message', 'Unknown error')}")
        return
    elif status == "pending":
        st.warning("This analysis has not been started yet.")
        return

    # ── Parse stored JSON ──
    analysis_data = parse_json_field(record.get("analysis_json"))
    memo_data = parse_json_field(record.get("memo_json"))

    if analysis_data is None:
        st.warning("Analysis data is not yet available.")
        return

    # ── Reconstruct Pydantic models (with graceful fallback) ──
    try:
        from schema import (
            ICMemo,
            MemoOutput,
            SaaSAnalysis,
            BenchmarkRating,
            ARRBridge,
            CohortVintage,
            NonSaaSAnalysis,
            Risk,
            Competitor,
            MarketAnalysis,
            ManagementAssessment,
            InvestmentThesis,
        )

        ic_memo = ICMemo(**analysis_data)
    except Exception as e:
        ic_memo = None
        st.warning(f"Could not parse analysis into structured model: {e}")

    memo_output = None
    if memo_data:
        try:
            from schema import MemoOutput

            memo_output = MemoOutput(**memo_data)
        except Exception:
            memo_output = None

    # ── Tabs ──
    tab_exec, tab_market, tab_financial, tab_mgmt, tab_risks, tab_memo = st.tabs(
        [
            "Executive Summary",
            "Market & Competition",
            "Financial Analysis",
            "Management & Thesis",
            "Risks & Diligence",
            "IC Memo & Export",
        ]
    )

    # ═══════════════════════════════════════════
    # Tab 1: Executive Summary
    # ═══════════════════════════════════════════
    with tab_exec:
        if ic_memo:
            # Thesis one-liner callout
            if ic_memo.investment_thesis:
                st.markdown(
                    f'<div style="background: rgba(26,188,156,0.1); border-left: 4px solid {COLORS["teal"]}; '
                    f'padding: 1rem; border-radius: 4px; margin-bottom: 1rem;">'
                    f'<strong style="color: {COLORS["navy"]};">Investment Thesis:</strong> '
                    f'{ic_memo.investment_thesis.thesis_one_liner}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                f'<div class="section-header">Executive Summary</div>',
                unsafe_allow_html=True,
            )
            st.markdown(ic_memo.executive_summary)

            # Key metrics grid
            st.markdown(
                f'<div class="section-header">Key Metrics</div>',
                unsafe_allow_html=True,
            )
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
            st.markdown(
                f'<div class="section-header">Company Snapshot</div>',
                unsafe_allow_html=True,
            )
            if ic_memo.company_overview:
                for claim in ic_memo.company_overview:
                    st.markdown(
                        f"- {claim.claim} _({claim.source.value}, {claim.confidence:.0%} confidence)_"
                    )
        else:
            st.info("Executive summary data is not available.")

    # ═══════════════════════════════════════════
    # Tab 2: Market & Competition
    # ═══════════════════════════════════════════
    with tab_market:
        if ic_memo:
            st.markdown(
                f'<div class="section-header">Market Sizing</div>',
                unsafe_allow_html=True,
            )
            market = ic_memo.market_analysis

            # TAM/SAM/SOM bar chart
            if market.tam_value_b or market.sam_value_b or market.som_value_b:
                try:
                    from viz import tam_sam_chart

                    fig = tam_sam_chart(
                        market.tam_value_b or 0,
                        market.sam_value_b or 0,
                        market.som_value_b or 0,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    pass

            st.markdown(f"**TAM:** {market.tam}")
            st.markdown(f"**SAM:** {market.sam}")
            st.markdown(f"**SOM:** {market.som}")
            st.caption(f"_Methodology: {market.methodology}_")

            # Why Now
            st.markdown(
                f'<div class="section-header">Why Now?</div>',
                unsafe_allow_html=True,
            )
            for claim in market.why_now:
                st.markdown(f"- {claim.claim}")

            # Competitors
            st.markdown(
                f'<div class="section-header">Competitive Landscape</div>',
                unsafe_allow_html=True,
            )
            try:
                from components.competitor_table import render_competitor_table

                render_competitor_table(ic_memo.competitive_positioning)
            except Exception as e:
                st.warning(f"Could not render competitor table: {e}")

            # Expansion paths
            if market.expansion_paths:
                st.markdown(
                    f'<div class="section-header">Expansion Paths</div>',
                    unsafe_allow_html=True,
                )
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
            except ImportError as e:
                st.error(f"Missing component: {e}")

            if ic_memo.saas_analysis:
                saas = ic_memo.saas_analysis
                st.markdown(
                    f'<div class="section-header">SaaS Metrics Dashboard</div>',
                    unsafe_allow_html=True,
                )

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
                    st.markdown(
                        f'<div class="section-header">ARR Bridge</div>',
                        unsafe_allow_html=True,
                    )
                    try:
                        from viz import arr_bridge_chart

                        fig = arr_bridge_chart(saas.arr_bridge)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass

                # Cohort Retention
                if saas.cohort_vintages:
                    st.markdown(
                        f'<div class="section-header">Cohort Retention</div>',
                        unsafe_allow_html=True,
                    )
                    try:
                        from viz import cohort_retention_chart

                        fig = cohort_retention_chart(saas.cohort_vintages)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass

                # Revenue Quality
                if saas.revenue_quality_assessment:
                    st.markdown(
                        f'<div class="section-header">Revenue Quality Assessment</div>',
                        unsafe_allow_html=True,
                    )
                    for claim in saas.revenue_quality_assessment:
                        st.markdown(f"- {claim.claim} _({claim.source.value})_")

            elif ic_memo.non_saas_analysis:
                nonsaas = ic_memo.non_saas_analysis
                st.markdown(
                    f'<div class="section-header">Financial Metrics Dashboard</div>',
                    unsafe_allow_html=True,
                )

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
                    st.markdown(
                        f'<div class="section-header">Revenue Quality Assessment</div>',
                        unsafe_allow_html=True,
                    )
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
            st.markdown(
                f'<div class="section-header">Management Assessment</div>',
                unsafe_allow_html=True,
            )
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
            st.markdown(
                f'<div class="section-header">Investment Thesis</div>',
                unsafe_allow_html=True,
            )
            thesis = ic_memo.investment_thesis

            col_bull, col_bear = st.columns(2)
            with col_bull:
                st.markdown("**Bull Case**")
                for claim in thesis.bull_case:
                    st.markdown(
                        f'<div style="background: rgba(26,188,156,0.1); border-left: 4px solid {COLORS["teal"]}; '
                        f'padding: 0.5rem 0.75rem; margin: 0.3rem 0; border-radius: 4px;">'
                        f'{claim.claim}</div>',
                        unsafe_allow_html=True,
                    )
            with col_bear:
                st.markdown("**Bear Case**")
                for claim in thesis.bear_case:
                    st.markdown(
                        f'<div style="background: rgba(231,76,60,0.1); border-left: 4px solid {COLORS["red_accent"]}; '
                        f'padding: 0.5rem 0.75rem; margin: 0.3rem 0; border-radius: 4px;">'
                        f'{claim.claim}</div>',
                        unsafe_allow_html=True,
                    )

            # Value Creation Levers
            if thesis.value_creation_levers:
                st.markdown(
                    f'<div class="section-header">Value Creation Levers</div>',
                    unsafe_allow_html=True,
                )
                for lever in thesis.value_creation_levers:
                    st.markdown(f"- {lever}")

            # What Makes This a No
            st.markdown(
                f'<div class="section-header">What Makes This a No</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="background: rgba(231,76,60,0.1); border-left: 4px solid {COLORS["red_accent"]}; '
                f'padding: 1rem; border-radius: 4px;">'
                f'<strong style="color: {COLORS["navy"]};">Key Risk:</strong> '
                f'{thesis.what_makes_this_a_no}</div>',
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
            st.markdown(
                f'<div class="section-header">Risk Heatmap</div>',
                unsafe_allow_html=True,
            )
            if ic_memo.risks:
                try:
                    from viz import risk_heatmap

                    fig = risk_heatmap(ic_memo.risks)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not render risk heatmap: {e}")

            # Risk Table
            st.markdown(
                f'<div class="section-header">Risk Register</div>',
                unsafe_allow_html=True,
            )
            try:
                from components.risk_table import render_risk_table

                render_risk_table(ic_memo.risks)
            except Exception as e:
                st.warning(f"Could not render risk table: {e}")

            # Next Steps
            if ic_memo.next_diligence_steps:
                st.markdown(
                    f'<div class="section-header">Next Diligence Steps</div>',
                    unsafe_allow_html=True,
                )
                for i, step in enumerate(ic_memo.next_diligence_steps, 1):
                    st.checkbox(step, key=f"step_{i}")

            # Data Requests
            if ic_memo.suggested_data_requests:
                st.markdown(
                    f'<div class="section-header">Suggested Data Requests</div>',
                    unsafe_allow_html=True,
                )
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
            st.markdown(
                f'<div class="section-header">Investment Committee Memo</div>',
                unsafe_allow_html=True,
            )
            st.markdown(memo_markdown)
        else:
            st.info("IC memo has not been generated yet.")

        st.markdown("---")
        st.markdown(
            f'<div class="section-header">Export</div>',
            unsafe_allow_html=True,
        )

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
            # Try PDF export, fall back to HTML download
            if memo_output and memo_output.memo_html:
                try:
                    from export import generate_memo_pdf

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
