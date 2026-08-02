.PHONY: install test assets spike lint

install:
	python -m pip install -e ".[dev,gemma]"

assets:
	python scripts/generate_demo_assets.py

test:
	python -m pytest -q

spike:
	python scripts/run_runtime_spike.py

spike-not-run:
	python scripts/run_runtime_spike.py --not-run-gpu

lint:
	python -m ruff check .
