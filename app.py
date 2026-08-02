"""EchoClause Gradio demo — Nuru Credit promise vs contract."""

from __future__ import annotations

import json

import gradio as gr

from echo_clause.config import ASSETS_DIR, DISCLAIMER
from echo_clause.pipeline import run_pipeline

ASSET_FILES = {
    "Advertisement": ASSETS_DIR / "advertisement.png",
    "Sales pitch (audio)": ASSETS_DIR / "sales_pitch.wav",
    "Support chat": ASSETS_DIR / "support_chat.png",
    "Contract": ASSETS_DIR / "contract.png",
}


def _format_claims(report: dict) -> str:
    lines = []
    for c in report.get("claims", []):
        lines.append(
            f"**{c['source_id']}** · `{c['field']}` → {c['raw_value'][:80]}"
        )
    return "\n\n".join(lines) if lines else "_No claims extracted._"


def _format_conflicts(report: dict) -> str:
    lines = []
    for c in report.get("contradictions", []):
        lines.append(
            f"### {c['canonical_field']} ({c['severity']})\n"
            f"**Status:** {c['status']}\n\n"
            f"{c.get('evidence_summary', '')[:300]}"
        )
    return "\n\n".join(lines) if lines else "_No contradictions detected._"


def _format_trace(report: dict) -> str:
    return json.dumps(
        {
            "model_id": report.get("model_id"),
            "demo_validation": report.get("demo_validation"),
            "extraction_trace": report.get("extraction_trace"),
            "clarification_questions": report.get("clarification_questions"),
        },
        indent=2,
    )


def run_demo(use_recorded: bool = True) -> tuple:
    report = run_pipeline(use_recorded=use_recorded)
    validation = report.get("demo_validation", {})
    summary = (
        f"**Conflicts:** {report['conflict_count']} · "
        f"**Gold detected:** {validation.get('detected_gold_contradictions', 0)}/5\n\n"
        f"{DISCLAIMER}"
    )
    images = [
        str(ASSET_FILES["Advertisement"]),
        str(ASSET_FILES["Support chat"]),
        str(ASSET_FILES["Contract"]),
    ]
    return (
        summary,
        images,
        str(ASSET_FILES["Sales pitch (audio)"]),
        _format_claims(report),
        _format_conflicts(report),
        _format_trace(report),
    )


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="EchoClause Demo") as demo:
        gr.Markdown("# EchoClause — What They Said vs. What You Sign")
        gr.Markdown(f"_{DISCLAIMER}_")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Demo evidence")
                asset_gallery = gr.Gallery(label="Images", columns=1, height=400)
                audio = gr.Audio(label="Sales pitch", type="filepath")
            with gr.Column(scale=1):
                gr.Markdown("### Extracted claims")
                claims_md = gr.Markdown()
            with gr.Column(scale=1):
                gr.Markdown("### Conflicts")
                conflicts_md = gr.Markdown()

        summary_md = gr.Markdown()
        with gr.Accordion("Debug trace", open=False):
            trace_json = gr.Code(language="json")

        run_btn = gr.Button("Run EchoClause analysis", variant="primary")
        run_btn.click(
            fn=lambda: run_demo(use_recorded=True),
            outputs=[summary_md, asset_gallery, audio, claims_md, conflicts_md, trace_json],
        )
        demo.load(
            fn=lambda: run_demo(use_recorded=True),
            outputs=[summary_md, asset_gallery, audio, claims_md, conflicts_md, trace_json],
        )
    return demo


def main() -> None:
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()
