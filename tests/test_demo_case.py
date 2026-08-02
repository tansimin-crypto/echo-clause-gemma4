"""Demo case gold.json structure tests (R0)."""

import json
from pathlib import Path

import pytest

from echo_clause.config import ASSETS_DIR
from echo_clause.schemas import ClaimField, ComparisonStatus, DemoGold

GOLD_PATH = ASSETS_DIR / "gold.json"


@pytest.fixture(scope="module", autouse=True)
def ensure_assets():
    if not GOLD_PATH.exists():
        import subprocess
        import sys

        subprocess.run(
            [sys.executable, str(Path(__file__).resolve().parent.parent / "scripts" / "generate_demo_assets.py")],
            check=True,
        )


def test_gold_json_exists_and_validates():
    data = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    gold = DemoGold.model_validate(data)
    assert gold.case_id == "nuru_credit_demo"
    assert gold.company == "Nuru Credit"


def test_gold_has_five_contradictions():
    data = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    gold = DemoGold.model_validate(data)
    assert len(gold.expected_contradictions) == 5
    assert gold.min_contradiction_count == 5


def test_gold_contradiction_fields():
    data = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    gold = DemoGold.model_validate(data)
    fields = {c.canonical_field for c in gold.expected_contradictions}
    assert ClaimField.PLATFORM_FEE in fields
    assert ClaimField.TOTAL_REPAYMENT in fields
    assert ClaimField.LATE_FEE in fields
    assert ClaimField.REPAYMENT_TERM_DAYS in fields
    assert ClaimField.AUTOMATIC_DEBIT in fields


def test_gold_all_contradicted():
    data = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    gold = DemoGold.model_validate(data)
    for c in gold.expected_contradictions:
        assert c.expected_status == ComparisonStatus.CONTRADICTED


def test_demo_assets_exist():
    required = [
        "advertisement.png",
        "sales_pitch.wav",
        "sales_pitch.txt",
        "support_chat.png",
        "contract.png",
        "gold.json",
    ]
    for name in required:
        assert (ASSETS_DIR / name).exists(), f"Missing {name}"


def test_sales_pitch_transcript_content():
    text = (ASSETS_DIR / "sales_pitch.txt").read_text(encoding="utf-8")
    assert "₦100,000" in text
    assert "no processing charges" in text.lower()
    assert "₦2,000" in text
