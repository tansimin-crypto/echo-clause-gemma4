"""Calculator stub tests (R0)."""

from echo_clause.calculators import (
    calculate_fee_percentage,
    calculate_total_repayment,
    compare_normalized_terms,
)
from echo_clause.schemas import (
    CalculateFeePercentageArgs,
    CalculateTotalRepaymentArgs,
    ClaimField,
    CompareNormalizedTermsArgs,
    ComparisonStatus,
)


def test_calculate_total_repayment():
    result = calculate_total_repayment(
        CalculateTotalRepaymentArgs(
            principal=1000, platform_fee=150, processing_fee=0, interest_rate_percent=0
        )
    )
    assert result["total_repayment"] == 1150.0


def test_compare_late_fee_flat_vs_percent():
    result = compare_normalized_terms(
        CompareNormalizedTermsArgs(
            promise_value=20,
            contract_value=5,
            field=ClaimField.LATE_FEE,
            promise_evidence="one-time $20 fee",
            contract_evidence="5% of outstanding balance per week",
        )
    )
    assert result["status"] == "CONTRADICTED"
    assert result["deterministic_difference"].startswith("$20 one-time vs 5%")
    assert "-15" not in result["deterministic_difference"]


def test_calculate_fee_percentage():
    result = calculate_fee_percentage(
        CalculateFeePercentageArgs(fee_amount=150, principal=1000)
    )
    assert result["fee_percentage"] == 15.0


def test_compare_contradicted():
    result = compare_normalized_terms(
        CompareNormalizedTermsArgs(
            promise_value=1000,
            contract_value=1150,
            field=ClaimField.TOTAL_REPAYMENT,
            promise_evidence="Repay $1,000",
            contract_evidence="Total $1,150",
        )
    )
    assert result["status"] == ComparisonStatus.CONTRADICTED.value


def test_compare_supported_bool():
    result = compare_normalized_terms(
        CompareNormalizedTermsArgs(
            promise_value=True,
            contract_value=True,
            field=ClaimField.AUTOMATIC_DEBIT,
            promise_evidence="auto enabled",
            contract_evidence="auto enabled",
        )
    )
    assert result["status"] == ComparisonStatus.SUPPORTED.value
