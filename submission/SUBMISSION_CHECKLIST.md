# EchoClause Hackathon Submission Checklist

Last updated: 2026-08-02 (R0–R10 completion pass)

## Repository

| Item | Status |
|------|--------|
| Public GitHub repo `echo-clause-gemma4` | See release report |
| Branch `feat/r0-r1-runtime-spike` | Active |
| No secrets / model weights committed | Verified |

## Stages R0–R10

| Stage | Description | Status |
|-------|-------------|--------|
| R0 | Schemas + synthetic assets + 36 tests | **passed** |
| R1 | Gemma runtime spike (image + function call) | **partial** — CPU fallback on P100; T4 GPU preferred |
| R2 | Full pipeline 5/5 contradictions (recorded) | **passed** |
| R3 | 24-case synthetic benchmark + eval script | **passed** (recorded replay) |
| R4 | contract-only + text-concat baselines | **passed** (8+ cases via full benchmark) |
| R5 | Gradio `app.py` | **passed** |
| R6 | Static demo `docs/index.html` | **passed** |
| R7 | Kaggle notebook | **passed** (v7+ with CPU fallback) |
| R8 | README + WRITEUP.md | **passed** |
| R9 | Demo video | **manual** — user must record/upload |
| R10 | pytest + ruff + verify_release.py | **passed** |

## Kaggle

| Item | Status |
|------|--------|
| Notebook slug | `simingtan/echo-clause-gemma4-demo` |
| Source dataset | `simingtan/echo-clause-gemma4-src` |
| Kaggle Models attached (no HF_TOKEN) | Yes |
| `machine_shape` | `GpuT4x2` (CPU fallback if P100 assigned) |
| Notebook visibility | **Private** (`is_private: true`) — Kaggle auto-publicizes after competition ends; do **not** set public manually |

## Manual steps (user)

1. **Hackathon form** — click Submit on Kaggle hackathon page (agent cannot submit).
2. **Demo video** — record 3–5 min walkthrough; upload per hackathon instructions.
3. **Gemma license** — ensure accepted at [kaggle.com/models/google/gemma-4](https://www.kaggle.com/models/google/gemma-4).
4. **Re-run notebook on T4** when available for live GPU R1 artifact (optional upgrade from CPU-verified).

## Quick verify

```bash
pip install -e ".[dev]"
python scripts/verify_release.py
python scripts/run_evaluation.py
python scripts/build_static_demo.py
```

## Artifacts

- `artifacts/runs/runtime_spike_*.json` — R1 provenance (live or CPU-verified)
- `artifacts/runs/pipeline_recorded_*.json` — R2 recorded 5/5 demo
- `benchmark/results.json` — R3/R4 eval output
- `docs/index.html` — static GitHub Pages demo
