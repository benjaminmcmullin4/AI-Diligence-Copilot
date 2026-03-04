"""Shared schema components used across analysis types."""

from enum import Enum

from pydantic import BaseModel, Field


class EvidenceSource(str, Enum):
    WEBSITE = "website"
    FINANCIALS = "financials"
    NOTES = "notes"
    REVIEWS = "reviews"
    TRANSCRIPTS = "transcripts"
    MANAGEMENT = "management"
    INFERRED = "inferred"


class SourcedClaim(BaseModel):
    """A claim with its evidence source and confidence level."""

    claim: str
    source: EvidenceSource
    confidence: float = Field(ge=0.0, le=1.0)


class Risk(BaseModel):
    """A diligence risk with severity scoring."""

    category: str = Field(description="E.g., 'Market', 'Technology', 'Regulatory', 'Financial'")
    description: str
    severity: int = Field(ge=1, le=5, description="1=Low, 5=Critical")
    likelihood: int = Field(ge=1, le=5, description="1=Unlikely, 5=Very likely")
    mitigant: str = Field(description="How this risk could be mitigated")
    diligence_question: str = Field(description="Question to ask management about this risk")


class Competitor(BaseModel):
    """Competitor with positioning assessment."""

    name: str
    description: str
    estimated_revenue: str = Field(default="Unknown")
    threat_level: int = Field(ge=1, le=5, description="1=Low, 5=Critical threat")
    differentiation: str = Field(description="How the target company differs")
    source: EvidenceSource = EvidenceSource.INFERRED


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

    strengths: list[SourcedClaim] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list, description="Missing roles or capabilities")
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
