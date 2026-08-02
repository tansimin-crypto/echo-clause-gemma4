"""Claim extraction orchestration (R2 stub)."""

from __future__ import annotations

from pathlib import Path

from echo_clause.gemma_runtime import GemmaRuntime
from echo_clause.schemas import ExtractionResult, SourceType


def extract_claims_from_image(
    runtime: GemmaRuntime,
    image_path: Path,
    source_id: str,
    source_type: SourceType,
) -> ExtractionResult:
    return runtime.extract_claims_from_image(image_path, source_id, source_type)


def extract_claims_from_audio(
    runtime: GemmaRuntime,
    audio_path: Path,
    source_id: str,
) -> ExtractionResult:
    return runtime.extract_claims_from_audio(audio_path, source_id)
