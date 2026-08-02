"""Evidence-grounded report builder (R2 stub)."""

from __future__ import annotations

from typing import Any

from echo_clause.schemas import ComparisonResult, SourceClaim


def build_report(
    claims: list[SourceClaim],
    comparisons: list[ComparisonResult],
) -> dict[str, Any]:
    return {
        "conflict_count": sum(
            1 for c in comparisons if c.status.value == "CONTRADICTED"
        ),
        "claims": [c.model_dump() for c in claims],
        "comparisons": [c.model_dump() for c in comparisons],
    }
