"""SaaS-specific analysis schemas."""

from pydantic import BaseModel, Field

from schemas.common import SourcedClaim


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

    arr: BenchmarkRating
    arr_growth_yoy: BenchmarkRating
    nrr: BenchmarkRating
    grr: BenchmarkRating
    gross_margin: BenchmarkRating
    cac_payback: BenchmarkRating
    ltv_cac: BenchmarkRating
    rule_of_40: BenchmarkRating
    magic_number: BenchmarkRating
    logo_retention: BenchmarkRating


class SaaSAnalysis(BaseModel):
    """Complete SaaS financial analysis."""

    metrics: SaaSMetrics
    arr_bridge: ARRBridge | None = None
    cohort_vintages: list[CohortVintage] = Field(default_factory=list)
    revenue_quality_assessment: list[SourcedClaim] = Field(default_factory=list)
    unit_economics_assessment: list[SourcedClaim] = Field(default_factory=list)
    growth_durability: list[SourcedClaim] = Field(default_factory=list)
