"""Tool registry tests (R0)."""

import pytest

from echo_clause.schemas import ClaimField
from echo_clause.tool_registry import ALLOWLIST, execute_tool_call, get_tool_definitions


def test_allowlist_has_five_tools():
    assert len(ALLOWLIST) == 5
    assert set(ALLOWLIST.keys()) == {
        "normalize_financial_term",
        "calculate_total_repayment",
        "calculate_fee_percentage",
        "compare_normalized_terms",
        "generate_clarification_questions",
    }


def test_tool_definitions_count():
    defs = get_tool_definitions()
    assert len(defs) == 5


def test_execute_calculate_fee_percentage():
    trace = execute_tool_call(
        {
            "name": "calculate_fee_percentage",
            "arguments": {"fee_amount": 15000, "principal": 100000},
        }
    )
    assert trace.validation_ok
    assert trace.output["fee_percentage"] == 15.0


def test_reject_unknown_tool():
    trace = execute_tool_call({"name": "shell_exec", "arguments": {"cmd": "ls"}})
    assert not trace.validation_ok


def test_reject_invalid_args():
    trace = execute_tool_call(
        {"name": "calculate_fee_percentage", "arguments": {"fee_amount": "bad"}}
    )
    assert not trace.validation_ok


def test_normalize_via_registry():
    trace = execute_tool_call(
        {
            "name": "normalize_financial_term",
            "arguments": {"raw_text": "₦100,000", "field": ClaimField.PRINCIPAL.value},
        }
    )
    assert trace.validation_ok
    assert trace.output["normalized_value"] == 100000.0
