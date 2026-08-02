# EchoClause — What They Said vs. What You Sign

Evidence-grounded promise-to-contract reconciliation powered by **Gemma 4** multimodal extraction and deterministic financial calculators.

[![Hackathon](https://img.shields.io/badge/Kaggle-Build%20with%20Gemma-blue)](https://www.kaggle.com/competitions/gemma-hackathon)

## Hero

Borrowers sign loan contracts after seeing ads, hearing sales pitches, and chatting with support — but the fine print often contradicts what they were told. **EchoClause** ingests multimodal evidence (images, audio, chat screenshots), extracts structured financial claims with Gemma 4, normalizes terms deterministically, and surfaces contradictions *before* signing.

**Demo case:** fictional **Nuru Credit** micro-loan — 5 contradictions across platform fee, total repayment, late fee, term days, and automatic debit.

## Architecture

```
Evidence (PNG/WAV) → Gemma 4 claim extraction → Deterministic normalization
    → Reconciliation (promise vs contract) → Evidence-grounded conflict report
```

| Layer | Component | Role |
|-------|-----------|------|
| 1 | Source ingestion | Advertisement, sales audio, support chat, contract |
| 2 | Gemma 4 runtime | Multimodal JSON claim extraction + function calling |
| 3 | Normalization | `normalize_financial_term` (deterministic) |
| 4 | Calculators | Fee %, total repayment, term comparison |
| 5 | Reconciliation | Promise vs contract → `ComparisonResult` |
| 6 | Report | Conflicts + clarification questions + provenance |

## Quick start (local)

```bash
cd echo-clause-gemma4
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev,gemma,ui]"
python scripts/generate_demo_assets.py
python -m pytest -q
python scripts/run_demo_pipeline.py --use-recorded   # offline replay
python scripts/build_static_demo.py
python app.py                                        # Gradio UI on :7860
```

### Live Gemma inference (GPU required)

```bash
python scripts/run_runtime_spike.py      # R1 multimodal + function-calling gate
python scripts/run_demo_pipeline.py      # full pipeline with live extraction
```

On Windows without CUDA/HF access, run on **Kaggle T4** (see below).

## Kaggle reproduction

1. Accept Gemma 4 license on Hugging Face; add `HF_TOKEN` to Kaggle Secrets.
2. Push kernel: `python scripts/kaggle_push.py` (requires `~/.kaggle/kaggle.json`).
3. Open notebook **EchoClause Gemma 4 Demo**, enable **GPU T4**, Run All.
4. Expected: R1 spike passes; pipeline detects **5/5** gold contradictions.

## Model strategy

| Priority | Model | Notes |
|----------|-------|-------|
| 1 | `google/gemma-4-E4B-it` | bf16_auto, then bnb_4bit (max 2 attempts) |
| 2 | `google/gemma-4-E2B-it` | Public reproducible fallback |
| Audio | Gemma native WAV | ASR transcript fallback disclosed if needed |

No cloud APIs, fine-tuning, RAG, or model weights in git.

## Project layout

```
echo-clause-gemma4/
├── echo_clause/          # Core library (schemas, runtime, pipeline)
├── assets/demo_case/     # Synthetic Nuru Credit evidence + gold.json
├── scripts/              # Spike, pipeline, static demo, Kaggle push
├── notebooks/            # Kaggle demo notebook + kernel metadata
├── docs/index.html       # Static replay demo (GitHub Pages)
├── app.py                # Gradio UI
└── submission/WRITEUP.md # Hackathon writeup
```

## Test results

```bash
python -m pytest -q
# 36 passed — schemas, calculators, normalization, tools, demo case, pipeline
```

## Disclaimer

EchoClause compares representations across supplied evidence. It does not provide legal advice or determine legal enforceability.

## License

MIT
