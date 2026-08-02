#!/usr/bin/env python3
"""Run R1 Gemma runtime spike and write provenance artifact."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _clear_proxy_env() -> None:
    """Avoid broken local SOCKS/HTTP proxy blocking Hugging Face downloads."""
    for key in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ):
        os.environ.pop(key, None)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from echo_clause.config import ASSETS_DIR
from echo_clause.gemma_runtime import GemmaRuntime
from echo_clause.provenance import get_gpu_info


def main() -> int:
    _clear_proxy_env()
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
        try:
            loaded = runtime.load()
        except Exception as exc:
            print(f"Model load crashed: {exc}")
            runtime.load_attempts.append(
                type("LoadAttempt", (), {
                    "model_id": runtime.model_id,
                    "config": {"label": "crash"},
                    "success": False,
                    "error": str(exc),
                })()
            )
            loaded = False
        if not loaded:
            print("Model load failed after all attempts; writing partial artifact.")
            not_run = True

    out = runtime.run_spike(ASSETS_DIR, not_run_gpu=not_run, skipped_load=args.not_run_gpu)
    print(f"Artifact written: {out}")
    print(f"GPU: {gpu}")
    print(f"Model: {runtime.model_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
