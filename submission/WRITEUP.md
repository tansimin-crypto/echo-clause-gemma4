# EchoClause — What They Said vs. What You Sign

## The Problem

Digital micro-loans move fast. A borrower sees a bright advertisement promising zero interest and no hidden fees, hears a sales agent confirm the repayment amount on a phone call, receives reassuring chat support, and then taps through a dense contract on a small screen. The contract may include a platform fee, a higher total repayment, weekly compounding late penalties, a shorter term, and automatic debit authorization. By the time contradictions become visible, the loan is already disbursed.

Existing tools focus on credit scoring or generic document OCR. They rarely connect **multimodal marketing promises** to **contract clauses** with auditable provenance. EchoClause fills that gap for the Kaggle "Build with Gemma" Hackathon.

## Our Solution

EchoClause is an evidence-grounded reconciliation pipeline. It ingests four demo sources for fictional lender **Nuru Credit** — an advertisement image, a sales pitch audio file, a support chat screenshot, and a contract page — and produces a structured conflict report before signing.

The architecture deliberately separates probabilistic perception from deterministic finance logic:

1. **Gemma 4 multimodal extraction** reads images and audio, returning JSON `SourceClaim` objects with verbatim evidence quotes.
2. **Deterministic normalization** converts raw text ("No hidden fees", "₦15,000 platform fee") into comparable numeric and boolean values.
3. **Allowlisted function calling** lets Gemma invoke Pydantic-validated tools (`calculate_fee_percentage`, `compare_normalized_terms`, etc.) without arbitrary code execution.
4. **Reconciliation** compares promise-side evidence against contract-side claims field by field.
5. **Provenance artifacts** record model ID, prompt hashes, asset checksums, and raw model output for every run.

This split keeps the demo auditable: Gemma interprets messy human communications; calculators and schemas decide whether two representations contradict each other.

## How We Use Gemma 4

We target `google/gemma-4-E4B-it` with two bounded load attempts (bf16 auto, then 4-bit quantization). If VRAM is insufficient on Kaggle T4, we freeze `google/gemma-4-E2B-it` as the public reproducible configuration — never more than two E4B retries.

Gemma handles three critical capabilities:

**Vision claim extraction.** Advertisement and contract PNGs contain fees, terms, and authorization language. Gemma returns structured claims with evidence spans tied to each field (`platform_fee`, `repayment_term_days`, `automatic_debit`).

**Native audio understanding.** The sales pitch WAV is processed directly by Gemma. If native audio extraction fails, we disclose an ASR fallback using the bundled transcript — image processing always stays Gemma-native.

**Function calling for financial reasoning.** When marketing says "no hidden fees" but the contract shows ₦15,000 on ₦100,000 principal, Gemma calls `calculate_fee_percentage(fee_amount=15000, principal=100000)` and receives a deterministic 15% result through our allowlisted registry.

Every inference writes immutable JSON artifacts under `artifacts/runs/` with RAW model output, never synthetic placeholders.

## Demo Case: Five Contradictions

Our frozen `gold.json` defines five contradictions for Nuru Credit:

| Field | Promise | Contract |
|-------|---------|----------|
| Platform fee | No hidden fees | ₦15,000 |
| Total repayment | ₦100,000 | ₦115,000 |
| Late fee | One-time ₦2,000 | 5% per week |
| Term | 30 days | 21 days |
| Automatic debit | Disabled after repayment | Authorization enabled |

The pipeline normalizes each claim, reconciles promise sources (advertisement, audio, chat) against contract clauses, and flags all five as `CONTRADICTED`. Unit tests and the Kaggle notebook assert `5/5` gold detection.

## Technical Highlights

**Frozen Pydantic contracts (R0).** Thirty-six pytest tests validate schemas, calculators, normalization, tool allowlists, and demo assets before any GPU work begins.

**Bounded runtime spike (R1).** `scripts/run_runtime_spike.py` validates image claims, audio claims, and function calling on Kaggle T4, writing provenance JSON with load-attempt traces.

**End-to-end pipeline (R2).** `echo_clause/pipeline.py` orchestrates extraction → normalization → reconciliation → report generation with optional recorded replay for offline development.

**Minimal Gradio UI (R5).** Three-column layout: demo assets, extracted claims, detected conflicts, plus collapsible debug trace.

**Static GitHub Pages replay (R6).** `docs/index.html` renders a recorded Gemma run with the required label: *"Interactive replay generated from a recorded Gemma 4 run."*

## What We Deliberately Exclude

- No cloud LLM APIs — Gemma runs locally or on Kaggle GPU.
- No fine-tuning or RAG — zero-shot extraction with deterministic post-processing.
- No model weights in git — Hugging Face download at runtime with `HF_TOKEN`.
- No legal determinations — EchoClause compares representations; it does not advise on enforceability.

## Reproducibility

```bash
pip install -e ".[dev,gemma,ui]"
python scripts/generate_demo_assets.py
python scripts/run_runtime_spike.py          # GPU: R1 gate
python scripts/run_demo_pipeline.py            # full live pipeline
python -m pytest -q                            # 36 tests
python app.py                                  # Gradio demo
```

Kaggle notebook `notebooks/echo_clause_kaggle_demo.ipynb` sets `RUN_FULL_BENCHMARK = False` and runs the complete demo on T4 with HF secrets.

## Impact

EchoClause demonstrates how Gemma 4's multimodal and tool-use capabilities can protect borrowers in high-velocity lending flows. By grounding every conflict in quoted evidence and deterministic math, it gives consumers a concrete checklist — *"You were told X, but clause Y says Z"* — without replacing legal counsel.

For hackathon judges, the project shows responsible Gemma integration: bounded model fallback, provenance-first artifacts, allowlisted tools, and a complete vertical slice from PNG/WAV ingestion to interactive UI.

---

*EchoClause compares representations across supplied evidence. It does not provide legal advice or determine legal enforceability.*
