"""Schema contract tests (R0 — no model calls)."""

import pytest
from pydantic import ValidationError

from echo_clause.schemas import (
    CalculateFeePercentageArgs,
    CalculateTotalRepaymentArgs,
    ClaimField,
    ComparisonResult,
    ComparisonStatus,
    DemoGold,
    NormalizeFinancialTermArgs,
    SourceClaim,
    SourceType,
    ToolCallRequest,
)


def test_source_claim_all_fields():
    claim = SourceClaim(
        claim_id="c1",
        source_id="advertisement",
        source_type=SourceType.ADVERTISEMENT,
        field=ClaimField.PLATFORM_FEE,
        raw_value="No hidden fees",
        normalized_value=0.0,
        currency="USD",
        unit="currency",
        frequency=None,
        polarity="negative",
        evidence_text="No hidden fees",
        page_number=1,
        timestamp_start=None,
        timestamp_end=None,
        confidence=0.95,
        explicitness="explicit",
        needs_review=False,
    )
    assert claim.field == ClaimField.PLATFORM_FEE
    assert claim.currency == "USD"


def test_comparison_result_status_enum():
    result = ComparisonResult(
        canonical_field=ClaimField.TOTAL_REPAYMENT,
        promise_claim_ids=["p1"],
        contract_claim_ids=["c1"],
        status=ComparisonStatus.CONTRADICTED,
        severity="critical",
        deterministic_difference="+150",
        evidence_summary="Repay $1k vs $1.15k",
        clarification_question="Why is total $1,150?",
    )
    assert result.status == ComparisonStatus.CONTRADICTED


def test_tool_call_schemas():
    norm = NormalizeFinancialTermArgs(raw_text="$1,000", field=ClaimField.PRINCIPAL)
    assert norm.field == ClaimField.PRINCIPAL

    repay = CalculateTotalRepaymentArgs(principal=1000, platform_fee=150)
    assert repay.platform_fee == 150

    fee_pct = CalculateFeePercentageArgs(fee_amount=150, principal=1000)
    assert fee_pct.fee_amount == 150


def test_tool_call_request_allowlist_names():
    req = ToolCallRequest(
        name="calculate_fee_percentage",
        arguments={"fee_amount": 150, "principal": 1000},
    )
    assert req.name == "calculate_fee_percentage"


def test_invalid_tool_name_rejected():
    with pytest.raises(ValidationError):
        ToolCallRequest(name="eval", arguments={"code": "1+1"})


def test_claim_field_enum_complete():
    expected = {
        "principal",
        "interest_rate",
        "platform_fee",
        "processing_fee",
        "total_repayment",
        "repayment_term_days",
        "late_fee",
        "late_fee_frequency",
        "automatic_debit",
        "automatic_renewal",
        "cancellation_fee",
        "prepayment_penalty",
    }
    assert {f.value for f in ClaimField} == expected


def test_comparison_status_enum_complete():
    expected = {
        "SUPPORTED",
        "CONTRADICTED",
        "HIDDEN_IN_CONTRACT",
        "AMBIGUOUS",
        "MISSING_EVIDENCE",
        "NEEDS_REVIEW",
    }
    assert {s.value for s in ComparisonStatus} == expected


def test_demo_gold_schema():
    gold = DemoGold(
        expected_contradictions=[
            {
                "id": "c1",
                "canonical_field": "platform_fee",
                "promise_summary": "No hidden fees",
                "contract_summary": "Platform fee $150",
                "expected_status": "CONTRADICTED",
                "severity": "high",
            }
        ]
    )
    assert gold.min_contradiction_count == 5
