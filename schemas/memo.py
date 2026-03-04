"""Top-level IC memo and pipeline output schemas."""

from pydantic import BaseModel, Field

from schemas.common import (
    Competitor,
    InvestmentThesis,
    ManagementAssessment,
    MarketAnalysis,
    Risk,
    SourcedClaim,
)
from schemas.non_saas import NonSaaSAnalysis
from schemas.saas import SaaSAnalysis


class CondensedInput(BaseModel):
    """Stage A output: condensed and classified inputs."""

    company_name: str
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

    executive_summary: str
    company_overview: list[SourcedClaim]
    business_model_description: list[SourcedClaim]
    market_analysis: MarketAnalysis
    competitive_positioning: list[Competitor]
    saas_analysis: SaaSAnalysis | None = None
    non_saas_analysis: NonSaaSAnalysis | None = None
    management_assessment: ManagementAssessment
    investment_thesis: InvestmentThesis
    risks: list[Risk]
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
