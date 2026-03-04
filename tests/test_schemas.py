"""Tests for Pydantic schema validation."""

import pytest
from schema import Competitor, EvidenceSource, Risk, SourcedClaim
from schema import AnalysisRequest, BusinessModelType
from schema import CondensedInput
from schema import ARRBridge, BenchmarkRating, CohortVintage


class TestSourcedClaim:
    def test_valid_claim(self):
        claim = SourcedClaim(claim="Revenue grew 50%", source=EvidenceSource.FINANCIALS, confidence=0.9)
        assert claim.claim == "Revenue grew 50%"
        assert claim.source == EvidenceSource.FINANCIALS
        assert claim.confidence == 0.9

    def test_confidence_bounds(self):
        with pytest.raises(Exception):
            SourcedClaim(claim="test", source=EvidenceSource.INFERRED, confidence=1.5)
        with pytest.raises(Exception):
            SourcedClaim(claim="test", source=EvidenceSource.INFERRED, confidence=-0.1)


class TestRisk:
    def test_valid_risk(self):
        risk = Risk(
            category="Market",
            description="Cyclical end market",
            severity=4,
            likelihood=3,
            mitigant="Diversified customer base",
            diligence_question="What happened in the last downturn?",
        )
        assert risk.severity == 4
        assert risk.likelihood == 3

    def test_severity_bounds(self):
        with pytest.raises(Exception):
            Risk(
                category="Market",
                description="test",
                severity=6,
                likelihood=3,
                mitigant="none",
                diligence_question="test?",
            )


class TestCompetitor:
    def test_valid_competitor(self):
        comp = Competitor(
            name="Acme Corp",
            description="Market leader",
            threat_level=4,
            differentiation="Better product",
        )
        assert comp.name == "Acme Corp"
        assert comp.threat_level == 4
        assert comp.source == EvidenceSource.INFERRED


class TestAnalysisRequest:
    def test_saas_request(self):
        req = AnalysisRequest(
            company_name="TestCo",
            business_model=BusinessModelType.SAAS,
            arr=15.0,
            nrr=125.0,
        )
        summary = req.get_financial_summary()
        assert "ARR: $15.0M" in summary
        assert "NRR: 125.0%" in summary

    def test_non_saas_request(self):
        req = AnalysisRequest(
            company_name="RetailCo",
            business_model=BusinessModelType.NON_SAAS,
            revenue=45.0,
            ebitda=8.0,
        )
        summary = req.get_financial_summary()
        assert "Revenue: $45.0M" in summary
        assert "EBITDA: $8.0M" in summary

    def test_empty_financials(self):
        req = AnalysisRequest(company_name="EmptyCo")
        summary = req.get_financial_summary()
        assert summary == "No financial data provided."

    def test_company_name_required(self):
        with pytest.raises(Exception):
            AnalysisRequest(company_name="")


class TestBenchmarkRating:
    def test_valid_rating(self):
        rating = BenchmarkRating(
            value="$15M",
            numeric_value=15.0,
            benchmark="Strong for growth stage",
            rating="green",
            commentary="Good ARR base",
        )
        assert rating.rating == "green"
        assert rating.numeric_value == 15.0


class TestARRBridge:
    def test_bridge_components(self):
        bridge = ARRBridge(
            beginning_arr=9.1,
            new_arr=4.8,
            expansion_arr=2.3,
            contraction_arr=-0.6,
            churn_arr=-0.6,
            ending_arr=15.0,
        )
        calculated = (
            bridge.beginning_arr
            + bridge.new_arr
            + bridge.expansion_arr
            + bridge.contraction_arr
            + bridge.churn_arr
        )
        assert abs(calculated - bridge.ending_arr) < 0.01


class TestCohortVintage:
    def test_valid_cohort(self):
        cohort = CohortVintage(
            cohort_label="Q1 2023",
            months=[0, 3, 6, 12],
            retention_pct=[100, 98, 95, 90],
        )
        assert len(cohort.months) == len(cohort.retention_pct)


class TestCondensedInput:
    def test_valid_condensed(self):
        condensed = CondensedInput(
            company_name="TestCo",
            business_model="saas",
            condensed_summary="Test summary",
            data_quality_flags=["No financials"],
            financial_data_available=False,
            key_topics=["SaaS", "B2B"],
        )
        assert condensed.company_name == "TestCo"
        assert not condensed.financial_data_available
