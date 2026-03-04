"""Input schemas for analysis requests."""

from enum import Enum

from pydantic import BaseModel, Field


class BusinessModelType(str, Enum):
    SAAS = "saas"
    NON_SAAS = "non_saas"


class AnalysisRequest(BaseModel):
    """User-submitted analysis request."""

    company_name: str = Field(..., min_length=1, max_length=200)
    business_model: BusinessModelType = BusinessModelType.SAAS
    website_url: str = ""
    fetch_website: bool = True

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
    company_description: str = ""
    internal_notes: str = ""
    customer_reviews: str = ""
    call_transcripts: str = ""
    management_bios: str = ""
    known_competitors: str = ""
    uploaded_text: str = ""

    def get_financial_summary(self) -> str:
        """Return a text summary of provided financial data."""
        lines = []
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
