"""Provenance tracking for immutable run artifacts."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from echo_clause.config import ARTIFACTS_DIR


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_git_sha(project_root: Path) -> str | None:
    git_dir = project_root / ".git"
    if git_dir.is_dir():
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
        if head.startswith("ref:"):
            ref_path = git_dir / head.split(":", 1)[1].strip()
            if ref_path.exists():
                return ref_path.read_text(encoding="utf-8").strip()
        elif len(head) == 40:
            return head

    git_candidates = [
        "git",
        r"C:\Program Files\Git\bin\git.exe",
        r"D:\CodexData\cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe",
        "/usr/bin/git",
    ]
    for git_bin in git_candidates:
        try:
            result = subprocess.run(
                [git_bin, "rev-parse", "HEAD"],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except OSError:
            continue
    return None


def get_package_versions() -> dict[str, str]:
    versions: dict[str, str] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }
    for pkg in ("torch", "transformers", "accelerate", "bitsandbytes", "pydantic", "PIL"):
        try:
            mod = __import__(pkg if pkg != "PIL" else "PIL")
            versions[pkg] = getattr(mod, "__version__", "unknown")
        except ImportError:
            versions[pkg] = "not_installed"
    return versions


def get_gpu_info() -> dict[str, Any]:
    info: dict[str, Any] = {
        "available": False,
        "device_name": None,
        "vram_gb": None,
        "compute_capability": None,
        "cuda_usable": False,
    }
    try:
        import torch

        if torch.cuda.is_available():
            info["available"] = True
            info["device_name"] = torch.cuda.get_device_name(0)
            props = torch.cuda.get_device_properties(0)
            info["vram_gb"] = round(props.total_memory / (1024**3), 2)
            major, minor = torch.cuda.get_device_capability(0)
            info["compute_capability"] = f"{major}.{minor}"
            info["cuda_usable"] = major >= 7
            if info["cuda_usable"]:
                try:
                    probe = torch.zeros(1, device="cuda")
                    del probe
                    torch.cuda.synchronize()
                except Exception as exc:
                    info["cuda_usable"] = False
                    info["cuda_probe_error"] = str(exc)
    except ImportError:
        info["error"] = "torch not installed"
    return info


def write_runtime_artifact(
    payload: dict[str, Any],
    prefix: str = "runtime_spike",
) -> Path:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = ARTIFACTS_DIR / f"{prefix}_{ts}.json"
    payload.setdefault("timestamp_utc", ts)
    out_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return out_path
