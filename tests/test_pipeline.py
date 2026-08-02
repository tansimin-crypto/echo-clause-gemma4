"""Pipeline integration tests (R2)."""

import json

from echo_clause.config import ASSETS_DIR
from echo_clause.pipeline import run_pipeline
from echo_clause.schemas import ComparisonStatus, DemoGold


def test_pipeline_detects_five_gold_contradictions():
    report = run_pipeline(use_recorded=True)
    validation = report["demo_validation"]
    assert validation["expected_contradictions"] == 5
    assert validation["detected_gold_contradictions"] == 5
    assert validation["all_gold_detected"] is True
    assert report["conflict_count"] >= 5


def test_pipeline_contradiction_fields_match_gold():
    report = run_pipeline(use_recorded=True)
    gold = DemoGold.model_validate(json.loads((ASSETS_DIR / "gold.json").read_text()))
    expected = {c.canonical_field for c in gold.expected_contradictions}
    detected = {
        c["canonical_field"]
        for c in report["contradictions"]
        if c["status"] == ComparisonStatus.CONTRADICTED.value
    }
    # canonical_field in report is enum value string
    from echo_clause.schemas import ClaimField

    detected_fields = {ClaimField(d) for d in detected if d in {f.value for f in ClaimField}}
    assert expected <= detected_fields


def test_pipeline_generates_clarification_questions():
    report = run_pipeline(use_recorded=True)
    assert len(report["clarification_questions"]) >= 1
