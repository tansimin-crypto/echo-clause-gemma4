"""Evidence-grounded report builder."""

from __future__ import annotations

from typing import Any

from echo_clause.calculators import generate_clarification_questions
from echo_clause.schemas import (
    ComparisonResult,
    ComparisonStatus,
    GenerateClarificationQuestionsArgs,
    SourceClaim,
)


def build_report(
    claims: list[SourceClaim],
    comparisons: list[ComparisonResult],
) -> dict[str, Any]:
    contradicted = [c for c in comparisons if c.status == ComparisonStatus.CONTRADICTED]
    questions = generate_clarification_questions(
        GenerateClarificationQuestionsArgs(comparisons=comparisons, max_questions=5)
    )
    return {
        "conflict_count": len(contradicted),
        "claims": [c.model_dump() for c in claims],
        "comparisons": [c.model_dump() for c in comparisons],
        "contradictions": [c.model_dump() for c in contradicted],
        "clarification_questions": questions["questions"],
    }
