# EchoClause (R0/R1 scope)

**EchoClause — What They Said vs. What You Sign**

Minimal MVP for the Kaggle "Build with Gemma" Hackathon. This repository stage covers:

- **R0**: Frozen Pydantic contracts, synthetic Nuru Credit demo assets, gold.json
- **R1**: Gemma 4 multimodal + function-calling runtime spike with provenance artifacts

Not included yet: Gradio UI, static demo, Writeup, Kaggle notebook packaging, public GitHub publish.

## Quick start

```bash
cd echo-clause-gemma4
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev,gemma]"
python scripts/generate_demo_assets.py
python -m pytest -q
python scripts/run_runtime_spike.py
```

## Disclaimer

EchoClause compares representations across supplied evidence. It does not provide legal advice or determine legal enforceability.
