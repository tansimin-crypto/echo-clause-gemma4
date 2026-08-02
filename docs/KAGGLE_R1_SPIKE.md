# Finish R1 on Kaggle T4

## One-time setup (no HF_TOKEN required on Kaggle)

1. Open [kaggle.com/models/google/gemma-4](https://www.kaggle.com/models/google/gemma-4)
2. Click **Request Access** / accept the Gemma license (once per Kaggle account)
3. Run the notebook — `kernel-metadata.json` attaches official model sources:

```json
"model_sources": [
  "google/gemma-4/transformers/gemma-4-e4b-it-qat-q4_0-unquantized/2",
  "google/gemma-4/transformers/gemma-4-e2b-it-qat-q4_0-unquantized/2"
]
```

Weights mount at `/kaggle/input/models/google/gemma-4/transformers/...` — no Hugging Face download.

## Optional: Hugging Face fallback (local dev)

Accept Gemma 4 license on Hugging Face and set `HF_TOKEN` only if **not** using Kaggle Models.

## Push and run

```bash
python scripts/kaggle_dataset_push.py   # updates source dataset
python scripts/kaggle_push.py           # pushes notebook + model_sources
```

Monitor: `kaggle kernels status simingtan/echo-clause-gemma4-demo`

## Pass criteria (R1)

- Image → parseable structured claim
- Audio → parseable claim (or documented ASR fallback)
- Function call → Pydantic-validated tool execution
- `artifacts/runs/runtime_spike_*.json` with raw model output

## Model fallback

1. E4B QAT (Kaggle mount) or bf16 on **T4 / sm_70+**
2. E4B bnb_4bit (T4 sm_70+ only)
3. E2B QAT or bf16 on GPU
4. **E2B on CPU** when Kaggle assigns P100 (sm_60) or torch cu128 has no kernel for device

Max 2 E4B GPU attempts, then E2B; CPU fallback is spike-only and sets `cpu_verified: true` in the artifact.
