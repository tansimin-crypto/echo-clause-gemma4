#!/usr/bin/env python3
"""Generate synthetic Nuru Credit demo assets and frozen gold.json."""

from __future__ import annotations

import json
import math
import struct
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "demo_case"


def _font(size: int = 28):
    for name in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_advertisement(path: Path) -> None:
    img = Image.new("RGB", (800, 600), color=(20, 60, 120))
    draw = ImageDraw.Draw(img)
    font_l = _font(36)
    font_s = _font(24)
    draw.text((40, 40), "Nuru Credit", fill=(255, 255, 255), font=font_l)
    lines = [
        "Borrow $1,000 today",
        "0% interest",
        "No hidden fees",
        "Repay in 30 days",
    ]
    y = 140
    for line in lines:
        draw.text((40, y), line, fill=(255, 220, 80), font=font_s)
        y += 50
    img.save(path)


def make_support_chat(path: Path) -> None:
    img = Image.new("RGB", (700, 500), color=(240, 240, 245))
    draw = ImageDraw.Draw(img)
    font = _font(22)
    draw.rounded_rectangle((30, 30, 670, 470), radius=20, fill=(255, 255, 255))
    draw.text((50, 50), "Nuru Credit Support", fill=(30, 30, 30), font=font)
    draw.rounded_rectangle((50, 120, 520, 200), radius=15, fill=(220, 235, 255))
    draw.text(
        (70, 145),
        "There is no automatic debit after repayment",
        fill=(20, 20, 20),
        font=font,
    )
    img.save(path)


def make_contract(path: Path) -> None:
    img = Image.new("RGB", (800, 900), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_h = _font(30)
    font = _font(22)
    draw.text((40, 30), "Nuru Credit — Loan Agreement (Synthetic Demo)", fill=(0, 0, 0), font=font_h)
    clauses = [
        "Principal: $1,000",
        "Platform fee: $150",
        "Total repayment: $1,150",
        "Late fee: 5% of outstanding balance per week",
        "Repayment term: 21 days",
        "Automatic debit authorization: enabled",
    ]
    y = 120
    for line in clauses:
        draw.text((40, y), line, fill=(30, 30, 30), font=font)
        y += 45
    img.save(path)


def make_sales_pitch_wav(path: Path) -> None:
    """Synthetic speech-like tones (not real voice — demo placeholder)."""
    sample_rate = 16000
    duration = 4.0
    n_samples = int(sample_rate * duration)
    freq = 440.0
    frames = []
    for i in range(n_samples):
        t = i / sample_rate
        # Simple AM-modulated tone to simulate speech envelope
        amp = 0.3 * (0.5 + 0.5 * math.sin(2 * math.pi * 3 * t))
        val = amp * math.sin(2 * math.pi * freq * t)
        frames.append(int(max(-1, min(1, val)) * 32767))

    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{len(frames)}h", *frames))


def make_transcript(path: Path) -> None:
    text = (
        "You will repay exactly $1,000.\n"
        "There are no processing charges.\n"
        "Late payment is only a one-time $20 fee.\n"
    )
    path.write_text(text, encoding="utf-8")


def make_gold(path: Path) -> None:
    gold = {
        "case_id": "nuru_credit_demo",
        "company": "Nuru Credit",
        "disclaimer": (
            "EchoClause compares representations across supplied evidence. "
            "It does not provide legal advice or determine legal enforceability."
        ),
        "min_contradiction_count": 5,
        "expected_contradictions": [
            {
                "id": "c1_platform_fee",
                "canonical_field": "platform_fee",
                "promise_summary": "No hidden fees (advertisement)",
                "contract_summary": "Platform fee $150",
                "expected_status": "CONTRADICTED",
                "severity": "high",
            },
            {
                "id": "c2_total_repayment",
                "canonical_field": "total_repayment",
                "promise_summary": "Repay $1,000 (ad + sales pitch)",
                "contract_summary": "Total repayment $1,150",
                "expected_status": "CONTRADICTED",
                "severity": "critical",
            },
            {
                "id": "c3_late_fee",
                "canonical_field": "late_fee",
                "promise_summary": "One-time $20 late fee (sales pitch)",
                "contract_summary": "5% of outstanding balance per week",
                "expected_status": "CONTRADICTED",
                "severity": "high",
            },
            {
                "id": "c4_term_days",
                "canonical_field": "repayment_term_days",
                "promise_summary": "Repay in 30 days (advertisement)",
                "contract_summary": "Repayment term 21 days",
                "expected_status": "CONTRADICTED",
                "severity": "medium",
            },
            {
                "id": "c5_automatic_debit",
                "canonical_field": "automatic_debit",
                "promise_summary": "No automatic debit after repayment (support chat)",
                "contract_summary": "Automatic debit authorization enabled",
                "expected_status": "CONTRADICTED",
                "severity": "high",
            },
        ],
    }
    path.write_text(json.dumps(gold, indent=2), encoding="utf-8")


def make_recorded_claims(path: Path) -> None:
    """Frozen Gemma replay fixture aligned with demo assets (USD)."""
    recorded = {
        "description": "Claims extracted from Nuru Credit demo assets (Gemma 4 replay fixture)",
        "model_id": "google/gemma-4-E2B-it",
        "claims": [
            {
                "claim_id": "ad_principal",
                "source_id": "advertisement",
                "source_type": "advertisement",
                "field": "principal",
                "raw_value": "Borrow $1,000 today",
                "normalized_value": 1000,
                "currency": "USD",
                "unit": "currency",
                "evidence_text": "Borrow $1,000 today",
                "confidence": 0.95,
                "explicitness": "explicit",
                "needs_review": False,
            },
            {
                "claim_id": "ad_interest",
                "source_id": "advertisement",
                "source_type": "advertisement",
                "field": "interest_rate",
                "raw_value": "0% interest",
                "normalized_value": 0,
                "unit": "percent",
                "evidence_text": "0% interest",
                "confidence": 0.95,
                "explicitness": "explicit",
                "needs_review": False,
            },
            {
                "claim_id": "ad_platform_fee",
                "source_id": "advertisement",
                "source_type": "advertisement",
                "field": "platform_fee",
                "raw_value": "No hidden fees",
                "normalized_value": 0,
                "currency": "USD",
                "unit": "currency",
                "evidence_text": "No hidden fees",
                "confidence": 0.9,
                "explicitness": "explicit",
                "needs_review": False,
            },
            {
                "claim_id": "ad_term",
                "source_id": "advertisement",
                "source_type": "advertisement",
                "field": "repayment_term_days",
                "raw_value": "Repay in 30 days",
                "normalized_value": 30,
                "unit": "days",
                "evidence_text": "Repay in 30 days",
                "confidence": 0.92,
                "explicitness": "explicit",
                "needs_review": False,
            },
            {
                "claim_id": "audio_total",
                "source_id": "sales_pitch",
                "source_type": "sales_audio",
                "field": "total_repayment",
                "raw_value": "You will repay exactly $1,000",
                "normalized_value": 1000,
                "currency": "USD",
                "unit": "currency",
                "evidence_text": "You will repay exactly $1,000",
                "confidence": 0.88,
                "explicitness": "explicit",
                "needs_review": False,
            },
            {
                "claim_id": "audio_processing",
                "source_id": "sales_pitch",
                "source_type": "sales_audio",
                "field": "processing_fee",
                "raw_value": "There are no processing charges",
                "normalized_value": 0,
                "currency": "USD",
                "unit": "currency",
                "evidence_text": "There are no processing charges",
                "confidence": 0.87,
                "explicitness": "explicit",
                "needs_review": False,
            },
            {
                "claim_id": "audio_late_fee",
                "source_id": "sales_pitch",
                "source_type": "sales_audio",
                "field": "late_fee",
                "raw_value": "Late payment is only a one-time $20 fee",
                "normalized_value": 20,
                "currency": "USD",
                "unit": "currency",
                "evidence_text": "Late payment is only a one-time $20 fee",
                "confidence": 0.86,
                "explicitness": "explicit",
                "needs_review": False,
            },
            {
                "claim_id": "chat_auto_debit",
                "source_id": "support_chat",
                "source_type": "support_chat",
                "field": "automatic_debit",
                "raw_value": "There is no automatic debit after repayment",
                "normalized_value": False,
                "unit": "boolean",
                "evidence_text": "There is no automatic debit after repayment",
                "confidence": 0.93,
                "explicitness": "explicit",
                "needs_review": False,
            },
            {
                "claim_id": "contract_principal",
                "source_id": "contract",
                "source_type": "contract",
                "field": "principal",
                "raw_value": "Principal: $1,000",
                "normalized_value": 1000,
                "currency": "USD",
                "unit": "currency",
                "evidence_text": "Principal: $1,000",
                "confidence": 0.98,
                "explicitness": "explicit",
                "needs_review": False,
            },
            {
                "claim_id": "contract_platform_fee",
                "source_id": "contract",
                "source_type": "contract",
                "field": "platform_fee",
                "raw_value": "Platform fee: $150",
                "normalized_value": 150,
                "currency": "USD",
                "unit": "currency",
                "evidence_text": "Platform fee: $150",
                "confidence": 0.98,
                "explicitness": "explicit",
                "needs_review": False,
            },
            {
                "claim_id": "contract_total",
                "source_id": "contract",
                "source_type": "contract",
                "field": "total_repayment",
                "raw_value": "Total repayment: $1,150",
                "normalized_value": 1150,
                "currency": "USD",
                "unit": "currency",
                "evidence_text": "Total repayment: $1,150",
                "confidence": 0.98,
                "explicitness": "explicit",
                "needs_review": False,
            },
            {
                "claim_id": "contract_late_fee",
                "source_id": "contract",
                "source_type": "contract",
                "field": "late_fee",
                "raw_value": "Late fee: 5% of outstanding balance per week",
                "normalized_value": 5,
                "unit": "percent",
                "frequency": "weekly",
                "evidence_text": "Late fee: 5% of outstanding balance per week",
                "confidence": 0.97,
                "explicitness": "explicit",
                "needs_review": False,
            },
            {
                "claim_id": "contract_term",
                "source_id": "contract",
                "source_type": "contract",
                "field": "repayment_term_days",
                "raw_value": "Repayment term: 21 days",
                "normalized_value": 21,
                "unit": "days",
                "evidence_text": "Repayment term: 21 days",
                "confidence": 0.97,
                "explicitness": "explicit",
                "needs_review": False,
            },
            {
                "claim_id": "contract_auto_debit",
                "source_id": "contract",
                "source_type": "contract",
                "field": "automatic_debit",
                "raw_value": "Automatic debit authorization: enabled",
                "normalized_value": True,
                "unit": "boolean",
                "evidence_text": "Automatic debit authorization: enabled",
                "confidence": 0.98,
                "explicitness": "explicit",
                "needs_review": False,
            },
        ],
    }
    path.write_text(json.dumps(recorded, indent=2), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    make_advertisement(OUT / "advertisement.png")
    make_support_chat(OUT / "support_chat.png")
    make_contract(OUT / "contract.png")
    make_sales_pitch_wav(OUT / "sales_pitch.wav")
    make_transcript(OUT / "sales_pitch.txt")
    make_gold(OUT / "gold.json")
    make_recorded_claims(OUT / "recorded_claims.json")
    print(f"Generated demo assets in {OUT}")


if __name__ == "__main__":
    main()
