"""Parser utility tests for gemma_runtime (R1, no model)."""

from echo_clause.gemma_runtime import (
    extract_tool_call,
    parse_json_with_one_repair,
    strip_code_fences,
)


def test_strip_code_fences():
    raw = '```json\n{"claims": []}\n```'
    assert strip_code_fences(raw) == '{"claims": []}'


def test_parse_json_with_trailing_comma_repair():
    broken = '{"claims": [{"claim_id": "c1",},]}'
    data, err = parse_json_with_one_repair(broken)
    assert data is not None
    assert err is None


def test_parse_json_fail_returns_error():
    data, err = parse_json_with_one_repair("not json at all {{{")
    assert data is None
    assert err is not None


def test_extract_tool_call_from_json():
    raw = '{"name": "calculate_fee_percentage", "arguments": {"fee_amount": 15000, "principal": 100000}}'
    tc = extract_tool_call(raw)
    assert tc["name"] == "calculate_fee_percentage"
    assert tc["arguments"]["fee_amount"] == 15000
