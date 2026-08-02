"""Deterministic financial calculators."""

from __future__ import annotations

from typing import Any

from echo_clause.schemas import (
    CalculateFeePercentageArgs,
    CalculateTotalRepaymentArgs,
    CompareNormalizedTermsArgs,
    ComparisonStatus,
    GenerateClarificationQuestionsArgs,
)


def calculate_total_repayment(args: CalculateTotalRepaymentArgs) -> dict[str, Any]:
    interest = args.principal * (args.interest_rate_percent / 100.0)
    total = args.principal + args.platform_fee + args.processing_fee + interest
    return {
        "principal": args.principal,
        "platform_fee": args.platform_fee,
        "processing_fee": args.processing_fee,
        "interest": round(interest, 2),
        "total_repayment": round(total, 2),
        "currency": args.currency,
    }


def calculate_fee_percentage(args: CalculateFeePercentageArgs) -> dict[str, Any]:
    if args.principal <= 0:
        return {
            "fee_amount": args.fee_amount,
            "principal": args.principal,
            "fee_percentage": None,
            "currency": args.currency,
            "error": "principal must be positive",
        }
    pct = (args.fee_amount / args.principal) * 100.0
    return {
        "fee_amount": args.fee_amount,
        "principal": args.principal,
        "fee_percentage": round(pct, 4),
        "currency": args.currency,
    }


def compare_normalized_terms(args: CompareNormalizedTermsArgs) -> dict[str, Any]:
    promise = args.promise_value
    contract = args.contract_value
    status = ComparisonStatus.SUPPORTED
    diff: str | None = None

    if isinstance(promise, (int, float)) and isinstance(contract, (int, float)):
        if promise != contract:
            status = ComparisonStatus.CONTRADICTED
            diff = f"{contract - promise:+.2f}"
    elif isinstance(promise, bool) and isinstance(contract, bool):
        if promise != contract:
            status = ComparisonStatus.CONTRADICTED
            diff = f"{promise} vs {contract}"
    elif str(promise).lower() != str(contract).lower():
        status = ComparisonStatus.CONTRADICTED
        diff = f"{promise} vs {contract}"

    return {
        "field": args.field.value,
        "promise_value": promise,
        "contract_value": contract,
        "status": status.value,
        "deterministic_difference": diff,
        "promise_evidence": args.promise_evidence,
        "contract_evidence": args.contract_evidence,
    }


def generate_clarification_questions(
    args: GenerateClarificationQuestionsArgs,
) -> dict[str, Any]:
    questions: list[str] = []
    for comp in args.comparisons:
        if comp.status in {
            ComparisonStatus.CONTRADICTED,
            ComparisonStatus.HIDDEN_IN_CONTRACT,
            ComparisonStatus.AMBIGUOUS,
        }:
            q = comp.clarification_question or (
                f"Can you clarify the {comp.canonical_field.value} terms? "
                f"Sales said: {comp.evidence_summary[:120]}"
            )
            questions.append(q)
        if len(questions) >= args.max_questions:
            break
    return {"questions": questions, "count": len(questions)}
