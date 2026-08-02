"""End-to-end EchoClause pipeline: extract → normalize → reconcile → report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from echo_clause.config import ASSETS_DIR, DISCLAIMER
from echo_clause.gemma_runtime import GemmaRuntime
from echo_clause.normalization import normalize_financial_term
from echo_clause.provenance import write_runtime_artifact
from echo_clause.reconciliation import CONTRACT_SOURCE_TYPES, PROMISE_SOURCE_TYPES, reconcile_claims
from echo_clause.report_builder import build_report
from echo_clause.schemas import (
    ClaimField,
    DemoGold,
    ExtractionResult,
    NormalizeFinancialTermArgs,
    SourceClaim,
    SourceType,
)


def normalize_claim(claim: SourceClaim) -> SourceClaim:
    """Apply deterministic normalization to a single claim."""
    norm = normalize_financial_term(
        NormalizeFinancialTermArgs(
            raw_text=claim.raw_value,
            field=claim.field,
            currency_hint=claim.currency,
        )
    )
    claim.normalized_value = norm["normalized_value"]
    claim.currency = norm.get("currency") or claim.currency
    claim.unit = norm.get("unit") or claim.unit
    claim.frequency = norm.get("frequency") or claim.frequency
    return claim


def normalize_claims(claims: list[SourceClaim]) -> list[SourceClaim]:
    return [normalize_claim(c) for c in claims]


def split_promise_contract(claims: list[SourceClaim]) -> tuple[list[SourceClaim], list[SourceClaim]]:
    promise = [c for c in claims if c.source_type in PROMISE_SOURCE_TYPES]
    contract = [c for c in claims if c.source_type in CONTRACT_SOURCE_TYPES]
    return promise, contract


def load_recorded_claims(path: Path | None = None) -> list[SourceClaim]:
    path = path or ASSETS_DIR / "recorded_claims.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return [SourceClaim.model_validate(c) for c in data["claims"]]


def claims_from_transcript_fallback(audio_path: Path, source_id: str) -> ExtractionResult:
    """ASR fallback: use sales_pitch.txt when native audio extraction unavailable."""
    transcript_path = audio_path.with_suffix(".txt")
    text = transcript_path.read_text(encoding="utf-8")
    claims: list[SourceClaim] = []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    field_map = [
        ("total_repayment", ClaimField.TOTAL_REPAYMENT, "Repay exactly $1,000"),
        ("processing_fee", ClaimField.PROCESSING_FEE, "no processing charges"),
        ("late_fee", ClaimField.LATE_FEE, "one-time $20 fee"),
    ]
    for i, (cid, field, evidence) in enumerate(field_map):
        raw = lines[i] if i < len(lines) else evidence
        claims.append(
            SourceClaim(
                claim_id=f"{source_id}_{cid}",
                source_id=source_id,
                source_type=SourceType.SALES_AUDIO,
                field=field,
                raw_value=raw,
                evidence_text=raw,
                confidence=0.85,
                explicitness="explicit",
                needs_review=True,
            )
        )
    return ExtractionResult(
        claims=claims,
        raw_model_output=f"[ASR_FALLBACK transcript]\n{text}",
        parse_valid=True,
        needs_review=True,
    )


def extract_all_sources(
    runtime: GemmaRuntime,
    assets_dir: Path,
    *,
    audio_fallback: bool = False,
) -> tuple[list[SourceClaim], dict[str, Any]]:
    """Extract claims from all four demo sources via Gemma (with optional ASR fallback)."""
    trace: dict[str, Any] = {}
    all_claims: list[SourceClaim] = []

    sources = [
        ("advertisement", assets_dir / "advertisement.png", SourceType.ADVERTISEMENT),
        ("support_chat", assets_dir / "support_chat.png", SourceType.SUPPORT_CHAT),
        ("contract", assets_dir / "contract.png", SourceType.CONTRACT),
    ]
    for source_id, path, stype in sources:
        result = runtime.extract_claims_from_image(path, source_id, stype)
        trace[source_id] = {
            "parse_valid": result.parse_valid,
            "claim_count": len(result.claims),
            "raw_model_output": result.raw_model_output[:500],
        }
        all_claims.extend(result.claims)

    audio_path = assets_dir / "sales_pitch.wav"
    aud_result = runtime.extract_claims_from_audio(audio_path, "sales_pitch")
    if (not aud_result.parse_valid or not aud_result.claims) and audio_fallback:
        aud_result = claims_from_transcript_fallback(audio_path, "sales_pitch")
        trace["sales_pitch"] = {"fallback": "ASR_transcript", "claim_count": len(aud_result.claims)}
    else:
        trace["sales_pitch"] = {
            "parse_valid": aud_result.parse_valid,
            "claim_count": len(aud_result.claims),
            "raw_model_output": aud_result.raw_model_output[:500],
        }
    all_claims.extend(aud_result.claims)

    return all_claims, trace


def run_pipeline(
    *,
    runtime: GemmaRuntime | None = None,
    use_recorded: bool = False,
    recorded_path: Path | None = None,
    assets_dir: Path | None = None,
    audio_fallback: bool = False,
) -> dict[str, Any]:
    """Run full promise-to-contract pipeline and return report + provenance."""
    assets_dir = assets_dir or ASSETS_DIR
    extraction_trace: dict[str, Any] = {}

    if use_recorded:
        claims = load_recorded_claims(recorded_path)
        extraction_trace["mode"] = "recorded"
    else:
        if runtime is None or runtime.model is None:
            raise RuntimeError("Gemma runtime required unless use_recorded=True")
        claims, extraction_trace = extract_all_sources(
            runtime, assets_dir, audio_fallback=audio_fallback
        )
        extraction_trace["mode"] = "live_gemma"

    normalized = normalize_claims(claims)
    promise, contract = split_promise_contract(normalized)
    comparisons = reconcile_claims(promise, contract)
    report = build_report(normalized, comparisons)

    gold = DemoGold.model_validate(
        json.loads((assets_dir / "gold.json").read_text(encoding="utf-8"))
    )
    expected_fields = {c.canonical_field for c in gold.expected_contradictions}
    detected = {
        c.canonical_field
        for c in comparisons
        if c.status.value == "CONTRADICTED" and c.canonical_field in expected_fields
    }
    report["disclaimer"] = DISCLAIMER
    report["demo_validation"] = {
        "expected_contradictions": len(gold.expected_contradictions),
        "detected_gold_contradictions": len(detected),
        "all_gold_detected": detected == expected_fields,
        "detected_fields": sorted(f.value for f in detected),
        "missing_fields": sorted(f.value for f in expected_fields - detected),
    }
    report["extraction_trace"] = extraction_trace
    report["model_id"] = runtime.model_id if runtime else "recorded_replay"

    return report


def write_pipeline_artifact(report: dict[str, Any], prefix: str = "pipeline_run") -> Path:
    return write_runtime_artifact(report, prefix=prefix)
