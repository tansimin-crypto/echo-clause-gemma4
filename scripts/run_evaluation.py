#!/usr/bin/env python3
"""Run R3 synthetic benchmark and R4 baselines; write results.json + RESULTS.md."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from echo_clause.baselines import (
    contract_only_baseline,
    echo_clause_baseline,
    split_claims,
    text_concat_baseline,
)
from echo_clause.pipeline import normalize_claims
from echo_clause.schemas import SourceClaim

BENCHMARK_DIR = ROOT / "benchmark"
CASES_PATH = BENCHMARK_DIR / "cases.jsonl"
RESULTS_JSON = BENCHMARK_DIR / "results.json"
RESULTS_MD = BENCHMARK_DIR / "RESULTS.md"


def load_cases(path: Path) -> list[dict]:
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            cases.append(json.loads(line))
    return cases


def evaluate_case(case: dict) -> dict:
    claims = [SourceClaim.model_validate(c) for c in case["claims"]]
    normalized = normalize_claims(claims)
    promise, contract = split_claims(normalized)

    expected = {e["field"]: e["expected_status"] for e in case.get("expected", [])}

    methods = {
        "echo_clause": echo_clause_baseline(promise, contract),
        "contract_only": contract_only_baseline(promise, contract),
        "text_concat": text_concat_baseline(promise, contract),
    }

    scores: dict[str, dict[str, int]] = {}
    for name, rows in methods.items():
        hit = 0
        total = len(expected)
        for field, exp_status in expected.items():
            row = next((r for r in rows if r["canonical_field"] == field), None)
            if row and row["status"] == exp_status:
                hit += 1
        scores[name] = {"correct": hit, "total": total, "accuracy": round(hit / total, 3) if total else 0.0}

    return {
        "case_id": case["case_id"],
        "family": case.get("family", "synthetic"),
        "expected": expected,
        "scores": scores,
        "methods": methods,
    }


def render_markdown(summary: dict, per_case: list[dict]) -> str:
    lines = [
        "# EchoClause Benchmark Results (R3/R4)",
        "",
        f"- Cases: **{summary['case_count']}**",
        f"- Mode: **{summary['mode']}** (recorded-claim replay, no live Gemma)",
        "",
        "## Aggregate accuracy (status match per field)",
        "",
        "| Method | Correct | Total | Accuracy |",
        "|--------|---------|-------|----------|",
    ]
    for method, agg in summary["aggregate"].items():
        lines.append(
            f"| {method} | {agg['correct']} | {agg['total']} | {agg['accuracy']:.1%} |"
        )
    lines.extend(["", "## Per-case (echo_clause)", ""])
    for row in per_case:
        ec = row["scores"]["echo_clause"]
        lines.append(f"- `{row['case_id']}`: {ec['correct']}/{ec['total']} ({ec['accuracy']:.0%})")
    lines.append("")
    lines.append(
        "_Honest note: benchmark uses synthetic normalized claims (replay path). "
        "Live multimodal extraction is validated separately via R1 runtime spike._"
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run EchoClause benchmark")
    parser.add_argument("--cases", type=Path, default=CASES_PATH)
    parser.add_argument("--output-json", type=Path, default=RESULTS_JSON)
    parser.add_argument("--output-md", type=Path, default=RESULTS_MD)
    args = parser.parse_args()

    if not args.cases.exists():
        print(f"Missing benchmark cases: {args.cases}", file=sys.stderr)
        return 1

    cases = load_cases(args.cases)
    per_case = [evaluate_case(c) for c in cases]

    aggregate: dict[str, dict[str, float | int]] = {}
    for method in ("echo_clause", "contract_only", "text_concat"):
        correct = sum(r["scores"][method]["correct"] for r in per_case)
        total = sum(r["scores"][method]["total"] for r in per_case)
        aggregate[method] = {
            "correct": correct,
            "total": total,
            "accuracy": round(correct / total, 3) if total else 0.0,
        }

    summary = {
        "case_count": len(cases),
        "mode": "recorded_replay",
        "aggregate": aggregate,
        "cases": per_case,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(summary, per_case), encoding="utf-8")
    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_md}")
    print(f"echo_clause accuracy: {aggregate['echo_clause']['accuracy']:.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
