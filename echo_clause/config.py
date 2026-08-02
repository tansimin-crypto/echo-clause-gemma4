"""EchoClause configuration."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets" / "demo_case"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts" / "runs"

PRIMARY_MODEL_ID = "google/gemma-4-E4B-it"
FALLBACK_MODEL_ID = "google/gemma-4-E2B-it"

MAX_E4B_LOAD_ATTEMPTS = 2

DISCLAIMER = (
    "EchoClause compares representations across supplied evidence. "
    "It does not provide legal advice or determine legal enforceability."
)
