#!/usr/bin/env python3
"""R10 release audit: pytest, ruff, artifact and doc gates."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GIT = Path(r"D:\CodexData\cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe")


def run(cmd: list[str], cwd: Path = ROOT) -> tuple[int, str]:
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    out = (result.stdout or "") + (result.stderr or "")
    return result.returncode, out


def check_pytest() -> bool:
    code, out = run([sys.executable, "-m", "pytest", "-q"])
    print(out)
    return code == 0


def check_ruff() -> bool:
    code, out = run([sys.executable, "-m", "ruff", "check", "echo_clause", "scripts", "tests", "app.py"])
    print(out)
    return code == 0


def check_files() -> list[str]:
    errors: list[str] = []
    required = [
        ROOT / "README.md",
        ROOT / "submission" / "WRITEUP.md",
        ROOT / "submission" / "SUBMISSION_CHECKLIST.md",
        ROOT / "benchmark" / "cases.jsonl",
        ROOT / "docs" / "index.html",
        ROOT / "notebooks" / "kernel-metadata.json",
        ROOT / "assets" / "demo_case" / "gold.json",
    ]
    for path in required:
        if not path.exists():
            errors.append(f"Missing required file: {path.relative_to(ROOT)}")
    index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    if "Interactive replay generated from a recorded Gemma 4 run" not in index:
        errors.append("docs/index.html missing recorded-run banner text")
    meta = (ROOT / "notebooks" / "kernel-metadata.json").read_text(encoding="utf-8")
    if "model_sources" not in meta:
        errors.append("kernel-metadata.json missing model_sources")
    return errors


def check_benchmark() -> bool:
    cases = ROOT / "benchmark" / "cases.jsonl"
    if not cases.exists():
        print("benchmark/cases.jsonl missing")
        return False
    lines = [ln for ln in cases.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(lines) < 24:
        print(f"Expected >=24 benchmark cases, found {len(lines)}")
        return False
    code, out = run([sys.executable, "scripts/run_evaluation.py"])
    print(out)
    return code == 0 and (ROOT / "benchmark" / "results.json").exists()


def main() -> int:
    ok = True
    print("=== verify_release.py ===")
    file_errors = check_files()
    if file_errors:
        ok = False
        for err in file_errors:
            print(f"FAIL: {err}")
    else:
        print("OK: required files present")

    if not check_ruff():
        ok = False
        print("FAIL: ruff")
    else:
        print("OK: ruff")

    if not check_pytest():
        ok = False
        print("FAIL: pytest")
    else:
        print("OK: pytest")

    if not check_benchmark():
        ok = False
        print("FAIL: benchmark")
    else:
        print("OK: benchmark")

    if GIT.exists():
        code, out = run([str(GIT), "rev-parse", "HEAD"])
        if code == 0:
            print(f"Git HEAD: {out.strip()}")

    print("=== RESULT:", "PASSED" if ok else "FAILED", "===")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
