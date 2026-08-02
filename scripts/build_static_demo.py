#!/usr/bin/env python3
"""Build static GitHub Pages demo from recorded pipeline run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "demo_case"
DOCS = ROOT / "docs"
DEFAULT_REPORT = ROOT / "artifacts" / "runs" / "pipeline_recorded.json"


def _load_report(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    # Generate on the fly
    import sys

    sys.path.insert(0, str(ROOT))
    from echo_clause.pipeline import run_pipeline, write_pipeline_artifact

    report = run_pipeline(use_recorded=True)
    write_pipeline_artifact(report, prefix="pipeline_recorded")
    return report


def build_html(report: dict) -> str:
    contradictions = report.get("contradictions", [])
    claims = report.get("claims", [])
    model_id = report.get("model_id", "google/gemma-4-E2B-it")
    rows = ""
    for c in contradictions:
        rows += f"""<tr>
          <td>{c['canonical_field']}</td>
          <td class="status contradicted">{c['status']}</td>
          <td>{c.get('severity','')}</td>
          <td>{c.get('evidence_summary','')[:200]}</td>
        </tr>\n"""

    claim_rows = ""
    for cl in claims[:20]:
        claim_rows += f"""<tr>
          <td>{cl['source_id']}</td>
          <td>{cl['field']}</td>
          <td>{cl['raw_value'][:60]}</td>
        </tr>\n"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>EchoClause — Nuru Credit Demo</title>
  <style>
    :root {{ font-family: system-ui, sans-serif; color: #1a1a2e; }}
    body {{ max-width: 960px; margin: 0 auto; padding: 1.5rem; background: #f8f9fc; }}
    h1 {{ color: #16213e; }}
    .banner {{ background: #e8f4fd; border-left: 4px solid #0d6efd; padding: 0.75rem 1rem; margin-bottom: 1.5rem; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; margin-bottom: 1.5rem; }}
    th, td {{ border: 1px solid #dee2e6; padding: 0.5rem; text-align: left; font-size: 0.9rem; }}
    th {{ background: #16213e; color: #fff; }}
    .contradicted {{ color: #c0392b; font-weight: bold; }}
    .assets {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; }}
    .assets img {{ max-width: 100%; border: 1px solid #ccc; border-radius: 4px; }}
    footer {{ font-size: 0.85rem; color: #666; margin-top: 2rem; }}
  </style>
</head>
<body>
  <h1>EchoClause — What They Said vs. What You Sign</h1>
  <div class="banner">
    Interactive replay generated from a recorded Gemma 4 run.
    Model: <strong>{model_id}</strong> · Conflicts: <strong>{report.get('conflict_count', 0)}</strong>
  </div>

  <h2>Demo Evidence (Nuru Credit)</h2>
  <div class="assets">
    <figure><img src="../assets/demo_case/advertisement.png" alt="Advertisement"/><figcaption>Advertisement</figcaption></figure>
    <figure><img src="../assets/demo_case/support_chat.png" alt="Support chat"/><figcaption>Support chat</figcaption></figure>
    <figure><img src="../assets/demo_case/contract.png" alt="Contract"/><figcaption>Contract</figcaption></figure>
  </div>

  <h2>Detected Contradictions</h2>
  <table>
    <thead><tr><th>Field</th><th>Status</th><th>Severity</th><th>Evidence</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>

  <h2>Extracted Claims (sample)</h2>
  <table>
    <thead><tr><th>Source</th><th>Field</th><th>Raw value</th></tr></thead>
    <tbody>{claim_rows}</tbody>
  </table>

  <footer>
    EchoClause compares representations across supplied evidence.
    It does not provide legal advice or determine legal enforceability.
  </footer>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build static GitHub Pages demo")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--output", type=Path, default=DOCS / "index.html")
    args = parser.parse_args()

    report = _load_report(args.report)
    html = build_html(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"Static demo written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
