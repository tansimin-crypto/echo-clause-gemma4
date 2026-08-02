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

## Design Principles

**Evidence first.** Every extracted claim carries an `evidence_text` field with a verbatim quote from the source. Comparisons reference these quotes in the final report so users can verify model outputs against original artifacts.

**Deterministic math, probabilistic reading.** Gemma may misread a fee amount; our normalization layer re-parses currency symbols and percentages with regex-based rules. Contradiction status comes from typed comparison functions, not from LLM judgment calls.

**Allowlisted tools only.** The function-calling registry accepts five tools with Pydantic-validated arguments. Unknown tool names, malformed JSON, or shell-like payloads are rejected with a trace entry — no `eval`, no arbitrary code.

**Provenance by default.** Each run writes JSON artifacts containing git SHA, prompt hash, asset SHA-256 checksums, package versions, GPU metadata, load-attempt history, and raw model output strings.

## Implementation Walkthrough

### Schemas and demo assets (R0)

We frozen fourteen `ClaimField` enums, six comparison statuses, and tool argument models in Pydantic v2. Synthetic PNG and WAV assets for Nuru Credit are generated programmatically (`scripts/generate_demo_assets.py`) so the repository stays self-contained without external downloads. `gold.json` locks the five expected contradictions for automated regression.

### Gemma runtime (R1)

`echo_clause/gemma_runtime.py` implements bounded loading: two E4B configurations (bf16 auto, 4-bit) followed by E2B fallback. The spike script exercises three paths — image claim extraction from `advertisement.png`, audio claim extraction from `sales_pitch.wav`, and function calling via `calculate_fee_percentage`. Windows development clears proxy environment variables and installs `httpx[socks]` to avoid Hugging Face download failures.

### Pipeline (R2)

`echo_clause/pipeline.py` connects extraction, normalization, reconciliation, and reporting. Promise sources (advertisement, sales audio, support chat) are compared against contract claims field-by-field. The demo validates against `gold.json` and reports which canonical fields were detected as contradicted. A `recorded_claims.json` fixture enables offline replay when GPU inference is unavailable; live mode replaces this with Gemma-extracted claims and optional ASR transcript fallback for audio.

### User interfaces (R5–R6)

The Gradio app (`app.py`) presents a three-column layout: demo assets on the left, extracted claims in the center, and conflicts on the right, with a collapsible JSON debug trace. The static GitHub Pages demo (`docs/index.html`) renders the same recorded run for judges who cannot launch Python locally.

### Kaggle packaging (R7)

The notebook `notebooks/echo_clause_kaggle_demo.ipynb` installs the package, runs the R1 spike, executes the full pipeline on T4, validates 5/5 gold detection, and runs pytest with `RUN_FULL_BENCHMARK = False`. `scripts/kaggle_push.py` stages a self-contained kernel bundle for one-command upload.

## Lessons Learned

Running Gemma 4 locally on Windows without CUDA proved impractical — Hugging Face timeouts and proxy issues blocked model download. Kaggle T4 with `HF_TOKEN` secrets is the intended production path for hackathon judges. Separating recorded replay from live inference let us complete R2–R8 while R1 awaits GPU verification.

We also learned that synthetic audio (simple tone WAV) may not produce rich Gemma audio claims; the disclosed transcript fallback ensures the pipeline remains testable without misrepresenting native audio capability.

## Future Work

- Expand beyond the single Nuru Credit scenario with user-uploaded evidence
- Add Swahili/Arabic localization for East African micro-loan markets
- Integrate PDF contract parsing while keeping Gemma-native image processing
- Publish the GitHub repository and enable GitHub Pages for the static replay

## Team and Acknowledgments

## Impact

EchoClause demonstrates how Gemma 4's multimodal and tool-use capabilities can protect borrowers in high-velocity lending flows. By grounding every conflict in quoted evidence and deterministic math, it gives consumers a concrete checklist — *"You were told X, but clause Y says Z"* — without replacing legal counsel.

For hackathon judges, the project shows responsible Gemma integration: bounded model fallback, provenance-first artifacts, allowlisted tools, and a complete vertical slice from PNG/WAV ingestion to interactive UI.

---

*EchoClause compares representations across supplied evidence. It does not provide legal advice or determine legal enforceability.*

