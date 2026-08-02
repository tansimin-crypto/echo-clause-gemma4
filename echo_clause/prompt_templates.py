"""Prompt templates for Gemma 4 claim extraction and tool use."""

from __future__ import annotations

CLAIM_EXTRACTION_SYSTEM = """You are EchoClause, an evidence-grounded financial claim extractor.
Extract structured claims from the provided evidence (image, audio, or text).
Return ONLY valid JSON matching this schema:
{
  "claims": [
    {
      "claim_id": "unique_id",
      "source_id": "source_name",
      "source_type": "advertisement|sales_audio|support_chat|contract|other",
      "field": "principal|interest_rate|platform_fee|processing_fee|total_repayment|repayment_term_days|late_fee|late_fee_frequency|automatic_debit|automatic_renewal|cancellation_fee|prepayment_penalty",
      "raw_value": "exact text from evidence",
      "normalized_value": null,
      "currency": "USD or null",
      "unit": null,
      "frequency": null,
      "polarity": "positive|negative|neutral",
      "evidence_text": "verbatim quote",
      "page_number": null,
      "timestamp_start": null,
      "timestamp_end": null,
      "confidence": 0.0-1.0,
      "explicitness": "explicit|implicit|inferred",
      "needs_review": false
    }
  ]
}
Do NOT provide legal advice. Do NOT judge fraud or legality.
EchoClause compares representations across supplied evidence. It does not provide legal advice or determine legal enforceability.
"""

IMAGE_EXTRACTION_USER = (
    "Extract all financial claims from this image for Nuru Credit (fictional demo). "
    "Include principal, fees, interest, repayment terms, late fees, and automatic debit mentions."
)

AUDIO_EXTRACTION_USER = (
    "Extract all financial claims from this sales pitch audio for Nuru Credit (fictional demo). "
    "Include repayment amount, processing charges, and late fee terms."
)

FUNCTION_CALL_DEMO_USER = (
    "The advertisement promises no hidden fees but the contract shows a platform fee of "
    "$150 on $1,000 principal. Call calculate_fee_percentage with fee_amount=150 "
    "and principal=1000 to compute the hidden fee percentage."
)


def build_image_messages(source_id: str) -> list[dict]:
    return [
        {"role": "system", "content": CLAIM_EXTRACTION_SYSTEM},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": IMAGE_EXTRACTION_USER + f" Source: {source_id}"},
                {"type": "image"},
            ],
        },
    ]


def build_audio_messages(source_id: str) -> list[dict]:
    return [
        {"role": "system", "content": CLAIM_EXTRACTION_SYSTEM},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": AUDIO_EXTRACTION_USER + f" Source: {source_id}"},
                {"type": "audio"},
            ],
        },
    ]


def build_function_call_messages() -> list[dict]:
    return [
        {"role": "system", "content": CLAIM_EXTRACTION_SYSTEM},
        {"role": "user", "content": FUNCTION_CALL_DEMO_USER},
    ]
