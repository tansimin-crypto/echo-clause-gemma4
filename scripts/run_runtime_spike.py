#!/usr/bin/env python3
"""Run R1 Gemma runtime spike and write provenance artifact."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from echo_clause.config import ASSETS_DIR  # noqa: E402
from echo_clause.gemma_runtime import GemmaRuntime  # noqa: E402
from echo_clause.provenance import get_gpu_info  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="EchoClause R1 runtime spike")
    parser.add_argument(
        "--not-run-gpu",
        action="store_true",
        help="Skip model load; write NOT_RUN_GPU artifact with Kaggle commands",
    )
    args = parser.parse_args()

    gpu = get_gpu_info()
    runtime = GemmaRuntime()
    not_run = args.not_run_gpu

    if not not_run:
        loaded = runtime.load()
        if not loaded:
            print("Model load failed after all attempts; writing partial artifact.")
            not_run = True

    out = runtime.run_spike(ASSETS_DIR, not_run_gpu=not_run)
    print(f"Artifact written: {out}")
    print(f"GPU: {gpu}")
    print(f"Model: {runtime.model_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
