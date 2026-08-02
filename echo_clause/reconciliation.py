"""Claim reconciliation (R2 stub)."""

from __future__ import annotations

from echo_clause.schemas import ComparisonResult, SourceClaim


def reconcile_claims(
    promise_claims: list[SourceClaim],
    contract_claims: list[SourceClaim],
) -> list[ComparisonResult]:
    """Placeholder for R2 pipeline."""
    return []
