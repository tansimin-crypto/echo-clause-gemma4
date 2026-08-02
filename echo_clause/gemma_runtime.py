"""Gemma 4 multimodal runtime with bounded load attempts and provenance."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from echo_clause.config import (
    FALLBACK_MODEL_ID,
    MAX_E4B_LOAD_ATTEMPTS,
    PRIMARY_MODEL_ID,
    PROJECT_ROOT,
)
from echo_clause.prompt_templates import (
    CLAIM_EXTRACTION_SYSTEM,
    build_audio_messages,
    build_function_call_messages,
    build_image_messages,
)
from echo_clause.provenance import (
    get_git_sha,
    get_gpu_info,
    get_package_versions,
    sha256_file,
    sha256_text,
    write_runtime_artifact,
)
from echo_clause.schemas import ExtractionResult, SourceClaim, SourceType
from echo_clause.tool_registry import execute_tool_call, get_tool_definitions


@dataclass
class LoadAttempt:
    model_id: str
    config: dict[str, Any]
    success: bool
    error: str | None = None


@dataclass
class GemmaRuntime:
    model_id: str = PRIMARY_MODEL_ID
    model: Any = None
    processor: Any = None
    load_attempts: list[LoadAttempt] = field(default_factory=list)
    dtype: str | None = None
    quantization: str | None = None
    revision: str | None = None

    E4B_CONFIGS: list[dict[str, Any]] = field(
        default_factory=lambda: [
            {"dtype": "auto", "quantization": "none", "label": "bf16_auto"},
            {
                "dtype": "auto",
                "quantization": "4bit",
                "label": "bnb_4bit",
                "load_in_4bit": True,
            },
        ]
    )

    def load(self) -> bool:
        """Try up to 2 E4B configs, then fallback to E2B."""
        for cfg in self.E4B_CONFIGS[:MAX_E4B_LOAD_ATTEMPTS]:
            ok = self._try_load(PRIMARY_MODEL_ID, cfg)
            if ok:
                return True
        return self._try_load(
            FALLBACK_MODEL_ID,
            {"dtype": "auto", "quantization": "none", "label": "e2b_fallback"},
        )

    def _try_load(self, model_id: str, cfg: dict[str, Any]) -> bool:
        attempt = LoadAttempt(model_id=model_id, config=cfg, success=False)
        try:
            import torch
            from transformers import AutoModelForMultimodalLM, AutoProcessor

            load_kwargs: dict[str, Any] = {
                "dtype": cfg.get("dtype", "auto"),
                "device_map": "auto",
            }
            if cfg.get("load_in_4bit"):
                from transformers import BitsAndBytesConfig

                load_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                )
                self.quantization = "bnb_4bit"
            else:
                self.quantization = cfg.get("quantization", "none")

            self.processor = AutoProcessor.from_pretrained(model_id)
            self.model = AutoModelForMultimodalLM.from_pretrained(model_id, **load_kwargs)
            self.model_id = model_id
            self.dtype = str(cfg.get("dtype", "auto"))
            attempt.success = True
            self.load_attempts.append(attempt)
            return True
        except Exception as exc:
            attempt.error = str(exc)
            self.load_attempts.append(attempt)
            self.model = None
            self.processor = None
            return False

    def _generate(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        image_path: Path | None = None,
        audio_path: Path | None = None,
        max_new_tokens: int = 1024,
    ) -> tuple[str, float]:
        if self.model is None or self.processor is None:
            raise RuntimeError("Model not loaded")

        from PIL import Image

        content_parts: list[Any] = []
        for msg in messages:
            if msg["role"] != "user":
                continue
            user_content = msg.get("content")
            if isinstance(user_content, str):
                content_parts.append({"type": "text", "text": user_content})
            elif isinstance(user_content, list):
                for part in user_content:
                    if part.get("type") == "text":
                        content_parts.append(part)
                    elif part.get("type") == "image" and image_path:
                        content_parts.append({"type": "image", "image": Image.open(image_path)})
                    elif part.get("type") == "audio" and audio_path:
                        content_parts.append({"type": "audio", "audio": str(audio_path)})

        chat = [
            {"role": "system", "content": CLAIM_EXTRACTION_SYSTEM},
            {"role": "user", "content": content_parts},
        ]

        apply_kwargs: dict[str, Any] = {
            "chat_template_kwargs": {"enable_thinking": False},
            "tokenize": True,
            "return_dict": True,
            "return_tensors": "pt",
            "add_generation_prompt": True,
        }
        if tools:
            apply_kwargs["tools"] = tools

        inputs = self.processor.apply_chat_template(chat, **apply_kwargs)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        t0 = time.perf_counter()
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
        latency = time.perf_counter() - t0

        input_len = inputs["input_ids"].shape[-1]
        generated = outputs[0][input_len:]
        text = self.processor.decode(generated, skip_special_tokens=True)
        return text, latency

    def parse_claims_json(self, raw: str) -> ExtractionResult:
        cleaned = strip_code_fences(raw)
        data, err = parse_json_with_one_repair(cleaned)
        if data is None:
            return ExtractionResult(
                claims=[],
                raw_model_output=raw,
                parse_valid=False,
                needs_review=True,
                parse_error=err,
            )
        try:
            claims_raw = data.get("claims", [])
            claims = [SourceClaim.model_validate(c) for c in claims_raw]
            return ExtractionResult(
                claims=claims,
                raw_model_output=raw,
                parse_valid=True,
                needs_review=any(c.needs_review for c in claims),
            )
        except Exception as exc:
            return ExtractionResult(
                claims=[],
                raw_model_output=raw,
                parse_valid=False,
                needs_review=True,
                parse_error=str(exc),
            )

    def extract_claims_from_image(
        self,
        image_path: Path,
        source_id: str,
        source_type: SourceType,
    ) -> ExtractionResult:
        messages = build_image_messages(source_id)
        raw, _ = self._generate(messages, image_path=image_path)
        result = self.parse_claims_json(raw)
        for claim in result.claims:
            claim.source_id = source_id
            claim.source_type = source_type
        return result

    def extract_claims_from_audio(
        self,
        audio_path: Path,
        source_id: str,
    ) -> ExtractionResult:
        messages = build_audio_messages(source_id)
        raw, _ = self._generate(messages, audio_path=audio_path)
        result = self.parse_claims_json(raw)
        for claim in result.claims:
            claim.source_id = source_id
            claim.source_type = SourceType.SALES_AUDIO
        return result

    def run_function_call_demo(self) -> dict[str, Any]:
        messages = build_function_call_messages()
        tools = get_tool_definitions()
        raw, latency = self._generate(messages, tools=tools, max_new_tokens=512)
        tool_call = extract_tool_call(raw)
        trace = None
        if tool_call:
            trace = execute_tool_call(tool_call)
        return {
            "raw_output": raw,
            "tool_call": tool_call,
            "trace": trace.model_dump() if trace else None,
            "latency_s": latency,
        }

    def run_spike(
        self,
        assets_dir: Path,
        not_run_gpu: bool = False,
        skipped_load: bool = False,
    ) -> Path:
        """Run R1 validation spike and write provenance artifact."""
        ad_path = assets_dir / "advertisement.png"
        audio_path = assets_dir / "sales_pitch.wav"

        prompt_hash = sha256_text(CLAIM_EXTRACTION_SYSTEM)
        asset_hashes = {
            "advertisement.png": sha256_file(ad_path) if ad_path.exists() else None,
            "sales_pitch.wav": sha256_file(audio_path) if audio_path.exists() else None,
        }

        artifact: dict[str, Any] = {
            "stage": "R1",
            "model_id": self.model_id,
            "revision": self.revision,
            "dtype": self.dtype,
            "quantization": self.quantization,
            "gpu": get_gpu_info(),
            "package_versions": get_package_versions(),
            "prompt_hash": prompt_hash,
            "source_asset_hashes": asset_hashes,
            "git_sha": get_git_sha(PROJECT_ROOT.parent),
            "load_attempts": [
                {"model_id": a.model_id, "config": a.config, "success": a.success, "error": a.error}
                for a in self.load_attempts
            ],
            "tests": {},
        }

        if not_run_gpu or self.model is None:
            artifact["status"] = "NOT_RUN_GPU"
            blockers: list[str] = []
            if not get_gpu_info().get("available"):
                blockers.append("No CUDA GPU detected locally")
            if self.load_attempts:
                blockers.append("Model load failed — see load_attempts")
            elif skipped_load:
                blockers.append("Skipped model load (--not-run-gpu)")
            else:
                blockers.append("Model load failed — see load_attempts")
            artifact["blockers"] = blockers
            # Validate deterministic tool-calling path without model (not a fake model output)
            demo_trace = execute_tool_call(
                {
                    "name": "calculate_fee_percentage",
                    "arguments": {"fee_amount": 15000, "principal": 100000},
                }
            )
            artifact["deterministic_tool_validation"] = {
                "description": "Host-side allowlist + Pydantic validation (no model)",
                "passed": demo_trace.validation_ok,
                "trace": demo_trace.model_dump(),
            }
            artifact["kaggle_commands"] = [
                "cd /kaggle/working/echo-clause-gemma4",
                "pip install -e '.[dev,gemma]'",
                "python scripts/run_runtime_spike.py",
            ]
            return write_runtime_artifact(artifact)

        # Image test
        try:
            img_result = self.extract_claims_from_image(
                ad_path, "advertisement", SourceType.ADVERTISEMENT
            )
            artifact["tests"]["image"] = {
                "passed": img_result.parse_valid and len(img_result.claims) > 0,
                "parse_valid": img_result.parse_valid,
                "claim_count": len(img_result.claims),
                "raw_model_output": img_result.raw_model_output,
                "parsed_output": [c.model_dump() for c in img_result.claims],
                "parse_error": img_result.parse_error,
            }
        except Exception as exc:
            artifact["tests"]["image"] = {"passed": False, "error": str(exc)}

        # Audio test
        try:
            aud_result = self.extract_claims_from_audio(audio_path, "sales_pitch")
            artifact["tests"]["audio"] = {
                "passed": aud_result.parse_valid and len(aud_result.claims) > 0,
                "parse_valid": aud_result.parse_valid,
                "claim_count": len(aud_result.claims),
                "raw_model_output": aud_result.raw_model_output,
                "parsed_output": [c.model_dump() for c in aud_result.claims],
                "parse_error": aud_result.parse_error,
            }
        except Exception as exc:
            artifact["tests"]["audio"] = {"passed": False, "error": str(exc)}

        # Function calling test
        try:
            fc = self.run_function_call_demo()
            trace = fc.get("trace") or {}
            artifact["tests"]["function_calling"] = {
                "passed": bool(trace.get("validation_ok")),
                "raw_model_output": fc["raw_output"],
                "tool_call": fc["tool_call"],
                "trace": trace,
                "inference_latency_s": fc["latency_s"],
            }
        except Exception as exc:
            artifact["tests"]["function_calling"] = {"passed": False, "error": str(exc)}

        passed = sum(1 for t in artifact["tests"].values() if t.get("passed"))
        artifact["status"] = "passed" if passed == 3 else ("partial" if passed else "failed")
        return write_runtime_artifact(artifact)


def strip_code_fences(text: str) -> str:
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


def parse_json_with_one_repair(text: str) -> tuple[dict | None, str | None]:
    try:
        return json.loads(text), None
    except json.JSONDecodeError as first_err:
        repaired = _repair_json_once(text)
        try:
            return json.loads(repaired), None
        except json.JSONDecodeError:
            return None, str(first_err)


def _repair_json_once(text: str) -> str:
    """Single constrained repair: trailing commas and unquoted keys."""
    t = text.strip()
    t = re.sub(r",\s*}", "}", t)
    t = re.sub(r",\s*]", "]", t)
    t = re.sub(r"(\{|,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', t)
    return t


def extract_tool_call(raw: str) -> dict[str, Any] | None:
    """Extract function call from model output."""
    cleaned = strip_code_fences(raw)
    data, _ = parse_json_with_one_repair(cleaned)
    if isinstance(data, dict):
        if "name" in data and "arguments" in data:
            return data
        if "function_call" in data:
            fc = data["function_call"]
            args = fc.get("arguments", {})
            if isinstance(args, str):
                args, _ = parse_json_with_one_repair(args)
            return {"name": fc.get("name"), "arguments": args or {}}
        if "tool_calls" in data and data["tool_calls"]:
            tc = data["tool_calls"][0]
            fn = tc.get("function", tc)
            args = fn.get("arguments", {})
            if isinstance(args, str):
                args, _ = parse_json_with_one_repair(args)
            return {"name": fn.get("name"), "arguments": args or {}}

    # Pattern: calculate_fee_percentage({...})
    match = re.search(
        r"(normalize_financial_term|calculate_total_repayment|calculate_fee_percentage|"
        r"compare_normalized_terms|generate_clarification_questions)\s*\(\s*(\{.*?\})\s*\)",
        raw,
        re.DOTALL,
    )
    if match:
        args, _ = parse_json_with_one_repair(match.group(2))
        return {"name": match.group(1), "arguments": args or {}}
    return None
