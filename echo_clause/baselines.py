"""Baseline reconcilers for R4 evaluation (contract-only, text-concat)."""

from __future__ import annotations

import re
from typing import Any

from echo_clause.reconciliation import reconcile_claims
from echo_clause.schemas import ComparisonStatus, SourceClaim, SourceType


def contract_only_baseline(
    promise_claims: list[SourceClaim],
    contract_claims: list[SourceClaim],
) -> list[dict[str, Any]]:
    """Ignore promise evidence; only surface contract-side fields."""
    _ = promise_claims
    results = reconcile_claims([], contract_claims)
    return [
        {
            "canonical_field": r.canonical_field.value,
            "status": r.status.value,
            "severity": r.severity,
        }
        for r in results
    ]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def text_concat_baseline(
    promise_claims: list[SourceClaim],
    contract_claims: list[SourceClaim],
) -> list[dict[str, Any]]:
    """Naive string overlap baseline per canonical field."""
    results: list[dict[str, Any]] = []
    fields = sorted(
        {c.field for c in promise_claims} | {c.field for c in contract_claims},
        key=lambda f: f.value,
    )
    for field in fields:
        promises = [c for c in promise_claims if c.field == field]
        contracts = [c for c in contract_claims if c.field == field]
        if not promises and contracts:
            status = ComparisonStatus.HIDDEN_IN_CONTRACT
        elif promises and not contracts:
            status = ComparisonStatus.MISSING_EVIDENCE
        else:
            p_text = _normalize_text(" ".join(c.raw_value for c in promises))
            c_text = _normalize_text(" ".join(c.raw_value for c in contracts))
            if p_text == c_text:
                status = ComparisonStatus.SUPPORTED
            elif p_text in c_text or c_text in p_text:
                status = ComparisonStatus.AMBIGUOUS
            else:
                status = ComparisonStatus.CONTRADICTED
        results.append(
            {
                "canonical_field": field.value,
                "status": status.value,
                "severity": "medium",
            }
        )
    return results


def echo_clause_baseline(
    promise_claims: list[SourceClaim],
    contract_claims: list[SourceClaim],
) -> list[dict[str, Any]]:
    """Full deterministic reconciliation (recorded-claim replay path)."""
    results = reconcile_claims(promise_claims, contract_claims)
    return [
        {
            "canonical_field": r.canonical_field.value,
            "status": r.status.value,
            "severity": r.severity,
        }
        for r in results
    ]


def split_claims(claims: list[SourceClaim]) -> tuple[list[SourceClaim], list[SourceClaim]]:
    promise = [c for c in claims if c.source_type != SourceType.CONTRACT]
    contract = [c for c in claims if c.source_type == SourceType.CONTRACT]
    return promise, contract
