"""Non-SaaS analysis schemas."""

from pydantic import BaseModel, Field

from schemas.common import SourcedClaim
from schemas.saas import BenchmarkRating


class NonSaaSMetrics(BaseModel):
    """Non-SaaS metric framework."""

    revenue: BenchmarkRating
    revenue_growth_yoy: BenchmarkRating
    gross_margin: BenchmarkRating
    ebitda_margin: BenchmarkRating
    adjusted_ebitda: BenchmarkRating
    fcf_conversion: BenchmarkRating
    working_capital: BenchmarkRating
    same_store_growth: BenchmarkRating
    customer_concentration: BenchmarkRating
    unit_economics: BenchmarkRating


class NonSaaSAnalysis(BaseModel):
    """Complete Non-SaaS financial analysis."""

    metrics: NonSaaSMetrics
    revenue_quality_assessment: list[SourcedClaim] = Field(default_factory=list)
    unit_economics_assessment: list[SourcedClaim] = Field(default_factory=list)
    growth_durability: list[SourcedClaim] = Field(default_factory=list)
    working_capital_dynamics: str = ""
    customer_concentration_detail: str = ""
