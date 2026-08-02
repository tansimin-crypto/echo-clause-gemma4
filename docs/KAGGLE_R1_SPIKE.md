# Finish R1 on Kaggle T4

Local R0 is complete; R1 code is on disk but **live Gemma inference was not run** (no CUDA GPU, Hugging Face unreachable from this machine).

## Prerequisites

1. Accept Gemma 4 license on Hugging Face for `google/gemma-4-E4B-it` and `google/gemma-4-E2B-it`.
2. Kaggle account with **Secrets** → add `HF_TOKEN` (read token).
3. Notebook or script session with **GPU T4 x2** (or T4 x1) enabled.

## Run spike

```bash
cd /kaggle/working/echo-clause-gemma4
pip install -e ".[dev,gemma]"
export HF_TOKEN="$HF_TOKEN"   # Kaggle secret injects this automatically in notebooks
python scripts/run_runtime_spike.py
python -m pytest -q
```

## Pass criteria (R1)

- [ ] At least one **image** → parseable structured claim
- [ ] At least one **audio** → parseable claim (or documented ASR fallback)
- [ ] At least one **function call** → Pydantic-validated tool execution
- [ ] Artifact written to `artifacts/runs/runtime_spike_*.json` with raw model output

## Model fallback rule

1. Try E4B `bf16_auto` (attempt 1)
2. Try E4B `bnb_4bit` (attempt 2)
3. If both fail on T4 VRAM → freeze **E2B** as public Notebook model; note in artifact

Do **not** retry E4B more than twice.

## After success

Commit from a machine with Git:

```powershell
cd D:\kaggle\gemma-finance
git checkout feat/r0-r1-runtime-spike
git add echo-clause-gemma4/
git commit -m "feat: validate Gemma 4 multimodal and function-calling runtime"
```

Replace `artifacts/runs/runtime_spike_*.json` with the **successful** Kaggle run artifact before committing.
