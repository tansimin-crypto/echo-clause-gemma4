"""Allowlisted tool registry with Pydantic validation and trace logging."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import ValidationError

from echo_clause.calculators import (
    calculate_fee_percentage,
    calculate_total_repayment,
    compare_normalized_terms,
    generate_clarification_questions,
)
from echo_clause.normalization import normalize_financial_term
from echo_clause.schemas import (
    CalculateFeePercentageArgs,
    CalculateTotalRepaymentArgs,
    CompareNormalizedTermsArgs,
    GenerateClarificationQuestionsArgs,
    NormalizeFinancialTermArgs,
    ToolCallRequest,
    ToolCallTrace,
)

ToolFn = Callable[..., dict[str, Any]]

ALLOWLIST: dict[str, tuple[type, ToolFn]] = {
    "normalize_financial_term": (NormalizeFinancialTermArgs, normalize_financial_term),
    "calculate_total_repayment": (CalculateTotalRepaymentArgs, calculate_total_repayment),
    "calculate_fee_percentage": (CalculateFeePercentageArgs, calculate_fee_percentage),
    "compare_normalized_terms": (CompareNormalizedTermsArgs, compare_normalized_terms),
    "generate_clarification_questions": (
        GenerateClarificationQuestionsArgs,
        generate_clarification_questions,
    ),
}


def get_tool_definitions() -> list[dict[str, Any]]:
    """Return JSON-schema tool definitions for Gemma function calling."""
    return [
        {
            "type": "function",
            "function": {
                "name": "normalize_financial_term",
                "description": "Normalize a raw financial term from evidence text.",
                "parameters": NormalizeFinancialTermArgs.model_json_schema(),
            },
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_total_repayment",
                "description": "Compute total repayment from principal and fees.",
                "parameters": CalculateTotalRepaymentArgs.model_json_schema(),
            },
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_fee_percentage",
                "description": "Compute fee as percentage of principal.",
                "parameters": CalculateFeePercentageArgs.model_json_schema(),
            },
        },
        {
            "type": "function",
            "function": {
                "name": "compare_normalized_terms",
                "description": "Compare promise vs contract normalized values.",
                "parameters": CompareNormalizedTermsArgs.model_json_schema(),
            },
        },
        {
            "type": "function",
            "function": {
                "name": "generate_clarification_questions",
                "description": "Generate user-facing clarification questions.",
                "parameters": GenerateClarificationQuestionsArgs.model_json_schema(),
            },
        },
    ]


def execute_tool_call(raw: dict[str, Any]) -> ToolCallTrace:
    """Validate and execute a single tool call. No eval/exec/shell."""
    trace = ToolCallTrace(
        raw_tool_call=raw,
        tool_name=str(raw.get("name", "")),
        validation_ok=False,
    )
    try:
        request = ToolCallRequest.model_validate(raw)
    except ValidationError as exc:
        trace.validation_error = str(exc)
        return trace

    if request.name not in ALLOWLIST:
        trace.validation_error = f"Tool '{request.name}' not in allowlist"
        return trace

    schema_cls, fn = ALLOWLIST[request.name]
    try:
        args = schema_cls.model_validate(request.arguments)
    except ValidationError as exc:
        trace.validation_error = str(exc)
        return trace

    trace.validation_ok = True
    trace.output = fn(args)
    return trace
