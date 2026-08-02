#!/usr/bin/env python3
"""Stage and push EchoClause Kaggle kernel bundle."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "notebooks" / "_kaggle_bundle"
NB_NAME = "echo_clause_kaggle_demo.ipynb"
INCLUDE = [
    "echo_clause",
    "scripts",
    "assets",
    "tests",
    "pyproject.toml",
    "README.md",
    NB_NAME,
    "kernel-metadata.json",
]


def stage_bundle() -> Path:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    for item in INCLUDE:
        src = ROOT / "notebooks" / item if item in (NB_NAME, "kernel-metadata.json") else ROOT / item
        dst = STAGE / item
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    return STAGE


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage and push Kaggle kernel")
    parser.add_argument("--stage-only", action="store_true")
    args = parser.parse_args()

    creds = Path.home() / ".kaggle" / "kaggle.json"
    if not creds.exists() and not args.stage_only:
        print("BLOCKER: ~/.kaggle/kaggle.json not found. Run with --stage-only to prepare bundle.")
        return 1

    bundle = stage_bundle()
    print(f"Staged bundle: {bundle}")

    if args.stage_only:
        return 0

    result = subprocess.run(
        ["kaggle", "kernels", "push", "-p", str(bundle)],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
