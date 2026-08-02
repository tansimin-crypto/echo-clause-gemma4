"""Deterministic financial term normalization (Layer 3)."""

from __future__ import annotations

import re
from typing import Any

from echo_clause.schemas import ClaimField, NormalizeFinancialTermArgs


_CURRENCY_SYMBOLS = {"₦": "NGN", "ngn": "NGN", "naira": "NGN"}
_NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "ten": 10,
    "twenty": 20,
    "thirty": 30,
    "hundred": 100,
    "thousand": 1000,
}


def _parse_amount(text: str) -> tuple[float | None, str | None]:
    lowered = text.lower().strip()
    currency = None
    for sym, code in _CURRENCY_SYMBOLS.items():
        if sym in lowered or sym.lower() in lowered:
            currency = code
            break

    match = re.search(r"[\d,]+(?:\.\d+)?", text.replace(",", ""))
    if match:
        return float(match.group().replace(",", "")), currency

    if "no hidden fees" in lowered or "no processing charges" in lowered:
        return 0.0, currency or "NGN"
    if "0%" in text:
        return 0.0, currency or "NGN"

    return None, currency


def _parse_days(text: str) -> int | None:
    match = re.search(r"(\d+)\s*days?", text.lower())
    if match:
        return int(match.group(1))
    return None


def _parse_frequency(text: str) -> str | None:
    lowered = text.lower()
    if "one-time" in lowered or "one time" in lowered:
        return "one_time"
    if "weekly" in lowered or "per week" in lowered:
        return "weekly"
    if "daily" in lowered:
        return "daily"
    if "monthly" in lowered:
        return "monthly"
    return None


def _parse_bool(text: str) -> bool | None:
    lowered = text.lower()
    if any(k in lowered for k in ("no automatic debit", "disabled", "not enabled", "no auto")):
        return False
    if any(k in lowered for k in ("enabled", "automatic debit authorization", "auto-debit")):
        return True
    return None


def normalize_financial_term(args: NormalizeFinancialTermArgs) -> dict[str, Any]:
    """Normalize a raw financial term to structured values."""
    text = args.raw_text
    field = args.field
    currency = args.currency_hint or "NGN"

    result: dict[str, Any] = {
        "field": field.value,
        "raw_text": text,
        "normalized_value": text,
        "currency": currency,
        "unit": None,
        "frequency": None,
    }

    if field in {
        ClaimField.PRINCIPAL,
        ClaimField.PLATFORM_FEE,
        ClaimField.PROCESSING_FEE,
        ClaimField.TOTAL_REPAYMENT,
        ClaimField.LATE_FEE,
        ClaimField.CANCELLATION_FEE,
        ClaimField.PREPAYMENT_PENALTY,
    }:
        amount, detected_currency = _parse_amount(text)
        if amount is not None:
            result["normalized_value"] = amount
            result["currency"] = detected_currency or currency
            result["unit"] = "currency"

    elif field == ClaimField.INTEREST_RATE:
        pct = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
        if pct:
            result["normalized_value"] = float(pct.group(1))
            result["unit"] = "percent"
        elif "0%" in text or "zero interest" in text.lower():
            result["normalized_value"] = 0.0
            result["unit"] = "percent"

    elif field == ClaimField.REPAYMENT_TERM_DAYS:
        days = _parse_days(text)
        if days is not None:
            result["normalized_value"] = days
            result["unit"] = "days"

    elif field == ClaimField.LATE_FEE_FREQUENCY:
        freq = _parse_frequency(text)
        if freq:
            result["normalized_value"] = freq
            result["frequency"] = freq

    elif field in {ClaimField.AUTOMATIC_DEBIT, ClaimField.AUTOMATIC_RENEWAL}:
        val = _parse_bool(text)
        if val is not None:
            result["normalized_value"] = val
            result["unit"] = "boolean"

    return result
