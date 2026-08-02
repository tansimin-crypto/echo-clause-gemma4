#!/usr/bin/env python3
"""Upload EchoClause source bundle as a Kaggle dataset."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "notebooks" / "_kaggle_dataset"
DATASET_SLUG = "simingtan/echo-clause-gemma4-src"
INCLUDE = ["echo_clause", "scripts", "assets", "tests", "benchmark", "pyproject.toml", "README.md"]


def _find_kaggle_exe() -> str:
    import shutil as sh

    found = sh.which("kaggle")
    if found:
        return found
    candidate = Path.home() / "Documents" / "simil" / ".tools" / "python" / "Scripts" / "kaggle.exe"
    return str(candidate) if candidate.is_file() else "kaggle"


def stage_dataset() -> Path:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    for item in INCLUDE:
        src = ROOT / item
        dst = STAGE / item
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
        else:
            shutil.copy2(src, dst)
    meta = {
        "title": "echo-clause-gemma4-src",
        "id": DATASET_SLUG,
        "licenses": [{"name": "MIT"}],
    }
    (STAGE / "dataset-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return STAGE


def main() -> int:
    stage = stage_dataset()
    print(f"Staged dataset: {stage}")
    kaggle = _find_kaggle_exe()
    result = subprocess.run(
        [kaggle, "datasets", "create", "-p", str(stage), "--dir-mode", "zip"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    print(result.stdout)
    if result.returncode != 0:
        if "already exists" in (result.stderr + result.stdout).lower():
            result = subprocess.run(
                [kaggle, "datasets", "version", "-p", str(stage), "-m", "EchoClause source update", "--dir-mode", "zip"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            print(result.stdout)
            if result.returncode != 0:
                print(result.stderr, file=sys.stderr)
                return result.returncode
            return 0
        print(result.stderr, file=sys.stderr)
        return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
