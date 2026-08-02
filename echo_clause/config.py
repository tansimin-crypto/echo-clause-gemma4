"""EchoClause configuration."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets" / "demo_case"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts" / "runs"

PRIMARY_MODEL_ID = "google/gemma-4-E4B-it"
FALLBACK_MODEL_ID = "google/gemma-4-E2B-it"

# Kaggle Models mounts (see kernel-metadata model_sources)
KAGGLE_MODEL_CANDIDATES: dict[str, list[Path]] = {
    PRIMARY_MODEL_ID: [
        Path("/kaggle/input/models/google/gemma-4/transformers/gemma-4-e4b-it-qat-q4_0-unquantized/2"),
        Path("/kaggle/input/models/google/gemma-4/transformers/gemma-4-e4b-it/1"),
    ],
    FALLBACK_MODEL_ID: [
        Path("/kaggle/input/models/google/gemma-4/transformers/gemma-4-e2b-it-qat-q4_0-unquantized/2"),
        Path("/kaggle/input/models/google/gemma-4/transformers/gemma-4-e2b-it/1"),
    ],
}


def resolve_model_source(model_id: str) -> tuple[str | Path, bool]:
    """Return (path_or_hub_id, is_local_kaggle_mount)."""
    for candidate in KAGGLE_MODEL_CANDIDATES.get(model_id, []):
        if candidate.is_dir() and (candidate / "config.json").exists():
            return candidate, True
    return model_id, False


def kaggle_models_available() -> bool:
    return any(
        p.is_dir() and (p / "config.json").exists()
        for paths in KAGGLE_MODEL_CANDIDATES.values()
        for p in paths
    )

MAX_E4B_LOAD_ATTEMPTS = 2

DEFAULT_CURRENCY = "USD"

DISCLAIMER = (
    "EchoClause compares representations across supplied evidence. "
    "It does not provide legal advice or determine legal enforceability."
)
