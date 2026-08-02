# Commit R1 runtime spike (run from Git Bash or a shell where `git` is on PATH)
$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..").Path

git checkout feat/r0-r1-runtime-spike
git add echo-clause-gemma4/echo_clause/gemma_runtime.py `
        echo-clause-gemma4/echo_clause/provenance.py `
        echo-clause-gemma4/echo_clause/prompt_templates.py `
        echo-clause-gemma4/echo_clause/tool_registry.py `
        echo-clause-gemma4/scripts/run_runtime_spike.py `
        echo-clause-gemma4/scripts/commit_r1.ps1 `
        echo-clause-gemma4/docs/KAGGLE_R1_SPIKE.md `
        echo-clause-gemma4/tests/test_parser.py `
        echo-clause-gemma4/artifacts/runs/
git status --short
git commit -m "feat: validate Gemma 4 multimodal and function-calling runtime"
git rev-parse HEAD
