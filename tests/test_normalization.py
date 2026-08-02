"""Normalization stub tests (R0)."""

from echo_clause.normalization import normalize_financial_term
from echo_clause.schemas import ClaimField, NormalizeFinancialTermArgs


def test_normalize_naira_amount():
    result = normalize_financial_term(
        NormalizeFinancialTermArgs(raw_text="₦100,000", field=ClaimField.PRINCIPAL)
    )
    assert result["normalized_value"] == 100000.0
    assert result["currency"] == "NGN"


def test_normalize_zero_interest():
    result = normalize_financial_term(
        NormalizeFinancialTermArgs(raw_text="0% interest", field=ClaimField.INTEREST_RATE)
    )
    assert result["normalized_value"] == 0.0


def test_normalize_repayment_days():
    result = normalize_financial_term(
        NormalizeFinancialTermArgs(raw_text="Repay in 30 days", field=ClaimField.REPAYMENT_TERM_DAYS)
    )
    assert result["normalized_value"] == 30


def test_normalize_late_fee_frequency():
    result = normalize_financial_term(
        NormalizeFinancialTermArgs(
            raw_text="5% per week", field=ClaimField.LATE_FEE_FREQUENCY
        )
    )
    assert result["normalized_value"] == "weekly"


def test_normalize_late_fee_percent():
    result = normalize_financial_term(
        NormalizeFinancialTermArgs(
            raw_text="Late fee: 5% of outstanding balance per week",
            field=ClaimField.LATE_FEE,
        )
    )
    assert result["normalized_value"] == 5.0
    assert result["unit"] == "percent"
    assert result["frequency"] == "weekly"
    assert result["currency"] is None


def test_normalize_late_fee_flat_naira():
    result = normalize_financial_term(
        NormalizeFinancialTermArgs(
            raw_text="Late payment is only a one-time ₦2,000 fee",
            field=ClaimField.LATE_FEE,
        )
    )
    assert result["normalized_value"] == 2000.0
    assert result["unit"] == "currency"
    assert result["currency"] == "NGN"
    assert result["frequency"] == "one_time"


def test_normalize_automatic_debit_false():
    result = normalize_financial_term(
        NormalizeFinancialTermArgs(
            raw_text="There is no automatic debit after repayment",
            field=ClaimField.AUTOMATIC_DEBIT,
        )
    )
    assert result["normalized_value"] is False
