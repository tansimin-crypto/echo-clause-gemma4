"""Tests for R4 baseline reconcilers."""

from echo_clause.baselines import contract_only_baseline, text_concat_baseline
from echo_clause.schemas import ClaimField, SourceClaim, SourceType


def _claim(field: ClaimField, raw: str, norm, stype: SourceType, cid: str) -> SourceClaim:
    return SourceClaim(
        claim_id=cid,
        source_id="s1",
        source_type=stype,
        field=field,
        raw_value=raw,
        normalized_value=norm,
        evidence_text=raw,
        confidence=0.9,
        explicitness="explicit",
        needs_review=False,
    )


def test_contract_only_ignores_promises():
    promise = [_claim(ClaimField.PLATFORM_FEE, "No fees", 0, SourceType.ADVERTISEMENT, "p1")]
    contract = [
        _claim(ClaimField.PLATFORM_FEE, "Fee ₦1000", 1000, SourceType.CONTRACT, "c1")
    ]
    rows = contract_only_baseline(promise, contract)
    assert rows[0]["status"] == "HIDDEN_IN_CONTRACT"


def test_text_concat_detects_contradiction():
    promise = [_claim(ClaimField.LATE_FEE, "No late fees", 0, SourceType.ADVERTISEMENT, "p1")]
    contract = [
        _claim(ClaimField.LATE_FEE, "5% weekly", 5, SourceType.CONTRACT, "c1")
    ]
    rows = text_concat_baseline(promise, contract)
    assert rows[0]["status"] == "CONTRADICTED"


def test_text_concat_supports_match():
    promise = [_claim(ClaimField.PRINCIPAL, "₦50,000", 50000, SourceType.ADVERTISEMENT, "p1")]
    contract = [_claim(ClaimField.PRINCIPAL, "₦50,000", 50000, SourceType.CONTRACT, "c1")]
    rows = text_concat_baseline(promise, contract)
    assert rows[0]["status"] == "SUPPORTED"
