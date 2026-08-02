#!/usr/bin/env python3
"""Run EchoClause end-to-end demo pipeline."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _clear_proxy_env() -> None:
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        os.environ.pop(key, None)


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from echo_clause.config import ASSETS_DIR  # noqa: E402
from echo_clause.gemma_runtime import GemmaRuntime  # noqa: E402
from echo_clause.pipeline import run_pipeline, write_pipeline_artifact  # noqa: E402


def main() -> int:
    _clear_proxy_env()
    parser = argparse.ArgumentParser(description="EchoClause demo pipeline")
    parser.add_argument(
        "--use-recorded",
        action="store_true",
        help="Use recorded Gemma claims fixture (offline replay)",
    )
    parser.add_argument(
        "--audio-fallback",
        action="store_true",
        help="Fall back to transcript if Gemma audio extraction fails",
    )
    parser.add_argument("--output", type=Path, default=None, help="Write JSON report to path")
    args = parser.parse_args()

    runtime = None
    if not args.use_recorded:
        runtime = GemmaRuntime()
        if not runtime.load():
            print("Gemma load failed; re-run with --use-recorded or on Kaggle GPU.")
            return 1

    report = run_pipeline(
        runtime=runtime,
        use_recorded=args.use_recorded,
        audio_fallback=args.audio_fallback,
    )
    validation = report.get("demo_validation", {})
    print(f"Conflicts detected: {report['conflict_count']}")
    print(f"Gold contradictions: {validation.get('detected_gold_contradictions')}/5")
    print(f"All gold detected: {validation.get('all_gold_detected')}")

    out = args.output or write_pipeline_artifact(report)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Report written: {out}")
    return 0 if validation.get("all_gold_detected") else 1


if __name__ == "__main__":
    raise SystemExit(main())
