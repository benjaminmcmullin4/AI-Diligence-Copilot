"""Pydantic models for the Meridian Diligence Copilot.

Consolidates all schemas: enums, common models, SaaS models, Non-SaaS models,
input models, and memo/pipeline models into a single flat module.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════════

class EvidenceSource(str, Enum):
    """Source type for an evidence-backed claim."""
    WEBSITE = "website"
    FINANCIALS = "financials"
    NOTES = "notes"
    REVIEWS = "reviews"
    TRANSCRIPTS = "transcripts"
    MANAGEMENT = "management"
    INFERRED = "inferred"


class BusinessModelType(str, Enum):
    """Top-level business model classifier."""
    SAAS = "saas"
    NON_SAAS = "non_saas"


# ═══════════════════════════════════════════════════════════════════════════
# Common Models
# ═══════════════════════════════════════════════════════════════════════════

class SourcedClaim(BaseModel):
    """A claim with its evidence source and confidence level."""

    claim: str = Field(description="The textual claim or finding")
    source: EvidenceSource = Field(description="Where this claim originated")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")


class Risk(BaseModel):
    """A diligence risk with severity scoring."""

    category: str = Field(description="E.g., 'Market', 'Technology', 'Regulatory', 'Financial'")
    description: str = Field(description="Detailed description of the risk")
    severity: int = Field(ge=1, le=5, description="1=Low, 5=Critical")
    likelihood: int = Field(ge=1, le=5, description="1=Unlikely, 5=Very likely")
    mitigant: str = Field(description="How this risk could be mitigated")
    diligence_question: str = Field(description="Question to ask management about this risk")


class Competitor(BaseModel):
    """Competitor with positioning assessment."""

    name: str = Field(description="Competitor company name")
    description: str = Field(description="Brief description of the competitor")
    estimated_revenue: str = Field(default="Unknown", description="Estimated revenue or scale")
    threat_level: int = Field(ge=1, le=5, description="1=Low, 5=Critical threat")
    differentiation: str = Field(description="How the target company differs")
    source: EvidenceSource = Field(
        default=EvidenceSource.INFERRED, description="Source of competitor information"
    )


class MarketAnalysis(BaseModel):
    """TAM/SAM/SOM analysis with methodology."""

    tam: str = Field(description="Total Addressable Market with sizing methodology")
    sam: str = Field(description="Serviceable Addressable Market")
    som: str = Field(description="Serviceable Obtainable Market")
    tam_value_b: float | None = Field(None, description="TAM in $B")
    sam_value_b: float | None = Field(None, description="SAM in $B")
    som_value_b: float | None = Field(None, description="SOM in $B")
    methodology: str = Field(description="How market sizes were estimated")
    why_now: list[SourcedClaim] = Field(description="Why this market is attractive now")
    expansion_paths: list[str] = Field(description="Adjacent markets or expansion opportunities")


class ManagementAssessment(BaseModel):
    """Assessment of management team."""

    strengths: list[SourcedClaim] = Field(
        default_factory=list, description="Management team strengths"
    )
    gaps: list[str] = Field(
        default_factory=list, description="Missing roles or capabilities"
    )
    scaling_readiness: str = Field(description="Assessment of team's ability to scale")
    key_person_risk: str = Field(description="Dependency on specific individuals")


class InvestmentThesis(BaseModel):
    """Bull/bear case and value creation plan."""

    thesis_one_liner: str = Field(description="Single sentence investment thesis")
    bull_case: list[SourcedClaim] = Field(description="Reasons to invest")
    bear_case: list[SourcedClaim] = Field(description="Reasons to pass")
    value_creation_levers: list[str] = Field(description="How to drive value post-investment")
    what_makes_this_a_no: str = Field(
        description="The single biggest reason this deal could fail — intellectual honesty"
    )


# ═══════════════════════════════════════════════════════════════════════════
# SaaS Models
# ═══════════════════════════════════════════════════════════════════════════

class BenchmarkRating(BaseModel):
    """A metric value with benchmark comparison."""

    value: str = Field(description="The metric value as displayed")
    numeric_value: float | None = Field(None, description="Numeric value for charting")
    benchmark: str = Field(description="Industry benchmark context")
    rating: str = Field(description="'green', 'yellow', or 'red'")
    commentary: str = Field(description="Brief interpretation")


class CohortVintage(BaseModel):
    """A single cohort vintage for retention curves."""

    cohort_label: str = Field(description="E.g., 'Q1 2023'")
    months: list[int] = Field(description="Month numbers (0, 3, 6, 12, ...)")
    retention_pct: list[float] = Field(description="Retention % at each month")


class ARRBridge(BaseModel):
    """ARR bridge waterfall components."""

    beginning_arr: float = Field(description="Starting ARR ($M)")
    new_arr: float = Field(description="New logo ARR ($M)")
    expansion_arr: float = Field(description="Expansion ARR ($M)")
    contraction_arr: float = Field(description="Contraction ARR ($M, negative)")
    churn_arr: float = Field(description="Churned ARR ($M, negative)")
    ending_arr: float = Field(description="Ending ARR ($M)")


class SaaSMetrics(BaseModel):
    """Full SaaS metric framework."""

    arr: BenchmarkRating = Field(description="Annual Recurring Revenue")
    arr_growth_yoy: BenchmarkRating = Field(description="ARR year-over-year growth")
    nrr: BenchmarkRating = Field(description="Net Revenue Retention")
    grr: BenchmarkRating = Field(description="Gross Revenue Retention")
    gross_margin: BenchmarkRating = Field(description="Gross margin percentage")
    cac_payback: BenchmarkRating = Field(description="CAC payback period")
    ltv_cac: BenchmarkRating = Field(description="LTV to CAC ratio")
    rule_of_40: BenchmarkRating = Field(description="Rule of 40 score")
    magic_number: BenchmarkRating = Field(description="SaaS magic number")
    logo_retention: BenchmarkRating = Field(description="Logo retention rate")


class SaaSAnalysis(BaseModel):
    """Complete SaaS financial analysis."""

    metrics: SaaSMetrics = Field(description="Full SaaS metrics framework")
    arr_bridge: ARRBridge | None = Field(None, description="ARR bridge waterfall data")
    cohort_vintages: list[CohortVintage] = Field(
        default_factory=list, description="Cohort retention vintage data"
    )
    revenue_quality_assessment: list[SourcedClaim] = Field(
        default_factory=list, description="Revenue quality assessment claims"
    )
    unit_economics_assessment: list[SourcedClaim] = Field(
        default_factory=list, description="Unit economics assessment claims"
    )
    growth_durability: list[SourcedClaim] = Field(
        default_factory=list, description="Growth durability assessment claims"
    )


# ═══════════════════════════════════════════════════════════════════════════
# Non-SaaS Models
# ═══════════════════════════════════════════════════════════════════════════

class NonSaaSMetrics(BaseModel):
    """Non-SaaS metric framework."""

    revenue: BenchmarkRating = Field(description="Total revenue")
    revenue_growth_yoy: BenchmarkRating = Field(description="Revenue year-over-year growth")
    gross_margin: BenchmarkRating = Field(description="Gross margin percentage")
    ebitda_margin: BenchmarkRating = Field(description="EBITDA margin percentage")
    adjusted_ebitda: BenchmarkRating = Field(description="Adjusted EBITDA")
    fcf_conversion: BenchmarkRating = Field(description="Free cash flow conversion rate")
    working_capital: BenchmarkRating = Field(description="Working capital efficiency")
    same_store_growth: BenchmarkRating = Field(description="Same-store or same-unit growth")
    customer_concentration: BenchmarkRating = Field(description="Customer concentration risk")
    unit_economics: BenchmarkRating = Field(description="Unit-level economics")


class NonSaaSAnalysis(BaseModel):
    """Complete Non-SaaS financial analysis."""

    metrics: NonSaaSMetrics = Field(description="Full non-SaaS metrics framework")
    revenue_quality_assessment: list[SourcedClaim] = Field(
        default_factory=list, description="Revenue quality assessment claims"
    )
    unit_economics_assessment: list[SourcedClaim] = Field(
        default_factory=list, description="Unit economics assessment claims"
    )
    growth_durability: list[SourcedClaim] = Field(
        default_factory=list, description="Growth durability assessment claims"
    )
    working_capital_dynamics: str = Field(
        default="", description="Working capital cycle analysis"
    )
    customer_concentration_detail: str = Field(
        default="", description="Detailed customer concentration analysis"
    )


# ═══════════════════════════════════════════════════════════════════════════
# Input Models
# ═══════════════════════════════════════════════════════════════════════════

class AnalysisRequest(BaseModel):
    """User-submitted analysis request."""

    company_name: str = Field(..., min_length=1, max_length=200, description="Target company name")
    business_model: BusinessModelType = Field(
        default=BusinessModelType.SAAS, description="Business model classification"
    )
    website_url: str = Field(default="", description="Company website URL")
    fetch_website: bool = Field(default=True, description="Whether to scrape the website")

    # SaaS-specific financials
    arr: float | None = Field(None, description="Annual Recurring Revenue ($M)")
    nrr: float | None = Field(None, description="Net Revenue Retention (%)")
    grr: float | None = Field(None, description="Gross Revenue Retention (%)")
    customer_count: int | None = Field(None, description="Total customers")
    acv: float | None = Field(None, description="Average Contract Value ($K)")
    yoy_growth: float | None = Field(None, description="Year-over-year growth (%)")
    gross_margin: float | None = Field(None, description="Gross margin (%)")
    cac_payback: float | None = Field(None, description="CAC Payback period (months)")
    ltv_cac: float | None = Field(None, description="LTV/CAC ratio")

    # Non-SaaS financials
    revenue: float | None = Field(None, description="Total revenue ($M)")
    ebitda: float | None = Field(None, description="EBITDA ($M)")
    ebitda_margin: float | None = Field(None, description="EBITDA margin (%)")
    fcf: float | None = Field(None, description="Free Cash Flow ($M)")
    unit_count: int | None = Field(None, description="Number of units/locations")
    same_store_growth: float | None = Field(None, description="Same-store/unit growth (%)")

    # Qualitative inputs
    company_description: str = Field(default="", description="Free-text company description")
    internal_notes: str = Field(default="", description="Internal notes or CIM excerpts")
    customer_reviews: str = Field(default="", description="Customer reviews and NPS data")
    call_transcripts: str = Field(default="", description="Call transcripts or expert interviews")
    management_bios: str = Field(default="", description="Management team bios")
    known_competitors: str = Field(default="", description="Known competitor names or descriptions")
    uploaded_text: str = Field(default="", description="Text extracted from uploaded documents")

    def get_financial_summary(self) -> str:
        """Return a text summary of provided financial data."""
        lines: list[str] = []
        if self.business_model == BusinessModelType.SAAS:
            if self.arr is not None:
                lines.append(f"ARR: ${self.arr}M")
            if self.nrr is not None:
                lines.append(f"NRR: {self.nrr}%")
            if self.grr is not None:
                lines.append(f"GRR: {self.grr}%")
            if self.customer_count is not None:
                lines.append(f"Customers: {self.customer_count:,}")
            if self.acv is not None:
                lines.append(f"ACV: ${self.acv}K")
            if self.yoy_growth is not None:
                lines.append(f"YoY Growth: {self.yoy_growth}%")
            if self.gross_margin is not None:
                lines.append(f"Gross Margin: {self.gross_margin}%")
            if self.cac_payback is not None:
                lines.append(f"CAC Payback: {self.cac_payback} months")
            if self.ltv_cac is not None:
                lines.append(f"LTV/CAC: {self.ltv_cac}x")
        else:
            if self.revenue is not None:
                lines.append(f"Revenue: ${self.revenue}M")
            if self.ebitda is not None:
                lines.append(f"EBITDA: ${self.ebitda}M")
            if self.ebitda_margin is not None:
                lines.append(f"EBITDA Margin: {self.ebitda_margin}%")
            if self.fcf is not None:
                lines.append(f"FCF: ${self.fcf}M")
            if self.unit_count is not None:
                lines.append(f"Units/Locations: {self.unit_count}")
            if self.same_store_growth is not None:
                lines.append(f"Same-Store Growth: {self.same_store_growth}%")
        return "\n".join(lines) if lines else "No financial data provided."


# ═══════════════════════════════════════════════════════════════════════════
# Memo / Pipeline Models
# ═══════════════════════════════════════════════════════════════════════════

class CondensedInput(BaseModel):
    """Stage A output: condensed and classified inputs."""

    company_name: str = Field(description="Name of the target company")
    business_model: str = Field(description="'saas' or 'non_saas'")
    condensed_summary: str = Field(description="~1500 token summary with labeled sections")
    data_quality_flags: list[str] = Field(
        default_factory=list, description="Missing data or quality issues"
    )
    financial_data_available: bool = Field(
        default=False, description="Whether meaningful financial data was provided"
    )
    key_topics: list[str] = Field(
        default_factory=list, description="Main topics identified from inputs"
    )


class ICMemo(BaseModel):
    """Stage B output: full structured analysis."""

    executive_summary: str = Field(description="3-5 sentence executive summary")
    company_overview: list[SourcedClaim] = Field(description="Key company facts and claims")
    business_model_description: list[SourcedClaim] = Field(
        description="Business model analysis claims"
    )
    market_analysis: MarketAnalysis = Field(description="TAM/SAM/SOM and market analysis")
    competitive_positioning: list[Competitor] = Field(description="Competitive landscape")
    saas_analysis: SaaSAnalysis | None = Field(
        None, description="SaaS-specific analysis (populated for SaaS companies)"
    )
    non_saas_analysis: NonSaaSAnalysis | None = Field(
        None, description="Non-SaaS analysis (populated for non-SaaS companies)"
    )
    management_assessment: ManagementAssessment = Field(description="Management team assessment")
    investment_thesis: InvestmentThesis = Field(description="Bull/bear case and thesis")
    risks: list[Risk] = Field(description="Identified diligence risks")
    next_diligence_steps: list[str] = Field(
        description="10 concrete next steps for due diligence"
    )
    suggested_data_requests: list[str] = Field(
        description="Specific data to request from the company"
    )


class MemoOutput(BaseModel):
    """Stage C output: rendered memo for display/export."""

    memo_markdown: str = Field(description="Full IC memo in Markdown format")
    memo_html: str = Field(description="Full IC memo in HTML for PDF rendering")
    sections: list[str] = Field(description="Ordered list of section titles")
