"""Claim reconciliation: promise evidence vs contract terms."""

from __future__ import annotations

from typing import Any

from echo_clause.calculators import compare_normalized_terms
from echo_clause.schemas import (
    ClaimField,
    CompareNormalizedTermsArgs,
    ComparisonResult,
    ComparisonStatus,
    SourceClaim,
    SourceType,
)

PROMISE_SOURCE_TYPES = {
    SourceType.ADVERTISEMENT,
    SourceType.SALES_AUDIO,
    SourceType.SUPPORT_CHAT,
    SourceType.OTHER,
}

CONTRACT_SOURCE_TYPES = {SourceType.CONTRACT}

_SEVERITY_BY_FIELD: dict[ClaimField, str] = {
    ClaimField.PLATFORM_FEE: "high",
    ClaimField.TOTAL_REPAYMENT: "critical",
    ClaimField.LATE_FEE: "high",
    ClaimField.REPAYMENT_TERM_DAYS: "medium",
    ClaimField.AUTOMATIC_DEBIT: "high",
}


def _pick_representative_claim(claims: list[SourceClaim]) -> SourceClaim | None:
    if not claims:
        return None
    explicit = [c for c in claims if c.explicitness == "explicit"]
    pool = explicit or claims
    return max(pool, key=lambda c: c.confidence)


def _merge_promise_values(claims: list[SourceClaim]) -> tuple[Any, str]:
    """Return best normalized value and combined evidence summary."""
    if not claims:
        return None, ""
    rep = _pick_representative_claim(claims)
    assert rep is not None
    value = rep.normalized_value if rep.normalized_value is not None else rep.raw_value
    evidence = "; ".join(c.evidence_text[:80] for c in claims[:3])
    return value, evidence


def reconcile_claims(
    promise_claims: list[SourceClaim],
    contract_claims: list[SourceClaim],
) -> list[ComparisonResult]:
    """Compare normalized promise claims against contract claims by canonical field."""
    contract_by_field: dict[ClaimField, list[SourceClaim]] = {}
    promise_by_field: dict[ClaimField, list[SourceClaim]] = {}

    for claim in contract_claims:
        contract_by_field.setdefault(claim.field, []).append(claim)
    for claim in promise_claims:
        promise_by_field.setdefault(claim.field, []).append(claim)

    all_fields = set(promise_by_field) | set(contract_by_field)
    results: list[ComparisonResult] = []

    for field in sorted(all_fields, key=lambda f: f.value):
        promises = promise_by_field.get(field, [])
        contracts = contract_by_field.get(field, [])

        if not promises and contracts:
            rep = _pick_representative_claim(contracts)
            assert rep is not None
            results.append(
                ComparisonResult(
                    canonical_field=field,
                    promise_claim_ids=[],
                    contract_claim_ids=[c.claim_id for c in contracts],
                    status=ComparisonStatus.HIDDEN_IN_CONTRACT,
                    severity=_SEVERITY_BY_FIELD.get(field, "medium"),  # type: ignore[arg-type]
                    evidence_summary=f"Contract specifies {rep.raw_value}; no matching promise found.",
                )
            )
            continue

        if promises and not contracts:
            rep = _pick_representative_claim(promises)
            assert rep is not None
            results.append(
                ComparisonResult(
                    canonical_field=field,
                    promise_claim_ids=[c.claim_id for c in promises],
                    contract_claim_ids=[],
                    status=ComparisonStatus.MISSING_EVIDENCE,
                    severity=_SEVERITY_BY_FIELD.get(field, "medium"),  # type: ignore[arg-type]
                    evidence_summary=f"Promise: {rep.raw_value}; contract silent.",
                )
            )
            continue

        promise_value, promise_evidence = _merge_promise_values(promises)
        contract_rep = _pick_representative_claim(contracts)
        assert contract_rep is not None
        contract_value = (
            contract_rep.normalized_value
            if contract_rep.normalized_value is not None
            else contract_rep.raw_value
        )

        cmp_out = compare_normalized_terms(
            CompareNormalizedTermsArgs(
                promise_value=promise_value,
                contract_value=contract_value,
                field=field,
                promise_evidence=promise_evidence,
                contract_evidence=contract_rep.evidence_text,
            )
        )
        status = ComparisonStatus(cmp_out["status"])
        results.append(
            ComparisonResult(
                canonical_field=field,
                promise_claim_ids=[c.claim_id for c in promises],
                contract_claim_ids=[c.claim_id for c in contracts],
                status=status,
                severity=_SEVERITY_BY_FIELD.get(field, "medium"),  # type: ignore[arg-type]
                deterministic_difference=cmp_out.get("deterministic_difference"),
                evidence_summary=(
                    f"Promise: {promise_evidence[:120]} | Contract: {contract_rep.evidence_text[:120]}"
                ),
                clarification_question=(
                    f"What is the correct {field.value} — "
                    f"as promised ({promise_value}) or as contracted ({contract_value})?"
                    if status == ComparisonStatus.CONTRADICTED
                    else None
                ),
            )
        )

    return results
